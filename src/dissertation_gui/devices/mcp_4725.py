from busio import I2C

from .base import BaseDevice


class MCP4725(BaseDevice):
    min_code = 0
    max_code = 4095

    def __init__(self, protocol: I2C, address: int):
        super().__init__(protocol)
        self._address = address
        self._i2c = protocol

    def _perform_send_data(self, data: bytes) -> None:
        self._i2c.writeto(self._address, data)
