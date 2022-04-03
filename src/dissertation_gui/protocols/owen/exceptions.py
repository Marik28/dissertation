# TODO использовать более конкретные ошибки

class OwenError(Exception):
    """Базовый класс для исключений"""
    pass


class OwenUnpackError(OwenError):
    """Исключение вызвано ошибкой распаковки данных
    Attributes:
        msg -- текст ошибки
        data -- данные
    """

    def __init__(self, msg, data):
        self.msg = msg
        self.data = data

    def __str__(self):
        return '{} Data: {}'.format(self.msg, list(self.data))


class OwenProtocolError(OwenError):
    pass


class HashMismatchError(OwenProtocolError):
    pass


class CRCMismatchError(OwenProtocolError):
    pass
