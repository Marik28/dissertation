import time

import typer as typer

from dissertation_gui.__main__ import relay_1, relay_2, relay_3, relay_4

relays = [relay_1, relay_2, relay_3, relay_4]
app = typer.Typer()


@app.command
def main(delay: float = typer.Argument(0.5)):
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
