import enum


class SensorType(enum.Enum):
    RESISTANCE_THERMOMETER = "Термометр сопротивления"
    THERMO_COUPLE = "Термопара"
    UNIFIED_ANALOG_SIGNAL = "Унифицированный аналоговый сигнал"
