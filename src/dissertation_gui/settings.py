from pathlib import Path

from loguru import logger
from pydantic import BaseSettings

base_dir: Path = Path(__file__).parent.parent


class Settings(BaseSettings):
    base_dir: Path = base_dir
    db_url = f'sqlite:///{base_dir / "dissertation_gui" / "db.sqlite3"}'
    plot_update_frequency: int = 10
    plot_points: int = 1000
    port: str
    baudrate: int = 19200
    trm_address: int = 1


settings = Settings(_env_file=base_dir.parent / ".env")
logger.add(settings.base_dir.parent / "logs.log", rotation="10 MB", compression="zip")
