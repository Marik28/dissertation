import math
from typing import (
    Iterable,
    Dict,
    Tuple,
    Union,
)

import numpy as np
import pandas as pd

Number = Union[int, float]


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


a = find_nearest([1., 2., 3.], 2)


def fill_empty(data: pd.DataFrame) -> Dict:
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
    new_resistances = map(lambda x: round(x, 2), new_resistances)
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


def remap(x: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def generate_resistance_thermometer_dataframe(
        sensor_characteristics: pd.DataFrame,
        simulation_range: Tuple[int, int],
        digipot1_data: pd.DataFrame,
        digipot2_data: pd.DataFrame,
) -> pd.DataFrame:
    """

    :param sensor_characteristics: Датафрейм с характеристикой датчика
    :param simulation_range: Диапазон температур датчика, который необходимо симулировать. Пример - (-200, 750)
    :param digipot1_data: Датафрейм с характеристикой первого цифрового резистора
    :param digipot2_data: Датафрейм с характеристикой второго цифрового резистора
    """

    # перебираем все возможные сочетания сопротивлений цифровых резисторов
    possible_values = {}
    for _, r1 in digipot1_data.iterrows():
        for _, r2 in digipot2_data.iterrows():
            possible_value = round((r1["resistance"] * r2["resistance"]) / (r1["resistance"] + r2["resistance"]), 5)
            possible_values[possible_value] = [int(r1["code"]), int(r2["code"])]
    min_temp, max_temp = simulation_range

    # найдем диапазон сопротивления, который необходимо симулировать
    min_value = sensor_characteristics.loc[min_temp]["value"]
    max_value = sensor_characteristics.loc[max_temp]["value"]
    _simulation_range = [value for value in possible_values if min_value < value < max_value]

    df = pd.DataFrame()
    df["R"] = sensor_characteristics[sensor_characteristics.index.isin(range(min_temp, max_temp + 1))]["value"]
    df["calc"] = df["R"].apply(lambda x: find_nearest(_simulation_range, x))
    df["error"] = abs(df["R"] - df["calc"])
    df["code"] = df["calc"].apply(lambda x: possible_values[x])
    df["R1_code"] = df["code"].apply(lambda x: x[0])
    df["R2_code"] = df["code"].apply(lambda x: x[1])
    df["R1"] = df["R1_code"].apply(lambda x: digipot1_data[digipot1_data["code"] == x].iloc[0]["resistance"])
    df["R2"] = df["R2_code"].apply(lambda x: digipot2_data[digipot2_data["code"] == x].iloc[0]["resistance"])
    del df["code"]
    return df


def generate_thermocouple_dataframe(
        sensor_characteristics: pd.DataFrame,
        simulation_range: Tuple[int, int],
        mcp_data: pd.DataFrame,
) -> pd.DataFrame:
    min_temp, max_temp = simulation_range

    df = pd.DataFrame()
    df["voltage"] = sensor_characteristics[sensor_characteristics.index.isin(range(min_temp, max_temp + 1))]["value"]
    df["calc"] = df["voltage"].apply(
        lambda x: int(math.copysign(1, x)) * find_nearest(mcp_data["divided_voltage (mV)"], abs(x)),
    )
    df["error"] = abs(df["voltage"] - df["calc"])
    df["code"] = df["calc"].apply(lambda x: int(mcp_data[mcp_data["divided_voltage (mV)"] == abs(x)].iloc[0]["code"]))
    return df


if __name__ == '__main__':
    import doctest

    doctest.testmod()
