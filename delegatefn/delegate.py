import inspect
import sys


def delegate(
    delegatee: callable, kwonly: bool = False, delegate_docstring: bool = True
):
    """
    Delegate kwargs to another function.

    :param delegatee: The function to delegate to.
    :param kwonly: Whether to delegate only keyword arguments.
    :param delegate_docstring: Whether to copy the docstring from the delegated function.
    :return: A decorator that delegates kwargs to the given function.

    ## Example

    >>> from delegatefn import delegate
    >>> import inspect
    >>>
    >>> def foo(a, b, c):
    ...     \"""This is the docstring for foo.\"""
    ...
    >>> @delegate(foo)
    ... def bar(a, b, c):
    ...     pass
    ...
    >>> assert inspect.signature(bar) == inspect.signature(foo)
    >>> print(inspect.signature(bar))
    (a, b, c)
    >>> print(inspect.getdoc(bar))
    This is the docstring for foo.
    """

    def decorator(
        delegator: callable, ):
        "Transfer keyword arguments, including annotations and docstrings, from delegatee to delegator"
        delegatee_sig = inspect.signature(delegatee)
        delegator_sig = inspect.signature(delegator)
        # The last parameter of the delegator must be **kwargs.
        assert delegator_sig.parameters[list(delegator_sig.parameters.keys())[-1]].kind == inspect.Parameter.VAR_KEYWORD
        # Transfer annotations from delegatee to delegator for keyword arguments without annotations in delegator
        for name, param in delegatee_sig.parameters.items():
            if param.kind == param.KEYWORD_ONLY or param.kind == param.POSITIONAL_OR_KEYWORD:
                if name in delegator_sig.parameters and delegator_sig.parameters[name].annotation is inspect._empty:
                    delegator.__annotations__[name] = param.annotation
        # Gather parameters from delegatee
        # Exclude:
        # - arguments that are already defined in delegator
        # - positional-only arguments
        # - if kwonly, positional-or-keyword arguments
        delegatee_kwargs = {}
        for k, v in delegatee_sig.parameters.items():
            if v.kind == v.VAR_KEYWORD:
                delegatee_kwargs[k] = v
            elif k in delegator_sig.parameters:
                continue
            elif v.kind == v.POSITIONAL_OR_KEYWORD:
                if not kwonly:
                    # Make the argument keyword-only
                    delegatee_kwargs[k] = v.replace(kind=v.KEYWORD_ONLY)
            elif v.kind == v.KEYWORD_ONLY:
                delegatee_kwargs[k] = v
        assert all([param.kind != param.VAR_KEYWORD for param in delegatee_sig.parameters.values()]) or any(
            [param.kind == param.VAR_KEYWORD for param in delegatee_kwargs.values()]
        ), f"If the delegatee has a **kwargs parameter, the delegator must have a **kwargs parameter. Got signatures {delegatee_sig} and {delegator_sig} for delegatee and delegator, respectively, but computed signature {inspect.Signature(delegatee_kwargs.values())} for the combined parameters."
        # Add parameters to delegator
        parameters = list(delegator_sig.parameters.values())[:-1] + list(delegatee_kwargs.values())
        # Transfer it
        delegator.__signature__ = delegator_sig.replace(parameters=parameters)
        if delegate_docstring:
            delegator.__doc__ = delegatee.__doc__
        # Return delegator
        return delegator

    return decorator


if "pytest" in sys.modules:
    import pytest


    def make_readme_example_1_fns():
        def foo(a, b, c):
            """This is the docstring for foo."""
            pass

        @delegate(foo)
        def bar(**kwargs):
            pass

        def bar_expected(*, a, b, c):
            """This is the docstring for foo."""

        return foo, bar, bar_expected


    def make_readme_example_2_fns():
        def foo(a, b, c):
            """This is the docstring for foo."""

        @delegate(foo, delegate_docstring=False)
        def bar(**kwargs):
            """This is the docstring for bar."""

        def bar_expected(*, a, b, c):
            """This is the docstring for bar."""

        return foo, bar, bar_expected


    def make_other_1_fns():
        def func(b: int, c=None, *, d, e=None):
            "A docstring"

        @delegate(func)
        def func2(x, **kwargs):
            return func(**kwargs)

        def func2_expected(x, *, b: int, c=None, d, e=None):
            "A docstring"

        return func, func2, func2_expected


    def make_other_2_fns():
        "Retain **kwargs."

        def func(a, b, c, **kwargs):
            "A docstring"

        @delegate(func)
        def func2(**kwargs):
            return func(**kwargs)

        def func2_expected(*, a, b, c, **kwargs):
            "A docstring"

        return func, func2, func2_expected


    @pytest.mark.parametrize(
        "delegatee, delegator, expected",
        [make_readme_example_1_fns(), make_readme_example_2_fns(), make_other_1_fns(), make_other_2_fns(), ]
    )
    def test_delegate(delegatee, delegator, expected):
        assert inspect.signature(delegator) == inspect.signature(expected)
