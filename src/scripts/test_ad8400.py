import board
import typer
from adafruit_extended_bus import ExtendedSPI as SPI

from dissertation_gui.devices.ad8400 import AD8400
from dissertation_gui.devices.relay import DigitalIORelay
from dissertation_gui.settings import settings

app = typer.Typer()

ad8400_1 = AD8400(SPI(1, 0), getattr(board, settings.cs0_pin))
ad8400_2 = AD8400(SPI(1, 1), getattr(board, settings.cs1_pin))
relay_1 = DigitalIORelay(getattr(board, settings.relay_1_pin))
relay_2 = DigitalIORelay(getattr(board, settings.relay_2_pin))
relay_3 = DigitalIORelay(getattr(board, settings.relay_3_pin))
relay_4 = DigitalIORelay(getattr(board, settings.relay_4_pin))


def configure_relays():
    pass


@app.command
def main():
    configure_relays()


if __name__ == '__main__':
    app()
