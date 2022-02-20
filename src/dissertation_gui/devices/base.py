from abc import abstractmethod
from contextlib import contextmanager
from typing import Union

Number = Union[float, int]


class DeviceManager:
    @abstractmethod
    def set_temperature(self, temperature: Number) -> None:
        pass


class BaseDevice:
    min_code = None
    max_code = None

    @abstractmethod
    @contextmanager
    def _begin_transaction(self):
        pass

    @abstractmethod
    def _perform_send_data(self, data: bytes) -> None:
        pass

    def send_data(self, data: bytes) -> None:
        with self._begin_transaction():
            self._perform_send_data(data)

    def send_code(self, code: int) -> None:
        validated_code = self._validate_code(code)
        data_to_send = bytes([validated_code])
        self.send_data(data_to_send)

    def _validate_code(self, code: int) -> int:
        if self.min_code is None or self.max_code is None:
            raise TypeError("Необходимо указать диапазон кодов")
        if code < self.min_code:
            code = self.min_code
        elif code > self.max_code:
            code = self.max_code
        return code


class SensorEmulator:
    def __init__(self, manager: DeviceManager = None):
        self._manager = manager

    def perform_set_temperature(self, temperature: Number) -> None:
        if self._manager is None:
            raise RuntimeError("Manager is not set.")

        self._manager.set_temperature(temperature)

    def set_manager(self, manager: DeviceManager) -> None:
        self._manager = manager
