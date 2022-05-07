from typing import NamedTuple, Union


class TRMParameter(NamedTuple):
    name: str
    value: Union[int, float, str, tuple]
