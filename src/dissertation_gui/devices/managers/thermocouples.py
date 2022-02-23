import pandas as pd

from .base import SensorManager
from ..mcp_4725 import MCP4725
from ...types import Number


class ThermocoupleManager(SensorManager):

    def __init__(self, dac: MCP4725, characteristics_dataframe: pd.DataFrame):
        self._dac = dac
        self._df = characteristics_dataframe

    def calculate_code(self, temperature: int) -> int:
        _temperature = round(temperature)

        # TODO: реализовать

    def set_temperature(self, temperature: Number) -> None:
        code = self.calculate_code(temperature)
        self._dac.send_code(code)

    def select(self) -> None:
        pass

    def unselect(self) -> None:
        pass
