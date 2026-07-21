from fastapi import APIRouter, Depends

from app.api.deps import get_detector
from app.schemas.reading import ReadingOut, SensorReadingIn
from app.services.ml_model import AnomalyDetector
from app.services.pipeline import process_reading

router = APIRouter(tags=["simulate"])


@router.post("/simulate", response_model=ReadingOut)
async def simulate_reading(
    payload: SensorReadingIn,
    detector: AnomalyDetector = Depends(get_detector),
):
    return await process_reading(payload.model_dump(), detector)
