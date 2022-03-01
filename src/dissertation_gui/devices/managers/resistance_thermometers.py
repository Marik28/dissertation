from typing import Dict

from .base import SensorManager
from ...devices.ad8400 import AD8400
from ...types import Number


# TODO: реализовать
class ResistanceThermometerManager(SensorManager):

    def __init__(self, *digipots: AD8400):
        self._digipots = list(digipots)

    def select(self):
        pass

    def unselect(self) -> None:
        pass

    def calculate_codes(self, temperature: Number) -> Dict[AD8400, int]:
        _temperature = round(temperature)

    def set_temperature(self, temperature: Number) -> None:
        codes = self.calculate_codes(temperature)
        for digipot, code in codes.items():
            digipot.send_code(code)