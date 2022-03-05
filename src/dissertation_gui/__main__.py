from PyQt5.QtCore import (
    QThread,
)
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QTextBrowser,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QCheckBox,
)
from PyQt5.uic import loadUi
from pyqtgraph.widgets.PlotWidget import PlotWidget

from .database import Session
from .services.sensor_characteristics import SensorCharacteristicsService
from .services.sensors import SensorsService
from .settings import settings
# from .threads.plot import ExamplePlotThread
from .threads.calculations import TemperatureCalculationThread
from .utils.plot_manager import PlotManager
from .widgets.combo_boxes import SensorsComboBox
from .widgets.tables import CharacteristicsTableWidget

app = QApplication([])
ui: QMainWindow = loadUi(settings.base_dir / "dissertation_gui" / "main_window.ui")
# plot_thread = ExamplePlotThread(frequency=settings.plot_update_frequency)
plot_thread = TemperatureCalculationThread()
tab_menu: QTabWidget = ui.tab_menu
graph: PlotWidget = ui.graph
reset_plot_button: QPushButton = ui.reset_plot_button
sensors_combo_box: SensorsComboBox = ui.sensors_combo_box
sensor_info_text_browser: QTextBrowser = ui.sensor_info_text_browser
sensor_characteristics_table: CharacteristicsTableWidget = ui.sensor_characteristics_table
temp_spin_box: QSpinBox = ui.temp_spin_box
k_spin_box: QDoubleSpinBox = ui.k_spin_box
bursts_check_box: QCheckBox = ui.bursts_check_box
plot_manager = PlotManager(graph, plot_length=settings.plot_points)

with Session() as session:
    sensors_service = SensorsService(session)
    sensors_characteristics_service = SensorCharacteristicsService(session)

    sensor_characteristics_table.set_service(sensors_characteristics_service)

    sensor_list = sensors_service.get_sensors()
    sensors_combo_box.sensor_changed.connect(sensor_characteristics_table.display_characteristics)
    sensors_combo_box.set_sensors(sensor_list)
    # sensors_combo_box.sensor_changed.connect(sensor_info_text_browser.setText)
    temp_spin_box.valueChanged.connect(plot_thread.set_temperature)
    k_spin_box.valueChanged.connect(plot_thread.set_k_ratio)
    bursts_check_box.stateChanged.connect(plot_thread.set_enable_bursts)
    plot_thread.temperature_signal.connect(plot_manager.update_graph)
    plot_thread.start(priority=QThread.Priority.HighPriority)
    reset_plot_button.clicked.connect(lambda: graph.getPlotItem().enableAutoRange())

    ui.show()
    exit(app.exec_())
