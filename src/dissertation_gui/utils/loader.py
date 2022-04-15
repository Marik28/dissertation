import pandas as pd

from ..settings import settings

characteristics_dir = settings.base_dir.parent / "data" / "real_sensors"


def load_characteristics(sensor: str) -> pd.DataFrame:
    """Возвращает датафрейм с характеристикой переданного датчика для симуляции"""
    return pd.read_csv(
        characteristics_dir / f"{sensor}.csv",
        index_col="temp",
    )
