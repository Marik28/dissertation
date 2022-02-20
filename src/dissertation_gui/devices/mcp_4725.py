import microcontroller
from busio import I2C

from .base import BaseDevice


class MCP4725(BaseDevice):
    min_code = 0
    max_code = 4095

    def __init__(self, scl: microcontroller.Pin, sda: microcontroller.Pin, address: int):
        super().__init__()
        self._i2c = I2C(scl, sda)
        self._address = address

    def _perform_send_data(self, data: bytes) -> None:
        self._i2c.writeto(self._address, data)

    def _begin_transaction(self):
        self._logger.info(f"Отправка данных на {self.get_device_name()} начата")
        while not self._i2c.try_lock():
            pass
        yield
        self._i2c.unlock()
        self._logger.info(f"Отправка данных на {self.get_device_name()} закончена")
