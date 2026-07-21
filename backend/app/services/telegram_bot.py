import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


async def send_telegram_alert(message: str) -> None:
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        logger.warning("Telegram no configurado (falta token o chat_id); alerta no enviada.")
        return

    url = TELEGRAM_API_URL.format(token=settings.telegram_bot_token)
    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.error("Error enviando alerta a Telegram: %s", exc)


def build_alert_message(sensor_id: str, temperature: float, vibration: float, pressure: float, score: float) -> str:
    return (
        "⚠️ *ALERTA CRÍTICA*\n"
        f"Anomalía detectada en *Sensor {sensor_id}*\n"
        f"🌡️ Temperatura: {temperature}°C\n"
        f"📳 Vibración: {vibration}\n"
        f"🔧 Presión: {pressure}\n"
        f"Score del modelo: {score}\n"
        "El modelo de ML clasificó el evento como riesgo. Tomar acción inmediata."
    )
