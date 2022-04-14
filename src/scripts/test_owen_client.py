import typer

from dissertation_gui.protocols.owen import OwenClient
from dissertation_gui.settings import settings

app = typer.Typer()

client = OwenClient(port=settings.port, baudrate=settings.baudrate, address=settings.trm_address)


@app.command
def main():
    model = client.get_string("Dev")
    version = client.get_string("VER")
    typer.echo(f"Соединение успешно проверено. Устройство - {model} версии {version}")


if __name__ == '__main__':
    app()
