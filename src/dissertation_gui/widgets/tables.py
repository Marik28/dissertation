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
        rows = [i for i in range(0, 100, 10)]
        columns = [i for i in range(10)]

        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels([str(x) for x in columns])
        self.setRowCount(len(rows))
        self.setVerticalHeaderLabels([str(y) for y in rows])

        sensor_characteristics = self.service.get_characteristics_by_sensor_name(sensor.name)

        for value in sensor_characteristics:
            temperature = value.temperature
            resistance = value.resistance
            column = temperature // 10
            row = temperature % 10
            self.setItem(column, row, QTableWidgetItem(str(resistance)))

        self.resizeColumnsToContents()
