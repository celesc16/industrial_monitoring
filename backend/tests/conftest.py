from collections.abc import Iterator
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base import Base
from app.db.seed import seed_sensors
from app.services.ml_model import AnomalyDetector


@pytest.fixture(scope="session")
def detector() -> AnomalyDetector:
    return AnomalyDetector(settings.model_path)


@pytest.fixture()
def session_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    factory = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
    )

    return factory


@pytest.fixture()
def db(session_factory) -> Iterator:
    session = session_factory()

    try:
        seed_sensors(session)
        yield session
    finally:
        session.rollback()
        session.close()


def _disable_external_side_effects(
    monkeypatch: pytest.MonkeyPatch,
    session_factory,
) -> None:
    from app.services import pipeline

    monkeypatch.setattr(pipeline, "SessionLocal", session_factory)
    monkeypatch.setattr(
        pipeline,
        "send_telegram_alert",
        AsyncMock(return_value=False),
    )
    monkeypatch.setattr(
        pipeline.manager,
        "broadcast",
        AsyncMock(return_value=None),
    )


@pytest.fixture()
def client(monkeypatch, db, detector, session_factory):
    from fastapi.testclient import TestClient

    from app.db.session import get_db
    from app.main import create_app

    test_app = create_app()
    test_app.state.detector = detector

    def override_get_db():
        yield db

    test_app.dependency_overrides[get_db] = override_get_db

    _disable_external_side_effects(monkeypatch, session_factory)

    return TestClient(test_app)


@pytest.fixture()
def auth(client, db):
    from app.db.seed import seed_users

    seed_users(db)

    def _auth(email: str = "admin@demo.com", password: str = "1234") -> dict:
        response = client.post(
            "/api/login",
            json={"email": email, "password": password},
        )
        assert response.status_code == 200, response.text
        return {
            "Authorization": (
                f"Bearer {response.json()['access_token']}"
            )
        }

    return _auth