from __future__ import annotations

from contextlib import contextmanager
from datetime import UTC, datetime

from fastapi.testclient import TestClient

from ioai.adapters.vocabulary.runtime import load_generated_vocabulary
from ioai.application.vocabulary.queries import VocabularyQuery
from ioai.domain.vocabulary.proposals import ProposalNote, VocabularyProposal
from ioai.domain.vocabulary.values import (
    VocabularyIdentity,
    VocabularyRecord,
    VocabularyType,
)
from ioai.entrypoints.api.factory import create_app


class FakeVocabularyReader:
    def __init__(self, records: tuple[VocabularyRecord, ...]) -> None:
        self.records = records
        self.last_query: VocabularyQuery | None = None

    def query(self, query: VocabularyQuery) -> tuple[VocabularyRecord, ...]:
        self.last_query = query
        return tuple(
            record
            for record in self.records
            if record.identity.vocabulary_type.value == query.vocabulary_type
        )[: query.limit]

    def breadcrumbs(self, identity: VocabularyIdentity) -> tuple[VocabularyRecord, ...]:
        return tuple(record for record in self.records if record.identity == identity)


def client_with_reader(reader: FakeVocabularyReader) -> TestClient:
    @contextmanager
    def reader_factory():
        yield reader

    return TestClient(create_app(vocabulary_reader_factory=reader_factory))


class FakeProposalService:
    def __init__(self) -> None:
        self.items: list[VocabularyProposal] = []

    def __call__(self, *, vocabulary_type: str, note: str) -> VocabularyProposal:
        proposal = VocabularyProposal.create(
            proposal_id=f"proposal-{len(self.items) + 1}",
            vocabulary_type=VocabularyType(vocabulary_type),
            note=ProposalNote(note),
            created_at=datetime(2026, 8, 9, tzinfo=UTC),
        )
        self.items.append(proposal)
        return proposal

    def list_pending(self) -> tuple[VocabularyProposal, ...]:
        return tuple(self.items)


def test_public_vocabulary_read_returns_active_canonical_projection_only() -> None:
    reader = FakeVocabularyReader(load_generated_vocabulary())
    client = client_with_reader(reader)

    response = client.get(
        "/api/v1/vocabulary",
        params={"vocabulary_type": "TOPIC", "search": "logistic", "limit": 1},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    item = payload["items"][0]
    assert set(item["identity"]) == {"vocabulary_type", "code"}
    assert set(item["labels"]) == {"en", "vi"}
    assert "is_available" not in item
    assert "status" not in item
    assert "proposal" not in str(payload).lower()


def test_author_vocabulary_read_includes_typed_release_availability() -> None:
    reader = FakeVocabularyReader(load_generated_vocabulary())
    client = client_with_reader(reader)

    response = client.get(
        "/api/v1/author/vocabulary",
        params={"vocabulary_type": "TASK_TYPE", "limit": 100},
    )

    assert response.status_code == 200
    by_code = {item["identity"]["code"]: item for item in response.json()["items"]}
    assert by_code["QUIZ_SINGLE"]["availability"]["is_available"] is True
    assert by_code["MODEL_TRAINING"]["availability"] == {
        "is_available": False,
        "reason_code": "UNAVAILABLE_IN_RELEASE_0",
        "message": "MODEL_TRAINING is canonical but unavailable in Release 0.",
    }
    assert by_code["MODEL_TRAINING"]["status"] == "ACTIVE"


def test_query_contract_preserves_explicit_descendant_option() -> None:
    reader = FakeVocabularyReader(load_generated_vocabulary())
    client = client_with_reader(reader)

    response = client.get(
        "/api/v1/vocabulary",
        params={
            "vocabulary_type": "TOPIC",
            "root_code": "TOPIC_MATHEMATICS",
            "include_descendants": "true",
        },
    )

    assert response.status_code == 200
    assert reader.last_query is not None
    assert reader.last_query.root_code == "TOPIC_MATHEMATICS"
    assert reader.last_query.include_descendants is True


def test_invalid_query_uses_stable_machine_readable_error() -> None:
    client = client_with_reader(FakeVocabularyReader(load_generated_vocabulary()))

    response = client.get(
        "/api/v1/vocabulary", params={"vocabulary_type": "topic", "limit": 0}
    )

    assert response.status_code == 422
    assert response.json()["error"] == {
        "code": "invalid_request",
        "message": "The request parameters are invalid.",
    }


def test_openapi_separates_public_and_author_vocabulary_schemas() -> None:
    app = create_app(vocabulary_reader_factory=lambda: None)
    schema = app.openapi()

    assert "/api/v1/vocabulary" in schema["paths"]
    assert "/api/v1/author/vocabulary" in schema["paths"]
    public_schema = str(schema["components"]["schemas"]["PublicVocabularyRecord"])
    author_schema = str(schema["components"]["schemas"]["AuthorVocabularyRecord"])
    assert "availability" not in public_schema
    assert "status" not in public_schema
    assert "availability" in author_schema
    assert "VocabularyRecordModel" not in str(schema)


def test_author_can_record_and_review_pending_proposals() -> None:
    proposal_service = FakeProposalService()
    client = TestClient(create_app(proposal_service=proposal_service))

    created = client.post(
        "/api/v1/author/vocabulary/proposals",
        json={"vocabulary_type": "TOPIC", "note": "Add causal inference"},
    )
    listed = client.get("/api/v1/author/vocabulary/proposals")

    assert created.status_code == 201
    assert created.json()["proposal_id"] == "proposal-1"
    assert created.json()["status"] == "PENDING"
    assert listed.status_code == 200
    assert listed.json()["items"] == [created.json()]


def test_proposal_note_validation_is_safe_and_bounded() -> None:
    client = TestClient(create_app(proposal_service=FakeProposalService()))

    response = client.post(
        "/api/v1/author/vocabulary/proposals",
        json={"vocabulary_type": "TOPIC", "note": ""},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"
