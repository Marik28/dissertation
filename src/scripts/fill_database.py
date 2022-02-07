import pandas as pd
import sqlalchemy.orm
import sqlalchemy.orm

from dissertation_gui import tables
from dissertation_gui.database import Session, engine
from dissertation_gui.models.sensors import SensorType
from dissertation_gui.settings import settings


def insert_sensors(session: sqlalchemy.orm.Session) -> list[tables.Sensor]:
    df = pd.read_csv(settings.base_dir.parent / "data" / "sensors.csv")
    sensors_to_add = [
        tables.Sensor(
            name=row["name"],
            type=SensorType(row["type"]),
            trm_code=row["trm_code"],
        ) for _, row in df.iterrows()
    ]
    session.add_all(sensors_to_add)
    session.commit()
    return sensors_to_add


def add_characteristics(session: sqlalchemy.orm.Session, sensors: list[tables.Sensor]):
    for sensor in sensors:
        df = pd.read_csv(settings.base_dir.parent / "data" / "real_sensors" / f"{sensor.name}.csv")
        characteristics = [
            tables.ResistanceThermometerCharacteristics(
                sensor=sensor,
                temperature=float(row["T"]),
                resistance=float(row["R"]),
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
