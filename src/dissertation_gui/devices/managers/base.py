from abc import abstractmethod

from ...types import Number


class SensorManager:
    @abstractmethod
    def set_temperature(self, temperature: Number) -> None:
        pass

    @abstractmethod
    def select(self) -> None:
        """Переключает все релюшки и настраивает интерфейс для использования устройства, если это необходимо"""

    @abstractmethod
    def unselect(self) -> None:
        """Подчищает все пины и прочее для того, чтобы использовать другое устройство"""


class SensorEmulator:
    def __init__(self, manager: SensorManager = None):
        self._manager = manager

    def perform_set_temperature(self, temperature: Number) -> None:
        if self._manager is None:
            raise RuntimeError("Manager is not set.")

        self._manager.set_temperature(temperature)

    def set_manager(self, manager: SensorManager) -> None:
        if self._manager is not None:
            self._manager.unselect()
        self._manager = manager
        self._manager.select()
