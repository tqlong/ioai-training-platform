from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from ioai.entrypoints.api.factory import create_app
from ioai.entrypoints.api.settings import ApiSettings


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
