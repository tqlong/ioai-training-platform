from __future__ import annotations

from pathlib import Path

from tests.fixtures.problem_fixtures import draft_problem, published_problem

from ioai.entrypoints.api.factory import create_app


def test_compose_declares_runtime_and_isolated_test_services() -> None:
    compose_text = Path("docker-compose.yml").read_text()

    assert "postgres:" in compose_text
    assert "api:" in compose_text
    assert "learn:" in compose_text
    assert "studio:" in compose_text
    assert "postgres-test:" in compose_text
    assert "postgres-test-data:" in compose_text
    assert "'127.0.0.1:5433:5432'" in compose_text
    assert "depends_on:" in compose_text
    assert "postgres" in compose_text.split("api:")[1]


def test_studio_binding_remains_loopback_in_compose() -> None:
    compose_text = Path("docker-compose.yml").read_text()

    assert "'127.0.0.1:3001:3001'" in compose_text
    assert Path("frontend/apps/studio/app/author/problems/page.tsx").is_file()


def test_studio_uses_compose_api_service_for_server_side_requests() -> None:
    compose_text = Path("docker-compose.yml").read_text()
    studio_service = compose_text.split("\n  studio:\n", maxsplit=1)[1].split(
        "\nvolumes:", maxsplit=1
    )[0]

    assert "API_INTERNAL_BASE: http://api:8000" in studio_service
    assert Path("frontend/apps/studio/next.config.mjs").is_file()


def test_public_vocabulary_schema_does_not_expose_author_fields() -> None:
    app = create_app()
    openapi = app.openapi()

    public_schema = openapi["components"]["schemas"]["PublicVocabularyRecord"]
    assert "availability" in public_schema["properties"]
    assert "status" not in public_schema["properties"]


def test_public_list_foundation_rejects_draft_fixture() -> None:
    assert published_problem().published is True
    assert draft_problem().published is False
