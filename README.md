A tiny utility for preserving signature information (parameter names, annotations, and docstrings) when delegating one
function to another.

Works for keyword arguments only; positional arguments are not supported.

# Installation

```bash
pip install delegatefn
```

# Usage

```python
from delegatefn import delegate
import inspect

def foo(a, b, c):
    """This is the docstring for foo."""

@delegate(foo)
def bar(**kwargs):
    """This is the docstring for bar."""

assert inspect.signature(bar) == inspect.signature(foo)

print(inspect.signature(bar))
# (a, b, c)

print(inspect.getdoc(bar))
# This is the docstring for bar.
```

# Limitations

Unfortunately, there isn't an easy way to combine docstrings from multiple functions. Instead, `delegate` lets you
decide which function's docstring to use.

```python
from delegatefn import delegate
import inspect


def foo(a, b, c):
    """This is the docstring for foo."""


@delegate(foo, delegate_docstring=False)
def bar(**kwargs):
    """This is the docstring for bar."""


print(inspect.getdoc(bar))
# This is the docstring for foo.
```
    