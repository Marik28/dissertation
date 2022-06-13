from contextlib import contextmanager
from threading import Lock
from typing import (
    Tuple,
    Dict,
    Union,
    Callable,
)

from loguru import logger
from serial import Serial
from typing_extensions import Literal

from .const import Type
from .exceptions import OwenProtocolError
from .helpers import (
    calculate_crc,
    calculate_name_hash,
    pack_faw_frame,
    unpack_raw_frame,
)
from .sctructs import (
    unpack_short,
    unpack_unsigned_short,
    unpack_signed_char,
    unpack_float24,
    unpack_string,
    unpack_nerr,
)

__all__ = ["OwenClient"]


class OwenClient:
    """Класс, реализующий протокол ОВЕН"""

    SUPPORTED_BAUDRATES = [2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600, 115200]
    """Поддерживаемые ТРМ-ом скорости обмена в бод"""

    FRAME_MIN_LENGTH = 6

    parsers: Dict[Type, Callable[[bytes], Union[int, float, str, Tuple[int, int]]]] = {
        Type.SIGNED_CHAR: unpack_signed_char,
        Type.UNSIGNED_CHAR: unpack_signed_char,
        Type.SHORT: unpack_short,
        Type.UNSIGNED_SHORT: unpack_unsigned_short,
        Type.FLOAT24: unpack_float24,
        Type.STRING: unpack_string,
        Type.NERR: unpack_nerr,
    }

    def __init__(self,
                 port: str,
                 baudrate: int = 9600,
                 timeout: float = 0.2,
                 address: int = 0,
                 address_length: Literal[8, 11] = 8):
        """
        :param port: Название используемого порта. Пример - для Windows - 'COM1', для Linux - '/dev/ttyUSB0'
        :param baudrate: Скорость передачи данных
        :param timeout: Таймаут в секундах
        :param address: Адрес прибора в сети. Положительное целое число
        :param address_length: Длина адреса прибора в сети в битах (8 либо 11)
        """
        if baudrate not in self.SUPPORTED_BAUDRATES:
            raise OwenProtocolError("Unsupported baudrate!")
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
        if len(frame) < self.FRAME_MIN_LENGTH:
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
        return frame

    def get_parameter(self, name: str, type_: Type, index: int = None):
        """\
        Запрашивает значение параметра.

        :param name: Имя запрашиваемого параметра
        :param index: Индекс запрашиваемого параметра (если имеется)
        :param type_: Тип запрашиваемого параметра
        :return: Значение параметра соответствующего типа python
        :raises OwenProtocolError:
        """
        _hash = calculate_name_hash(name)
        request_frame = self.pack_frame(_hash, self._address, index)
        raw_request_frame = pack_faw_frame(request_frame)
        self._logger.debug(f'Request parameter: name={name} hash={_hash:#x} address={self._address:#x} index={index} '
                           f'sent frame={raw_request_frame}')
        self._serial.reset_input_buffer()
        self._serial.write(raw_request_frame)
        raw_response_frame = self._serial.read_until(b'\r')
        if len(raw_response_frame) == 0:
            raise OwenProtocolError('OwenProtocolError: No data received from serial port!')
        self._logger.debug(f'Response: frame={raw_response_frame}')
        frame = unpack_raw_frame(raw_response_frame)
        response_hash, response_data = self.unpack_frame(frame)
        if response_hash != _hash:
            raise OwenProtocolError('OwenProtocolError: Hash mismatch!')
        if index is not None:
            response_data = response_data[:-2]
        return self.parsers[type_](response_data)

    def get_short(self, name: str, index: int = None) -> int:
        return self.get_parameter(name, Type.SHORT, index)

    def get_unsigned_short(self, name: str, index: int = None) -> int:
        return self.get_parameter(name, Type.UNSIGNED_SHORT, index)

    def get_signed_char(self, name: str, index: int = None) -> int:
        return self.get_parameter(name, Type.SIGNED_CHAR, index)

    def get_unsigned_char(self, name: str, index: int = None) -> int:
        return self.get_parameter(name, Type.UNSIGNED_CHAR, index)

    def get_float24(self, name: str, index: int = None) -> float:
        return self.get_parameter(name, Type.FLOAT24, index)

    def get_string(self, name: str, index: int = None) -> str:
        return self.get_parameter(name, Type.STRING, index)

    def get_last_error(self) -> Tuple[int, int]:
        """\
        Возвращает значение параметра N.err.

        :returns: (error_code, parameter_hash)
        error_code - код ошибки.
        parameter_hash - Хэш параметра, при запросе которого произошла ошибка
        """
        return self.get_parameter("N.err", Type.NERR)

    def close(self):
        self._serial.close()
