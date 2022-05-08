import time
from abc import (
    ABCMeta,
    abstractmethod,
)
from typing import List

import digitalio
from loguru import logger

from utils.periphery import get_pin


class Relay(metaclass=ABCMeta):

    def turn_on(self) -> None:
        self.set_value(True)

    def turn_off(self) -> None:
        self.set_value(False)

    @abstractmethod
    def set_value(self, value: bool) -> None:
        pass


class DigitalIORelay(Relay):

    def __init__(self, pin: str, delay: float = 0.005):
        """

        :param pin: Название пина в библиотеке `board`
        :param delay: Задержка после переключения реле (в секундах)
        """
        self._pin_name = pin
        self._pin = digitalio.DigitalInOut(get_pin(pin))
        self._pin.direction = digitalio.Direction.OUTPUT
        self._delay = delay
        self.turn_off()

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
        state = "Включено" if self._pin.value else "Выключено"
        return f"<{self.__class__.__name__} {self._pin_name}; Состояние - {state})> "


class RelaysController:

    def __init__(self, relays: List[Relay]):
        self._relays = relays

    def __setitem__(self, key: int, value: bool):
        """Устанавливает состояние для заданного реле. Нумерация начинается с 1"""
        index = key - 1
        if index < 0 or index >= len(self._relays):
            raise LookupError(f"No relay with index {key} found")
        self._relays[index].set_value(bool(value))

    def __repr__(self):
        return ' '.join([repr(f"{relay} #{index}" for index, relay in enumerate(self._relays, start=1))])
