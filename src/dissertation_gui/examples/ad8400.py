import board
import digitalio
from busio import SPI

from ..devices.ad8400 import AD8400

cs = digitalio.DigitalInOut(board.CE0)
sclk = board.SCLK
mosi = board.MOSI
spi = SPI(clock=sclk, MOSI=mosi)
ad8400 = AD8400(spi, cs=cs)

if __name__ == '__main__':
    import time

    for i in range(ad8400.min_code, ad8400.max_code + 1):
        ad8400.send_code(i)
        time.sleep(2)
