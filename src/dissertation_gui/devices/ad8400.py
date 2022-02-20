from contextlib import contextmanager

import digitalio
import microcontroller
from busio import SPI

from .base import BaseDevice


class AD8400(BaseDevice):
    min_code = 0
    max_code = 255

    def __init__(self, clock: microcontroller.Pin, mosi: microcontroller.Pin, cs: digitalio.DigitalInOut):
        self._spi = SPI(clock=clock, MOSI=mosi)
        self._cs = cs
        self._cs.direction = digitalio.Direction.OUTPUT
        self._cs.value = True

    @contextmanager
    def _begin_transaction(self):
        while not self._spi.try_lock():
            pass
        self._cs.value = False
        yield
        self._cs.value = True
        self._spi.unlock()

    def _perform_send_data(self, data: bytes) -> None:
        self._spi.write(data)
