from typing import List

import pandas as pd
import sqlalchemy.orm
import sqlalchemy.orm

from dissertation_gui import tables
from dissertation_gui.database import Session, engine
from dissertation_gui.models.sensors import SensorType
from dissertation_gui.settings import settings


def insert_sensors(session: sqlalchemy.orm.Session) -> List[tables.Sensor]:
    df = pd.read_csv(settings.base_dir.parent / "data" / "sensors.csv")
    sensors_to_add = [
        tables.Sensor(
            name=row["name"],
            type=SensorType(row["type"]),
            trm_code=row["trm_code"],
            units=row["units"],
            physical_quantity=row["physical_quantity"],
        ) for _, row in df.iterrows()
    ]
    session.add_all(sensors_to_add)
    session.commit()
    return sensors_to_add


def add_characteristics(session: sqlalchemy.orm.Session, sensors: List[tables.Sensor]):
    for sensor in sensors:
        if sensor.type == SensorType.UNIFIED_ANALOG_SIGNAL:
            continue
        df = pd.read_csv(settings.base_dir.parent / "data" / "sensors_characteristics" / f"{sensor.name}.csv")
        characteristics = [
            tables.SensorCharacteristics(
                sensor=sensor,
                temperature=float(row["temp"]),
                value=float(row["value"]),
            ) for _, row in df.iterrows()
        ]
        session.add_all(characteristics)
        session.commit()


def main(session: sqlalchemy.orm.Session):
    tables.Base.metadata.create_all(engine)
    added_sensors = insert_sensors(session)
    add_characteristics(session, added_sensors)


if __name__ == '__main__':
    with Session() as session:
        main(session)
