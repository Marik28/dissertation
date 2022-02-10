from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QComboBox

from .. import tables


class SensorsComboBox(QComboBox):
    sensor_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._sensors = []
        self._sensors_as_text = []
        self.currentTextChanged.connect(self.on_text_changed)

    def set_sensors(self, sensors: list[tables.Sensor]):
        self._sensors = sensors
        self._sensors_as_text = [s.name for s in sensors]
        self.addItems(self._sensors_as_text)
        self.setCurrentText(self._sensors_as_text[0])

    def on_text_changed(self, text: str):
        sensor = [s for s in self._sensors if s.name == text][0]
        text = f"Датчик: {sensor.name}. Код - {sensor.trm_code}"
        self.sensor_changed.emit(text)