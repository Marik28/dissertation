from typing import List

import pandas as pd
import typer

from dissertation_gui import tables
from dissertation_gui.database import Session
from dissertation_gui.models.sensors import SensorType
from dissertation_gui.services.sensors import SensorsService
from dissertation_gui.settings import settings
from utils.utils import generate_resistance_thermometer_dataframe

app = typer.Typer()


@app.command()
def main():
    data_dir = settings.base_dir.parent / "data"
    typer.echo("Чтение датафреймов с характеристиками цифровых резисторов")
    digipot1_data = pd.read_csv(data_dir / "ad8400" / f"{settings.ad8400_1}.csv")
    digipot2_data = pd.read_csv(data_dir / "ad8400" / f"{settings.ad8400_2}.csv")
    with Session() as session:
        service = SensorsService(session)
        typer.echo("Чтение списка датчиков")
        sensors: List[tables.Sensor] = service.get_sensors()
    for sensor in sensors:
        if sensor.type == SensorType.RESISTANCE_THERMOMETER:
            typer.echo(f"Генерация датафрейма для датчика {sensor.name}")
            sensor_characteristics = pd.read_csv(
                data_dir / "sensors_characteristics" / f"{sensor.name}.csv",
                index_col="temp",
            )
            df = generate_resistance_thermometer_dataframe(
                sensor_characteristics,
                simulation_range=(-50, 100),
                digipot1_data=digipot1_data,
                digipot2_data=digipot2_data,
            )
            output_file = data_dir / "dataframes" / f"{sensor.name}.csv"
            df.to_csv(output_file)
            typer.echo(f"Датафрейм сохранен в {output_file}")


if __name__ == '__main__':
    app()
