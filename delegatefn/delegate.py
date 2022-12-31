import inspect
from typing import Callable, Set

def delegate(delegatee: Callable, *, kwonly: bool = False, delegate_docstring: bool = True, ignore: Set[str] = set()):
    def decorator(delegator: Callable):
        delegatee_sig = inspect.signature(delegatee)
        delegator_sig = inspect.signature(delegator)
        if not any([param.kind == param.VAR_KEYWORD for param in delegator_sig.parameters.values()]):
            raise ValueError("The delegator function must have a **kwargs parameter")
        if any([param.kind == param.VAR_KEYWORD for param in delegatee_sig.parameters.values()]) and not any([param.kind == param.VAR_KEYWORD for param in delegator_sig.parameters.values()]):
            raise ValueError(f"If the delegatee has a **kwargs parameter, the delegator must have a **kwargs parameter. Delegatee: {delegatee}, delegator: {delegator}")
        delegatee_kwargs = {
            name: param for name, param in delegatee_sig.parameters.items()
            if name not in ignore and (param.kind == param.KEYWORD_ONLY or (param.kind == param.POSITIONAL_OR_KEYWORD and name not in ignore))
        }
        for name, param in delegatee_kwargs.items():
            if param.kind == param.VAR_KEYWORD:
                delegatee_kwargs[name] = param
            elif name in delegator_sig.parameters:
                continue
            elif param.kind == param.POSITIONAL_OR_KEYWORD:
                if not kwonly:
                    delegatee_kwargs[name] = param.replace(kind=param.KEYWORD_ONLY)
            elif param.kind == param.KEYWORD_ONLY:
                delegatee_kwargs[name] = param
        delegatee_kwargs.update(delegator_sig.parameters)
        delegatee_kwargs = {k: v for k, v in sorted(delegatee_kwargs.items(), key=lambda item: item[1].kind)}
        if any([param.kind == param.VAR_KEYWORD for param in delegator_sig.parameters.values()]) and not any([param.kind == param.VAR_KEYWORD for param in delegatee_sig.parameters.values()]):
            del delegatee_kwargs["kwargs"]
        delegator_sig = delegator_sig.replace(parameters=delegatee_kwargs.values())
        if delegate_docstring:
            delegator.__doc__ = delegatee.__doc__
        delegator.__signature__ = delegator_sig
        return delegator
    return decorator
