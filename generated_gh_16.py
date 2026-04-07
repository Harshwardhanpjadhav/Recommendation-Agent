"""Math utilities module containing only addition functionality.

This module provides a single, robust function for adding two numbers.
All other mathematical operations have been removed to focus exclusively
on addition functionality as requested.
"""

from __future__ import annotations

from typing import Union


def add(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """Add two numbers and return the result.

    This function adds two numeric values (integers or floating-point numbers)
    and returns their sum. It includes type validation to ensure both inputs
    are valid numeric types.

    Args:
        a: The first number to add. Must be an int or float.
        b: The second number to add. Must be an int or float.

    Returns:
        The sum of a and b. Returns an int if both inputs are ints,
        otherwise returns a float.

    Raises:
        TypeError: If either a or b is not an int or float.

    Examples:
        >>> add(2, 3)
        5
        >>> add(2.5, 3.7)
        6.2
        >>> add(-1, 1)
        0
        >>> add(0, 0)
        0
        >>> add(1000000000000, 1)
        1000000000001
        >>> add(1.5, 2)
        3.5
    """
    if not isinstance(a, (int, float)):
        raise TypeError(f"First argument must be int or float, got {type(a).__name__}")
    if not isinstance(b, (int, float)):
        raise TypeError(f"Second argument must be int or float, got {type(b).__name__}")
    
    return a + b
```