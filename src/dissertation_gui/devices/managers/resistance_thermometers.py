from typing import List, Tuple, Optional

import pandas as pd

from .base import BaseSensorManager
from ..relay import DigitalIORelay
from ... import tables
from ...devices.ad8400 import AD8400
from ...types import Number
from ...utils.loader import load_characteristics


# TODO: реализовать
#  1. CalcThread рассчитывает температуру и: QThread.signal.emit(temp)
#  2. Текущий воркер высчитывает значение для отправки на устройство: Worker.calc(temp) -> code
#  3. Значение отправляется на устройство: Device.send(code)


class ResistanceThermometerManager(BaseSensorManager):

    def __init__(self, digipots: List[AD8400], relays: List[DigitalIORelay]):
        self._digipots = digipots
        self._relays = relays
        self._df: Optional[pd.DataFrame] = None

    def select(self) -> None:
        pass

    def unselect(self) -> None:
        pass

    def set_sensor(self, sensor: tables.Sensor):
        self._df = load_characteristics(sensor.name)

    def _calculate_codes(self, temperature: Number) -> List[Tuple[AD8400, int]]:  # TODO жесть какая то
        _temperature = round(temperature)
        if self._df is None:
            raise RuntimeError("Сенсор для симуляции не установлен")
        row = self._df.iloc[_temperature]
        codes = []
        for index, digipot in enumerate(self._digipots, start=1):
            code = row[f"R{index}_code"]
            codes.append((digipot, code))
        return codes

    def set_temperature(self, temperature: Number) -> None:
        codes = self._calculate_codes(temperature)
        for digipot, code in codes:
            digipot.send_code(code)
