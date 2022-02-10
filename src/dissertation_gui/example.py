import math
import time

from PyQt5.QtCore import (
    QThread,
    pyqtSignal,
)
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QComboBox,
    QTextBrowser,
    QTableWidget,
)
from PyQt5.uic import loadUi
from pyqtgraph.widgets.PlotWidget import PlotWidget

from dissertation_gui import tables
from dissertation_gui.utils.plot_manager import PlotManager
from .database import Session
from .models.plot import PlotPoint
from .services.sensors import SensorsService
from .settings import settings


class PlotThread(QThread):
    my_signal = pyqtSignal(PlotPoint)

    def run(self) -> None:
        start_time = time.time()
        while True:
            now = time.time() - start_time
            value = math.sin(now)
            self.my_signal.emit(PlotPoint(time=now, value=value))  # noqa
            time.sleep(0.1)


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
        self.sensor_changed.emit(f"Датчик: {sensor.name}. Код - {sensor.trm_code}")


app = QApplication([])
ui: QMainWindow = loadUi(settings.base_dir / "dissertation_gui" / "main_window.ui")
plot_thread = PlotThread()
tab_menu: QTabWidget = ui.tab_menu
graph: PlotWidget = ui.graph
sensors_combo_box: SensorsComboBox = ui.sensors_combo_box
sensor_info_text_browser: QTextBrowser = ui.sensor_info_text_browser
sensor_characteristics_table: QTableWidget = ui.sensor_characteristics_table
plot_manager = PlotManager(graph)

if __name__ == '__main__':
    with Session() as session:
        sensors_service = SensorsService(session)
        sensor_list = sensors_service.get_sensors()
        sensors_combo_box.set_sensors(sensor_list)
        sensors_combo_box.sensor_changed.connect(sensor_info_text_browser.setText)  # noqa
        plot_thread.my_signal.connect(plot_manager.update_graph)  # noqa

        plot_thread.start(priority=QThread.Priority.HighPriority)
        ui.show()
        exit(app.exec_())
