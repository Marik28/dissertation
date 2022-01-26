from numbers import Number
from typing import Iterable

import numpy as np


def find_nearest(values: Iterable[Number], value: Number) -> Number:
    """
    >>> find_nearest([1, 2.1, 2.12, 2.15, 5], 2.13)
    2.12

    :param values:
    :param value:
    :return: nearest number to given value in given array
    """
    array = np.asarray(values)
    idx = np.abs(array - value).argmin()
    return array[idx]


if __name__ == '__main__':
    import doctest

    doctest.testmod()
