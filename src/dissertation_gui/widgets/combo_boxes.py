from typing import List

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QComboBox

from .. import tables
from ..models.interference import InterferenceMode


class SensorsComboBox(QComboBox):
    sensor_changed = pyqtSignal(tables.Sensor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._sensors: List[tables.Sensor] = []
        self._sensors_as_text = []
        self.currentTextChanged.connect(self.on_text_changed)

    def set_sensors(self, sensors: List[tables.Sensor]):
        self._sensors = sensors
        self._sensors_as_text = [s.name for s in sensors]
        self.addItems(self._sensors_as_text)
        self.setCurrentText(self._sensors_as_text[0])
        self.sensor_changed.emit(self._sensors[0])  # noqa

    def on_text_changed(self, text: str):
        sensor = [s for s in self._sensors if s.name == text][0]
        self.sensor_changed.emit(sensor)  # noqa


class InterferenceModesComboBox(QComboBox):
    mode_changed = pyqtSignal(InterferenceMode)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.currentTextChanged.connect(self.on_text_changed)
        self.addItems([mode.value for mode in InterferenceMode])
        self.setCurrentText(InterferenceMode.NO.name)

    def on_text_changed(self, text: str):
        self.mode_changed.emit(InterferenceMode(text))  # noqa
