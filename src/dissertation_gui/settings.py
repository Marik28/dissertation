from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    base_dir: Path = Path(__file__).parent.parent
    db_url = f'sqlite:///{base_dir / "dissertation_gui" / "db.sqlite3"}'


settings = Settings()
