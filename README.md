# delegatefn

A Python package for adding the parameters of a delegatee function to a delegator function, while keeping the original parameters of the delegator function.

## Installation

To install `delegatefn`, use `pip`:

```bash
pip install delegatefn
```

## Usage

To use the `delegate` decorator function, import it from `delegatefn`:

```python
from delegatefn import delegate
```

Then, decorate your delegator function with the `delegate` decorator, passing in the delegatee function as an argument:

```python
@delegate(delegatee)
def delegator(c: int, d: int, e: int, **kwargs):
    ...
```

The delegator function will now have the parameters of delegatee added to it, while keeping its original parameters.

You can also customize the behavior of the `delegate` decorator by passing in the following keyword arguments:

- `kwonly`: A boolean value indicating whether the parameters of delegatee should be converted to keyword-only arguments. The default value is `True`.

- `delegate_docstring`: A boolean value indicating whether the docstring of delegatee should be used as the docstring of the delegator function. The default value is `True`.

- `ignore`: A set of strings containing the names of the parameters of delegatee that should be ignored. The default value is an empty set.

Here is an example of how to use these keyword arguments:

```python
@delegate(delegatee, kwonly=True, delegate_docstring=True, ignore={"a", "b"})
def delegator(c: int, d: int, e: int, **kwargs):
    ...
```

## Example

Here is an example of how to use the `delegate` decorator:

```python
from delegatefn import delegate

def delegatee(a: int, b: int, **kwargs):
    ...

@delegate(delegatee)
def delegator(c: int, d: int, e: int, **kwargs):
    ...
```

The delegator function will now have the parameters `a: int`, `b: int`, and `kwargs` added to it, in addition to its original parameters `c: int`, `d: int`, and `e: int`.

## Acknowledgements

This approach was inspired by [fast.ai](https://www.fast.ai/posts/2019-08-06-delegation.html).
