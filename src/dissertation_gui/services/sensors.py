import sqlalchemy.orm

from .. import tables


class SensorsService:
    def __init__(self, session: sqlalchemy.orm.Session):
        self.session = session

    def get_sensors(self) -> list[tables.Sensor]:
        return self.session.query(tables.Sensor).all()
