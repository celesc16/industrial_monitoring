import asyncio
import json
import logging
from app.core.exceptions import InactiveSensorError, SensorNotFoundError
import paho.mqtt.client as mqtt

from app.core.config import settings
from app.services.ml_model import AnomalyDetector
from app.services.pipeline import process_reading

logger = logging.getLogger(__name__)


class MQTTHandler:

    def __init__(self, detector: AnomalyDetector, loop: asyncio.AbstractEventLoop):
        self.detector = detector
        self.loop = loop
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            logger.info("Conectado al broker MQTT %s:%s", settings.mqtt_broker, settings.mqtt_port)
            client.subscribe(settings.mqtt_topic)
        else:
            logger.error("Fallo al conectar a MQTT, código: %s", reason_code)

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            logger.error(
                "Mensaje MQTT inválido en topic %s: %r",
                msg.topic,
                msg.payload,
            )
            return

        future = asyncio.run_coroutine_threadsafe(
            process_reading(payload, self.detector),
            self.loop,
        )

        future.add_done_callback(self._handle_processing_result)

    @staticmethod
    def _handle_processing_result(future) -> None:
        try:
            future.result()
        except SensorNotFoundError as exc:
            logger.warning("Lectura MQTT rechazada: %s", exc)
        except InactiveSensorError as exc:
            logger.warning("Lectura MQTT rechazada: %s", exc)
        except Exception:
            logger.exception("Error procesando lectura MQTT")

    def start(self) -> None:
        self.client.connect(settings.mqtt_broker, settings.mqtt_port, keepalive=60)
        self.client.loop_start()  # hilo aparte, no bloqueante

    def stop(self) -> None:
        self.client.loop_stop()
        self.client.disconnect()
