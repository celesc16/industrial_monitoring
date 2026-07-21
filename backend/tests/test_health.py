"""
Test de humo. Requiere que exista app/ml/artifacts/model.pkl
(correr scripts/train_model.py antes de testear).
"""

from fastapi.testclient import TestClient

from app.main import app


def test_health():
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
