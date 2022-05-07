import random
from typing import (
    List,
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

    params_to_read = [
        {"name": "PV", "index": None, "type_": Type.FLOAT24},
        {"name": "inF", "index": 0, "type_": Type.FLOAT24},
        {"name": "r.oUt", "index": None, "type_": Type.FLOAT24},
        {"name": "CmP", "index": 0, "type_": Type.UNSIGNED_CHAR},
        {"name": "in.L", "index": 0, "type_": Type.FLOAT24},
        {"name": "in.H", "index": 0, "type_": Type.FLOAT24},
    ]

    def __init__(self, client: OwenClient, update_period: float, parent=None):
        """
        :param update_period: Период опроса ТРМ в секундах
        """
        super().__init__(parent)
        self.client = client
        self.update_period = update_period

    def read_parameters(self) -> List[TRMParameter]:
        read_parameters = []

        for param in self.params_to_read:
            try:
                value = self.client.get_parameter(**param)
            except OwenUnpackError:
                try:
                    value = self.client.get_last_error()
                except Exception as e:  # fixme: да да я
                    logger.error(e)
                    value = 0.0
            except Exception as e:
                logger.error(e)
                value = 0.
            read_parameters.append(TRMParameter(param["name"], value))
        return read_parameters

    def run(self) -> None:  # TODO: сделать красиво
        while True:
            read_parameters = self.read_parameters()
            filtered_temp_param = [p for p in read_parameters if p.name.lower() == "pv"]
            if len(filtered_temp_param) > 0:
                temperature = filtered_temp_param[0].value
                if not isinstance(temperature, tuple):
                    self.temperature_signal.emit(temperature)  # noqa
            filtered_output_param = [p for p in read_parameters if p.name.lower() == "r.out"]
            if len(filtered_output_param) > 0:
                output = int(filtered_output_param[0].value)
                self.output_signal.emit(output)  # noqa
            logger.debug(read_parameters)
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
        ]
