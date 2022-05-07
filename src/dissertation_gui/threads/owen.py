from dataclasses import (
    dataclass,
    fields,
)
from typing import (
    Union,
    Optional,
    Iterator, Dict, NamedTuple, Any, List,
)

from PyQt5.QtCore import (
    QThread,
    pyqtSignal,
)
from loguru import logger

from ..protocols.owen import OwenClient
from ..protocols.owen.const import Type
from ..protocols.owen.exceptions import OwenUnpackError

__all__ = ["TRMParametersReadThread", "FakeTRMParametersReadThread"]


@dataclass
class Parameter:
    value: Union[int, float]
    name: str
    type: Type
    index: Optional[int]


@dataclass
class TRMParameters:
    pv: Parameter
    inf: Parameter
    r_out: Parameter
    cmp: Parameter

    def __iter__(self) -> Iterator[Parameter]:
        return (getattr(self, field.name) for field in fields(self))


class TRMParameter(NamedTuple):
    name: str
    value: Any


class TRMParametersReadThread(QThread):
    parameters_signal = pyqtSignal(list)

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

    def read_parameters(self) -> List[Dict]:
        read_parameters = []

        for param in self.params_to_read:
            try:
                value = self.client.get_parameter(**param)
            except OwenUnpackError:
                value = self.client.get_last_error()
            read_parameters.append({"name": param["name"], "value": value})
        return read_parameters

    def run(self) -> None:  # TODO: сделать красиво
        while True:
            read_parameters = self.read_parameters()
            logger.debug(read_parameters)
            self.parameters_signal.emit(read_parameters)  # noqa
            self.msleep(int(self.update_period * 1000))


class FakeTRMParametersReadThread(TRMParametersReadThread):
    def __init__(self, client=None, update_period: float = 1., parent=None):
        super().__init__(client, update_period, parent)

    def read_parameters(self) -> List[Dict]:
        return [{"name": "PV", "value": 20.}, {"name": "r.oUt", "value": 1.}, {"name": "Fake", "value": 1}]
