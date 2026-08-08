from __future__ import annotations

from ioai.entrypoints.api.factory import create_app


def test_api_factory_returns_fastapi_app() -> None:
    app = create_app()

    assert app.title
    assert app.openapi_url == "/api/v1/openapi.json"
