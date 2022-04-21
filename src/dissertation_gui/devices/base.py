from abc import (
    abstractmethod,
    ABCMeta,
)
from contextlib import contextmanager

from adafruit_blinka import Lockable
from loguru import logger


class FakeLockable(Lockable):
    def try_lock(self):
        return True

    def unlock(self):
        pass


class BaseDevice(metaclass=ABCMeta):
    min_code: int = None
    max_code: int = None

    def __init__(self, protocol: Lockable):
        self._logger = logger
        self._protocol = protocol

    def before_transaction(self):
        pass

    def after_transaction(self):
        pass

    @contextmanager
    def _begin_transaction(self):
        while not self._protocol.try_lock():
            pass
        self.before_transaction()
        try:
            yield
        finally:
            self.after_transaction()
            self._protocol.unlock()

    @abstractmethod
    def _perform_send_data(self, data: bytes) -> None:
        pass

    def send_data(self, data: bytes) -> None:
        with self._begin_transaction():
            self._perform_send_data(data)
            self._logger.debug(f"На {self} отправлены данные: {data}")

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

    def get_device_name(self) -> str:
        return self.__class__.__name__
