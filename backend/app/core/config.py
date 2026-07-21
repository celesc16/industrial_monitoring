from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR.parent / ".env" 


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8")  # <-- CAMBIAR ".env" por ENV_FILE

    # Proyecto
    project_name: str = "Sistema de Monitoreo Industrial y Detección de Anomalías"
    api_v1_prefix: str = "/api/v1"

    # CORS (en producción restringir al dominio real del dashboard)
    cors_origins: list[str] = ["*"]

    # MQTT
    mqtt_broker: str = "localhost"
    mqtt_port: int = 1883
    mqtt_topic: str = "sensores/+/datos"

    # Base de datos
    database_url: str = "sqlite:///./monitoreo.db"

    # Telegram
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # Modelo de IA
    model_path: str = str(BASE_DIR / "ml" / "artifacts" / "model.pkl")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()