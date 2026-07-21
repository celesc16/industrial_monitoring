from fastapi import APIRouter

from app.api.v1.endpoints import health, readings, simulate, stats

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(readings.router)
api_router.include_router(stats.router)
api_router.include_router(simulate.router)
