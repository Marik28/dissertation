import struct
from typing import Tuple

from .exceptions import OwenUnpackError


def unpack_float(data: bytes, with_time: bool = False, with_index: bool = False):
    """Извлекает из данных число с плавающей точкой и время"""
    data_size = len(data)
    additional_bytes = 0
    if with_time:
        additional_bytes += 2
    if with_index:
        additional_bytes += 2
    if data_size != 4 + additional_bytes:
        raise OwenUnpackError(
            'OwenUnpackError: Wrong size of data ({0}) when IEEE32 unpacking, should be {1}!'.format(data_size, (
                    4 + additional_bytes)), data)
    value = struct.unpack('>f', data[0:4])[0]
    if with_time:
        time_pos = 4
        time = (((data[time_pos] & 0xff) << 8) | (data[time_pos + 1] & 0xff)) & 0xffff
    else:
        time = None
    if with_index:
        index_pos = 2 + additional_bytes
        index = (((data[index_pos] & 0xff) << 8) | (data[index_pos + 1] & 0xff)) & 0xffff
    else:
        index = None
    return value, time, index


def unpack_float24(data: bytes) -> float:
    data_size = len(data)
    if data_size != 3:
        raise OwenUnpackError('OwenUnpackError: Wrong size of data ({0}) when float24 unpacking!'.format(data_size),
                              data)
    return struct.unpack('>f', data[0:3] + b'\x00')[0]


def unpack_short(data: bytes) -> int:
    data_size = len(data)
    if data_size < 1:
        raise OwenUnpackError(
            'OwenUnpackError: Wrong size of data ({}) when short int unpacking!'.format(data_size),
            data)
    elif data_size == 1:
        data = b'\x00' + data  # дополняем до двух байтов
    return struct.unpack('>h', data[0:2])[0]


def unpack_unsigned_short(data: bytes) -> int:
    data_size = len(data)
    if data_size < 1:
        raise OwenUnpackError(
            'OwenUnpackError: Wrong size of data ({}) when unsigned short int unpacking!'.format(data_size), data)
    elif data_size == 1:
        data = b'\x00' + data  # дополняем до двух байтов
    return struct.unpack('>H', data[0:2])[0]


def unpack_string(data: bytes) -> str:
    return data[::-1].decode("cp1251")


def unpack_signed_char(data: bytes) -> int:
    data_size = len(data)
    if data_size != 1:
        raise OwenUnpackError('OwenUnpackError: Wrong size of data ({0}) when char unpacking!'.format(data_size),
                              data)
    return struct.unpack('b', data[:1])[0]


def unpack_unsigned_char(data: bytes) -> int:
    data_size = len(data)
    if data_size != 1:
        raise OwenUnpackError('OwenUnpackError: Wrong size of data ({0}) when char unpacking!'.format(data_size),
                              data)
    return struct.unpack('B', data[:1])[0]


def unpack_nerr(data: bytes) -> Tuple[int, int]:
    """

    :param data:
    :return: (error_code, parameter_hash)
    """
    error_code = struct.unpack(">B", data[0:1])[0]
    parameter_hash = struct.unpack('>H', data[1:3])[0]
    return error_code, parameter_hash
