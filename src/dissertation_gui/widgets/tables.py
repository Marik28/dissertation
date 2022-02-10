from typing import Optional

from PyQt5.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
)

from .. import tables
from ..services.sensor_characteristics import SensorCharacteristicsService


class CharacteristicsTableWidget(QTableWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.service: Optional[SensorCharacteristicsService] = None

    def set_service(self, service: SensorCharacteristicsService):
        self.service = service

    def display_characteristics(self, sensor: tables.Sensor):
        y_axis = [i for i in range(0, 100, 10)]
        x_axis = [i for i in range(10)]

        self.setColumnCount(len(x_axis))
        self.setHorizontalHeaderLabels([str(x) for x in x_axis])
        self.setRowCount(len(y_axis))
        self.setVerticalHeaderLabels([str(y) for y in y_axis])

        sensor_characteristics = self.service.get_characteristics_by_sensor_name(sensor.name)

        for row in sensor_characteristics:
            temperature = row.temperature
            resistance = row.resistance
            y_coord = temperature // 10
            x_coord = temperature % 10
            self.setItem(y_coord, x_coord, QTableWidgetItem(str(resistance)))

        self.resizeColumnsToContents()
