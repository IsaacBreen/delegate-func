import inspect
from typing import Callable, Set


def delegate(delegatee: Callable, *, kwonly: bool = False, delegate_docstring: bool = True, ignore: Set[str] = set(), kwargs_name: str = 'kwargs', default_values: bool = False, preserve_signature: bool = False):
    """
    Delegate kwargs to another function.

    This function returns a decorator that can be used to transfer keyword arguments, including
    annotations and docstrings, from a "delegatee" function to a "delegator" function. The
    delegator function must accept a **kwargs parameter, which will be populated with the
    keyword arguments from the delegatee function.

    :param delegatee: The function to delegate to.
    :param kwonly: Whether to delegate only keyword arguments. If True, any positional or
    keyword arguments in the delegatee function will be converted to keyword-only
    arguments in the delegator function.
    :param delegate_docstring: Whether to copy the docstring from the delegatee function to the
    delegator function.
    :param ignore: A set of argument names to ignore in the delegatee function. These arguments
    will not be included in the delegator function.
    :param kwargs_name: The name of the **kwargs parameter in the delegator function.
    :param default_values: Whether to transfer default values for arguments from the delegatee to the delegator.
    :param preserve_signature: Whether to preserve the function signature of the delegator function.
    :return: A decorator that can be used to delegate kwargs from the delegatee function to the
    delegator function
    """

    def decorator(delegator: Callable):
        """
        Transfer keyword arguments, including annotations and docstrings, from delegatee to delegator.

        Parameters:
            - delegator: The function to delegate to. This function must accept a **kwargs
              parameter.

        Returns:
            The modified delegator function.
        """
        # Get the signature objects for the delegatee and delegator functions
        delegatee_sig = inspect.signature(delegatee)
        delegator_sig = inspect.signature(delegator)

        # Check that the last parameter of the delegator is a **kwargs parameter with the specified name
        assert delegator_sig.parameters[kwargs_name].kind == inspect.Parameter.VAR_KEYWORD, f"The delegator must have a **kwargs parameter named {kwargs_name}."

        # Gather the keyword-only and **kwargs parameters from the delegatee function
        delegatee_kwargs = {}
        for name, param in delegatee_sig.parameters.items():
            # Skip ignored arguments
            if name in ignore:
                continue
            # Transfer annotations from delegatee to delegator for keyword arguments without annotations in delegator
            if param.kind == param.KEYWORD_ONLY or param.kind == param.POSITIONAL_OR_KEYWORD and name not in ignore:
                if name in delegator_sig.parameters and delegator_sig.parameters[name].annotation is inspect._empty:
                    delegator.__annotations__[name] = param.annotation
            # Add **kwargs parameters and keyword-only parameters from delegatee to delegatee_kwargs
            if param.kind == param.VAR_KEYWORD:
                delegatee_kwargs[name] = param
            # Skip arguments that are already defined in the delegator function
            elif name in delegator_sig.parameters:
                continue
            # Convert positional or keyword arguments in the delegatee function to keyword-only arguments
            # if kwonly is True
            elif param.kind == param.POSITIONAL_OR_KEYWORD:
                if not kwonly:
                    delegatee_kwargs[name] = param.replace(kind=param.KEYWORD_ONLY)
            # Add keyword-only arguments from delegatee to delegatee_kwargs
            elif param.kind == param.KEYWORD_ONLY:
                delegatee_kwargs[name] = param
            # Add default values from delegatee to delegatee_kwargs if default_values is True
            elif default_values:
                delegatee_kwargs[name] = param.replace(default=param.default)

        # Check that the delegatee function does not have any **kwargs parameters, or that at least
        # one **kwargs parameter is included in delegatee_kwargs
        assert all([param.kind != param.VAR_KEYWORD for param in delegatee_sig.parameters.values()]) or any(
            [param.kind == param.VAR_KEYWORD for param in delegatee_kwargs.values()]
        ), f"If the delegatee has a **kwargs parameter, the delegator must have a **kwargs parameter. Got signatures {delegatee_sig} and {delegator_sig} for delegatee and delegator, respectively, but computed signature {inspect.Signature(delegatee_kwargs.values())} for the combined parameters."

        # Combine the parameters of the delegator and delegatee functions, with the parameters from
        # the delegatee function coming after the **kwargs parameter in the delegator function
        parameters = list(delegator_sig.parameters.values())[:-1] + list(delegatee_kwargs.values())
        # Update the signature of the delegator function with the combined parameters
        if preserve_signature:
            # Convert the parameters from the delegatee function to default-only parameters
            for name, param in delegatee_kwargs.items():
                parameters[name] = param.replace(kind=param.POSITIONAL_OR_KEYWORD, default=param.default)
        delegator.__signature__ = delegator_sig.replace(parameters=parameters)

        # If delegate_docstring is True, copy the docstring from the delegatee function to the delegator function
        if delegate_docstring:
            delegator.__doc__ = delegatee.__doc__

        # Return the modified delegator function
        return delegator

    # Return the decorator function
    return decorator
