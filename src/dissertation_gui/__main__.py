import sys
import traceback

import pandas as pd
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QCheckBox,
)
from PyQt5.uic import loadUi
from loguru import logger
from pyqtgraph.widgets.PlotWidget import PlotWidget

from .database import Session
from .models.sensors import SensorType
from .services.sensor_characteristics import SensorCharacteristicsService
from .services.sensors import SensorsService
from .settings import settings
from .threads.calculations import TemperatureCalculationThread
from .threads.testing import (
    SetpointThread,
)
from .utils.calculations import LinearSolver
from .utils.plot_manager import TemperaturePlotManager
from .widgets import (
    SensorsComboBox,
    CharacteristicsTableWidget,
    SensorInfoTable,
    TRMParametersInfoTable,
)
from .workers import SensorWorker

if not settings.test_gui:
    import board
    from busio import (
        I2C,
        SPI,
    )
    from utils.periphery import get_pin
    from .threads.owen import TRMParametersReadThread
    from .protocols.owen import OwenClient
    from .devices import (
        AD8400,
        MCP4725,
        DigitalIORelay,
        RelaysController,
    )
    from .devices.managers import (
        ResistanceThermometerManager,
        UnifiedAnalogSignalManager,
        ThermocoupleManager,
    )
else:
    from .threads.owen import FakeTRMParametersReadThread
    from .devices.managers.mock import FakeManager

if not settings.test_gui:
    # пины и протоколы
    spi = SPI(clock=board.SCLK, MOSI=board.MOSI, MISO=None)
    ad8400_1 = AD8400(
        spi,
        settings.cs0_pin,
    )
    ad8400_2 = AD8400(
        spi,
        settings.cs1_pin,
    )
    mcp4725 = MCP4725(
        I2C(get_pin(settings.i2c_scl_pin), get_pin(settings.i2c_sda_pin)),
        settings.mcp4725_address,
    )
    relay_1 = DigitalIORelay(settings.relay_1_pin)
    relay_2 = DigitalIORelay(settings.relay_2_pin)
    relay_3 = DigitalIORelay(settings.relay_3_pin)
    relay_4 = DigitalIORelay(settings.relay_4_pin)
    relays = RelaysController([relay_1, relay_2, relay_3, relay_4])

    owen_client = OwenClient(port=settings.port,
                             baudrate=settings.baudrate,
                             timeout=settings.port_timeout,
                             address=settings.trm_address)
    trm_thread = TRMParametersReadThread(owen_client, update_period=settings.trm_update_period)

    resistance_thermometer_manager = ResistanceThermometerManager([ad8400_1, ad8400_2], relays)
    thermocouple_manager = ThermocoupleManager(mcp4725, relays)
    unified_analog_signal_manager = UnifiedAnalogSignalManager(mcp4725, relays)
else:
    trm_thread = FakeTRMParametersReadThread(update_period=settings.trm_update_period)  # noqa
    resistance_thermometer_manager = FakeManager()
    thermocouple_manager = FakeManager()
    unified_analog_signal_manager = FakeManager()

logger.info("Инициализация GUI")

app = QApplication([])
ui: QMainWindow = loadUi(settings.base_dir / "dissertation_gui" / "main_window.ui")
linear_solver = LinearSolver(k=1.0,
                             start_temperature=0.,
                             set_temperature=25.,
                             interference_amplitude=1.,
                             interference_frequency=1.)
temperature_calculation_thread = TemperatureCalculationThread(
    linear_solver,
    frequency=settings.plot_update_frequency
)
tab_menu: QTabWidget = ui.tab_menu

# вкладка График
temp_spin_box: QSpinBox = ui.temp_spin_box
k_spin_box: QDoubleSpinBox = ui.k_spin_box
bursts_check_box: QCheckBox = ui.bursts_check_box
reset_plot_button: QPushButton = ui.reset_plot_button
clear_plot_button: QPushButton = ui.clear_plot_button
sin_check_box: QCheckBox = ui.sin_check_box
interference_frequency_spin_box: QDoubleSpinBox = ui.interference_frequency_spin_box
interference_amplitude_spin_box: QDoubleSpinBox = ui.interference_amplitude_spin_box
# Вкладка Датчики
sensors_combo_box: SensorsComboBox = ui.sensors_combo_box
sensor_characteristics_table: CharacteristicsTableWidget = ui.sensor_characteristics_table
sensor_info_table: SensorInfoTable = ui.sensor_info_table
trm_plot: PlotWidget = ui.trm_plot
trm_plot.setBackground(settings.plot_background)
plot_manager = TemperaturePlotManager(trm_plot)

# вкладка Параметры ТРМ
trm_parameters_table: TRMParametersInfoTable = ui.trm_parameters_table

# вкладка Страница
uas_max_temp: QSpinBox = ui.uas_max_temp
uas_min_temp: QSpinBox = ui.uas_min_temp
sensors_combo_box_2: SensorsComboBox = ui.sensors_combo_box_2  # fixme: :)

uas_max_temp.setMaximum(100)
uas_max_temp.setMinimum(-50)
uas_min_temp.setMaximum(100)
uas_min_temp.setMinimum(-50)

session = Session()
sensors_service = SensorsService(session)
sensors_characteristics_service = SensorCharacteristicsService(session)
sensor_characteristics_table.set_service(sensors_characteristics_service)

sensor_worker_thread = QThread()
sensor_worker = SensorWorker({
    SensorType.RESISTANCE_THERMOMETER: resistance_thermometer_manager,
    SensorType.THERMO_COUPLE: thermocouple_manager,
    SensorType.UNIFIED_ANALOG_SIGNAL: unified_analog_signal_manager,
})
sensor_worker.moveToThread(sensor_worker_thread)
sensor_worker_thread.start(priority=QThread.Priority.NormalPriority)
sensor_list = sensors_service.get_sensors()
sensors_combo_box.sensor_changed.connect(sensor_characteristics_table.display_characteristics)
sensors_combo_box.sensor_changed.connect(sensor_info_table.update_info)
sensors_combo_box.set_sensors(sensor_list)
sensors_combo_box_2.set_sensors(sensor_list)
sensors_combo_box_2.sensor_changed.connect(sensor_worker.set_sensor)
interference_frequency_spin_box.valueChanged.connect(linear_solver.set_interference_frequency)
interference_amplitude_spin_box.valueChanged.connect(linear_solver.set_interference_amplitude)
temp_spin_box.valueChanged.connect(temperature_calculation_thread.set_temperature)
k_spin_box.valueChanged.connect(temperature_calculation_thread.set_k_ratio)
bursts_check_box.stateChanged.connect(linear_solver.set_burst_interference_enabled)
sin_check_box.stateChanged.connect(linear_solver.set_sinusoidal_interference_enabled)
temperature_calculation_thread.temperature_signal.connect(plot_manager.update_set_temp_curve)
temperature_calculation_thread.temperature_signal.connect(sensor_worker.set_temperature)
reset_plot_button.clicked.connect(lambda: trm_plot.getPlotItem().enableAutoRange())
clear_plot_button.clicked.connect(lambda: plot_manager.clear())
trm_thread.parameters_signal.connect(trm_parameters_table.update_info)
trm_thread.temperature_signal.connect(plot_manager.update_measured_temp_curve)
setpoint_thread = SetpointThread()
setpoint_thread.setpoint_signal.connect(plot_manager.update_setpoint_curve)

temperature_calculation_thread.start(priority=QThread.Priority.HighPriority)
setpoint_thread.start(priority=QThread.Priority.NormalPriority)
trm_thread.start(priority=QThread.Priority.NormalPriority)


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
app.aboutToQuit.connect(on_shutdown)  # noqa
logger.info("Запуск приложения")
ui.show()
app.exec()
