from numbers import Number
from typing import Iterable

import numpy as np
import pandas as pd


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


def fill_empty(data: pd.DataFrame) -> dict:
    data_as_dict = {int(row["T"]): row["R"] for _, row in data.iterrows()}
    temperatures = list(data_as_dict.keys())
    new_values = {temp: None for temp in range(min(temperatures), max(temperatures) + 1)}
    for temp in sorted(list(new_values)):
        res = data_as_dict.get(temp)
        new_values[temp] = res
    for temp in sorted(list(new_values)):
        res = new_values.get(temp)
        if res is None:
            prev_r = new_values[temp - 1]
            next_r = new_values[temp + 1]
            mean = round((prev_r + next_r) / 2, 3)
            new_values[temp] = mean
    return new_values


if __name__ == '__main__':
    import doctest

    doctest.testmod()
