def _validate_numeric_array(data):
    """Validate that *data* is a non‑empty sequence of real numbers.

    Parameters
    ----------
    data : Sequence[float|int]
        Input data to validate.

    Returns
    -------
    list[float]
        A list of floats converted from *data*.

    Raises
    ------
    TypeError
        If *data* is not a sequence or contains non‑numeric items.
    ValueError
        If *data* is empty.
    """
    if not hasattr(data, "__iter__"):
        raise TypeError("Input must be an iterable")
    # Convert to list to allow multiple passes and to catch size
    try:
        numeric_data = [float(x) for x in data]
    except (TypeError, ValueError) as exc:
        raise TypeError("All items must be numeric (int or float)") from exc
    if not numeric_data:
        raise ValueError("Input data must not be empty")
    return numeric_data


def _check_finite(values):
    """Ensure all numbers in *values* are finite (no NaN or infinities).

    Parameters
    ----------
    values : list[float]

    Returns
    -------
    list[float]
        The same list, now known to contain only finite numbers.

    Raises
    ------
    ValueError
        If any element is NaN or infinite.
    """
    for v in values:
        if not (float("-inf") < v < float("inf")):
            raise ValueError("All input values must be finite numbers")
    return values


def mean(data):
    """Compute the arithmetic mean of *data*.

    Parameters
    ----------
    data : Sequence[float|int]
        Sample data.

    Returns
    -------
    float
        The mean of the input values.

    Examples
    --------
    >>> mean([1, 2, 3, 4])
    2.5
    """
    numeric_data = _validate_numeric_array(data)
    _check_finite(numeric_data)
    return sum(numeric_data) / len(numeric_data)


def variance(data, ddof=0):
    """Compute the variance of *data*.

    Parameters
    ----------
    data : Sequence[float|int]
        Sample data.
    ddof : int, optional
        "Delta Degrees of Freedom": divisor used is ``N - ddof`` where
        ``N`` is the number of elements. Default is 0 (population variance).

    Returns
    -------
    float
        The variance of the input values.

    Examples
    --------
    >>> variance([1, 2, 3, 4])
    1.25
    >>> variance([1, 2, 3, 4], ddof=1)  # doctest: +ELLIPSIS
    1.666...
    """
    if ddof < 0:
        raise ValueError("ddof must be non-negative")
    numeric_data = _validate_numeric_array(data)
    _check_finite(numeric_data)
    n = len(numeric_data)
    if n - ddof <= 0:
        raise ValueError("Variance undefined for ddof >= sample size")
    m = mean(numeric_data)
    return sum((x - m) ** 2 for x in numeric_data) / (n - ddof)


def std_dev(data, ddof=0):
    """Compute the standard deviation of *data*.

    Parameters
    ----------
    data : Sequence[float|int]
        Sample data.
    ddof : int, optional
        Delta degrees of freedom passed to :func:`variance`.

    Returns
    -------
    float
        Standard deviation.

    Examples
    --------
    >>> std_dev([1, 2, 3, 4])
    1.118033988749895
    """
    return variance(data, ddof=ddof) ** 0.5


def percentile(data, p):
    """Compute the *p*-th percentile of *data* using the nearest‑rank method.

    Parameters
    ----------
    data : Sequence[float|int]
        Sample data.
    p : float
        Percentile to compute, must be in the interval ``[0, 100]``.

    Returns
    -------
    float
        The value at the *p*-th percentile.

    Examples
    --------
    >>> percentile([1, 2, 3, 4, 5], 50)
    3
    >>> percentile([10, 20, 30], 0)
    10
    """
    if not 0 <= p <= 100:
        raise ValueError("Percentile p must be between 0 and 100 inclusive")
    numeric_data = _validate_numeric_array(data)
    _check_finite(numeric_data)
    sorted_data = sorted(numeric_data)
    # Nearest rank: index = ceil(p/100 * N) - 1, but using 0‑based indexing
    n = len(sorted_data)
    # Compute rank as the smallest integer >= p/100 * n
    import math
    rank = math.ceil(p / 100.0 * n) - 1
    # Clamp rank to valid range
    rank = max(0, min(rank, n - 1))
    return sorted_data[rank]


def normalize_vector(vector):
    """Return a unit vector in the direction of *vector*.

    Parameters
    ----------
    vector : Sequence[float|int]
        Input vector (non‑zero).

    Returns
    -------
    list[float]
        Vector scaled to length 1.

    Raises
    ------
    ValueError
        If the input vector is zero‑length.

    Examples
    --------
    >>> normalize_vector([3, 4])
    [0.6, 0.8]
    """
    numeric_vector = _validate_numeric_array(vector)
    _check_finite(numeric_vector)
    norm_sq = sum(x * x for x in numeric_vector)
    if norm_sq == 0:
        raise ValueError("Cannot normalize a zero vector")
    norm = norm_sq ** 0.5
    return [x / norm for x in numeric_vector]


def euclidean_distance(point_a, point_b):
    """Compute the Euclidean distance between two points.

    Parameters
    ----------
    point_a, point_b : Sequence[float|int]
        Coordinates of the two points. Must have the same dimensionality.

    Returns
    -------
    float
        Euclidean distance.

    Examples
    --------
    >>> euclidean_distance([0, 0], [3, 4])
    5.0
    """
    a = _validate_numeric_array(point_a)
    b = _validate_numeric_array(point_b)
    _check_finite(a)
    _check_finite(b)
    if len(a) != len(b):
        raise ValueError("Both points must have the same number of dimensions")
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5