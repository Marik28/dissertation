import time

from PyQt5.QtCore import QThread
from pymodbus.client.sync import BaseModbusClient


# TODO выбрать параметры для отслеживания
#   - Измеренная величина
#   - Тип входного датчика или сигнала
#   - Постоянная времени цифрового фильтра
#   - Способ управления для выхода (холодильник/нагреватель)
#   - Уставка

class ThermoRegulatorInfoThread(QThread):
    """Поток для периодического опроса ТРМ-а по Modbus"""

    def __init__(self, client: BaseModbusClient, frequency: int = 1, parent=None):
        """

        :param client: инициализированный Modbus клиент
        :param frequency: частота опросов ТРМ-а (Гц)
        :param parent:
        """
        super().__init__(parent)
        self._client = client
        self._update_period = 1 / frequency

    def run(self) -> None:
        while True:
            # TODO реализовать
            with self._client as client:
                client.read_input_registers()
            time.sleep(self._update_period)
