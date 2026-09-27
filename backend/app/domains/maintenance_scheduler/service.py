import math
from statistics import mean as sample_mean
from statistics import pstdev

from scipy.special import gammainc

from app.domains.maintenance_scheduler.repository import (
    SensorUsageHistory,
)
from app.domains.maintenance_scheduler.schemas import (
    MaintenanceCostConfig,
    MaintenanceScheduleOut,
)

DEFAULT_SHAPE = 1.6
MIN_SAMPLES = 4
_SHAPE_LOWER = 0.4
_SHAPE_UPPER = 8.0

_SCAN_POINTS = 256
_GOLDEN_SECTION_ITERATIONS = 64


def _survival(t: float, shape: float, scale: float) -> float:
    return math.exp(-((t / scale) ** shape))


def _expected_cycle_length(
    shape: float, scale: float, horizon: float
) -> float:
    if horizon <= 0 or shape <= 0 or scale <= 0:
        return 0.0

    # Closed form: int_0^h exp(-(t/scale)^shape) dt
    #             = scale/shape * gamma(1/shape) * P(1/shape, (h/scale)^shape)
    # with P the regularized lower incomplete gamma function.
    # This avoids quadrature on wide horizons, where the Weibull mass
    # concentrated near t=0 can be missed by adaptive integrators.
    x = (horizon / scale) ** shape
    return (
        (scale / shape)
        * math.gamma(1 / shape)
        * gammainc(1 / shape, x)
    )


def expected_cost_rate(
    shape: float,
    scale: float,
    preventive_cost: float,
    failure_cost: float,
    horizon: float,
) -> float:
    if horizon <= 0 or shape <= 0 or scale <= 0:
        return math.inf

    length = _expected_cycle_length(shape, scale, horizon)
    if length <= 0:
        return math.inf

    reliability = _survival(horizon, shape, scale)

    return (
        preventive_cost * reliability
        + failure_cost * (1 - reliability)
    ) / length


def _golden_section_min(f, left: float, right: float) -> float:
    inverse_phi = (math.sqrt(5) - 1) / 2
    b = right - inverse_phi * (right - left)
    c = left + inverse_phi * (right - left)
    f_b = f(b)
    f_c = f(c)

    for _ in range(_GOLDEN_SECTION_ITERATIONS):
        if f_b < f_c:
            right, c, f_c = c, b, f_b
            b = right - inverse_phi * (right - left)
            f_b = f(b)
        else:
            left, b, f_b = b, c, f_c
            c = left + inverse_phi * (right - left)
            f_c = f(c)

    return (left + right) / 2


def _shape_from_cv(cv: float) -> float:
    # Weibull CV = sqrt(gamma(1+2/beta)/gamma(1+1/beta)^2 - 1)
    # decreases monotonically with beta, so solve by bisection.
    def error(beta: float) -> float:
        ratio = math.gamma(1 + 2 / beta) / (
            math.gamma(1 + 1 / beta) ** 2
        )
        return math.sqrt(ratio - 1) - cv

    if error(_SHAPE_LOWER) < 0:
        return _SHAPE_LOWER
    if error(_SHAPE_UPPER) > 0:
        return _SHAPE_UPPER

    low, high = _SHAPE_LOWER, _SHAPE_UPPER
    for _ in range(120):
        middle = (low + high) / 2
        if error(middle) > 0:
            low = middle
        else:
            high = middle
    return (low + high) / 2


def estimate_weibull_params(
    intervals_days: list[float], span_days: float
) -> tuple[float, float, bool]:
    if len(intervals_days) < MIN_SAMPLES:
        shape = DEFAULT_SHAPE
        span = max(float(span_days), 1.0)
        scale = span / math.gamma(1 + 1 / shape)
        return shape, scale, False

    mean = sample_mean(intervals_days)
    standard_deviation = pstdev(intervals_days)

    if mean <= 0 or not math.isfinite(mean):
        return estimate_weibull_params([], span_days)

    shape = _shape_from_cv(standard_deviation / mean)
    scale = mean / math.gamma(1 + 1 / shape)

    if scale <= 0 or not math.isfinite(scale):
        return estimate_weibull_params([], span_days)

    return shape, scale, True


def optimal_window(
    shape: float,
    scale: float,
    config: MaintenanceCostConfig,
) -> float:
    lower = max(config.min_window_days, 1e-3)
    upper = max(config.max_window_days, lower + 1e-3)

    # The cost-rate curve can have a narrow basin next to a flat tail,
    # which defeats generic bounded minimizers. A coarse log-spaced scan
    # locates the basin, then golden-section refines it.
    def rate(t: float) -> float:
        return expected_cost_rate(
            shape,
            scale,
            config.preventive_cost,
            config.failure_cost,
            t,
        )

    grid = [
        lower * ((upper / lower) ** (index / (_SCAN_POINTS - 1)))
        for index in range(_SCAN_POINTS)
    ]
    rates = [rate(t) for t in grid]

    best_index = min(range(_SCAN_POINTS), key=rates.__getitem__)
    left = grid[max(0, best_index - 1)]
    right = grid[min(_SCAN_POINTS - 1, best_index + 1)]

    return min(max(_golden_section_min(rate, left, right), lower), upper)


class MaintenanceOptimizerService:
    """Pure OR logic: it never touches FastAPI or the database."""

    def __init__(self, repository):
        self._repository = repository

    def compute_schedule(
        self,
        sensor_id: str,
        config: MaintenanceCostConfig,
    ) -> MaintenanceScheduleOut:
        history: SensorUsageHistory = (
            self._repository.get_usage_history(sensor_id)
        )

        shape, scale, estimated = estimate_weibull_params(
            history.failure_intervals_days, history.span_days
        )

        window = optimal_window(shape, scale, config)

        reliability = _survival(window, shape, scale)
        failure_probability = 1 - reliability
        cycle_length = _expected_cycle_length(shape, scale, window)

        planned_per_day = (
            config.preventive_cost * reliability / cycle_length
        )
        unplanned_per_day = (
            config.failure_cost * failure_probability / cycle_length
        )
        total_per_day = planned_per_day + unplanned_per_day

        mttf = scale * math.gamma(1 + 1 / shape)
        run_to_failure_per_day = (
            config.failure_cost / mttf if mttf > 0 else math.inf
        )
        avoided_per_day = max(
            run_to_failure_per_day - total_per_day, 0.0
        )

        return MaintenanceScheduleOut(
            sensor_id=sensor_id,
            recommended_window_days=round(window, 2),
            minimum_window_days=config.min_window_days,
            maximum_window_days=config.max_window_days,
            expected_cost_per_day=round(total_per_day, 2),
            expected_unplanned_cost_per_day=round(unplanned_per_day, 2),
            expected_planned_cost_per_day=round(planned_per_day, 2),
            failure_probability_at_window=round(
                failure_probability, 4
            ),
            weibull_shape=round(shape, 3),
            weibull_scale_days=round(scale, 3),
            parameters_estimated=estimated,
            run_to_failure_cost_per_day=round(
                run_to_failure_per_day, 2
            ),
            avoided_cost_per_day=round(avoided_per_day, 2),
            config_used=config,
        )