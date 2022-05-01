from dataclasses import (
    dataclass,
    fields,
)
from typing import (
    Union,
    Optional,
    Iterator,
)

from PyQt5.QtCore import (
    QThread,
    pyqtSignal,
)

from ..protocols.owen import OwenClient
from ..protocols.owen.const import Type
from ..protocols.owen.exceptions import OwenUnpackError

__all__ = ["TRMParametersReadThread"]


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


class TRMParametersReadThread(QThread):
    parameter_signal = pyqtSignal(dict)

    def __init__(self, client: OwenClient, update_period: float, parent=None):
        """
        :param update_period: Период опроса ТРМ в секундах
        """
        super().__init__(parent)
        self.client = client
        self.update_period = update_period

    def run(self) -> None:  # TODO: сделать красиво
        while True:
            read_parameters = {}
            params_to_read = [
                {"name": "PV", "index": None, "type_": Type.FLOAT24},
                {"name": "inF", "index": 0, "type_": Type.FLOAT24},
                {"name": "r.oUt", "index": None, "type_": Type.FLOAT24},
                {"name": "CmP", "index": 0, "type_": Type.UNSIGNED_CHAR},
                {"name": "in.L", "index": 0, "type_": Type.FLOAT24},
                {"name": "in.H", "index": 0, "type_": Type.FLOAT24},
            ]
            for param in params_to_read:
                try:
                    value = self.client.get_parameter(**param)
                except OwenUnpackError:
                    value = self.client.get_last_error()
                read_parameters[param["name"]] = value

            self.parameter_signal.emit(read_parameters)
            self.msleep(int(self.update_period * 1000))
