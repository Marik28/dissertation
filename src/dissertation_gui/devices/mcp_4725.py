from busio import I2C

from .base import BaseDevice


# TODO: - https://gist.github.com/mcbridejc/d060602e892f6879e7bc8b93aa3f85be
#       - https://pinout.xyz/pinout/spi
#  чтобы добавить еще chip select-ов


class MCP4725(BaseDevice):
    min_code = 0
    max_code = 4095

    def __init__(self, protocol: I2C, address: int):
        super().__init__(protocol)
        self._address = address
        self._i2c = protocol

    def _perform_send_data(self, data: bytes) -> None:
        self._i2c.writeto(self._address, data)
