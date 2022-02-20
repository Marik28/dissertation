from contextlib import contextmanager

import digitalio
import microcontroller
from busio import SPI

from .base import BaseDevice


class AD8400(BaseDevice):
    min_code = 0
    max_code = 255

    def __init__(self,
                 clock: microcontroller.Pin,
                 mosi: microcontroller.Pin,
                 cs: digitalio.DigitalInOut,
                 baudrate: int = 100_000):
        super().__init__()
        self._spi = SPI(clock=clock, MOSI=mosi)
        self._baudrate = baudrate
        self._cs = cs
        self._cs.direction = digitalio.Direction.OUTPUT
        self._cs.value = True
        self._logger.info(f"{self.get_device_name()} инициализирован пинами {clock=}, {mosi=}, {cs=}; {baudrate=}")

    @contextmanager
    def _begin_transaction(self):
        self._logger.info(f"Отправка данных на {self.get_device_name()} начата")
        while not self._spi.try_lock():
            pass
        self._spi.configure(self._baudrate)
        self._cs.value = False
        yield
        self._cs.value = True
        self._spi.unlock()
        self._logger.info(f"Отправка данных на {self.get_device_name()} закончена")

    def _perform_send_data(self, data: bytes) -> None:
        self._spi.write(data)
