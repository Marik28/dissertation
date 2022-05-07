from abc import (
    abstractmethod,
    ABCMeta,
)

__all__ = ["Device"]


class Device(metaclass=ABCMeta):
    min_code: int = None
    max_code: int = None

    def __init__(self):
        if self.min_code is None or self.max_code is None:
            raise TypeError("Необходимо указать диапазон кодов")

    @abstractmethod
    def send_code(self, code: int) -> None:
        pass

    def validate_code(self, code: int) -> int:
        if code < self.min_code:
            code = self.min_code
        elif code > self.max_code:
            code = self.max_code
        return code

    def get_device_name(self) -> str:
        return self.__class__.__name__
