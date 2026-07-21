import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

TELEGRAM_API_URL = (
    "https://api.telegram.org/bot{token}/sendMessage"
)


async def send_telegram_alert(message: str) -> bool:
    if (
        not settings.telegram_bot_token
        or not settings.telegram_chat_id
    ):
        logger.warning(
            "Telegram no configurado "
            "(falta token o chat_id); alerta no enviada."
        )
        return False

    url = TELEGRAM_API_URL.format(
        token=settings.telegram_bot_token
    )

    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                url,
                json=payload,
            )

            response.raise_for_status()

            response_data = response.json()

            message_id = (
                response_data
                .get("result", {})
                .get("message_id")
            )

            logger.info(
                "Telegram aceptó la alerta | message_id=%s",
                message_id,
            )

            return True

    except httpx.HTTPStatusError as exc:
        logger.error(
            "Telegram rechazó la alerta | "
            "status=%s | respuesta=%s",
            exc.response.status_code,
            exc.response.text,
        )

    except httpx.RequestError as exc:
        logger.error(
            "Error de conexión con Telegram: %s",
            exc,
        )

    return False


def build_alert_message(
    sensor_id: str,
    temperature: float,
    vibration: float,
    pressure: float,
    score: float,
) -> str:
    return (
        "⚠️ *ALERTA DE ANOMALÍA*\n\n"
        f"Sensor: *{sensor_id}*\n"
        f"🌡️ Temperatura: {temperature:.2f} °C\n"
        f"📳 Vibración: {vibration:.2f} mm/s\n"
        f"🔧 Presión: {pressure:.2f} kPa\n"
        f"🧠 Score del modelo: `{score:.5f}`\n\n"
        "El modelo de Machine Learning clasificó "
        "esta lectura como anómala."
    )


def build_sensor_status_message(
    sensor_id: str,
    sensor_name: str,
    is_active: bool,
) -> str:
    if is_active:
        return (
            "✅ *SENSOR ACTIVADO*\n\n"
            f"Sensor: *{sensor_id}*\n"
            f"Equipo: *{sensor_name}*\n\n"
            "El sensor volvió a estar activo y puede recibir lecturas."
        )

    return (
        "⛔ *SENSOR DESACTIVADO*\n\n"
        f"Sensor: *{sensor_id}*\n"
        f"Equipo: *{sensor_name}*\n\n"
        "El sensor fue desactivado. "
        "Las nuevas lecturas serán rechazadas por el backend."
    )