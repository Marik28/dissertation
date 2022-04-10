from PyQt5.QtCore import (
    QObject,
    pyqtSlot,
)

from ..devices.managers.base import SensorManager
from ..types import Number


class SensorWorker(QObject):
    """Воркер, который переключается между устройствами и отправляет им данные"""

    def __init__(self, manager: SensorManager, parent=None):
        super().__init__(parent)
        self._manager = manager

    @pyqtSlot(Number)
    def set_temperature(self, temperature: Number) -> None:
        self._manager.set_temperature(temperature)

    @pyqtSlot(SensorManager)
    def set_manager(self, manager: SensorManager) -> None:
        self._manager.unselect()
        self._manager = manager
        self._manager.select()
