import time
from pathlib import Path
from typing import Tuple, List

import board
import numpy as np
import pandas as pd
import typer
from adafruit_extended_bus import ExtendedSPI as SPI

from dissertation_gui.devices import AD8400
from dissertation_gui.protocols.owen import OwenClient
from dissertation_gui.protocols.owen.exceptions import OwenProtocolError
from dissertation_gui.settings import settings

app = typer.Typer()


def test_owen(client: OwenClient):
    device = client.get_string("Dev")
    typer.echo(f"Протокол OWEN настроен. Устройство - {device}")


def save_result(codes: List, resistances: List, output: Path):
    df = pd.DataFrame({
        "code": codes,
        "value": resistances,
    })
    path = output / f"ad8400_{int(time.time())}.csv"
    df.to_csv(path, index=False)
    typer.echo(f"Файл сохранен по пути:\n{path}")


@app.command()
def main(
        cs: str = typer.Argument(...),
        bus: Tuple[int, int] = typer.Option((1, 0)),
        delay: float = typer.Option(1.0),
        output: Path = typer.Option(settings.base_dir.parent / "data" / "ad8400"),
        retries: int = typer.Option(1),
        precision: int = typer.Option(2),
        start: int = typer.Option(0),
        stop: int = typer.Option(256),
):
    typer.echo("Не забывайте выставить датчик 100П!", err=True)
    client = OwenClient(port=settings.port, baudrate=settings.baudrate, address=settings.trm_address)
    ad_8400 = AD8400(SPI(*bus), getattr(board, cs))
    sensor_data = pd.read_csv(settings.base_dir / "data" / "sensors_characteristics" / "100П.csv", index_col="temp")
    test_owen(client)
    codes = []
    resistances = []
    for code in range(start, stop):
        temperature = None
        for _ in range(retries):
            ad_8400.send_code(code)
            time.sleep(delay)
            try:
                temperature = client.get_float24("PV")
            except OwenProtocolError as e:
                typer.echo(e, err=True)
            if temperature is not None:
                break
        if temperature is None:
            save_result(codes, resistances, output)
            raise typer.Abort("Ошибка протокола")
        try:
            resistance = sensor_data.iloc[round(temperature)]["value"]
        except LookupError as e:
            typer.echo(str(e), err=True)
            resistance = np.nan
        codes.append(code)
        resistances.append(round(resistance, precision))
        typer.echo(f"Код - {code}, температура - {temperature}, сопротивление - {resistance}")
    save_result(codes, resistances, output)


if __name__ == '__main__':
    app()
