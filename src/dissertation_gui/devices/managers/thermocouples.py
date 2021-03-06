from typing import (
    Optional,
)

import pandas as pd
from loguru import logger

from utils.utils import find_nearest
from .base import SensorManager
from ..mcp_4725 import MCP4725
from ..relay import RelaysController
from ... import tables
from ...types import Number
from ...utils.loader import load_characteristics


class ThermocoupleManager(SensorManager):  # TODO: ТПР(B) не симулируем

    def __init__(self, dac: MCP4725, relays: RelaysController):
        self._dac = dac
        self._df: Optional[pd.DataFrame] = None
        self._relays = relays

    def _calculate_code(self, temperature: int) -> int:
        _temperature = round(temperature)
        if self._df is None:
            raise RuntimeError("Сенсор для симуляции не установлен")
        try:
            row = self._df.loc[_temperature]
        except LookupError:
            logger.exception(f"Температуры {_temperature} нет в таблице датчика")
            closest = find_nearest(self._df.index, _temperature)
            row = self._df.loc[closest]
        code = row["code"]
        return code

    def set_sensor(self, sensor: tables.Sensor):
        self._df = load_characteristics(sensor.name)

    # TODO: если будет неточно, отрефакторить с использованием отрицательных величин в датафреймах
    def set_temperature(self, temperature: Number) -> None:
        if temperature > 0:
            self._relays[2] = False  # переключаем на положительное напряжение
        else:
            self._relays[2] = True  # переключаем на отрицательное напряжение
        code = int(self._calculate_code(temperature))
        try:
            self._dac.send_code(code)
        except Exception as e:
            logger.exception(str(e))

    def select(self) -> None:
        self._relays[1] = True
        self._relays[2] = False
        self._relays[3] = False
        self._relays[4] = True

    def unselect(self) -> None:
        pass
