import board
from adafruit_extended_bus import ExtendedSPI as SPI

from dissertation_gui.settings import settings
from ..devices.ad8400 import AD8400

ad8400 = AD8400(SPI(1, 0), getattr(board, settings.cs0_pin))

if __name__ == '__main__':
    import time

    for i in range(ad8400.min_code, ad8400.max_code + 1):
        ad8400.send_code(i)
        time.sleep(2)
