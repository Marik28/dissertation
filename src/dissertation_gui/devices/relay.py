from abc import ABCMeta, abstractmethod

import digitalio


class BaseRelay(metaclass=ABCMeta):

    @abstractmethod
    def turn_on(self) -> None:
        pass

    @abstractmethod
    def turn_off(self) -> None:
        pass


class DigitalIORelay(BaseRelay):

    def __init__(self, pin):
        self._pin = digitalio.DigitalInOut(pin)
        self._pin.direction = digitalio.Direction.OUTPUT
        self.turn_off()

    def turn_on(self) -> None:
        self._pin.value = True

    def turn_off(self) -> None:
        self._pin.value = False
