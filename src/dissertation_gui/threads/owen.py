import random
from typing import (
    List,
    Callable,
)

from PyQt5.QtCore import (
    QThread,
    pyqtSignal,
)
from loguru import logger

from ..models.owen import TRMParameter
from ..protocols.owen import OwenClient
from ..protocols.owen.const import Type
from ..protocols.owen.exceptions import OwenUnpackError

__all__ = ["TRMParametersReadThread", "FakeTRMParametersReadThread"]


class TRMParametersReadThread(QThread):
    parameters_signal = pyqtSignal(list)
    temperature_signal = pyqtSignal(float)
    output_signal = pyqtSignal(int)
    control_logic_signal = pyqtSignal(int)
    setpoint_signal = pyqtSignal(float)
    hysteresis_signal = pyqtSignal(float)

    params_to_read = [
        {"name": "PV", "index": None, "type_": Type.FLOAT24},
        {"name": "inF", "index": 0, "type_": Type.FLOAT24},
        {"name": "r.oUt", "index": None, "type_": Type.FLOAT24},
        {"name": "CmP", "index": 0, "type_": Type.UNSIGNED_CHAR},
        {"name": "in.L", "index": 0, "type_": Type.FLOAT24},
        {"name": "in.H", "index": 0, "type_": Type.FLOAT24},
        {"name": "in.t", "index": 0, "type_": Type.UNSIGNED_CHAR},
        {"name": "SP", "index": 0, "type_": Type.FLOAT24},
        {"name": "HYS", "index": 0, "type_": Type.FLOAT24},
    ]

    def __init__(self, client: OwenClient, update_period: float, parent=None, request_delay: float = 0.01):
        """
        :param update_period: Период опроса ТРМ в секундах
        :param request_delay: Задержка между запросами параметров в секундах
        """
        super().__init__(parent)
        self.client = client
        self.update_period = update_period
        self.request_delay = request_delay

    def read_parameters(self) -> List[TRMParameter]:
        read_parameters = []

        for param in self.params_to_read:
            try:
                value = self.client.get_parameter(**param)
            except OwenUnpackError:
                logger.exception(str(f"Не удалось распаковать параметр {param['name']}"))
            except Exception as e:
                logger.exception(str(e))
            else:
                read_parameters.append(TRMParameter(param["name"], value))
            self.msleep(int(self.request_delay * 1000))
        return read_parameters

    def emit_parameter(self,
                       params: List[TRMParameter],
                       name: str,
                       signal: pyqtSignal,
                       factory: Callable = None):
        filtered_param = [p for p in params if p.name.lower() == name.lower()]
        if len(filtered_param) > 0:
            value = filtered_param[0].value
            if factory is not None:
                value = factory(value)
            if not isinstance(value, tuple):
                signal.emit(value)  # noqa

    def run(self) -> None:  # TODO: сделать красиво
        while True:
            read_parameters = self.read_parameters()
            logger.debug(read_parameters)

            self.emit_parameter(read_parameters, "pv", self.temperature_signal)
            self.emit_parameter(read_parameters, "r.out", self.output_signal, int)
            self.emit_parameter(read_parameters, "cmp", self.control_logic_signal)
            self.emit_parameter(read_parameters, "sp", self.setpoint_signal)
            self.emit_parameter(read_parameters, "hys", self.hysteresis_signal)

            self.parameters_signal.emit(read_parameters)  # noqa
            self.msleep(int(self.update_period * 1000))


class FakeTRMParametersReadThread(TRMParametersReadThread):
    def __init__(self, update_period: float = 1., parent=None):
        super().__init__(None, update_period, parent)  # noqa

    def read_parameters(self) -> List[TRMParameter]:
        temperature = random.random() * 10
        return [
            TRMParameter("PV", temperature),
            TRMParameter("r.oUt", 1.),
            TRMParameter("Fake", 1),
            TRMParameter("CmP", 2),
            TRMParameter("SP", 20),
            TRMParameter("HYS", 2),
        ]
