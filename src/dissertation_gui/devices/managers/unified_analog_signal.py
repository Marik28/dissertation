from typing import List

from .base import BaseSensorManager
from ..mcp_4725 import MCP4725
from ..relay import BaseRelay
from ... import tables
from ...types import Number


# TODO сделать менюшку, где можно задавать диапазон измеряемых величин для датчиков 0...1/-50...50
class UnifiedAnalogSignalManager(BaseSensorManager):
    # TODO реализовать

    def __init__(self, mcp4725: MCP4725, relays: List[BaseRelay]):
        self._mcp4725 = mcp4725
        self._relays = relays
        # TODO: мы можем выдавать только 33 мВ,
        #  поэтому надо как то выкручиваться и брать диапазоны с запасом
        self._max_temperature = 100
        self._min_temperature = -50

    def set_sensor(self, sensor: tables.Sensor):
        ...

    def set_max_temperature(self, temperature: int):
        self._max_temperature = temperature

    def set_min_temperature(self, temperature: int):
        self._min_temperature = temperature

    def set_temperature(self, temperature: Number) -> None:
        pass

    def select(self) -> None:
        self._relays[0].turn_on()
        self._relays[1].turn_off()
        self._relays[2].turn_off()
        self._relays[3].turn_on()

    def unselect(self) -> None:
        pass
