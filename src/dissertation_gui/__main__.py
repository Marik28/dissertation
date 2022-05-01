import sys
import traceback

from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QCheckBox,
    QTextBrowser,
)
from PyQt5.uic import loadUi
from loguru import logger
from pyqtgraph.widgets.PlotWidget import PlotWidget

from .database import Session
from .services.sensor_characteristics import SensorCharacteristicsService
from .services.sensors import SensorsService
from .settings import settings
from .threads.calculations import TemperatureCalculationThread
from .threads.testing import (
    SetpointThread,
    MeasuredTempThread,
)
from .utils.plot_manager import (
    TRMInfoPlotManager,
    PlotManager,
)
from .widgets import (
    SensorsComboBox,
    CharacteristicsTableWidget,
    SensorInfoTable,
)
from .workers import SensorWorker

if not settings.test_gui:
    import board
    from utils.utils import get_pin
    from .threads.owen import TRMParametersReadThread
    from .protocols.owen import OwenClient
    from busio import (
        I2C,
        SPI,
    )
    from .devices import (
        AD8400,
        MCP4725,
        DigitalIORelay,
    )

if not settings.test_gui:
    # пины и протоколы
    ad8400_1 = AD8400(
        SPI(clock=board.SCLK, MOSI=board.MOSI, MISO=None),
        get_pin(settings.cs0_pin),
    )
    ad8400_2 = AD8400(
        SPI(clock=board.SCLK, MOSI=board.MOSI, MISO=None),
        get_pin(settings.cs1_pin),
    )
    mcp4725 = MCP4725(
        I2C(get_pin(settings.i2c_scl_pin), get_pin(settings.i2c_sda_pin)),
        settings.mcp4725_address,
    )
    relay_1 = DigitalIORelay(get_pin(settings.relay_1_pin))
    relay_2 = DigitalIORelay(get_pin(settings.relay_2_pin))
    relay_3 = DigitalIORelay(get_pin(settings.relay_3_pin))
    relay_4 = DigitalIORelay(get_pin(settings.relay_4_pin))

    owen_client = OwenClient(settings.port, settings.baudrate, address=settings.trm_address)
    trm_thread = TRMParametersReadThread(owen_client)
    trm_thread.parameter_signal.connect(
        lambda params: trm_relay_output_text.setText(
            "DEBUG:\n" + "\n".join([f"{k} - {v}" for k, v in params.items()])
        )
    )

    trm_thread.start(priority=QThread.Priority.NormalPriority)

logger.info("Инициализация GUI")

#  TODO добавить читалку документации ТРМ-а и протокола
app = QApplication([])
ui: QMainWindow = loadUi(settings.base_dir / "dissertation_gui" / "main_window.ui")
# plot_thread = ExamplePlotThread(frequency=settings.plot_update_frequency)
plot_thread = TemperatureCalculationThread()
tab_menu: QTabWidget = ui.tab_menu

# вкладка График
graph: PlotWidget = ui.graph
temp_spin_box: QSpinBox = ui.temp_spin_box
k_spin_box: QDoubleSpinBox = ui.k_spin_box
bursts_check_box: QCheckBox = ui.bursts_check_box
reset_plot_button: QPushButton = ui.reset_plot_button

# Вкладка Датчики
sensors_combo_box: SensorsComboBox = ui.sensors_combo_box
sensor_characteristics_table: CharacteristicsTableWidget = ui.sensor_characteristics_table
sensor_info_table: SensorInfoTable = ui.sensor_info_table
trm_plot: PlotWidget = ui.trm_plot

graph.setYRange(min=-50, max=100)
plot_manager = PlotManager(graph, max_points=settings.plot_points)
trm_plot_manager = TRMInfoPlotManager(trm_plot)

# вкладка Параметры ТРМ
trm_relay_output_text: QTextBrowser = ui.trm_relay_output_text
trm_measured_temp_text: QTextBrowser = ui.trm_measured_temp_text

# вкладка Страница
uas_max_temp: QSpinBox = ui.uas_max_temp
uas_min_temp: QSpinBox = ui.uas_min_temp

session = Session()
uas_max_temp.setMaximum(100)
uas_max_temp.setMinimum(-50)
uas_min_temp.setMaximum(100)
uas_min_temp.setMinimum(-50)

sensors_service = SensorsService(session)
sensors_characteristics_service = SensorCharacteristicsService(session)

sensor_characteristics_table.set_service(sensors_characteristics_service)

sensor_list = sensors_service.get_sensors()
sensors_combo_box.sensor_changed.connect(sensor_characteristics_table.display_characteristics)
sensors_combo_box.sensor_changed.connect(sensor_info_table.update_info)
sensors_combo_box.set_sensors(sensor_list)
temp_spin_box.valueChanged.connect(plot_thread.set_temperature)
k_spin_box.valueChanged.connect(plot_thread.set_k_ratio)
bursts_check_box.stateChanged.connect(plot_thread.set_enable_bursts)
plot_thread.temperature_signal.connect(plot_manager.update_graph)
plot_thread.temperature_signal.connect(trm_plot_manager.update_set_temp_curve)
reset_plot_button.clicked.connect(lambda: graph.getPlotItem().enableAutoRange())

temp_thread = MeasuredTempThread()
temp_thread.temp_signal.connect(trm_plot_manager.update_measured_temp_curve)
setpoint_thread = SetpointThread()
setpoint_thread.setpoint_signal.connect(trm_plot_manager.update_setpoint_curve)

sensor_worker_thread = QThread()
sensor_worker = SensorWorker({})
sensor_worker.moveToThread(sensor_worker_thread)

plot_thread.start(priority=QThread.Priority.HighPriority)
temp_thread.start(priority=QThread.Priority.NormalPriority)
setpoint_thread.start(priority=QThread.Priority.NormalPriority)
sensor_worker_thread.start(priority=QThread.Priority.NormalPriority)


def on_shutdown():
    session.close()
    logger.info(f"Завершение работы приложения")


def excepthook(exc_type, exc_value, exc_tb):
    if issubclass(exc_type, KeyboardInterrupt):
        msg = "KeyboardInterrupt"
    else:
        msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logger.error(msg)
    app.exit(-1)


sys.excepthook = excepthook
app.aboutToQuit.connect(on_shutdown)
logger.info("Запуск приложения")
ui.show()
app.exec()
