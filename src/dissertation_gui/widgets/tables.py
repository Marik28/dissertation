import math
from typing import Optional

from PyQt5.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
)

from .. import tables
from ..services.sensor_characteristics import SensorCharacteristicsService


# темп [ -11, -10,  -9,  -8,  -7,  -6,  -5,  -4,  -3,  -2,  -1,   0,   1,   2,   3,   4]
# знач [  20,  18,  16,  14,  12,  10,   8,   6,   4,   2,   0,  -2,  -4,  -6,  -8, -10]

#    | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
# -1 | 20| 18| - | - | - | - | - | - | - | - | # 0 строка
# -0 | -2|  0|  2|  4|  6|  8| 10| 12| 14| 16| # 1 строка
#  0 | -2| -4| -6| -8|-10| - | - | - | - | - | # 2 строка

class CharacteristicsTableWidget(QTableWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.service: Optional[SensorCharacteristicsService] = None

    def set_service(self, service: SensorCharacteristicsService):
        self.service = service

    def display_characteristics(self, sensor: tables.Sensor):
        sensor_characteristics = self.service.get_characteristics_by_sensor_name(sensor.name)
        neg_chars = [row for row in sensor_characteristics if row.temperature <= 0]
        pos_chars = [row for row in sensor_characteristics if row.temperature >= 0]

        neg_rows = [i for i in reversed(range(0, len(neg_chars), 10))]
        pos_rows = [i for i in range(0, len(pos_chars), 10)]
        rows = neg_rows + pos_rows

        columns = [i for i in range(10)]

        neg_labels = [f"-{i}" for i in neg_rows]
        pos_labels = [f"{i}" for i in pos_rows]
        vertical_labels = neg_labels + pos_labels
        horizontal_labels = [str(x) for x in columns]

        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(horizontal_labels)
        self.setRowCount(len(rows))
        self.setVerticalHeaderLabels(vertical_labels)

        offset = calculate_offset(sensor_characteristics[0].temperature)
        for value in sensor_characteristics:
            temperature = value.temperature
            resistance = value.resistance
            column = abs(temperature) % 10
            row = calculate_row(temperature, offset)
            self.setItem(column, row, QTableWidgetItem(str(resistance)))

        self.resizeColumnsToContents()


def calculate_offset(min_value: int) -> int:
    """
    >>> calculate_offset(-10)
    1
    >>> calculate_offset(-11)
    2

    :param min_value: отрицательное значение, от которого считать смещение
    :return: смещение строк - положительное число
    :raises ValueError: если min_value положительное
    """
    if min_value > 0:
        raise ValueError("Надо чтобы больше 0 было")

    if str(min_value).endswith("0"):
        offset = min_value // 10
    else:
        offset = (abs(min_value) + 10) // 10
    return abs(offset)


def calculate_row(temperature: int, offset: int) -> int:
    row = int(math.copysign(abs(temperature) // 10, temperature))
    return row + offset


if __name__ == '__main__':
    import doctest

    doctest.testmod()
