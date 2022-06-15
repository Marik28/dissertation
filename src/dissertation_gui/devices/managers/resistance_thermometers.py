from typing import List, Tuple, Optional

import pandas as pd
from loguru import logger

from utils.utils import find_nearest
from .base import SensorManager
from ..relay import RelaysController
from ... import tables
from ...devices.ad8400 import AD8400
from ...types import Number
from ...utils.loader import load_characteristics


class ResistanceThermometerManager(SensorManager):

    def __init__(self, digipots: List[AD8400], relays: RelaysController):
        self._digipots = digipots
        self._relays = relays
        self._df: Optional[pd.DataFrame] = None

    def select(self) -> None:
        self._relays[3] = True
        self._relays[4] = False

    def unselect(self) -> None:
        pass

    def set_sensor(self, sensor: tables.Sensor):
        self._df = load_characteristics(sensor.name)

    def _calculate_codes(self, temperature: Number) -> List[Tuple[AD8400, int]]:
        _temperature = round(temperature)
        if self._df is None:
            raise RuntimeError("Сенсор для симуляции не установлен")
        # находим строку по температуре
        try:
            row = self._df.loc[_temperature]
        except LookupError:
            logger.exception(f"Температуры {_temperature} нет в таблице датчика")
            closest = find_nearest(self._df.index, _temperature)
            row = self._df.loc[closest]
        codes = []
        # в датафрейме код для i-того резистора лежит в колонке под названием 'R{i}_code'
        for index, digipot in enumerate(self._digipots, start=1):
            code = int(row[f"R{index}_code"])
            codes.append((digipot, code))
        return codes

    def set_temperature(self, temperature: Number) -> None:
        codes = self._calculate_codes(temperature)
        for digipot, code in codes:
            try:
                digipot.send_code(code)
            except Exception as e:
                logger.exception(str(e))
