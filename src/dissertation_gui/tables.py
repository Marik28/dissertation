from typing import List

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Float,
    Enum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from .models.sensors import SensorType

Base = declarative_base()


def get_enum_values(enum) -> List[str]:
    return [str(e.value) for e in enum]


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    type = Column(
        Enum(SensorType, values_callable=get_enum_values),
        nullable=False,
    )
    min_temperature = Column(Integer(), nullable=False)
    max_temperature = Column(Integer(), nullable=False)
    units = Column(String(10), nullable=False)
    physical_quantity = Column(String(50), nullable=False)
    trm_code = Column(String(10), nullable=False, unique=True)


class SensorCharacteristics(Base):
    __tablename__ = "sensor_characteristics"

    id = Column(Integer(), primary_key=True, autoincrement=True)
    sensor_id = Column(Integer(), ForeignKey("sensors.id", ondelete="RESTRICT"), nullable=False)
    temperature = Column(Integer(), nullable=False)
    value = Column(Float(), nullable=False)

    sensor = relationship("Sensor")
