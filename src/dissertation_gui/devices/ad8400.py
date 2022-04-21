import digitalio
from busio import SPI

from .base import BaseDevice


class AD8400(BaseDevice):
    min_code = 0
    max_code = 255

    def __init__(self,
                 protocol: SPI,
                 cs,
                 baudrate: int = 100_000):
        super().__init__(protocol)
        self._spi = protocol
        self._baudrate = baudrate
        self._cs = digitalio.DigitalInOut(cs)
        self._cs.direction = digitalio.Direction.OUTPUT
        self._cs.value = True

    def get_used_pins(self):
        """
        :return: (clock_pin, mosi_pin, cs)
        """
        clock, mosi, _ = self._spi._pins
        cs = self._cs
        return clock, mosi, cs

    def before_transaction(self):
        self._spi.configure(self._baudrate)
        self._cs.value = False

    def after_transaction(self):
        self._cs.value = True

    def _perform_send_data(self, data: bytes) -> None:
        self._spi.write(data)

    def __repr__(self):
        clock, mosi, cs = self.get_used_pins()
        device = self.get_device_name()
        return f"<{device} SCLK={clock}, MOSI={mosi} CS={cs}>"
