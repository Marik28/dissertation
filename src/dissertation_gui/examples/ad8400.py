import board
from busio import SPI

from dissertation_gui.settings import settings
from ..devices.ad8400 import AD8400

ad8400 = AD8400(SPI(clock=board.SCLK, MOSI=board.MOSI), settings.cs0_pin)

if __name__ == '__main__':
    import time

    for i in range(ad8400.min_code, ad8400.max_code + 1):
        ad8400.send_code(i)
        time.sleep(2)
