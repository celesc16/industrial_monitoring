from fastapi import Request

from app.services.ml_model import AnomalyDetector


def get_detector(request: Request) -> AnomalyDetector:
    """Devuelve la instancia del modelo de IA cargada una sola vez en el startup."""
    return request.app.state.detector
