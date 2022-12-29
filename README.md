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

assert foo.__doc__ == bar.__doc__ == "This is the docstring for foo."
assert inspect.signature(bar).parameters.keys() == {"a", "b", "c"}
```

# Limitations

Unfortunately, there isn't an easy way to combine docstrings from multiple functions. Instead, `delegate` lets you
decide which function's docstring to use.

```python
from delegatefn import delegate

def foo(a, b, c):
    """This is the docstring for foo."""

@delegate(foo, delegate_docstring=False)
def bar(**kwargs):
    """This is the docstring for bar."""

assert foo.__doc__ != bar.__doc__ == "This is the docstring for bar."
```

# Acknowledgements

This approach was inspired by [fast.ai](https://www.fast.ai/posts/2019-08-06-delegation.html).