from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

from fastapi.testclient import TestClient

from ioai.application.problems.authoring import AuthorDraftListItem
from ioai.application.problems.errors import RevisionConflictError
from ioai.domain.problems.identity import ProblemId, RevisionId
from ioai.domain.problems.revision import ProblemRevision
from ioai.domain.problems.workflow import EditorialStatus
from ioai.entrypoints.api.contracts.problems import SaveDraftRequest
from ioai.entrypoints.api.factory import create_app


class FakeAuthorProblemService:
    def __init__(self) -> None:
        self.draft = ProblemRevision(
            problem_id=ProblemId("problem-1"),
            revision_id=RevisionId("revision-1"),
            version=1,
            slug=None,
            status=EditorialStatus.DRAFT,
            content=None,
            metadata=None,
            response=None,
            scoring=None,
        )
        self.now = datetime(2026, 8, 9, tzinfo=UTC)

    def create(self) -> ProblemRevision:
        return self.draft

    def list(self) -> tuple[AuthorDraftListItem, ...]:
        return (
            AuthorDraftListItem(
                problem_id=self.draft.problem_id,
                revision_id=self.draft.revision_id,
                version=self.draft.version,
                status=self.draft.status,
                last_saved_at=self.now,
            ),
        )

    def get(self, problem_id: ProblemId) -> ProblemRevision:
        assert problem_id == self.draft.problem_id
        return self.draft

    def save(
        self, revision_id: RevisionId, request: SaveDraftRequest
    ) -> ProblemRevision:
        if request.expected_version != self.draft.version:
            raise RevisionConflictError(revision_id, self.draft.version)
        self.draft = replace(
            self.draft,
            version=request.expected_version + 1,
        )
        return self.draft


def test_author_can_create_list_and_read_private_draft_contracts() -> None:
    service = FakeAuthorProblemService()
    client = TestClient(create_app(author_problem_service=service))

    created = client.post("/api/v1/author/problems", json={})
    listed = client.get("/api/v1/author/problems")
    read = client.get("/api/v1/author/problems/problem-1")

    assert created.status_code == 201
    assert created.json() == {
        "problem_id": "problem-1",
        "revision_id": "revision-1",
        "version": 1,
        "editorial_status": "DRAFT",
        "slug": None,
        "content": None,
        "metadata": None,
        "response": None,
        "scoring": None,
    }
    assert listed.status_code == 200
    assert listed.json()["items"][0]["last_saved_at"] == "2026-08-09T00:00:00Z"
    assert read.json() == created.json()


def test_author_draft_schemas_are_not_public_problem_contracts() -> None:
    app = create_app(author_problem_service=FakeAuthorProblemService())
    schema = app.openapi()

    assert "/api/v1/author/problems" in schema["paths"]
    assert "/api/v1/author/problems/{problem_id}" in schema["paths"]
    assert "/api/v1/problems" not in schema["paths"]
    author_schema = str(schema["components"]["schemas"]["AuthorDraftResponse"])
    assert "revision_id" in author_schema
    assert "editorial_status" in author_schema


def test_versioned_save_returns_increment_and_stable_conflict() -> None:
    service = FakeAuthorProblemService()
    client = TestClient(create_app(author_problem_service=service))
    body = {
        "problem_id": "problem-1",
        "expected_version": 1,
        "client_save_key": "save-1",
        "slug": None,
        "content": None,
        "metadata": None,
        "response": None,
        "scoring": None,
    }

    saved = client.put("/api/v1/author/problems/revisions/revision-1", json=body)
    stale = client.put("/api/v1/author/problems/revisions/revision-1", json=body)

    assert saved.status_code == 200
    assert saved.json()["version"] == 2
    assert stale.status_code == 409
    assert stale.json()["detail"] == {
        "code": "REVISION_CONFLICT",
        "message": "A newer draft version exists.",
        "current_version": 2,
    }
