import time
from abc import (
    ABCMeta,
    abstractmethod,
)

import digitalio
from loguru import logger


class BaseRelay(metaclass=ABCMeta):

    def turn_on(self) -> None:
        self.set_value(True)

    def turn_off(self) -> None:
        self.set_value(False)

    @abstractmethod
    def set_value(self, value: bool) -> None:
        pass


class DigitalIORelay(BaseRelay):
    registered_relays = []

    def __init__(self, pin: str, delay: float = 0.005):
        """

        :param pin: Название пина в библиотеке `board`
        :param delay: Задержка после переключения реле (в секундах)
        """
        self._pin_name = pin
        self._pin = digitalio.DigitalInOut(pin)
        self._pin.direction = digitalio.Direction.OUTPUT
        self.registered_relays.append(self)
        self.turn_off()
        self._delay = delay

    def turn_on(self) -> None:
        self.set_value(True)

    def turn_off(self) -> None:
        self.set_value(False)

    def set_value(self, value: bool):
        self._pin.value = value
        message = "включено" if value else "выключено"
        logger.debug(f"{self} {message}")
        time.sleep(self._delay)

    def __repr__(self):
        number = self.registered_relays.index(self) + 1
        state = "Включено" if self._pin.value else "Выключено"
        return f"<{self.__class__.__name__}> (#{number}; GPIO{self._pin_name}; Состояние - {state})"
