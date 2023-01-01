"""
Tests for the delegate decorator.
"""

import inspect
from typing import Callable, Set, NamedTuple, Optional, Type

import pytest

from delegatefn import delegate


class TestCase(NamedTuple):
    description: str
    delegatee: Callable
    delegator: Callable
    expected: Optional[Callable] = None
    raises: Optional[Type[Exception]] = None
    kwonly: bool = True
    delegate_docstring: bool = True
    ignore: Set[str] = set()


# Define the delegatee, delegator, and expected functions for each test case.
test_cases = [
    TestCase(
        description="Add the parameters of the delegatee function to the delegator function.",
        delegatee=lambda a: None,
        delegator=lambda b, **kwargs: None,
        expected=lambda b, *, a: None,
    ),
    TestCase(
        description="Convert the parameters of the delegatee function to keyword-only arguments.",
        delegatee=lambda a: None,
        delegator=lambda b: None,
        expected=lambda b, *, a: None,
        kwonly=True,
    ),
    TestCase(
        description="Set the docstring of the delegator function to the docstring of the delegatee function.",
        delegatee=lambda a: None,
        delegator=lambda b: None,
        expected=lambda b, *, a: None,
        delegate_docstring=True,
    ),
    TestCase(
        description="Ignore the specified parameters of the delegatee function.",
        delegatee=lambda a, b: None,
        delegator=lambda c: None,
        expected=lambda c, *, a: None,
        ignore={"b"},
    ),
    TestCase(
        description="Raise a ValueError if the delegator function and the delegatee function have parameters with the same name.",
        delegatee=lambda x: None,
        delegator=lambda x: None,
        raises=ValueError,
    ),
    TestCase(
        description="Retain **kwargs.",
        delegatee=lambda a, b, c, **kwargs: None,
        delegator=lambda **kwargs: None,
        expected=lambda *, a, b, c, **kwargs: None,
    ),
    TestCase(
        delegatee=lambda a, b, c: None,
        delegator=lambda **kwargs: None,
        expected=lambda *, a, b, c: None,
        description="Simple case with **kwargs.",
    ),
    TestCase(
        description="Simple case with **kwargs and delegate_docstring=False.",
        delegatee=lambda a, b, c: None,
        delegator=lambda **kwargs: None,
        expected=lambda *, a, b, c: None,
        delegate_docstring=False,
    ),
    TestCase(
        description="Positional-or-keyword argument before **kwargs.",
        delegatee=lambda b: None,
        delegator=lambda x, **kwargs: None,
        expected=lambda x, *, b: None,
    ),
    TestCase(
        description="Retain **kwargs 2.",
        delegatee=lambda a, b, c, **kwargs: None,
        delegator=lambda **kwargs: None,
        expected=lambda *, a, b, c, **kwargs: None,
    ),
    TestCase(
        description="Ignore a parameter.",
        delegatee=lambda a, b, c: None,
        delegator=lambda **kwargs: None,
        expected=lambda *, a, c: None,
        ignore={"b"},
    ),
]


# Run the tests.
@pytest.mark.parametrize("description, delegatee, delegator, expected, raises, kwonly, delegate_docstring, ignore", test_cases)
def test_delegate(
    description: str, delegatee: Callable, delegator: Callable, expected: Optional[Callable],
    raises: Optional[Type[Exception]], kwonly: bool, delegate_docstring: bool, ignore: Set[str]
):
    delegatee.__doc__ = "Delegatee docstring."
    delegator.__doc__ = "Delegator docstring."

    decorated_delegator_maker = lambda: delegate(delegatee, kwonly=kwonly, delegate_docstring=delegate_docstring, ignore=ignore)(delegator)
    if raises is not None:
        with pytest.raises(raises, match=f"Duplicate parameter names in .*{', '.join(ignore)}.*"):
            decorated_delegator_maker()
    else:
        decorated_delegator = decorated_delegator_maker()

        if expected is not None:
            # Decorate the delegator function with the delegate decorator, using the specified parameters.

            # Check that the decorated delegator function has the expected signature.
            assert inspect.signature(decorated_delegator) == inspect.signature(expected)

            # Check that the decorated delegator function has the expected docstring, if applicable.
            if delegate_docstring:
                assert decorated_delegator.__doc__ == delegatee.__doc__
            else:
                assert decorated_delegator.__doc__ == delegator.__doc__
