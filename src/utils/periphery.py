import board


def get_pin(pin_name: str):
    """
    :param pin_name: Название пина в библиотеке board
    """
    return getattr(board, pin_name)
