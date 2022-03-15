import enum

from pymodbus.client.sync import BaseModbusClient


class TRMModbusDataType(enum.Enum):
    """
    Типы данных, описанные в инструкции по работе с ТРМ201 по RS-485
    (https://owen.ru/uploads/20/ki_prm_trm201_032.pdf)
    """
    INT_16 = "Int16"
    SIGNED_INT_16 = "Signed Int16"
    FLOAT_32 = "float32"
    CHAR_8 = "Char[8]"
    HEX_WORD = "Hex word"
    BINARY = "Binary"


bytes_len = {  # fixme нормальное название
    TRMModbusDataType.INT_16: 1,
    TRMModbusDataType.SIGNED_INT_16: 1,
    TRMModbusDataType.FLOAT_32: 2,
    TRMModbusDataType.CHAR_8: 8 * 4,
    TRMModbusDataType.HEX_WORD: 2,
    TRMModbusDataType.BINARY: 2,
}
"""Количество регистров, занимаемое соответствующим типом данных"""


def cast_int_16(raw_value: bytes) -> int:
    ...


def cast_signed_int_16(raw_value: bytes) -> int:
    ...


def cast_float_32(raw_value: bytes) -> float:
    ...


def cast_binary(raw_value: bytes) -> int:
    ...


def cast_char_8(raw_value: bytes) -> str:
    ...


def cast_hex_word(raw_value: bytes) -> int:
    ...


class TRMModbusRegister:  # TODO: реализовать
    def __init__(self, address: int, datatype: TRMModbusDataType):
        self._address = address
        self._count = bytes_len[datatype]

    def cast(self, data: bytes):
        ...


class TRMModbusClient:  # TODO: реализовать
    def __init__(self, modbus_client: BaseModbusClient):
        self._client = modbus_client

    def read_register(self, register: TRMModbusRegister):
        ...
