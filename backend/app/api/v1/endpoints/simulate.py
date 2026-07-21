from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_detector
from app.core.exceptions import InactiveSensorError, SensorNotFoundError
from app.schemas.reading import ReadingOut, SensorReadingIn
from app.services.ml_model import AnomalyDetector
from app.services.pipeline import process_reading

router = APIRouter(tags=["simulate"])


@router.post("/simulate", response_model=ReadingOut)
async def simulate_reading(
    payload: SensorReadingIn,
    detector: AnomalyDetector = Depends(get_detector),
):
    try:
        return await process_reading(payload.model_dump(), detector)

    except SensorNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except InactiveSensorError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc