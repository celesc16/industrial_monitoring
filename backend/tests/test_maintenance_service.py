"""Unit tests for the maintenance scheduling domain (pure math + service)."""

import math

import numpy as np
import pytest

from app.core.exceptions import SensorNotFoundError
from app.domains.maintenance_scheduler.repository import (
    SensorUsageHistory,
)
from app.domains.maintenance_scheduler.schemas import (
    MaintenanceCostConfig,
)
from app.domains.maintenance_scheduler.service import (
    DEFAULT_SHAPE,
    MaintenanceOptimizerService,
    estimate_weibull_params,
    expected_cost_rate,
    optimal_window,
)


class FakeRepository:
    def __init__(self, history: SensorUsageHistory):
        self._history = history

    def get_usage_history(self, sensor_id: str):
        return self._history


class TestEstimateWeibullParams:
    def test_recovers_known_shape_and_scale(self):
        rng = np.random.default_rng(0)
        samples = (rng.weibull(a=2.0, size=20_000) * 100.0).tolist()

        shape, scale, estimated = estimate_weibull_params(
            samples, span_days=10_000.0
        )

        assert estimated is True
        assert math.isclose(shape, 2.0, rel_tol=0.1)
        assert math.isclose(scale, 100.0, rel_tol=0.1)

    def test_sparse_history_uses_default_shape_and_scale(self):
        shape, scale, estimated = estimate_weibull_params(
            [], span_days=90.0
        )

        assert estimated is False
        assert shape == DEFAULT_SHAPE
        assert scale == pytest.approx(
            90.0 / math.gamma(1 + 1 / DEFAULT_SHAPE)
        )

    def test_zero_span_floors_scale_at_one_day(self):
        shape, scale, estimated = estimate_weibull_params(
            [], span_days=0.0
        )

        assert estimated is False
        assert scale == pytest.approx(
            1.0 / math.gamma(1 + 1 / DEFAULT_SHAPE)
        )

    def test_tiny_variation_clamps_shape_at_upper_bound(self):
        shape, scale, estimated = estimate_weibull_params(
            [50.0, 50.0, 50.0, 50.0], span_days=100.0
        )

        assert estimated is True
        assert shape == pytest.approx(8.0)


class TestOptimalWindow:
    def test_respects_config_bounds(self):
        config = MaintenanceCostConfig(
            min_window_days=1.0, max_window_days=30.0
        )

        t_star = optimal_window(shape=2.0, scale=100.0, config=config)

        assert 1.0 <= t_star <= 30.0

    def test_higher_failure_cost_shortens_recommended_window(self):
        cheap = optimal_window(
            shape=2.0,
            scale=100.0,
            config=MaintenanceCostConfig(failure_cost=15_000.0),
        )
        expensive = optimal_window(
            shape=2.0,
            scale=100.0,
            config=MaintenanceCostConfig(failure_cost=2_000_000.0),
        )

        assert 0 < expensive < cheap

    def test_cost_rate_is_lower_at_optimum_than_at_bounds(self):
        config = MaintenanceCostConfig(
            min_window_days=0.5, max_window_days=180.0
        )
        shape, scale = 2.0, 100.0

        t_star = optimal_window(shape, scale, config)

        at_opt = expected_cost_rate(
            shape, scale, config.preventive_cost,
            config.failure_cost, t_star,
        )
        at_min = expected_cost_rate(
            shape, scale, config.preventive_cost,
            config.failure_cost, config.min_window_days,
        )
        at_max = expected_cost_rate(
            shape, scale, config.preventive_cost,
            config.failure_cost, config.max_window_days,
        )

        assert at_opt <= min(at_min, at_max)


class TestMaintenanceOptimizerService:
    def test_compute_schedule_returns_full_outcome(self):
        history = SensorUsageHistory(
            sensor_id="SENSOR-X",
            span_days=500.0,
            anomaly_count=8,
            failure_intervals_days=[
                30.0, 41.0, 38.0, 52.0, 45.0, 33.0, 60.0, 47.0,
            ],
        )
        service = MaintenanceOptimizerService(FakeRepository(history))
        config = MaintenanceCostConfig()

        result = service.compute_schedule("SENSOR-X", config)

        assert result.sensor_id == "SENSOR-X"
        assert result.parameters_estimated is True
        assert (
            result.minimum_window_days
            < result.recommended_window_days
            <= result.maximum_window_days
        )
        assert result.expected_cost_per_day == pytest.approx(
            result.expected_unplanned_cost_per_day
            + result.expected_planned_cost_per_day,
            rel=1e-3,
        )
        assert 0 <= result.failure_probability_at_window <= 1
        assert result.avoided_cost_per_day >= 0
        assert result.run_to_failure_cost_per_day > (
            result.expected_cost_per_day
        )
        assert result.config_used == config

    def test_history_without_anomalies_uses_defaults(self):
        history = SensorUsageHistory(
            sensor_id="SENSOR-X",
            span_days=45.0,
            anomaly_count=0,
            failure_intervals_days=[],
        )
        service = MaintenanceOptimizerService(FakeRepository(history))

        result = service.compute_schedule(
            "SENSOR-X", MaintenanceCostConfig()
        )

        assert result.parameters_estimated is False
        assert result.weibull_shape == DEFAULT_SHAPE
        assert result.weibull_scale_days == pytest.approx(
            45.0 / math.gamma(1 + 1 / DEFAULT_SHAPE)
        )

    def test_sensor_not_found_propagates(self):
        class RejectingRepository:
            def get_usage_history(self, sensor_id: str):
                raise SensorNotFoundError(sensor_id)

        service = MaintenanceOptimizerService(RejectingRepository())

        with pytest.raises(SensorNotFoundError):
            service.compute_schedule("NO-EXISTE", MaintenanceCostConfig())