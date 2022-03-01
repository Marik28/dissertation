from typing import List

import sqlalchemy.orm

from .. import tables


class SensorCharacteristicsService:
    def __init__(self, session: sqlalchemy.orm.Session):
        self.session = session

    def get_characteristics_by_sensor_name(self, sensor: str) -> List[tables.SensorCharacteristics]:
        return (
            self.session.query(tables.SensorCharacteristics)
                .join(tables.SensorCharacteristics.sensor)
                .filter(tables.SensorCharacteristics.sensor.has(name=sensor))
                .order_by(tables.SensorCharacteristics.temperature.asc())
                .all()
        )
