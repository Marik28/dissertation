from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    base_dir: Path = Path(__file__).parent.parent


settings = Settings()
print(settings.base_dir)
