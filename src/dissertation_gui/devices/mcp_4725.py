from adafruit_mcp4725 import MCP4725 as _MCP4725
from busio import I2C
from loguru import logger

from .base import BaseDevice

__all__ = ["MCP4725"]


class MCP4725(BaseDevice):
    min_code = 0
    max_code = 4095

    def __init__(self, i2c: I2C, address: int):
        super().__init__()
        self._mcp = _MCP4725(i2c, address=address)
        self._address = address

    def send_code(self, code: int) -> None:
        self._mcp.raw_value = code
        logger.debug(f"На {self} отправлен код {code}")

    def __repr__(self):
        return f"<{self.get_device_name()} адрес={hex(self._address)}>"
