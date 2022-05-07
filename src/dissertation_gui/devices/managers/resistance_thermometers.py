from typing import List, Tuple, Optional

import pandas as pd

from .base import BaseSensorManager
from ..relay import BaseRelay
from ... import tables
from ...devices.ad8400 import AD8400
from ...types import Number
from ...utils.loader import load_characteristics


# TODO: реализовать
#  1. CalcThread рассчитывает температуру и: QThread.signal.emit(temp)
#  2. Текущий воркер высчитывает значение для отправки на устройство: Worker.calc(temp) -> code
#  3. Значение отправляется на устройство: Device.send(code)


class ResistanceThermometerManager(BaseSensorManager):

    def __init__(self, digipots: List[AD8400], relays: List[BaseRelay]):
        self._digipots = digipots
        self._relays = relays
        self._df: Optional[pd.DataFrame] = None

    def select(self) -> None:
        self._relays[2].turn_on()
        self._relays[3].turn_off()

    def unselect(self) -> None:
        pass

    def set_sensor(self, sensor: tables.Sensor):
        self._df = load_characteristics(sensor.name)

    def _calculate_codes(self, temperature: Number) -> List[Tuple[AD8400, int]]:  # TODO жесть какая то
        _temperature = round(temperature)
        if self._df is None:
            raise RuntimeError("Сенсор для симуляции не установлен")
        # находим строку с по температуре
        row = self._df.iloc[_temperature]
        codes = []
        # в датафрейме код для i-того резистора лежит в колонке под названием 'R{i}_code'
        for index, digipot in enumerate(self._digipots, start=1):
            code = row[f"R{index}_code"]
            codes.append((digipot, int(code)))
        return codes

    def set_temperature(self, temperature: Number) -> None:
        codes = self._calculate_codes(temperature)
        for digipot, code in codes:
            digipot.send_code(code)
