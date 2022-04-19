from abc import ABCMeta, abstractmethod

import digitalio
from loguru import logger


class BaseRelay(metaclass=ABCMeta):

    @abstractmethod
    def turn_on(self) -> None:
        pass

    @abstractmethod
    def turn_off(self) -> None:
        pass


class DigitalIORelay(BaseRelay):
    registered_relays = []

    def __init__(self, pin):
        self._pin_name = pin
        self._pin = digitalio.DigitalInOut(pin)
        self._pin.direction = digitalio.Direction.OUTPUT
        self.registered_relays.append(self)
        self.turn_off()

    def turn_on(self) -> None:
        self._pin.value = True
        logger.debug(f"Реле {self} включено")

    def turn_off(self) -> None:
        self._pin.value = False
        logger.debug(f"Реле {self} выключено")

    def __repr__(self):
        number = self.registered_relays.index(self) + 1
        state = "Включено" if self._pin.value else "Выключено"
        return f"<{self.__class__.__name__}> (#{number}; GPIO{self._pin_name}; Состояние - {state})"
