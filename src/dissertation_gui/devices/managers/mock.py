from .base import BaseSensorManager
from ... import tables
from ...types import Number


class FakeManager(BaseSensorManager):
    """Костыль. А может гениальный мув 🤔"""

    def set_sensor(self, sensor: tables.Sensor):
        pass

    def set_temperature(self, temperature: Number) -> None:
        pass

    def select(self) -> None:
        pass

    def unselect(self) -> None:
        pass
