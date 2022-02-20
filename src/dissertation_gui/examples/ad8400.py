import board
import digitalio

from ..devices.ad8400 import AD8400

cs = digitalio.DigitalInOut(board.CE0)
sclk = board.SCLK
mosi = board.MOSI
ad8400 = AD8400(clock=sclk, mosi=mosi, cs=cs)

if __name__ == '__main__':
    import time
    from loguru import logger

    logger.info(f"Инициализирован ad8400 с портами {sclk=}, {mosi=}, {cs=}")
    for i in range(ad8400.min_code, ad8400.max_code + 1):
        ad8400.send_code(i)
        logger.info(f"Отправляется код {i}")
        time.sleep(2)
