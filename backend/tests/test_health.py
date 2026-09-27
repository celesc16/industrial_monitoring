from app.websocket.manager import manager


class TestHealth:
    def test_health(self, client):
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestWebSocket:
    def test_websocket_accepts_connection_and_cleans_up(self, client):
        assert manager.active_connections == []

        with client.websocket_connect("/ws") as websocket:
            assert len(manager.active_connections) == 1

        assert manager.active_connections == []

    def test_websocket_accepts_multiple_clients(self, client):
        with client.websocket_connect("/ws") as first:
            with client.websocket_connect("/ws") as second:
                assert len(manager.active_connections) == 2

        assert manager.active_connections == []

    def test_websocket_message_does_not_break_connection(self, client):
        with client.websocket_connect("/ws") as websocket:
            websocket.send_text("hola")
            assert len(manager.active_connections) == 1