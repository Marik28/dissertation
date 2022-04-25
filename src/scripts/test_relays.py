import time

import typer

from dissertation_gui.devices.relay import DigitalIORelay
from dissertation_gui.settings import settings
from utils.utils import get_pin

relays = [
    DigitalIORelay(get_pin(settings.relay_1_pin)),
    DigitalIORelay(get_pin(settings.relay_2_pin)),
    DigitalIORelay(get_pin(settings.relay_3_pin)),
    DigitalIORelay(get_pin(settings.relay_4_pin)),
]
app = typer.Typer()


@app.command()
def main(delay: float = typer.Argument(0.5, min=0)):
    typer.echo(f"Начало теста. Задержка между переключениями - {delay}")
    typer.echo("Включение всех релюх")
    for relay in relays:
        relay.turn_on()
        time.sleep(delay)
    time.sleep(delay)
    typer.echo("Отключение всех релюх")
    for relay in reversed(relays):
        relay.turn_off()
        time.sleep(delay)
    typer.echo("Тест завершен")


if __name__ == '__main__':
    app()
