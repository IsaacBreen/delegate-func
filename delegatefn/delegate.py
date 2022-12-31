import inspect
from typing import Callable, Set


def delegate(delegatee: Callable, *, kwonly: bool = True, delegate_docstring: bool = True, ignore: Set[str] = set()):
    """
    A decorator function that adds the parameters of a delegatee function to a delegator function,
    while keeping the original parameters of the delegator function.

    :param delegatee: The function whose parameters will be added to the delegator function.
    :param kwonly: A boolean value indicating whether the parameters of delegatee should be converted to keyword-only arguments.
                        The default value is True.
    :param delegate_docstring: A boolean value indicating whether the docstring of delegatee should be used as the docstring of the delegator function.
                        The default value is True.
    :param ignore: A set of strings containing the names of the parameters of delegatee that should be ignored.
                        The default value is an empty set.
    """
    # Retrieve the parameter information of delegatee and filter out the ignored parameters.
    delegatee_params = list(inspect.signature(delegatee).parameters.values())
    delegatee_params = filter(lambda param: param.name not in ignore, delegatee_params)
    # Keep only the positional or keyword parameters of delegatee.
    delegatee_params = filter(
        lambda param: param.kind in (param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY, param.VAR_KEYWORD),
        delegatee_params
    )
    # Convert the parameters of delegatee to keyword-only arguments if kwonly is True.
    if kwonly:
        delegatee_params = map(
            lambda param: param.replace(
                kind=param.KEYWORD_ONLY
            ) if param.kind == param.POSITIONAL_OR_KEYWORD else param, delegatee_params
        )

    def decorator(delegator: Callable):
        """
        The decorator function that modifies the delegator function by adding the parameters of delegatee to it.

        :param delegator: The function to be modified.
        """
        # Retrieve the parameter information of delegator and filter out the VAR_KEYWORD parameter.
        delegator_sig = inspect.signature(delegator)
        delegator_params = list(delegator_sig.parameters.values())
        delegator_params = filter(lambda param: param.kind != param.VAR_KEYWORD, delegator_params)
        # Combine the parameters of delegator and delegatee.
        delegator_params = [*delegator_params, *delegatee_params]
        # Check for duplicate parameter names.
        if len(delegator_params) != len(set([param.name for param in delegator_params])):
            raise ValueError(f"Duplicate parameter names in {delegator_params}")
        # Sort the combined parameters based on their type and default value.
        new_delegator_params = sorted(
            delegator_params, key=lambda param: (param.kind, param.default is not inspect.Parameter.empty)
        )
        # Create a new signature for the delegator function.
        new_delegator_sig = delegator_sig.replace(parameters=new_delegator_params)
        delegator.signature = new_delegator_sig
        # Use the docstring of delegatee as the docstring of delegator if delegate_docstring is True.
        if delegate_docstring:
            delegator.doc = delegatee.doc
        return delegator

    return decorator
