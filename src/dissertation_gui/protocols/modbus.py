import enum
from typing import List

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
    BINARY = "binary"


trm_datatype_to_python_type = {
    TRMModbusDataType.INT_16: int,
    TRMModbusDataType.SIGNED_INT_16: int,
    TRMModbusDataType.FLOAT_32: float,
    TRMModbusDataType.CHAR_8: str,
    TRMModbusDataType.HEX_WORD: int,
    TRMModbusDataType.BINARY: int,
}

type_register_lens = {  # fixme нормальное название
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
    datatype = None

    def __init__(self, address: int, client: BaseModbusClient):
        self._address = address
        self._count = type_register_lens[self.datatype]
        self._client = client

    def decode(self, data: List[bytes]):  # как понимаю, после чтения с трм-а, возвращается массив байт
        ...

    def read(self):
        ...

    def _read(self) -> bytes:
        return self._client.read_input_registers(self._address, self._count)


class TRMModbusClient:  # TODO: реализовать
    """
    Настройка обмена данными осуществляется параметрами группы COMM:
        - PROT – протокол обмена данными (ОВЕН, ModBus-RTU, ModBus-ASCII);
        - bPS – скорость обмена в сети, допустимые значения – 2400, 4800, 9600, 14400 19200, 28800, 38400, 57600, 115200 бит/с;
        - Addr – базовый адрес прибора, диапазон значений:

          - 0…255 при Prot = OWEN и A.LEN = 8;
          - 0…2047 при Prot = OWEN и A.LEN = 11;
          - 1…247 при Prot = M.RTU или M.ASC.
    """

    def __init__(self, modbus_client: BaseModbusClient):
        self._client = modbus_client

    def read_register(self, register: TRMModbusRegister):
        ...
