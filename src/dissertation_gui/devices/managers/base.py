from abc import (
    abstractmethod,
    ABCMeta,
)

from ... import tables
from ...types import Number


class SensorManager(metaclass=ABCMeta):
    @abstractmethod
    def set_sensor(self, sensor: tables.Sensor):
        """Устанавливает датчик, который необходимо симулировать"""
        pass

    @abstractmethod
    def set_temperature(self, temperature: Number) -> None:
        pass

    @abstractmethod
    def select(self) -> None:  # TODO: добавить в меню выбора датчика блокировку выбора от спама
        """Переключает все релюшки и настраивает интерфейс для использования устройства, если это необходимо"""

    @abstractmethod
    def unselect(self) -> None:  # TODO: возможно оставить только select()
        """Подчищает все пины и прочее для того, чтобы использовать другое устройство"""
