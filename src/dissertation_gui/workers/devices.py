from typing import Dict

from PyQt5.QtCore import QObject

from .. import tables
from ..devices.managers import (
    BaseSensorManager,
    MockManager,
)
from ..models.sensors import SensorType
from ..types import Number


class SensorWorker(QObject):
    """Воркер, который переключается между устройствами и отправляет им данные"""

    def __init__(self, managers: Dict[SensorType, BaseSensorManager], parent=None):
        super().__init__(parent)
        self._managers = managers
        self._current_manager = MockManager()

    def set_temperature(self, temperature: Number) -> None:
        self._current_manager.set_temperature(temperature)

    def set_sensor(self, sensor: tables.Sensor) -> None:
        manager = self._managers[sensor.type]
        if manager is not self._current_manager:
            self._current_manager.unselect()
            manager.select()
            self._current_manager = manager
        manager.set_sensor(sensor)
