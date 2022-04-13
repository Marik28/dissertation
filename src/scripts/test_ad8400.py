import board
import typer
from adafruit_extended_bus import ExtendedSPI as SPI

from dissertation_gui.devices.ad8400 import AD8400
from dissertation_gui.devices.relay import DigitalIORelay

app = typer.Typer()

ad8400_1 = AD8400(SPI(1, 0), board.GPIO5)
ad8400_2 = AD8400(SPI(1, 1), board.GPIO16)
relay_1 = DigitalIORelay(...)
relay_2 = DigitalIORelay(...)
relay_3 = DigitalIORelay(...)
relay_4 = DigitalIORelay(...)


def configure_relays():
    pass


@app.command
def main():
    configure_relays()


if __name__ == '__main__':
    app()
