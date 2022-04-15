import board
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
from adafruit_extended_bus import ExtendedSPI as SPI
from busio import I2C
from loguru import logger
from pyqtgraph.widgets.PlotWidget import PlotWidget

from .database import Session
from .devices import (
    AD8400,
    MCP4725,
    DigitalIORelay,
)
from .protocols.owen import OwenClient
from .services.sensor_characteristics import SensorCharacteristicsService
from .services.sensors import SensorsService
from .settings import settings
from .threads.calculations import TemperatureCalculationThread
from .threads.owen import TRMParametersReadThread
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

# пины и протоколы
ad8400_1 = AD8400(
    SPI(1, 0),
    getattr(board, settings.cs0_pin),
)
ad8400_2 = AD8400(
    SPI(1, 1),
    getattr(board, settings.cs1_pin),
)
mcp4725 = MCP4725(
    I2C(getattr(board, settings.i2c_scl_pin), getattr(board, settings.i2c_sda_pin)),
    settings.mcp4725_address,
)
relay_1 = DigitalIORelay(getattr(board, settings.relay_1_pin))
relay_2 = DigitalIORelay(getattr(board, settings.relay_2_pin))
relay_3 = DigitalIORelay(getattr(board, settings.relay_3_pin))
relay_4 = DigitalIORelay(getattr(board, settings.relay_4_pin))
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
plot_manager = PlotManager(graph, max_points=settings.plot_points)
trm_plot_manager = TRMInfoPlotManager(trm_plot)

# вкладка Параметры ТРМ
trm_relay_output_text: QTextBrowser = ui.trm_relay_output_text
trm_measured_temp_text: QTextBrowser = ui.trm_measured_temp_text

with Session() as session:
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
    plot_thread.start(priority=QThread.Priority.HighPriority)
    reset_plot_button.clicked.connect(lambda: graph.getPlotItem().enableAutoRange())
    owen_client = OwenClient(settings.port, settings.baudrate, address=settings.trm_address)
    trm_thread = TRMParametersReadThread(owen_client)
    trm_thread.parameter_signal.connect(
        lambda params: trm_relay_output_text.setText(
            "DEBUG:\n" + "\n".join([f"{k} - {v}" for k, v in params.items()])
        )
    )
    # doc_viewer: PdfViewer = ui.doc_viewer
    # doc_viewer.load_pdf(settings.base_dir.parent / "data" / "TRM" / "ТРМ201 документация.pdf")
    # doc_viewer.show()
    # fixme
    temp_thread = MeasuredTempThread()
    temp_thread.temp_signal.connect(trm_plot_manager.update_measured_temp_curve)
    setpoint_thread = SetpointThread()
    setpoint_thread.setpoint_signal.connect(trm_plot_manager.update_setpoint_curve)

    temp_thread.start(priority=QThread.Priority.NormalPriority)
    setpoint_thread.start(priority=QThread.Priority.NormalPriority)

    trm_thread.start(priority=QThread.Priority.NormalPriority)

    logger.info("Запуск приложения")
    try:
        ui.show()
        exit_code = app.exec_()
    except Exception as e:
        logger.error(e)
    finally:
        logger.info(f"Завершение работы приложения с кодом {exit_code}")
        exit(exit_code)
