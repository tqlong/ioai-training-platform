from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

from fastapi.testclient import TestClient

from ioai.application.problems.authoring import AuthorDraftListItem, PreviewResult
from ioai.application.problems.errors import RevisionConflictError
from ioai.domain.problems.identity import ProblemId, RevisionId, StableSlug
from ioai.domain.problems.revision import ProblemRevision, ValidationReport
from ioai.domain.problems.workflow import EditorialStatus
from ioai.domain.vocabulary.availability import Release0AvailabilityPolicy
from ioai.entrypoints.api.contracts.problems import (
    PreviewDraftRequest,
    SaveDraftRequest,
)
from ioai.entrypoints.api.factory import create_app
from ioai.entrypoints.api.routes.problems import _safe_response_schema


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

    def validate(
        self, revision_id: RevisionId, expected_version: int
    ) -> ValidationReport:
        if (
            revision_id != self.draft.revision_id
            or expected_version != self.draft.version
        ):
            raise RevisionConflictError(revision_id, self.draft.version)
        return self.draft.validate(Release0AvailabilityPolicy())

    def preview(
        self, revision_id: RevisionId, request: PreviewDraftRequest
    ) -> PreviewResult:
        if request.expected_version != self.draft.version:
            raise RevisionConflictError(revision_id, self.draft.version)
        revision = self.draft
        if request.unsaved_state and request.unsaved_state.slug:
            revision = replace(revision, slug=StableSlug(request.unsaved_state.slug))
        return PreviewResult(revision, revision.validate(Release0AvailabilityPolicy()))


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


def test_author_validates_current_revision_with_stable_layered_report() -> None:
    client = TestClient(create_app(author_problem_service=FakeAuthorProblemService()))

    response = client.post(
        "/api/v1/author/revisions/revision-1/validate",
        json={"expected_version": 1},
    )

    assert response.status_code == 200
    report = response.json()
    assert report["revision_id"] == "revision-1"
    assert report["revision_version"] == 1
    assert report["publication_eligible"] is False
    assert {issue["section"] for issue in report["errors"]} == {
        "CONTENT",
        "CURRICULUM",
        "ASSESSMENT",
        "PUBLICATION",
    }
    assert all(
        set(issue) == {"code", "section", "field_path", "message", "severity"}
        for issue in report["errors"]
    )


def test_author_validation_rejects_stale_revision_version() -> None:
    client = TestClient(create_app(author_problem_service=FakeAuthorProblemService()))
    response = client.post(
        "/api/v1/author/revisions/revision-1/validate",
        json={"expected_version": 2},
    )
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "REVISION_CONFLICT"


def test_preview_is_author_only_and_marks_learner_projection() -> None:
    client = TestClient(create_app(author_problem_service=FakeAuthorProblemService()))
    preview = client.post(
        "/api/v1/author/revisions/revision-1/preview",
        json={"expected_version": 1},
    )
    assert preview.status_code == 200
    assert preview.json()["marker"] == "Draft preview - not public"
    assert "revision_id" not in preview.json()["learner_problem"]
    assert client.get("/api/v1/problems/revision-1").status_code == 404
    assert client.get("/api/v1/problems?preview=revision-1").status_code == 404


def test_preview_accepts_explicit_unsaved_editor_state_without_persisting() -> None:
    service = FakeAuthorProblemService()
    client = TestClient(create_app(author_problem_service=service))
    preview = client.post(
        "/api/v1/author/revisions/revision-1/preview",
        json={
            "expected_version": 1,
            "unsaved_state": {
                "problem_id": "problem-1",
                "slug": "unsaved-title",
                "content": None,
                "metadata": None,
                "response": None,
                "scoring": None,
            },
        },
    )
    assert preview.status_code == 200
    assert preview.json()["learner_problem"]["slug"] == "unsaved-title"
    assert service.draft.slug is None


def test_preview_response_schema_omits_answer_keys_hidden_tests_and_author_states() -> (
    None
):
    safe = _safe_response_schema(
        {
            "type": "QUIZ_SINGLE",
            "choices": [
                {
                    "id": "a",
                    "content": {
                        "en": "A",
                        "vi": "Á",
                        "en_state": "COMPLETE",
                        "vi_state": "PENDING",
                    },
                }
            ],
            "correct_choice_id": "a",
            "hidden_tests": [{"id": "secret"}],
        }
    )
    assert safe == {
        "type": "QUIZ_SINGLE",
        "choices": [{"id": "a", "content": {"en": "A", "vi": "Á"}}],
    }
