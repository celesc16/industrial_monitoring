from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import SensorNotFoundError
from app.db.session import get_db
from app.domains.maintenance_scheduler.repository import (
    MaintenanceRepository,
)
from app.domains.maintenance_scheduler.schemas import (
    MaintenanceCostConfig,
    MaintenanceScheduleOut,
)
from app.domains.maintenance_scheduler.service import (
    MaintenanceOptimizerService,
)

router = APIRouter(tags=["maintenance"])


def get_maintenance_repository(
    db: Session = Depends(get_db),
) -> MaintenanceRepository:
    return MaintenanceRepository(db)


def get_maintenance_optimizer_service(
    repository: MaintenanceRepository = Depends(
        get_maintenance_repository
    ),
) -> MaintenanceOptimizerService:
    return MaintenanceOptimizerService(repository)


@router.post(
    "/maintenance/sensors/{sensor_id}/schedule",
    response_model=MaintenanceScheduleOut,
)
def compute_maintenance_schedule(
    sensor_id: str,
    service: MaintenanceOptimizerService = Depends(
        get_maintenance_optimizer_service
    ),
    config: MaintenanceCostConfig | None = Body(default=None),
):
    try:
        effective_config = config or MaintenanceCostConfig()
        return service.compute_schedule(sensor_id, effective_config)

    except SensorNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc