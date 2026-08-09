from __future__ import annotations

from ioai.entrypoints.api.factory import create_app


def test_openapi_has_stable_versioned_vocabulary_and_separate_author_route() -> None:
    app = create_app()
    schema = app.openapi()

    assert schema["openapi"].startswith("3.")
    assert "/health/live" in schema["paths"]
    assert "/api/v1/vocabulary" in schema["paths"]
    assert "/api/v1/author/vocabulary" in schema["paths"]
    assert (
        schema["components"]["schemas"]["PublicVocabularyRecord"]
        != schema["components"]["schemas"]["AuthorVocabularyRecord"]
    )


def test_openapi_contract_is_deterministic_on_dump() -> None:
    app = create_app()

    first = app.openapi()
    second = app.openapi()

    assert first == second
