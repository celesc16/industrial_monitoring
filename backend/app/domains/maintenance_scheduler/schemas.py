from pydantic import BaseModel, Field, model_validator


class MaintenanceCostConfig(BaseModel):
    preventive_cost: float = Field(
        default=1_000.0,
        gt=0,
        description="Cost of a planned maintenance stop.",
    )
    failure_cost: float = Field(
        default=20_000.0,
        gt=0,
        description="Cost of an unplanned failure stop.",
    )
    min_window_days: float = Field(
        default=0.5,
        gt=0,
        description="Earliest day a stop is allowed.",
    )
    max_window_days: float = Field(
        default=365.0,
        gt=0,
        description="Latest day a stop is allowed.",
    )

    @model_validator(mode="after")
    def _check_consistency(self) -> "MaintenanceCostConfig":
        if self.failure_cost < self.preventive_cost:
            raise ValueError(
                "failure_cost must be >= preventive_cost"
            )
        if self.min_window_days >= self.max_window_days:
            raise ValueError(
                "min_window_days must be < max_window_days"
            )
        return self


class MaintenanceScheduleOut(BaseModel):
    sensor_id: str
    recommended_window_days: float
    minimum_window_days: float
    maximum_window_days: float

    expected_cost_per_day: float
    expected_unplanned_cost_per_day: float
    expected_planned_cost_per_day: float

    failure_probability_at_window: float

    weibull_shape: float
    weibull_scale_days: float
    parameters_estimated: bool

    run_to_failure_cost_per_day: float
    avoided_cost_per_day: float

    config_used: MaintenanceCostConfig