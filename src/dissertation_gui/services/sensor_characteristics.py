from typing import List

import sqlalchemy.orm

from .. import tables


class SensorCharacteristicsService:
    def __init__(self, session: sqlalchemy.orm.Session):
        self.session = session

    def get_characteristics_by_sensor_name(self, sensor: str) -> List[tables.ResistanceThermometerCharacteristics]:
        return (
            self.session.query(tables.ResistanceThermometerCharacteristics)
                .join(tables.ResistanceThermometerCharacteristics.sensor)
                .filter(tables.ResistanceThermometerCharacteristics.sensor.has(name=sensor))
                .order_by(tables.ResistanceThermometerCharacteristics.temperature.asc())
                .all()
        )
