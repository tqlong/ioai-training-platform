from __future__ import annotations

from pathlib import Path

from ioai.entrypoints.api.factory import create_app


def test_openapi_has_stable_versioned_prefix_and_no_author_routes() -> None:
    app = create_app()
    schema = app.openapi()

    assert schema["openapi"].startswith("3.")
    assert any(path.startswith("/api/v1/health") for path in schema["paths"])
    assert all(not path.startswith("/api/v1/author") for path in schema["paths"])


def test_openapi_contract_is_deterministic_on_dump(tmp_path: Path) -> None:
    app = create_app()
    left = app.openapi()

    first = app.openapi()
    second = app.openapi()

    assert first == second
