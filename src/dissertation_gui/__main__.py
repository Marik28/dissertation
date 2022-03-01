from typing import List

from PyQt5.QtCore import (
    QThread,
)
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QTextBrowser,
    QTableWidget,
    QTableWidgetItem,
)
from PyQt5.uic import loadUi
from pyqtgraph.widgets.PlotWidget import PlotWidget

from . import tables
from .database import Session
from .services.sensor_characteristics import SensorCharacteristicsService
from .services.sensors import SensorsService
from .settings import settings
from .threads.plot import ExamplePlotThread
from .utils.plot_manager import PlotManager
from .widgets.combo_boxes import SensorsComboBox
from .widgets.tables import CharacteristicsTableWidget


def display_table(table: QTableWidget, sensor_characteristics: List[tables.ResistanceThermometerCharacteristics]):
    y_axis = [i for i in range(0, 100, 10)]
    x_axis = [i for i in range(10)]

    table.setColumnCount(len(x_axis))
    table.setHorizontalHeaderLabels([str(x) for x in x_axis])
    table.setRowCount(len(y_axis))
    table.setVerticalHeaderLabels([str(y) for y in y_axis])

    for row in sensor_characteristics:
        temperature = row.temperature
        resistance = row.value
        y_coord = temperature // 10
        x_coord = temperature % 10
        table.setItem(y_coord, x_coord, QTableWidgetItem(str(resistance)))

    table.resizeColumnsToContents()


app = QApplication([])
ui: QMainWindow = loadUi(settings.base_dir / "dissertation_gui" / "main_window.ui")
plot_thread = ExamplePlotThread(frequency=settings.plot_update_frequency)
tab_menu: QTabWidget = ui.tab_menu
graph: PlotWidget = ui.graph
sensors_combo_box: SensorsComboBox = ui.sensors_combo_box
sensor_info_text_browser: QTextBrowser = ui.sensor_info_text_browser
sensor_characteristics_table: CharacteristicsTableWidget = ui.sensor_characteristics_table

plot_manager = PlotManager(graph, plot_length=settings.plot_points)

with Session() as session:
    sensors_service = SensorsService(session)
    sensors_characteristics_service = SensorCharacteristicsService(session)

    sensor_characteristics_table.set_service(sensors_characteristics_service)

    sensor_list = sensors_service.get_sensors()
    sensors_combo_box.set_sensors(sensor_list)
    # sensors_combo_box.sensor_changed.connect(sensor_info_text_browser.setText)
    sensors_combo_box.sensor_changed.connect(sensor_characteristics_table.display_characteristics)
    plot_thread.my_signal.connect(plot_manager.update_graph)
    plot_thread.start(priority=QThread.Priority.HighPriority)

    ui.show()
    exit(app.exec_())
