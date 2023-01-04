import inspect
from typing import Callable, Set


def delegate(
    delegatee: Callable, *, kwonly: bool = True, delegate_docstring: bool = False, ignore: Set[str] = set()
) -> Callable:
    """
    A decorator function that adds the parameters of a delegatee function to a delegator function,
    while keeping the original parameters of the delegator function.

    Example usage:
        @delegate(delegatee, kwonly=True, delegate_docstring=True, ignore={"a", "b"})
        def delegator(c: int, d: int, e: int, **kwargs):
            ...

    :param delegatee: The function whose parameters will be added to the delegator function.
    :param kwonly: A boolean value indicating whether the parameters of delegatee should be converted to keyword-only arguments.
                        The default value is True.
    :param delegate_docstring: A boolean value indicating whether the docstring of delegatee should be used as the docstring of the delegator function.
                        The default value is True.
    :param ignore: A set of strings containing the names of the parameters of delegatee that should be ignored.
                        The default value is an empty set.
    :return: The decorator function that modifies the delegator function.
    """
    # Retrieve the parameter information of delegatee and filter out the ignored parameters.
    delegatee_params = list(inspect.signature(delegatee).parameters.values())
    delegatee_params = [param for param in delegatee_params if param.name not in ignore]
    # Keep only the positional or keyword parameters of delegatee.
    delegatee_params = [
        param for param in delegatee_params
        if param.kind in (param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY, param.VAR_KEYWORD)
    ]
    # Convert the parameters of delegatee to keyword-only arguments if kwonly is True.
    if kwonly:
        delegatee_params = [
            param.replace(kind=param.KEYWORD_ONLY) if param.kind == param.POSITIONAL_OR_KEYWORD else param
            for param in delegatee_params
        ]

    def decorator(delegator: Callable) -> Callable:
        """
        The decorator function that modifies the delegator function by adding the parameters of delegatee to it.

        :param delegator: The function to be modified.
        :return: The modified delegator function.
        """
        # Retrieve the parameter information of delegator and filter out the VAR_KEYWORD parameter.
        delegator_sig = inspect.signature(delegator)
        delegator_params = [param for param in delegator_sig.parameters.values() if param.kind != param.VAR_KEYWORD]
        # Combine the parameters of delegator and delegatee.
        delegator_params = delegator_params + delegatee_params
        # Check for duplicate parameter names.
        if len(delegator_params) != len(set(param.name for param in delegator_params)):
            raise ValueError(f"Duplicate parameter names in {delegator_params}")
        # Sort the combined parameters based on their type and default value.
        new_delegator_params = sorted(
            delegator_params, key=lambda param: (param.kind, param.default is not inspect.Parameter.empty)
        )
        # Create a new signature for the delegator function.
        new_delegator_sig = delegator_sig.replace(parameters=new_delegator_params)
        delegator.__signature__ = new_delegator_sig
        # Use the docstring of delegatee as the docstring of delegator if delegate_docstring is True.
        if delegate_docstring:
            delegator.__doc__ = delegatee.__doc__
        return delegator

    return decorator
