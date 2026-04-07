# File: utilities/__init__.py
"""Mathematical utility functions."""

# File: utilities/math_utils.py
import math


def calculate_circle_area(radius: float) -> float:
    """
    Calculate the area of a circle.

    Args:
        radius: Radius of the circle. Must be a non-negative number.

    Returns:
        The calculated area of the circle.

    Raises:
        ValueError: If radius is negative.
    """
    if radius < 0:
        raise ValueError("Radius cannot be negative.")
    return math.pi * (radius ** 2)