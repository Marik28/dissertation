import sqlalchemy.orm

from .. import tables


class SensorCharacteristicsService:
    def __init__(self, session: sqlalchemy.orm.Session):
        self.session = session

    def get_characteristics_by_sensor_name(self, sensor: str) -> list[tables.ResistanceThermometerCharacteristics]:
        return (
            self.session.query(tables.ResistanceThermometerCharacteristics)
                .join(tables.ResistanceThermometerCharacteristics.sensor)
                .filter(tables.ResistanceThermometerCharacteristics.sensor.has(name=sensor))
                .filter(tables.ResistanceThermometerCharacteristics.temperature >= 0)
                .order_by(tables.ResistanceThermometerCharacteristics.temperature.asc())
                .all()
        )
