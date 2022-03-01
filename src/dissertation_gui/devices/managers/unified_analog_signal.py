from .base import SensorManager
from ..mcp_4725 import MCP4725
from ...types import Number


class UnifiedAnalogSignalManager(SensorManager):

    def __init__(self, mcp4725: MCP4725):
        self._mcp4725 = mcp4725

    def set_temperature(self, temperature: Number) -> None:
        pass

    def select(self) -> None:
        pass

    def unselect(self) -> None:
        pass
