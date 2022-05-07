from typing import (
    Optional,
    List,
)

import pandas as pd

from .base import BaseSensorManager
from ..mcp_4725 import MCP4725
from ..relay import BaseRelay
from ... import tables
from ...types import Number
from ...utils.loader import load_characteristics


class ThermocoupleManager(BaseSensorManager):

    def __init__(self, dac: MCP4725, relays: List[BaseRelay]):
        self._dac = dac
        self._df: Optional[pd.DataFrame] = None
        self._relays = relays

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
        code = int(self._calculate_code(temperature))
        self._dac.send_code(code)

    def select(self) -> None:
        self._relays[0].turn_on()
        self._relays[1].turn_off()
        self._relays[2].turn_off()
        self._relays[3].turn_on()

    def unselect(self) -> None:
        pass
