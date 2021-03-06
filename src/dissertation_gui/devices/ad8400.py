from typing import Tuple

import digitalio
from adafruit_bus_device.spi_device import SPIDevice
from busio import SPI
from loguru import logger

from utils.periphery import get_pin
from .base import Device

__all__ = ["AD8400"]


class AD8400(Device):
    min_code = 0
    max_code = 255

    def __init__(self,
                 spi: SPI,
                 cs: str,
                 baudrate: int = 100_000,
                 address: int = 0):
        super().__init__()
        self._cs = get_pin(cs)
        self._address = address
        self._spidev = SPIDevice(spi,
                                 chip_select=digitalio.DigitalInOut(self._cs),
                                 baudrate=baudrate)

    def get_used_pins(self) -> Tuple[int, int, int]:
        """
        :return: (clock_pin, mosi_pin, cs)
        """
        clock, mosi, _ = self._spidev.spi._pins
        return clock.id, mosi.id, self._cs.id

    def send_code(self, code: int) -> None:
        validated_code = self.validate_code(code)
        data = bytes([self._address, validated_code])  # TODO: протестировать
        with self._spidev as spi:
            spi.write(data)
        logger.debug(f"На {self} отправлен код {validated_code}")

    def __repr__(self):
        clock, mosi, cs = self.get_used_pins()
        device = self.get_device_name()
        return f"<{device} SCLK=GPIO{clock}, MOSI=GPIO{mosi} CS=GPIO{cs}>"
