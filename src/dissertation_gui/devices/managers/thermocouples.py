from typing import Optional

import pandas as pd

from .base import BaseSensorManager
from ..mcp_4725 import MCP4725
from ... import tables
from ...types import Number
from ...utils.loader import load_characteristics


class ThermocoupleManager(BaseSensorManager):

    def __init__(self, dac: MCP4725):
        self._dac = dac
        self._df: Optional[pd.DataFrame] = None

    def _calculate_code(self, temperature: int) -> int:
        _temperature = round(temperature)
        if self._df is None:
            raise RuntimeError("Сенсор для симуляции не установлен")
        row = self._df.iloc[_temperature]
        code = row["code"]
        return code

    def set_sensor(self, sensor: tables.Sensor):
        self._df = load_characteristics(sensor.name)

    def set_temperature(self, temperature: Number) -> None:
        code = self._calculate_code(temperature)
        self._dac.send_code(code)

    def select(self) -> None:
        pass

    def unselect(self) -> None:
        pass
