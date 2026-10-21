import pytest
from starlette.websockets import WebSocketDisconnect

from app.websocket.manager import manager


def _ws_token(auth) -> str:
    return auth()["Authorization"].split(" ")[1]


class TestHealth:
    def test_health(self, client):
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestWebSocket:
    def test_websocket_accepts_connection_and_cleans_up(self, client, auth):
        assert manager.active_connections == []

        with client.websocket_connect(f"/ws?token={_ws_token(auth)}") as websocket:
            assert len(manager.active_connections) == 1

        assert manager.active_connections == []

    def test_websocket_accepts_multiple_clients(self, client, auth):
        token = _ws_token(auth)

        with client.websocket_connect(f"/ws?token={token}") as first:
            with client.websocket_connect(f"/ws?token={token}") as second:
                assert len(manager.active_connections) == 2

        assert manager.active_connections == []

    def test_websocket_message_does_not_break_connection(self, client, auth):
        with client.websocket_connect(f"/ws?token={_ws_token(auth)}") as websocket:
            websocket.send_text("hola")
            assert len(manager.active_connections) == 1

    def test_websocket_rejects_missing_token(self, client):
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/ws"):
                pass

        assert manager.active_connections == []

    def test_websocket_rejects_invalid_token(self, client):
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/ws?token=token-invalido"):
                pass

        assert manager.active_connections == []
