from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from ioai.entrypoints.api.factory import create_app
from ioai.entrypoints.api.settings import ApiSettings


class RecordingSink:
    def __init__(self) -> None:
        self.events = []

    def emit(self, event) -> None:
        self.events.append(event)


def test_api_factory_returns_fastapi_app() -> None:
    app = create_app()

    assert app.title
    assert app.openapi_url == "/api/v1/openapi.json"


def test_cors_allows_configured_local_apps_and_rejects_unknown_origins() -> None:
    client = TestClient(
        create_app(settings=ApiSettings(allowed_origins=("http://127.0.0.1:3000",)))
    )
    headers = {
        "Origin": "http://127.0.0.1:3000",
        "Access-Control-Request-Method": "GET",
    }

    allowed = client.options("/api/v1/problems", headers=headers)
    denied = client.options(
        "/api/v1/problems",
        headers={**headers, "Origin": "https://public.example"},
    )

    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"
    assert "access-control-allow-credentials" not in allowed.headers
    assert denied.status_code == 400
    assert "access-control-allow-origin" not in denied.headers


def test_api_settings_reject_wildcard_or_empty_origin_configuration() -> None:
    with pytest.raises(ValueError, match="explicit http"):
        ApiSettings(allowed_origins=("*",))
    with pytest.raises(ValueError, match="at least one"):
        ApiSettings(allowed_origins=())


def test_request_completion_event_uses_sanitized_request_id_and_route_template() -> (
    None
):
    sink = RecordingSink()
    client = TestClient(
        create_app(
            settings=ApiSettings(environment="test"),
            event_sink=sink,
        )
    )

    response = client.get(
        "/health/live?answer=do-not-log",
        headers={"x-request-id": "invalid request id\nsecret"},
    )

    request_id = response.headers["x-request-id"]
    assert request_id != "invalid request id\nsecret"
    assert len(request_id) <= 128
    event = sink.events[-1]
    assert event.event == "http.request.completed"
    assert event.request_id == request_id
    assert event.route == "/health/live"
    assert event.method == "GET"
    assert event.status_code == 200
    assert event.outcome == "success"
    assert "answer" not in repr(event)
    assert "secret" not in repr(event)


def test_validation_error_uses_sanitized_context_request_id() -> None:
    sink = RecordingSink()
    client = TestClient(
        create_app(settings=ApiSettings(environment="test"), event_sink=sink)
    )

    response = client.get(
        "/api/v1/problems?page=0",
        headers={"x-request-id": "unsafe request identifier"},
    )

    assert response.status_code == 422
    assert response.json()["request_id"] == response.headers["x-request-id"]
    assert response.json()["request_id"] != "unsafe request identifier"
    assert sink.events[-1].outcome == "client_error"
