from __future__ import annotations

from fastapi.testclient import TestClient

from ioai.entrypoints.api.factory import create_app


def test_health_endpoints_return_machine_readable_payload() -> None:
    app = create_app(readiness_probe=lambda: True)
    client = TestClient(app)

    live_response = client.get("/health/live")
    ready_response = client.get("/health/ready")
    root_response = client.get("/health")

    assert live_response.status_code == 200
    assert live_response.json()["status"] == "ok"
    assert root_response.status_code == 200
    assert ready_response.status_code == 200
    assert ready_response.json() == {
        "status": "ready",
        "database": "ready",
        "schema": "current",
    }


def test_readiness_fails_closed_while_liveness_remains_available() -> None:
    client = TestClient(create_app(readiness_probe=lambda: False))

    live_response = client.get("/health/live")
    ready_response = client.get("/health/ready")

    assert live_response.status_code == 200
    assert live_response.json() == {"status": "ok", "scope": "platform"}
    assert ready_response.status_code == 503
    assert ready_response.json() == {
        "status": "not_ready",
        "database": "unavailable",
        "schema": "unknown",
    }


def test_readiness_redacts_dependency_probe_exceptions() -> None:
    def broken_probe() -> bool:
        raise RuntimeError("postgresql://secret@database/internal SQL")

    response = TestClient(create_app(readiness_probe=broken_probe)).get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "database": "unavailable",
        "schema": "unknown",
    }
    assert "secret" not in response.text
    assert "SQL" not in response.text


def test_readiness_openapi_documents_success_and_dependency_failure() -> None:
    operation = create_app(readiness_probe=lambda: True).openapi()["paths"][
        "/health/ready"
    ]["get"]

    assert set(operation["responses"]) >= {"200", "503"}
    for status_code in ("200", "503"):
        assert operation["responses"][status_code]["content"]["application/json"][
            "schema"
        ]["$ref"].endswith("/ReadinessResponse")
