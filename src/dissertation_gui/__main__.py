from PyQt5.QtCore import (
    QThread,
)
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QTextBrowser,
    QTableWidget,
)
from PyQt5.uic import loadUi
from pyqtgraph.widgets.PlotWidget import PlotWidget

from .database import Session
from .services.sensors import SensorsService
from .settings import settings
from .threads.plot import ExamplePlotThread
from .utils.plot_manager import PlotManager
from .widgets.combo_boxes import SensorsComboBox

app = QApplication([])
ui: QMainWindow = loadUi(settings.base_dir / "dissertation_gui" / "main_window.ui")
plot_thread = ExamplePlotThread()
tab_menu: QTabWidget = ui.tab_menu
graph: PlotWidget = ui.graph
sensors_combo_box: SensorsComboBox = ui.sensors_combo_box
sensor_info_text_browser: QTextBrowser = ui.sensor_info_text_browser
sensor_characteristics_table: QTableWidget = ui.sensor_characteristics_table
plot_manager = PlotManager(graph)

with Session() as session:
    sensors_service = SensorsService(session)
    sensor_list = sensors_service.get_sensors()
    sensors_combo_box.set_sensors(sensor_list)
    sensors_combo_box.sensor_changed.connect(sensor_info_text_browser.setText)  # noqa
    plot_thread.my_signal.connect(plot_manager.update_graph)

    plot_thread.start(priority=QThread.Priority.HighPriority)
    ui.show()
    exit(app.exec_())
