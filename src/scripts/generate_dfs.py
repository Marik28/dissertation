from typing import List

import pandas as pd
import typer

from dissertation_gui import tables
from dissertation_gui.database import Session
from dissertation_gui.models.sensors import SensorType
from dissertation_gui.services.sensors import SensorsService
from dissertation_gui.settings import settings
from utils.utils import (
    generate_resistance_thermometer_dataframe,
    generate_thermocouple_dataframe,
)

app = typer.Typer()


@app.command()
def main(overwrite: bool = True):
    data_dir = settings.base_dir.parent / "data"
    not_simulated = [14, 25]
    typer.echo("Чтение датафреймов с характеристиками цифровых резисторов. "
               f"Используются {settings.ad8400_1} и {settings.ad8400_2}")
    digipot1_data = pd.read_csv(data_dir / "ad8400" / f"{settings.ad8400_1}.csv")
    digipot2_data = pd.read_csv(data_dir / "ad8400" / f"{settings.ad8400_2}.csv")
    simulation_range = (-50, 100)

    with Session() as session:
        service = SensorsService(session)
        typer.echo("Чтение списка датчиков")
        sensors: List[tables.Sensor] = service.get_sensors()

    for sensor in sensors:
        typer.echo(f"Генерация датафрейма для датчика {sensor.name}")
        output_file = data_dir / "dataframes" / f"{sensor.name}.csv"

        if sensor.int_code in not_simulated:
            typer.echo(f"{sensor.name} не симулируется, он будет пропущен")
            continue

        if not overwrite and output_file.exists():
            typer.echo(f"{output_file} существует, он будет пропущен.")
            continue

        if sensor.type == SensorType.RESISTANCE_THERMOMETER:
            sensor_characteristics = pd.read_csv(
                data_dir / "sensors_characteristics" / f"{sensor.name}.csv",
                index_col="temp",
            )
            df = generate_resistance_thermometer_dataframe(
                sensor_characteristics,
                simulation_range=simulation_range,
                digipot1_data=digipot1_data,
                digipot2_data=digipot2_data,
            )

        elif sensor.type == SensorType.THERMO_COUPLE:
            sensor_characteristics = pd.read_csv(
                data_dir / "sensors_characteristics" / f"{sensor.name}.csv",
                index_col="temp",
            )
            mcp_data = pd.read_csv(data_dir / "DAC" / "mcp4725.csv")
            df = generate_thermocouple_dataframe(
                sensor_characteristics,
                simulation_range=(0, 100),
                mcp_data=mcp_data,
            )
        else:
            df = None

        if df is not None:
            df.to_csv(output_file)
            typer.echo(f"Датафрейм сохранен в {output_file}")


if __name__ == '__main__':
    app()
