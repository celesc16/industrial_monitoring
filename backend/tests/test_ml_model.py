import pytest

from app.core.config import settings
from app.services.ml_model import AnomalyDetector


def test_detector_loads_model_artifact():
    detector = AnomalyDetector(settings.model_path)

    assert detector.model is not None
    assert detector.scaler is not None
    assert "temperature" in detector.feature_names


def test_detector_raises_when_model_missing():
    with pytest.raises(FileNotFoundError):
        AnomalyDetector("/ruta/inexistente/model.pkl")


def test_predict_returns_expected_shape(detector):
    result = detector.predict(
        {
            "temperature": 60.0,
            "vibration": 1.5,
            "pressure": 100.0,
        }
    )

    assert set(result.keys()) == {
        "prediction",
        "is_anomaly",
        "anomaly_score",
    }
    assert result["prediction"] in {-1, 1}
    assert result["is_anomaly"] == (result["prediction"] == -1)
    assert isinstance(result["anomaly_score"], float)


def test_predict_flags_clearly_anomalous_reading(detector):
    result = detector.predict(
        {
            "temperature": 160.0,
            "vibration": 20.0,
            "pressure": 400.0,
        }
    )

    assert result["is_anomaly"] is True
    assert result["prediction"] == -1


def test_predict_accepts_normal_operating_values(detector):
    result = detector.predict(
        {
            "temperature": 60.0,
            "vibration": 1.5,
            "pressure": 100.0,
        }
    )

    assert result["is_anomaly"] is False
    assert result["prediction"] == 1