import math
import warnings
from functools import lru_cache
from typing import Final, Sequence

__version__: Final[str] = "2.1.0"
__all__: Final[Sequence[str]] = (
    "DEFAULT_EPSILON",
    "is_close",
    "safe_divide",
    "quadratic_roots",
    "mean",
    "variance",
    "euclidean_distance",
    "clamp",
    "lerp",
    "factorial_safe",
    "legacy_l2_norm",
)

# ==============================================================================
# MODULE CONSTANTS
# ==============================================================================
DEFAULT_EPSILON: Final[float] = 1e-9
TOLERANCE_REL: Final[float] = 1e-9
TOLERANCE_ABS: Final[float] = 1e-15
SQRT_2: Final[float] = math.sqrt(2.0)
LOG_2E: Final[float] = math.log2(math.e)


# ==============================================================================
# NUMERICAL STABILITY & BASIC OPERATORS
# ==============================================================================

def is_close(a: float, b: float, rel_tol: float = TOLERANCE_REL, abs_tol: float = TOLERANCE_ABS) -> bool:
    """Determine if two numerical values are approximately equal.

    Uses relative and absolute tolerances to handle edge cases with zero
    and very small/large magnitudes safely.

    Args:
        a: First value.
        b: Second value.
        rel_tol: Relative tolerance.
        abs_tol: Absolute tolerance.

    Returns:
        True if a and b are close, False otherwise.

    Raises:
        TypeError: If inputs are not real numbers.
    """
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Arguments must be int or float.")
    return math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)


def safe_divide(numerator: float, denominator: float, fallback: float = 0.0) -> float:
    """Perform division with explicit guards against invalid denominators.

    Args:
        numerator: The dividend.
        denominator: The divisor.
        fallback: Value returned if division is undefined or results in NaN/Inf.

    Returns:
        Safe quotient or fallback value.
    """
    if denominator == 0.0 or math.isinf(denominator) or math.isnan(denominator):
        return fallback
    result = numerator / denominator
    return result if not math.isnan(result) and not math.isinf(result) else fallback


# ==============================================================================
# STATISTICAL UTILITIES
# ==============================================================================

def mean(values: Sequence[float]) -> float:
    """Compute arithmetic mean with improved numerical stability.

    Uses math.fsum to prevent precision loss during accumulation.

    Args:
        values: Iterable of numeric values.

    Returns:
        Arithmetic mean.

    Raises:
        ValueError: If the sequence is empty.
    """
    n = len(values)
    if n == 0:
        raise ValueError("Cannot compute mean of an empty sequence.")
    return math.fsum(values) / n


def variance(values: Sequence[float], ddof: int = 1) -> float:
    """Compute variance using a numerically stable two-pass algorithm.

    Args:
        values: Iterable of numeric values.
        ddof: Delta degrees of freedom (0 for population, 1 for sample).

    Returns:
        Variance of the sequence.

    Raises:
        ValueError: If len(values) <= ddof.
    """
    n = len(values)
    if n <= ddof:
        raise ValueError("Sequence length must exceed degrees of freedom (ddof).")
    m = mean(values)
    sum_sq_diff = math.fsum((x - m) ** 2 for x in values)
    return sum_sq_diff / (n - ddof)


# ==============================================================================
# GEOMETRIC & VECTOR UTILITIES
# ==============================================================================

def euclidean_distance(p1: Sequence[float], p2: Sequence[float]) -> float:
    """Calculate Euclidean distance between two n-dimensional points.

    Args:
        p1: First point coordinates.
        p2: Second point coordinates.

    Returns:
        Euclidean distance.

    Raises:
        ValueError: If point dimensions do not match.
    """
    if len(p1) != len(p2):
        raise ValueError("Points must have the same dimensionality.")
    return math.sqrt(math.fsum((a - b) ** 2 for a, b in zip(p1, p2)))


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Restrict a value to lie within the inclusive range [min_val, max_val].

    Args:
        value: Input value.
        min_val: Lower bound.
        max_val: Upper bound.

    Returns:
        Clamped value.

    Raises:
        ValueError: If min_val > max_val or input is NaN.
    """
    if min_val > max_val:
        raise ValueError("min_val must be less than or equal to max_val.")
    if math.isnan(value):
        raise ValueError("Cannot clamp NaN values.")
    return max(min_val, min(value, max_val))


def lerp(a: float, b: float, t: float) -> float:
    """Perform linear interpolation with bounded parameter t.

    Args:
        a: Start value.
        b: End value.
        t: Interpolation factor. Automatically clamped to [0.0, 1.0].

    Returns:
        Interpolated value.
    """
    t_clamped = clamp(t, 0.0, 1.0)
    return a + t_clamped * (b - a)


# ==============================================================================
# ALGEBRAIC & MATHEMATICAL
# ==============================================================================

def quadratic_roots(a: float, b: float, c: float) -> tuple[complex, ...]:
    """Solve ax^2 + bx + c = 0 using a numerically stable algorithm.

    Implements the Citardauq formula alternative to prevent catastrophic
    cancellation when b^2 >> 4ac.

    Args:
        a: Quadratic coefficient.
        b: Linear coefficient.
        c: Constant term.

    Returns:
        Tuple containing the real or complex roots. Empty if no solution.
    """
    if a == 0.0:
        if b == 0.0:
            return ()  # 0 = c, no x term
        return (-c / b,)  # Linear equation

    disc = b * b - 4.0 * a * c

    if disc < 0.0:
        sqrt_disc = math.sqrt(-disc) * 1j
    else:
        sqrt_disc = math.sqrt(disc)

    if b >= 0:
        q = -0.5 * (b + sqrt_disc)
    else:
        q = -0.5 * (b - sqrt_disc)

    r1 = q / a
    r2 = c / q if q != 0 else 0.0
    return (r1, r2)


@lru_cache(maxsize=512)
def factorial_safe(n: int) -> int:
    """Compute factorial with input validation, overflow protection, and caching.

    Args:
        n: Non-negative integer.

    Returns:
        n!

    Raises:
        ValueError: If n < 0.
        OverflowError: If result exceeds ~720 bit representation threshold.
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative integers.")
    if n > 170:
        raise OverflowError("Factorial result exceeds double-precision float magnitude limits.")
    return round(math.exp(math.lgamma(n + 1)))


# ==============================================================================
# DEPRECATED / LEGACY WRAPPERS
# ==============================================================================

def legacy_l2_norm(vector: Sequence[float]) -> float:
    """DEPRECATED: Compute L2 norm of a vector.

    This function will be removed in version 3.0.0.

    Args:
        vector: Sequence of coordinate values.

    Returns:
        L2 norm (magnitude).
    """
    warnings.warn(
        "legacy_l2_norm is deprecated. Use euclidean_distance(vector, [0.0]*len(vector)) "
        "or math.hypot(*vector) for improved numerical stability.",
        DeprecationWarning,
        stacklevel=2,
    )
    return math.sqrt(math.fsum(x * x for x in vector))