from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Float,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(), nullable=False)
    type = Column(String(), nullable=False)
    trm_code = Column(String(), nullable=False)


class ResistanceThermometerCharacteristic(Base):
    __tablename__ = "resistance_thermometer_characteristics"

    id = Column(Integer(), primary_key=True, autoincrement=True)
    sensor_id = Column(Integer(), ForeignKey("sensors.id", ondelete="RESTRICT"), nullable=False)
    temperature = Column(Integer(), nullable=False)
    resistance = Column(Float(), nullable=False)

    sensor = relationship("Sensor")
