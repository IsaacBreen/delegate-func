import inspect

import pytest

from delegatefn import delegate


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


def make_ignore_fns():
    def func(a, b, c):
        "A docstring"

    @delegate(func, ignore={"a"})
    def func2(**kwargs):
        return func(**kwargs)

    def func2_expected(*, b, c):
        "A docstring"

    return func, func2, func2_expected


@pytest.mark.parametrize(
    "delegatee, delegator, expected",
    [make_readme_example_1_fns(), make_readme_example_2_fns(), make_other_1_fns(), make_other_2_fns(),
        make_ignore_fns()], )
def test_delegate(delegatee, delegator, expected):
    assert inspect.signature(delegator) == inspect.signature(expected)
