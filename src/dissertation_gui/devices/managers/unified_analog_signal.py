from .base import BaseSensorManager
from ..mcp_4725 import MCP4725
from ... import tables
from ...types import Number


# TODO сделать менюшку, где можно задавать диапазон измеряемых величин для датчиков 0...1/-50...50
class UnifiedAnalogSignalManager(BaseSensorManager):
    # TODO реализовать

    def __init__(self, mcp4725: MCP4725):
        self._mcp4725 = mcp4725
        # TODO: мы можем выдавать только 33 мВ,
        #  поэтому надо как то выкручиваться и брать диапазоны с запасом
        self._max_temperature = 100
        self._min_temperature = -50

    def set_sensor(self, sensor: tables.Sensor):
        ...

    def set_max_temperature(self, new_temperature: int):
        self._max_temperature = new_temperature

    def set_min_temperature(self, new_temperature: int):
        self._min_temperature = new_temperature

    def set_temperature(self, temperature: Number) -> None:
        pass

    def select(self) -> None:
        pass

    def unselect(self) -> None:
        pass
