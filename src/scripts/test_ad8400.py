import time

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

relays = [relay_1, relay_2, relay_3, relay_4]


def configure_relays():
    relay_3.turn_on()
    relay_4.turn_off()


@app.command()
def main(delay: float = typer.Option(0.2)):
    configure_relays()
    typer.echo("Релюшки сконфигурированы")
    ad8400_1.send_code(0)
    for code in range(255):
        ad8400_2.send_code(code)
        typer.echo(f"Отправлен код {code}")
        time.sleep(delay)


if __name__ == '__main__':
    app()
