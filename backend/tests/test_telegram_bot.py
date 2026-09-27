import asyncio

import httpx
import pytest

from app.core.config import settings
from app.services.telegram_bot import (
    build_alert_message,
    build_sensor_status_message,
    send_telegram_alert,
)


class TestBuildAlertMessage:
    def test_includes_sensor_data_and_score(self):
        message = build_alert_message(
            sensor_id="SENSOR-001",
            temperature=95.0,
            vibration=4.5,
            pressure=142.0,
            score=-0.12345,
        )

        assert "ALERTA DE ANOMALÍA" in message
        assert "SENSOR-001" in message
        assert "95.00" in message
        assert "4.50" in message
        assert "142.00" in message
        assert "-0.12345" in message


class TestBuildSensorStatusMessage:
    def test_active_message(self):
        message = build_sensor_status_message(
            sensor_id="SENSOR-002",
            sensor_name="Compresor",
            is_active=True,
        )

        assert "SENSOR ACTIVADO" in message
        assert "SENSOR-002" in message
        assert "Compresor" in message

    def test_inactive_message(self):
        message = build_sensor_status_message(
            sensor_id="SENSOR-002",
            sensor_name="Compresor",
            is_active=False,
        )

        assert "SENSOR DESACTIVADO" in message
        assert "SENSOR-002" in message
        assert "Compresor" in message


class _FakeTelegramResponse:
    def __init__(self, status_code: int = 200, payload: dict | None = None):
        self.status_code = status_code
        self._payload = payload or {
            "ok": True,
            "result": {"message_id": 42},
        }

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            request = httpx.Request("POST", "https://api.telegram.org")
            response = httpx.Response(
                self.status_code,
                request=request,
                text="Not Found",
            )
            raise httpx.HTTPStatusError(
                "Error", request=request, response=response
            )

    def json(self) -> dict:
        return self._payload


class _FakeAsyncClient:
    def __init__(self, *args, **kwargs) -> None:
        self._response = _FakeTelegramResponse()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args) -> bool:
        return False

    async def post(self, url: str, json: dict | None = None):
        return self._response


class TestSendTelegramAlert:
    def test_returns_false_when_not_configured(self, monkeypatch):
        monkeypatch.setattr(settings, "telegram_bot_token", "")
        monkeypatch.setattr(settings, "telegram_chat_id", "")

        assert asyncio.run(send_telegram_alert("msg")) is False

    def test_returns_false_when_missing_only_chat_id(self, monkeypatch):
        monkeypatch.setattr(settings, "telegram_bot_token", "fake-token")
        monkeypatch.setattr(settings, "telegram_chat_id", "")

        assert asyncio.run(send_telegram_alert("msg")) is False

    def test_returns_true_on_success(self, monkeypatch):
        monkeypatch.setattr(
            settings, "telegram_bot_token", "fake-token"
        )
        monkeypatch.setattr(settings, "telegram_chat_id", "123")
        monkeypatch.setattr(httpx, "AsyncClient", _FakeAsyncClient)

        assert asyncio.run(send_telegram_alert("msg")) is True

    def test_returns_false_on_http_error(self, monkeypatch):
        monkeypatch.setattr(
            settings, "telegram_bot_token", "fake-token"
        )
        monkeypatch.setattr(settings, "telegram_chat_id", "123")

        class ErrorClient(_FakeAsyncClient):
            def __init__(self, *args, **kwargs) -> None:
                self._response = _FakeTelegramResponse(status_code=404)

        monkeypatch.setattr(httpx, "AsyncClient", ErrorClient)

        assert asyncio.run(send_telegram_alert("msg")) is False

    def test_returns_false_on_request_error(self, monkeypatch):
        monkeypatch.setattr(
            settings, "telegram_bot_token", "fake-token"
        )
        monkeypatch.setattr(settings, "telegram_chat_id", "123")

        class ConnectingErrorClient:
            def __init__(self, *args, **kwargs) -> None:
                pass

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args) -> bool:
                return False

            async def post(self, url: str, json: dict | None = None):
                raise httpx.ConnectError("sin red")

        monkeypatch.setattr(
            httpx, "AsyncClient", ConnectingErrorClient,
        )

        assert asyncio.run(send_telegram_alert("msg")) is False