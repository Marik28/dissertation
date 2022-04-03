from typing import List

from .exceptions import OwenProtocolError


def calculate_name_hash(name: str):
    # TODO подрефакторить
    id_ = [78, 78, 78, 78]
    index = 0
    for char in name:
        if '0' <= char <= '9':
            id_[index] = (ord(char) - ord('0')) * 2
        elif 'a' <= char <= 'z':
            id_[index] = (10 + ord(char) - ord('a')) * 2
        elif 'A' <= char <= 'Z':
            id_[index] = (10 + ord(char) - ord('A')) * 2
        elif '-' == char:
            id_[index] = 36 * 2
        elif '_' == char:
            id_[index] = 37 * 2
        elif '/' == char:
            id_[index] = 38 * 2
        elif '.' == char:
            id_[index - 1] += 1
            continue
        elif char == ' ':
            break  # пробел может находиться только в конце имени
        else:
            # недопустимый символ
            raise OwenProtocolError('OwenProtocol::Illegal symbol in name {} !'.format(name))
        index += 1
    return calculate_hash(id_)


def calculate_hash(data: List[int]) -> int:
    _hash = 0
    for byte in data:
        _hash ^= (byte << 9) & 0xFF00
        for i in range(7):
            if _hash & 0x8000:
                _hash = (_hash << 1) & 0xFFFF ^ 0x8F57
            else:
                _hash = (_hash << 1) & 0xFFFF
    return _hash


def calculate_crc(data: bytearray) -> int:
    crc = 0
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) & 0xFFFF ^ 0x8F57
            else:
                crc = (crc << 1) & 0xFFFF
    return crc
