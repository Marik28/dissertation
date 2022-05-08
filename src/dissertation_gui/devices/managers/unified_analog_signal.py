import enum

from loguru import logger

from utils.utils import (
    remap,
    find_nearest,
)
from .base import SensorManager
from ..mcp_4725 import MCP4725
from ..relay import RelaysController
from ... import tables
from ...types import Number
from ...utils import load_characteristics


# TODO: сделать менюшку, где можно задавать диапазон измеряемых величин для датчиков 0...1/-50...50
class UnifiedAnalogSignalManager(SensorManager):
    # TODO реализовать
    max_temperature = 100
    min_temperature = -50

    class Sensor(enum.Enum):
        FIFTY_MV = "Сигнал напряжения от -50 до 50 мВ"
        ONE_V = "Сигнал напряжения от 0 до 1 В"

    def __init__(self, mcp4725: MCP4725, relays: RelaysController):
        self._mcp4725 = mcp4725
        self._relays = relays
        self._df = load_characteristics(self.Sensor.ONE_V.name)
        self._current_sensor = self.Sensor.ONE_V
        self._current_max_temperature = self.max_temperature
        self._current_min_temperature = self.min_temperature

    def set_sensor(self, sensor: tables.Sensor):
        new_sensor = self.Sensor(sensor.name)
        if new_sensor == self.Sensor.ONE_V:
            self._relays[2] = False  # для этого датчика может быть только положительное напряжение
        self._current_sensor = new_sensor

    def set_max_temperature(self, temperature: int):  # TODO: добавить защиту от дурачка
        self._current_max_temperature = temperature

    def set_min_temperature(self, temperature: int):
        self._current_min_temperature = temperature

    def set_temperature(self, temperature: Number) -> None:
        if self._current_sensor == self.Sensor.ONE_V:
            voltage = remap(temperature, self._current_min_temperature, self._current_max_temperature, 0.0, 1.0)
        else:
            if temperature > 0:
                self._relays[2] = False  # переключаем на положительное напряжение
            else:
                self._relays[2] = True  # переключаем на отрицательное напряжение
            voltage = remap(abs(temperature), self._current_min_temperature, self._current_max_temperature, 0.0, 1.0)
        code = self._calculate_code(voltage)

        try:
            self._mcp4725.send_code(code)
        except Exception as e:
            logger.error(e)

    def _calculate_code(self, voltage: float) -> int:
        row = self._df[self._df["voltage"] == find_nearest(self._df["voltage"], voltage)]
        return int(row["code"])

    def select(self) -> None:
        self._relays[1] = False
        self._relays[2] = False
        self._relays[3] = False
        self._relays[4] = True

    def unselect(self) -> None:
        pass
