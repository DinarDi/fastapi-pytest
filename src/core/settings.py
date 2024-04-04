from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Основные настройки приложения"""
    BASE_DIR: Path = Path(__file__).parent.parent.resolve()
    model_config = SettingsConfigDict(env_file='.env')

    DB_URL: str


settings = Settings()
