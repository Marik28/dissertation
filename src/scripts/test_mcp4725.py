import board
import typer
from busio import I2C

from dissertation_gui.devices import (
    MCP4725,
    DigitalIORelay,
)
from dissertation_gui.settings import settings

app = typer.Typer()

mcp4725 = MCP4725(
    I2C(getattr(board, settings.i2c_scl_pin), getattr(board, settings.i2c_sda_pin)),
    settings.mcp4725_address,
)
relay_1 = DigitalIORelay(getattr(board, settings.relay_1_pin))
relay_2 = DigitalIORelay(getattr(board, settings.relay_2_pin))
relay_3 = DigitalIORelay(getattr(board, settings.relay_3_pin))
relay_4 = DigitalIORelay(getattr(board, settings.relay_4_pin))

relays = [relay_1, relay_2, relay_3, relay_4]


def configure_relays():
    pass


@app.command
def main():
    configure_relays()


if __name__ == '__main__':
    app()
