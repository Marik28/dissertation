import enum
from typing import Tuple

import pandas as pd
from loguru import logger

from utils.utils import (
    remap,
    find_nearest,
)
from .base import SensorManager
from ..mcp_4725 import MCP4725
from ..relay import RelaysController
from ... import tables
from ...settings import settings
from ...types import Number


# TODO: сделать менюшку, где можно задавать диапазон измеряемых величин для датчиков с УАС
class UnifiedAnalogSignalManager(SensorManager):
    class Sensor(enum.Enum):
        # FIFTY_MV = "Сигнал напряжения от -50 до 50 мВ"
        ONE_V = "Сигнал напряжения от 0 до 1 В"
        ZERO_FIVE_MA = "Сигнал тока от 0 до 5 мА"
        ZERO_TWENTY_MA = "Сигнал тока от 0 до 20 мА"
        FOUR_TWENTY_MA = "Сигнал тока от 4 до 20 мА"

    def __init__(self,
                 mcp4725: MCP4725,
                 relays: RelaysController,
                 max_temperature: int = 100,
                 min_temperature: int = -50):
        self._mcp4725 = mcp4725
        self._relays = relays
        self._df = pd.read_csv(settings.base_dir.parent / "data" / "DAC" / "mcp4725.csv", usecols=["code", "voltage"])
        self._current_sensor = self.Sensor.ONE_V
        self._max_temperature = max_temperature
        self._min_temperature = min_temperature
        self._resistor_value = 100
        """Сопротивление резистора, преобразующего ток в напряжение, Ом"""

    def _get_range(self) -> Tuple[float, float]:
        """

        :return: (min, max) - минимальное и максимальное напряжение, соответствующее диапазону выбранного датчика
        """
        return {
            # self.Sensor.FIFTY_MV: (0., 1.),
            self.Sensor.ONE_V: (0., 1.),
            self.Sensor.ZERO_FIVE_MA: (0., 5e-3 * self._resistor_value),
            self.Sensor.ZERO_TWENTY_MA: (0., 20e-3 * self._resistor_value),
            self.Sensor.FOUR_TWENTY_MA: (4e-3 * self._resistor_value, 20e-3 * self._resistor_value),
        }[self._current_sensor]

    def set_sensor(self, sensor: tables.Sensor):
        new_sensor = self.Sensor(sensor.name)
        # if new_sensor != self.Sensor.FIFTY_MV:
        #     self._relays[2] = False  # всех датчиков, кроме -50...+50 мВ, напряжение может быть только положительным
        self._current_sensor = new_sensor

    def set_max_temperature(self, temperature: int):  # TODO: добавить защиту от дурачка
        self._max_temperature = temperature

    def set_min_temperature(self, temperature: int):
        self._min_temperature = temperature

    def set_temperature(self, temperature: Number) -> None:
        out_min, out_max = self._get_range()
        voltage = remap(temperature, self._min_temperature, self._max_temperature, out_min, out_max)
        code = self._calculate_code(voltage)
        logger.debug(f"{voltage}")

        try:
            self._mcp4725.send_code(code)
        except Exception as e:
            logger.exception(str(e))

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
