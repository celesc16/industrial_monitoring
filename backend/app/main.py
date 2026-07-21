import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.api.v1.endpoints.websocket import router as websocket_router
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.db.session import init_db
from app.services.ml_model import AnomalyDetector
from app.services.mqtt_client import MQTTHandler

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    init_db()

    app.state.detector = AnomalyDetector(settings.model_path)

    loop = asyncio.get_event_loop()
    app.state.mqtt_handler = MQTTHandler(app.state.detector, loop)
    try:
        app.state.mqtt_handler.start()
    except Exception:
        logger.exception(
            "No se pudo conectar al broker MQTT (%s:%s). "
            "El backend sigue arriba; podés probar con POST /api/v1/simulate mientras tanto.",
            settings.mqtt_broker,
            settings.mqtt_port,
        )

    yield

    # --- shutdown ---
    handler = getattr(app.state, "mqtt_handler", None)
    if handler:
        handler.stop()


def create_app() -> FastAPI:
    app = FastAPI(title=settings.project_name, lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_v1_prefix)
    app.include_router(websocket_router)

    return app


app = create_app()
