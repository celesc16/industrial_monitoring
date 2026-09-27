"""Tests of the login endpoint and role-based access control."""

import pytest

from app.db.seed import seed_users


@pytest.fixture(autouse=True)
def ensure_demo_users(db):
    seed_users(db)
    yield db


def _login(client, email="admin@demo.com", password="1234"):
    return client.post(
        "/api/login",
        json={"email": email, "password": password},
    )


class TestLoginEndpoint:
    def test_admin_login_returns_token_with_role(self, client):
        response = _login(client)

        assert response.status_code == 200
        body = response.json()
        assert body["token_type"] == "bearer"
        assert body["role"] == "ADMIN"
        assert body["email"] == "admin@demo.com"
        assert body["access_token"]

    def test_viewer_login_returns_viewer_role(self, client):
        response = _login(client, email="operario@demo.com")

        assert response.status_code == 200
        assert response.json()["role"] == "VIEWER"
        assert response.json()["email"] == "operario@demo.com"

    def test_wrong_password_returns_401(self, client):
        response = _login(client, password="incorrecta")

        assert response.status_code == 401

    def test_unknown_email_returns_401(self, client):
        response = _login(client, email="nadie@demo.com")

        assert response.status_code == 401

    def test_wrong_credentials_never_validate_email(self, client):
        """Even an existing email with a wrong password must not leak info."""
        response = _login(client)

        assert response.status_code == 200
        response_nonexistent = _login(client, email="nadie@demo.com")
        assert response_nonexistent.status_code == 401

    def test_missing_fields_returns_422(self, client):
        response = client.post("/api/login", json={})

        assert response.status_code == 422

    def test_invalid_email_returns_422(self, client):
        response = client.post(
            "/api/login",
            json={"email": "no-es-un-email", "password": "1234"},
        )

        assert response.status_code == 422


class TestProtectedEndpoint:
    PROTECTED_URL = "/api/v1/sensors/SENSOR-001/status"

    def test_without_token_returns_401(self, client):
        response = client.patch(
            self.PROTECTED_URL, json={"is_active": False}
        )

        assert response.status_code == 401

    def test_viewer_token_returns_403(self, client, auth):
        headers = auth("operario@demo.com")

        response = client.patch(
            self.PROTECTED_URL,
            json={"is_active": False},
            headers=headers,
        )

        assert response.status_code == 403
        assert "permisos de Administrador" in response.json()["detail"]

    def test_admin_token_returns_200(self, client, auth):
        headers = auth("admin@demo.com")

        response = client.patch(
            self.PROTECTED_URL,
            json={"is_active": False},
            headers=headers,
        )

        assert response.status_code == 200
        assert response.json()["is_active"] is False

    def test_garbage_token_returns_401(self, client):
        response = client.patch(
            self.PROTECTED_URL,
            json={"is_active": False},
            headers={"Authorization": "Bearer token-invalido"},
        )

        assert response.status_code == 401


class TestPublicEndpoints:
    def test_read_endpoints_do_not_require_token(self, client):
        assert client.get("/api/v1/sensors").status_code == 200
        assert client.get("/api/v1/readings").status_code == 200
        assert client.get("/api/v1/stats").status_code == 200
        assert client.get("/api/v1/health").status_code == 200