from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR.parent / ".env" 


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        protected_namespaces=("settings_",),
    )

    project_name: str = "Sistema de Monitoreo Industrial y Detección de Anomalías"
    api_v1_prefix: str = "/api/v1"

    cors_origins: list[str] = ["*"]

    mqtt_broker: str = "localhost"
    mqtt_port: int = 1883
    mqtt_topic: str = "sensores/+/datos"

    sensor_offline_seconds: int = 10

    database_url: str = "sqlite:///./monitoreo.db"

    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    model_path: str = str(BASE_DIR / "ml" / "artifacts" / "model.pkl")

    # Temporal: se reemplazará por autorización ADMIN.
    demo_controls_enabled: bool = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()