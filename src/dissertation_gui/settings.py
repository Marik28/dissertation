import sys
from pathlib import Path

from loguru import logger
from pydantic import BaseSettings

base_dir: Path = Path(__file__).parent.parent


class Settings(BaseSettings):
    base_dir: Path = base_dir
    db_url = f'sqlite:///{base_dir / "dissertation_gui" / "db.sqlite3"}'

    test_gui: bool
    """Если True, то используются моки вместо внешних устройств, чтобы можно было протестировать GUI"""

    # логи
    log_level: str = "DEBUG"
    """Уровень логирования"""

    plot_update_frequency: int
    plot_points: int

    # настройки протокола ОВЕН
    port: str
    baudrate: int
    trm_address: int
    trm_update_period: float
    port_timeout: float
    request_delay: float

    # настройки протокола I2C
    mcp4725_address: int

    # пины - как они названы в библиотеке board
    relay_1_pin: str
    relay_2_pin: str
    relay_3_pin: str
    relay_4_pin: str
    cs0_pin: str
    cs1_pin: str
    i2c_sda_pin: str
    i2c_scl_pin: str

    # название файлов относительно директории `data/ad8400`
    # для генерации датафреймов с кодами для термометров сопротивления.
    ad8400_1: str
    ad8400_2: str

    # графики
    plot_background: str
    """Цвет фона графиков"""


settings = Settings(_env_file=base_dir.parent / ".env")
logger.remove()
logger.add(sys.stdout, level=settings.log_level)
logger.add(settings.base_dir.parent / "logs.log", level=settings.log_level, rotation="10 MB", compression="zip")
