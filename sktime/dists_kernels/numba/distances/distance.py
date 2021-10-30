# -*- coding: utf-8 -*-
"""Compute the distance between two timeseries."""

from typing import Callable, Union

import numpy as np

from sktime.dists_kernels._utils import (
    to_numba_pairwise_timeseries,
    to_numba_timeseries,
)
from sktime.dists_kernels.numba.distances._euclidean_distance import _EuclideanDistance
from sktime.dists_kernels.numba.distances._numba_utils import (
    _compute_distance,
    _compute_pairwise_distance,
)
from sktime.dists_kernels.numba.distances._resolve_metric import _resolve_metric
from sktime.dists_kernels.numba.distances._squared_distance import _SquaredDistance
from sktime.dists_kernels.numba.distances.base import (
    DistanceCallable,
    MetricInfo,
    NumbaDistance,
)
from sktime.dists_kernels.numba.distances.dtw_based._dtw_distance import _DtwDistance
from sktime.dists_kernels.numba.distances.dtw_based.lower_bounding import LowerBounding


def dtw_distance(
    x: np.ndarray,
    y: np.ndarray,
    lower_bounding: Union[LowerBounding, int] = LowerBounding.NO_BOUNDING,
    window: int = 2,
    itakura_max_slope: float = 2.0,
    custom_distance: DistanceCallable = _SquaredDistance().distance_factory,
    bounding_matrix: np.ndarray = None,
    **kwargs: dict,
):
    r"""Compute the dynamic time warping (Dtw) distance between two timeseries.

    Dtw distance is supported for 1d, 2d and 3d arrays.

    Originally put forward in [1]_ dtw goal is to compute a more accurate distance
    between two timeseries by considering their alignments during the calculation. This
    is done by measuring the distance (normally using Euclidean) between two timeseries
    and then generate a warping path to 'realign' the two timeseries thereby creating
    a path between the two that accounts for alignment.

    Mathematically dtw can be defined as:

    .. math::
        dtw(x, y) = \sqrt{\sum_{(i, j) \in \pi} \|x_{i} - y_{j}\|^2}


    Parameters
    ----------
    x: np.ndarray (2d array)
        First timeseries.
    y: np.ndarray (2d array)
        Second timeseries.
    lower_bounding: LowerBounding or int, defaults = LowerBounding.NO_BOUNDING
        Lower bounding technique to use.
    window: int, defaults = 2
        Integer that is the radius of the sakoe chiba window (if using Sakoe-Chiba
        lower bounding).
    itakura_max_slope: float, defaults = 2.
        Gradient of the slope for itakura parallelogram (if using Itakura
        Parallelogram lower bounding).
    custom_distance: Callable[[np.ndarray, np.ndarray], float],
                    defaults = squared_distance
        Distance function to used to compute distance between aligned timeseries.
    bounding_matrix: np.ndarray (2d array)
        Custom bounding matrix to use. If defined then other lower_bounding params
        and creation are ignored. The matrix should be structure so that indexes
        considered in bound should be the value 0. and indexes outside the bounding
        matrix should be infinity.
    kwargs: dict
        Extra arguments for custom distance should be put in the kwargs. See the
        documentation for the distance for kwargs.

    Returns
    -------
    distance: float
        Dtw distance between the two timeseries.

    Raises
    ------
    ValueError
        If the sakoe_chiba_window_radius is not an integer.
        If the itakura_max_slope is not a float or int.
        If the value of x or y provided is not a numpy array.
        If the value of x or y has more than 3 dimensions.
        If a metric string provided, and is not a defined valid string.
        If a metric object (instance of class) is provided and doesn't inherit from
        NumbaDistance.
        If a resolved metric is not no_python compiled.
        If the metric type cannot be determined

    References
    ----------
    .. [1] H. Sakoe, S. Chiba, "Dynamic programming algorithm optimization for
           spoken word recognition," IEEE Transactions on Acoustics, Speech and
           Signal Processing, vol. 26(1), pp. 43--49, 1978.
    """
    format_kwargs = {
        "lower_bounding": lower_bounding,
        "window": window,
        "itakura_max_slope": itakura_max_slope,
        "custom_distance": custom_distance,
        "bounding_matrix": bounding_matrix,
    }
    format_kwargs = {**format_kwargs, **kwargs}

    return distance(x, y, metric="dtw", **format_kwargs)


def squared_distance(x: np.ndarray, y: np.ndarray, **kwargs: dict) -> float:
    r"""Compute the Squared distance between two timeseries.

    Squared distance is supported for 1d, 2d and 3d arrays.

    The squared distance between two timeseries is defined as:

    .. math::
        sd(x, y) = \sum_{i=1}^{n} (x_i - y_i)^2

    Parameters
    ----------
    x: np.ndarray (1d, 2d or 3d)
        First timeseries.
    y: np.ndarray (1d, 2d or 3d)
        Second timeseries.
    kwargs: dict
        Extra kwargs. For squared there are none however, this is kept for
        consistency.

    Returns
    -------
    distance: float
        Squared distance between the two timeseries.

    Raises
    ------
    ValueError
        If the value of x or y provided is not a numpy array.
        If the value of x or y has more than 3 dimensions.
        If a metric string provided, and is not a defined valid string.
        If a metric object (instance of class) is provided and doesn't inherit from
        NumbaDistance.
        If a resolved metric is not no_python compiled.
        If the metric type cannot be determined.
    """
    return distance(x, y, metric="squared", **kwargs)


def euclidean_distance(x: np.ndarray, y: np.ndarray, **kwargs: dict) -> float:
    r"""Compute the Euclidean distance between two timeseries.

    Euclidean distance is supported for 1d, 2d and 3d arrays.

    The euclidean distance between two timeseries is defined as:

    .. math::
        ed(x, y) = \sqrt{\sum_{i=1}^{n} (x_i - y_i)^2}

    Parameters
    ----------
    x: np.ndarray (1d, 2d or 3d)
        First timeseries.
    y: np.ndarray (1d, 2d or 3d)
        Second timeseries.
    kwargs: dict
        Extra kwargs. For euclidean there are none however, this is kept for
        consistency.

    Returns
    -------
    distance: float
        Euclidean distance between the two timeseries.

    Raises
    ------
    ValueError
        If the value of x or y provided is not a numpy array.
        If the value of x or y has more than 3 dimensions.
        If a metric string provided, and is not a defined valid string.
        If a metric object (instance of class) is provided and doesn't inherit from
        NumbaDistance.
        If a resolved metric is not no_python compiled.
        If the metric type cannot be determined.
    """
    return distance(x, y, metric="euclidean", **kwargs)


def distance(
    x: np.ndarray,
    y: np.ndarray,
    metric: Union[
        str,
        Callable[
            [np.ndarray, np.ndarray, dict], Callable[[np.ndarray, np.ndarray], float]
        ],
        Callable[[np.ndarray, np.ndarray], float],
        NumbaDistance,
    ],
    **kwargs: dict,
) -> float:
    """Compute the distance between two timeseries.

    This function works for 1d, 2d and 3d timeseries. No matter how many dimensions
    passed, a single float will always be returned. If you want the distance between
    each timeseries individually look at the pairwise_distance function instead.

    Parameters
    ----------
    x: np.ndarray (1d, 2d or 3d array)
        First timeseries.
    y: np.ndarray (1d, 2d or 3d array)
        Second timeseries.
    metric: str or Callable or NumbaDistance
        The distance metric to use.
        If a string is given, the value must be one of the following strings:

        'euclidean', 'squared', 'dtw.

        If callable then it has to be a distance factory or numba distance callable.
        If the distance takes kwargs then a distance factory should be provided. The
        distance factory takes the form:

        Callable[
            [np.ndarray, np.ndarray, bool, dict],
            Callable[[np.ndarray, np.ndarray], float]
        ]

        and should validate the kwargs, and return a no_python callable described
        above as the return.

        If a no_python callable provided it should take the form:

        Callable[
            [np.ndarray, np.ndarray],
            float
        ],
    kwargs: dict, optional
        Extra arguments for metric. Refer to each metric documentation for a list of
        possible arguments.

    Returns
    -------
    float
        Distance between the two timeseries.

    Raises
    ------
    ValueError
        If the value of x or y provided is not a numpy array.
        If the value of x or y has more than 3 dimensions.
        If a metric string provided, and is not a defined valid string.
        If a metric object (instance of class) is provided and doesn't inherit from
        NumbaDistance.
        If a resolved metric is not no_python compiled.
        If the metric type cannot be determined.
    """
    _x = to_numba_timeseries(x)
    _y = to_numba_timeseries(y)

    _metric_callable = distance_factory(x, y, metric=metric, **kwargs)

    return _compute_distance(_x, _y, _metric_callable)


def distance_factory(
    x: np.ndarray,
    y: np.ndarray,
    metric: Union[
        str,
        Callable[
            [np.ndarray, np.ndarray, dict], Callable[[np.ndarray, np.ndarray], float]
        ],
        Callable[[np.ndarray, np.ndarray], float],
        NumbaDistance,
    ],
    **kwargs: dict,
) -> DistanceCallable:
    """Create a no_python distance callable.

    This function works for 1d, 2d and 3d timeseries.

    Parameters
    ----------
    x: np.ndarray (1d, 2d or 3d array)
        First timeseries.
    y: np.ndarray (1d, 2d or 3d array)
        Second timeseries.
    metric: str or Callable or NumbaDistance
        The distance metric to use.
        If a string is given, the value must be one of the following strings:

        'euclidean', 'squared', 'dtw.

        If callable then it has to be a distance factory or numba distance callable.
        If the distance takes kwargs then a distance factory should be provided. The
        distance factory takes the form:

        Callable[
            [np.ndarray, np.ndarray, bool, dict],
            Callable[[np.ndarray, np.ndarray], float]
        ]

        and should validate the kwargs, and return a no_python callable described
        above as the return.

        If a no_python callable provided it should take the form:

        Callable[
            [np.ndarray, np.ndarray],
            float
        ],
    kwargs: dict, optional
        Extra arguments for metric. Refer to each metric documentation for a list of
        possible arguments.

    Returns
    -------
    Callable[[np.ndarray, np.ndarray], float]]
        No_python compiled distance resolved from the metric input.

    Raises
    ------
    ValueError
        If the value of x or y provided is not a numpy array.
        If the value of x or y has more than 3 dimensions.
        If a metric string provided, and is not a defined valid string.
        If a metric object (instance of class) is provided and doesn't inherit from
        NumbaDistance.
        If a resolved metric is not no_python compiled.
        If the metric type cannot be determined.
    """
    _x = to_numba_timeseries(x)
    _y = to_numba_timeseries(y)

    return _resolve_metric(metric, _x, _y, _METRIC_INFOS, **kwargs)


def pairwise_distance(
    x: np.ndarray,
    y: np.ndarray,
    metric: Union[
        str,
        Callable[
            [np.ndarray, np.ndarray, dict], Callable[[np.ndarray, np.ndarray], float]
        ],
        Callable[[np.ndarray, np.ndarray], float],
        NumbaDistance,
    ],
    **kwargs: dict,
) -> np.ndarray:
    """Compute the pairwise distance matrix between two timeseries.

    This function works for 1d, 2d and 3d timeseries. No matter the number of dimensions
    passed a 2d array will always be returned.

    Parameters
    ----------
    x: np.ndarray (1d, 2d or 3d array)
        First timeseries.
    y: np.ndarray (1d, 2d or 3d array)
        Second timeseries.
    metric: str or Callable or NumbaDistance
        The distance metric to use.
        If a string is given, the value must be one of the following strings:

        'euclidean', 'squared', 'dtw.

        If callable then it has to be a distance factory or numba distance callable.
        If the distance takes kwargs then a distance factory should be provided. The
        distance factory takes the form:

        Callable[
            [np.ndarray, np.ndarray, bool, dict],
            Callable[[np.ndarray, np.ndarray], float]
        ]

        and should validate the kwargs, and return a no_python callable described
        above as the return.

        If a no_python callable provided it should take the form:

        Callable[
            [np.ndarray, np.ndarray],
            float
        ],
    kwargs: dict, optional
        Extra arguments for metric. Refer to each metric documentation for a list of
        possible arguments.

    Returns
    -------
    np.ndarray (2d of size mxn where m is len(x) and n is len(y)).
        Pairwise distance matrix between the two timeseries.

    Raises
    ------
    ValueError
        If the value of x or y provided is not a numpy array.
        If the value of x or y has more than 3 dimensions.
        If a metric string provided, and is not a defined valid string.
        If a metric object (instance of class) is provided and doesn't inherit from
        NumbaDistance.
        If a resolved metric is not no_python compiled.
        If the metric type cannot be determined.
    """
    _x = to_numba_pairwise_timeseries(x)
    _y = to_numba_pairwise_timeseries(y)
    symmetric = np.array_equal(_x, _y)

    _metric_callable = _resolve_metric(metric, _x, _y, _METRIC_INFOS, **kwargs)
    return _compute_pairwise_distance(_x, _y, symmetric, _metric_callable)


_METRIC_INFOS = [
    MetricInfo(
        canonical_name="euclidean",
        aka={"euclidean", "ed", "euclid", "pythagorean"},
        dist_func=euclidean_distance,
        dist_instance=_EuclideanDistance(),
    ),
    MetricInfo(
        canonical_name="squared",
        aka={"squared"},
        dist_func=squared_distance,
        dist_instance=_SquaredDistance(),
    ),
    MetricInfo(
        canonical_name="dtw",
        aka={"dtw", "dynamic time warping"},
        dist_func=dtw_distance,
        dist_instance=_DtwDistance(),
    ),
]

_METRICS = {info.canonical_name: info for info in _METRIC_INFOS}
_METRIC_ALIAS = dict((alias, info) for info in _METRIC_INFOS for alias in info.aka)
_METRIC_CALLABLES = dict(
    (info.canonical_name, info.dist_func) for info in _METRIC_INFOS
)
_METRICS_NAMES = list(_METRICS.keys())
