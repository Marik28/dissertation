from adafruit_mcp4725 import MCP4725 as _MCP4725
from busio import I2C

from .base import (
    BaseDevice,
    FakeLockable,
)

__all__ = ["MCP4725"]


class DeprecatedMCP4725(BaseDevice):
    min_code = 0
    max_code = 4095

    def __init__(self, protocol: I2C, address: int):
        super().__init__(protocol)
        self._address = address
        self._i2c = protocol

    def _perform_send_data(self, data: bytes) -> None:
        self._i2c.writeto(self._address, data)


class MCP4725(BaseDevice):
    min_code = 0
    max_code = 4095

    def __init__(self, i2c: I2C, address: int):
        super().__init__(FakeLockable())
        self._mcp = _MCP4725(i2c, address=address)
        self._address = address

    def _perform_send_data(self, data: bytes) -> None:
        raise NotImplemented("Нужно использовать send_code()")

    def send_data(self, data: bytes) -> None:
        raise NotImplemented("Нужно использовать send_code()")

    def send_code(self, code: int) -> None:
        self._mcp.raw_value = code
        self._logger.debug(f"На {self} отправлен код {code}")

    def __repr__(self):
        return f"<{self.get_device_name()} address={hex(self._address)}>"
