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


def pack_faw_frame(frame: bytearray) -> bytearray:
    """Добавляет маркировки конца и начала кадра, преобразует тетрады байт в ASCII символы для передачи"""
    raw_frame = bytearray()
    raw_frame.append(ord('#'))  # маркер начала кадра
    for byte in frame:
        raw_frame.append(0x47 + (byte >> 4))  # первая тетрада
        raw_frame.append(0x47 + (byte & 0x0F))  # вторая тетрада
    raw_frame.append(ord('\r'))  # маркер конца кадра
    return raw_frame


def unpack_raw_frame(raw_frame: bytes) -> bytearray:
    frame = bytearray()
    if raw_frame[0] != ord('#') or raw_frame[-1] != ord('\r'):
        raise OwenProtocolError('OwenProtocolError: Raw buffer does not have start or stop bytes!')
    for i in range(1, len(raw_frame) - 2, 2):
        # склеиваем тетрады
        first_tetrad = (raw_frame[i] - 0x47) << 4
        second_tetrad = (raw_frame[i + 1] - 0x47)
        frame.append(first_tetrad | second_tetrad)
    return frame
