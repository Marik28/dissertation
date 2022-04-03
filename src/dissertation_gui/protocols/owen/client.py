from contextlib import contextmanager
from threading import Lock
from typing import (
    Literal,
    Tuple,
)

from loguru import logger
from serial import Serial

from .exceptions import OwenProtocolError
from .helpers import (
    calculate_crc,
    calculate_name_hash,
)
from .sctructs import (
    unpack_int16,
    unpack_uint16,
    unpack_char,
    unpack_float32,
    unpack_float24,
    unpack_string,
    unpack_nerr,
)

__all__ = ["OwenClient"]


class OwenClient:
    """Класс, реализующий протокол ОВЕН"""

    frame_min_length = 6

    def __init__(self,
                 port: str,
                 baudrate: int = 9600,
                 timeout: float = 0.2,
                 address: int = 1,
                 address_length: Literal[8, 11] = 8):
        """
        :param port: Название используемого порта. Пример - для Windows - 'COM1', для Linux - '/dev/ttyUSB0'
        :param baudrate: Скорость передачи данных
        :param timeout: Таймаут в секундах
        :param address: Адрес прибора в сети. Положительное целое число
        :param address_length: Длина адреса прибора в сети в битах (8 либо 11)
        """
        self._serial = Serial(port, baudrate, timeout=timeout)
        self._address = address
        self._address_length = address_length
        self._mutex = Lock()
        self._logger = logger

    @contextmanager
    def _lock_thread(self):  # TODO: использовать либо вообще убрать
        self._mutex.acquire()
        try:
            yield
        finally:
            self._mutex.release()

    def unpack_frame(self, frame: bytearray) -> Tuple[int, bytes]:
        if len(frame) < self.frame_min_length:
            raise OwenProtocolError('OwenProtocolError: Small length of frame!')
        # контрольная сумма
        crc = frame[-2] << 8 | frame[-1]
        if crc != calculate_crc(frame[:-2]):
            raise OwenProtocolError('OwenProtocolError: CRC mismatch!')
        _hash = frame[2] << 8 | frame[3]
        # размер данных
        data_size = frame[1] & 0x0F
        if data_size > 0:
            if data_size != len(frame) - 6:
                raise OwenProtocolError('OwenProtocolError: Wrong data size value in frame!')
            data = bytes(frame[4:4 + data_size])
        else:
            data = b''
        return _hash, data

    def unpack_raw_frame(self, raw_frame: bytes) -> bytearray:
        frame = bytearray()
        if raw_frame[0] != ord('#') or raw_frame[-1] != ord('\r'):
            raise OwenProtocolError('OwenProtocolError: Raw buffer does not have start or stop bytes!')
        for i in range(1, len(raw_frame) - 2, 2):
            # склеиваем тетрады
            first_tetrad = (raw_frame[i] - 0x47) << 4
            second_tetrad = (raw_frame[i + 1] - 0x47)
            frame.append(first_tetrad | second_tetrad)
        return frame

    def pack_frame(self, hash_: int, address: int, index: int = None):
        frame = bytearray()
        if self._address_length == 8:
            frame.append(address & 0xff)
            frame.append(0)
        else:
            frame.append((address >> 3) & 0xff)
            frame.append((address & 0x07) << 5)
        frame[1] |= 0x10
        # хэш
        frame.append((hash_ >> 8) & 0xff)
        frame.append(hash_ & 0xff)
        # данные
        data = b''
        if index is not None:
            data += chr((index >> 8) & 0x0F).encode()
            data += chr(index & 0x0F).encode()
            frame[1] |= len(data)

        frame.extend(data)
        # контрольная сумма
        crc = calculate_crc(frame)
        frame.append((crc >> 8) & 0xff)
        frame.append(crc & 0xff)
        self._logger.info(f'Sending: frame size={len(frame)} hash={hash_:#x} address={self._address:#x} data={data} '
                          f'index={index} crc={crc}')
        return frame

    def pack_faw_frame(self, frame: bytearray) -> bytearray:
        """Добавляет маркировки конца и начала кадра, преобразует тетрады байт в ASCII символы для передачи"""
        raw_frame = bytearray()
        raw_frame.append(ord('#'))  # маркер начала кадра
        for byte in frame:
            raw_frame.append(0x47 + (byte >> 4))  # первая тетрада
            raw_frame.append(0x47 + (byte & 0x0F))  # вторая тетрада
        raw_frame.append(ord('\r'))  # маркер конца кадра
        return raw_frame

    def get_parameter(self, name: str, index: int = None) -> bytes:
        """\
        Запрашивает значение параметра.

        :param name: Имя запрашиваемого параметра
        :param index: Индекс запрашиваемого параметра (если имеется)
        :return: Значение параметра в байтах
        :raises OwenProtocolError:
        """
        _hash = calculate_name_hash(name)
        request_frame = self.pack_frame(_hash, self._address, index)
        raw_request_frame = self.pack_faw_frame(request_frame)
        self._logger.info('Sent: {}'.format(raw_request_frame))
        self._serial.reset_input_buffer()
        self._serial.write(raw_request_frame)
        raw_response_frame = self._serial.read_until(b'\r')
        raw_frame_size = len(raw_response_frame)
        if raw_frame_size == 0:
            raise OwenProtocolError('OwenProtocolError: No data received from serial port!')
        self._logger.info('Reading::Length: {1} Received: {0}'.format(raw_response_frame, raw_frame_size))
        frame = self.unpack_raw_frame(raw_response_frame)
        ret_hash, data_ret = self.unpack_frame(frame)
        if ret_hash != _hash:
            raise OwenProtocolError('OwenProtocolError: Hash mismatch!')
        return data_ret

    def get_int16(self, name: str) -> int:
        data = self.get_parameter(name)
        return unpack_int16(data)

    def get_uint16(self, name: str) -> int:
        data = self.get_parameter(name)
        return unpack_uint16(data)

    def get_char(self, name: str) -> int:
        data = self.get_parameter(name)
        return unpack_char(data)

    def get_float32(self, name: str, with_time: bool = False, with_index: bool = False) -> float:
        data = self.get_parameter(name)
        return unpack_float32(data, with_time, with_index)

    def get_float24(self, name: str) -> float:
        data = self.get_parameter(name)
        return unpack_float24(data)

    def get_string(self, name: str) -> str:
        data = self.get_parameter(name)
        return unpack_string(data)

    def get_last_error(self) -> Tuple[int, int]:
        """\
        Возвращает значение параметра N.err.

        1 число - код ошибки. 2 - Хэш параметра, при запросе на который произошла ошибка

        :returns: (error_code, parameter_hash)
        """
        data = self.get_parameter("N.err")
        return unpack_nerr(data)
