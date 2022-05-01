import time

import typer
from busio import I2C

from dissertation_gui.devices import (
    MCP4725,
    DigitalIORelay,
)
from dissertation_gui.settings import settings
from utils.utils import get_pin

app = typer.Typer()

mcp4725 = MCP4725(
    I2C(get_pin(settings.i2c_scl_pin), get_pin(settings.i2c_sda_pin)),
    settings.mcp4725_address,
)
relay_1 = DigitalIORelay(settings.relay_1_pin)
relay_2 = DigitalIORelay(settings.relay_2_pin)
relay_3 = DigitalIORelay(settings.relay_3_pin)
relay_4 = DigitalIORelay(settings.relay_4_pin)

relays = [relay_1, relay_2, relay_3, relay_4]


def configure_relays():
    relay_1.turn_off()
    relay_2.turn_off()
    relay_3.turn_off()
    relay_4.turn_on()


@app.command()
def main(
        delay: float = typer.Option(0.1),
        step: int = typer.Option(1),
        max_code: int = typer.Option(1000),
):
    configure_relays()
    typer.echo("Релюшки сконфигурированы")
    for code in range(0, max_code, step):
        mcp4725.send_code(code)
        typer.echo(f"Отправлен код {code}")
        time.sleep(delay)


if __name__ == '__main__':
    app()
