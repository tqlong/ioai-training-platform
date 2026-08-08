from __future__ import annotations

from fastapi.testclient import TestClient

from ioai.entrypoints.api.factory import create_app


def test_health_endpoints_return_machine_readable_payload() -> None:
    app = create_app()
    client = TestClient(app)

    live_response = client.get("/health/live")
    ready_response = client.get("/health/ready")
    root_response = client.get("/health")

    assert live_response.status_code == 200
    assert live_response.json()["status"] == "ok"
    assert root_response.status_code == 200
    assert ready_response.status_code == 200
    assert "database" in ready_response.json()
