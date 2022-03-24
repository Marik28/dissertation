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


def fill_empty_temperatures(
        data: pd.DataFrame,
        temp_col="T",
        res_col="R",
) -> pd.DataFrame:
    temperatures = list(data[temp_col])
    resistances = list(data[res_col])
    new_temperatures = []
    new_resistances = []
    assert len(temperatures) == len(resistances)
    for index in range(1, len(temperatures)):
        curr_temp = temperatures[index]
        prev_temp = temperatures[index - 1]
        temps_diff = abs(curr_temp - prev_temp)
        for _ in range(temps_diff):
            new_temperatures.append(prev_temp)
            prev_temp += 1

        prev_res = resistances[index - 1]
        curr_res = resistances[index]
        res_step = (curr_res - prev_res) / temps_diff
        for _ in range(temps_diff):
            new_resistances.append(prev_res)
            prev_res += res_step
    new_temperatures.append(temperatures[-1])
    new_resistances.append(resistances[-1])
    return pd.DataFrame({temp_col: new_temperatures, res_col: new_resistances})


def boolean_df(item_lists: pd.DataFrame, unique_items: Iterable[str]) -> pd.DataFrame:
    """Возвращает датафрейм со столбцами из `unique_items` типа bool для каждой записи"""
    # Create empty dict
    bool_dict = {}

    # Loop through all the tags
    for item in unique_items:
        # Apply boolean mask
        bool_dict[item] = item_lists.apply(lambda x: item in x)
    # Return the results as a dataframe
    return pd.DataFrame(bool_dict)


def create_dataframe(
        path_to_pt,
        possible_values: dict,
        values: Iterable[Number],
        step=1000 / 256,
) -> pd.DataFrame:
    df = pd.read_csv(path_to_pt)
    df["calc"] = df["R"].apply(lambda x: find_nearest(values, x))
    df["error"] = abs(df["R"] - df["calc"])
    df["code"] = df["calc"].apply(lambda x: possible_values[x])
    df["R1_code"] = df["code"].apply(lambda x: x[0])
    df["R2_code"] = df["code"].apply(lambda x: x[1])
    df["R3_code"] = df["code"].apply(lambda x: x[2])
    df["R1"] = df["R1_code"].apply(lambda x: step * x + step)
    df["R2"] = df["R2_code"].apply(lambda x: step * x + step)
    df["R3"] = df["R3_code"].apply(lambda x: step * x + step)
    del df["code"]
    return df


def parse_thermocouple_characteristics(df: pd.DataFrame) -> pd.DataFrame:
    df = df[~df.index.isna()]
    df = df.iloc[2:]
    min_value = int(df.index[0])
    voltages = sorted(list(set([float(x) for x in df.values.flatten() if not np.isnan(float(x))])))
    temperatures = [i + min_value for i in range(len(voltages))]
    return pd.DataFrame({"temp": temperatures, "value": voltages})


if __name__ == '__main__':
    import doctest

    doctest.testmod()
