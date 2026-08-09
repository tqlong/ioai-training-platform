from __future__ import annotations

import json

from fastapi.testclient import TestClient

from ioai.entrypoints.api.factory import create_app


def test_non_author_openapi_operations_cannot_reference_author_schemas() -> None:
    schema = create_app().openapi()
    forbidden = {
        "AuthorDraftResponse",
        "AuthorDraftListResponse",
        "EditorialHistoryResponse",
        "PreviewResponse",
        "PublishRevisionRequest",
        "revision_id",
        "editorial_status",
        "hidden_tests",
        "correct_choice_id",
    }

    for path, operations in schema["paths"].items():
        if path.startswith("/api/v1/author/"):
            continue
        serialized = json.dumps(operations, sort_keys=True)
        assert forbidden.isdisjoint(item for item in forbidden if item in serialized), (
            path
        )


def test_guessed_public_revision_preview_and_search_paths_reveal_nothing() -> None:
    client = TestClient(create_app())
    candidates = (
        ("/api/v1/problems/revision-secret", 404),
        ("/api/v1/problems?preview=revision-secret", 422),
        ("/api/v1/problems?editorial_status=APPROVED", 422),
        ("/api/v1/recommendations?revision_id=revision-secret", 404),
    )

    for path, expected_status in candidates:
        response = client.get(path)
        assert response.status_code == expected_status
        serialized = response.text
        assert "hidden_tests" not in serialized
        assert "correct_choice_id" not in serialized
        assert "Traceback" not in serialized
        assert "/data/" not in serialized
