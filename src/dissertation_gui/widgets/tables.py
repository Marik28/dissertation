import math
from typing import (
    Optional,
    Dict,
    List,
)

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
)

from dissertation_gui.models.sensors import SensorType
from .. import tables
from ..services.sensor_characteristics import SensorCharacteristicsService


# темп [ -11, -10,  -9,  -8,  -7,  -6,  -5,  -4,  -3,  -2,  -1,   0,   1,   2,   3,   4]
# знач [  20,  18,  16,  14,  12,  10,   8,   6,   4,   2,   0,  -2,  -4,  -6,  -8, -10]

#    | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
# -1 | 20| 18| - | - | - | - | - | - | - | - | # 0 строка
# -0 | -2|  0|  2|  4|  6|  8| 10| 12| 14| 16| # 1 строка
#  0 | -2| -4| -6| -8|-10| - | - | - | - | - | # 2 строка

# TODO: добавить график с характеристикой датчика, а также отображать на нем диапазон температур, используемых в ТРМ
class CharacteristicsTableWidget(QTableWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.service: Optional[SensorCharacteristicsService] = None
        self.currentCellChanged.connect(self.change_colors)  # noqa
        self.default_background = QTableWidgetItem().background()

    def set_service(self, service: SensorCharacteristicsService):
        self.service = service

    def change_colors(self, cur_row: int, cur_col: int, prev_row: int, prev_col: int):
        if cur_row != prev_row:
            self.change_row_bg_color(prev_row, self.default_background)
        if cur_col != prev_col:
            self.change_column_bg_color(prev_col, self.default_background)
        color = QColor("#DCDCDC")
        self.change_column_bg_color(cur_col, color)
        self.change_row_bg_color(cur_row, color)

    def change_column_bg_color(self, column: int, color: QColor):
        for row in range(self.rowCount()):
            item = self.item(row, column)
            if item is not None:
                item.setBackground(color)

    def change_row_bg_color(self, row: int, color: QColor):
        for column in range(self.colorCount()):
            item = self.item(row, column)
            if item is not None:
                item.setBackground(color)

    def display_characteristics(self, sensor: tables.Sensor):
        if sensor.type == SensorType.UNIFIED_ANALOG_SIGNAL:
            self.clear()
            return
        sensor_characteristics = self.service.get_characteristics_by_sensor_name(sensor.name)
        neg_chars = [row for row in sensor_characteristics if row.temperature <= 0]
        pos_chars = [row for row in sensor_characteristics if row.temperature >= 0]

        min_temperature = sensor_characteristics[0].temperature
        neg_rows = [i for i in reversed(range(0, len(neg_chars), 10))]
        if min_temperature == 0:
            neg_rows = [i for i in neg_rows if i != 0]
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
        for tuple_ in sensor_characteristics:
            temperature = tuple_.temperature
            value = tuple_.value
            column = abs(temperature) % 10
            row = calculate_row(temperature, offset, min_temperature)
            self.setItem(row, column, QTableWidgetItem(str(value)))
            if temperature == 0 and min_temperature != 0:  # костыль
                self.setItem(row + 1, column, QTableWidgetItem(str(value)))

        self.resizeColumnsToContents()
        self.resizeRowsToContents()


class SensorInfoTable(QTableWidget):
    def update_info(self, sensor: tables.Sensor):
        labels = ["Название", "Тип", "Код ТРМ", "Единицы измерения", "Диапазон, °C"]
        rows = [sensor.name, sensor.type.value, sensor.trm_code, f"{sensor.physical_quantity}, {sensor.units}",
                f"{sensor.min_temperature}…{sensor.max_temperature}"]
        self.setColumnCount(1)
        self.setRowCount(len(labels))
        self.setVerticalHeaderLabels(labels)
        for i, row in enumerate(rows):
            self.setItem(i, 0, QTableWidgetItem(row))
        self.resizeColumnsToContents()
        self.resizeRowsToContents()


class TRMParametersInfoTable(QTableWidget):
    def update_info(self, parameters: List[Dict]):
        labels = ["Параметр", "Значение"]
        rows = len(parameters)
        columns = len(labels)
        self.setColumnCount(columns)
        self.setRowCount(rows)
        self.setHorizontalHeaderLabels(labels)
        for i, param in enumerate(parameters):
            self.setItem(i, 0, QTableWidgetItem(str(param["name"])))
            self.setItem(i, 1, QTableWidgetItem(str(param["value"])))
        self.resizeRowsToContents()


def calculate_offset(min_value: int) -> int:
    """
    >>> calculate_offset(-10)
    1
    >>> calculate_offset(-11)
    2
    >>> calculate_offset(0)
    0

    :param min_value: отрицательное значение, от которого считать смещение
    :return: смещение строк - положительное число
    :raises ValueError: если min_value положительное
    """
    if min_value > 0:
        raise ValueError("Надо чтобы больше 0 было")
    if min_value == 0:
        return 0
    if str(min_value).endswith("0"):
        offset = min_value // 10
    else:
        offset = (abs(min_value) + 10) // 10
    return abs(offset)


def calculate_row(temperature: int, offset: int, min_temperature: int) -> int:
    row = int(math.copysign(abs(temperature) // 10, temperature))
    result = row + offset
    if temperature > 0 and min_temperature != 0:
        result += 1
    return result


if __name__ == '__main__':
    import doctest

    doctest.testmod()
