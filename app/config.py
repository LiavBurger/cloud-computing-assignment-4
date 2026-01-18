from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    ninja_api_key: str
    ninja_api_url: str
    app_host: str = "0.0.0.0"
    app_port: int = 5001
    pictures_dir: str = str(BASE_DIR / "pictures")
    store_name: str = "store1"
    mongodb_uri: str = "mongodb://localhost:27017"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
