from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

import pytest
from alembic import command
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from ioai.adapters.database.vocabulary_repository import (
    SqlAlchemyVocabularyUnitOfWork,
)
from ioai.adapters.vocabulary.runtime import load_generated_vocabulary
from ioai.application.observability import ObservabilityEvent
from ioai.application.vocabulary.synchronize import SynchronizeVocabulary
from ioai.entrypoints.api.factory import create_app
from ioai.entrypoints.api.settings import ApiSettings

from .database_environment import require_test_database_url
from .test_vocabulary_migration import alembic_config


@dataclass(frozen=True)
class ApiSystem:
    client: TestClient
    engine: Engine
    events: list[ObservabilityEvent]


class RecordingSink:
    def __init__(self) -> None:
        self.events: list[ObservabilityEvent] = []

    def emit(self, event: ObservabilityEvent) -> None:
        self.events.append(event)


@dataclass(frozen=True)
class PublishedProblem:
    problem_id: str
    revision_id: str
    snapshot_id: str
    slug: str
    publication_request: dict[str, object]


@pytest.fixture(scope="module")
def api_system() -> Iterator[ApiSystem]:
    database_url = require_test_database_url()
    engine = create_engine(database_url)
    command.downgrade(alembic_config(), "base")
    command.upgrade(alembic_config(), "head")
    synchronize = SynchronizeVocabulary(
        lambda: SqlAlchemyVocabularyUnitOfWork(
            sessionmaker(bind=engine, expire_on_commit=False)
        )
    )
    result = synchronize(load_generated_vocabulary())
    assert (result.added, result.updated, result.unchanged) == (343, 0, 0)

    sink = RecordingSink()
    with TestClient(
        create_app(settings=ApiSettings(environment="test"), event_sink=sink)
    ) as client:
        yield ApiSystem(client, engine, sink.events)

    command.downgrade(alembic_config(), "base")
    engine.dispose()


def _localized(en: str, vi: str) -> dict[str, str]:
    return {
        "en": en,
        "vi": vi,
        "en_state": "COMPLETE",
        "vi_state": "COMPLETE",
    }


def _response_configuration(task_type: str) -> dict[str, object]:
    if task_type == "QUIZ_SINGLE":
        return {
            "type": task_type,
            "choices": [
                {"id": "a", "content": _localized("Correct", "Đúng")},
                {"id": "b", "content": _localized("Wrong", "Sai")},
            ],
            "correct_choice_id": "a",
        }
    if task_type == "QUIZ_MULTIPLE":
        return {
            "type": task_type,
            "choices": [
                {"id": "a", "content": _localized("Correct", "Đúng")},
                {"id": "b", "content": _localized("Also correct", "Cũng đúng")},
                {"id": "c", "content": _localized("Wrong", "Sai")},
            ],
            "correct_choice_ids": ["a", "b"],
        }
    if task_type == "NUMERIC_ANSWER":
        return {
            "type": task_type,
            "expected": "0.3",
            "absolute_tolerance": "0.001",
            "unit": None,
        }
    if task_type == "SHORT_ANSWER":
        return {
            "type": task_type,
            "reference_answer": _localized("Reasoned answer", "Câu trả lời"),
            "accepted_keywords": [],
            "rubric_guidance": "Review reasoning.",
        }
    return {
        "type": "CODE_FUNCTION",
        "language": "PYTHON",
        "signature": "def solve(x):",
        "starter_code": "def solve(x):\n    pass",
        "public_tests": [{"id": "public", "invocation": "solve(1)", "expected": "1"}],
        "hidden_tests": [{"id": "hidden", "invocation": "solve(2)", "expected": "2"}],
        "rubric_guidance": "Review code.",
    }


def _human_rubric() -> dict[str, object]:
    return {
        "criteria": [
            {
                "id": "correctness",
                "title": _localized("Correctness", "Tính đúng"),
                "description": _localized(
                    "Produces a correct response.",
                    "Tạo câu trả lời đúng.",
                ),
                "maximum_points": "1",
                "levels": [
                    {
                        "id": "not-yet",
                        "label": _localized("Not yet", "Chưa đạt"),
                        "description": _localized(
                            "The response is not correct.",
                            "Câu trả lời chưa đúng.",
                        ),
                        "points": "0",
                    },
                    {
                        "id": "complete",
                        "label": _localized("Complete", "Hoàn thành"),
                        "description": _localized(
                            "The response is correct.",
                            "Câu trả lời đúng.",
                        ),
                        "points": "1",
                    },
                ],
            }
        ],
        "reviewer_guidance": "Private reviewer guidance.",
        "exemplar": "Private exemplar.",
    }


def _draft_payload(
    problem_id: str,
    version: int,
    slug: str,
    task_type: str,
) -> dict[str, object]:
    human_scored = task_type in {"SHORT_ANSWER", "CODE_FUNCTION"}
    return {
        "problem_id": problem_id,
        "expected_version": version,
        "client_save_key": f"save-{slug}",
        "slug": slug,
        "content": {
            "title": _localized(f"System {task_type} {slug}", f"Hệ thống {slug}"),
            "summary": _localized(
                "Solve the verified system problem.",
                "Giải bài toán hệ thống đã xác minh.",
            ),
            "objectives": [
                _localized(
                    "Calculate the correct response.",
                    "Tính đáp án đúng.",
                )
            ],
            "blocks": [
                {
                    "kind": "STATEMENT",
                    "content": _localized(
                        "Provide the correct response.",
                        "Cung cấp đáp án đúng.",
                    ),
                    "order": 1,
                    "reveal_order": None,
                }
            ],
        },
        "metadata": {
            "stage": ["PATHWAY_STAGE", "AI_1_FOUNDATIONS"],
            "difficulty": ["DIFFICULTY", "EASY"],
            "primary_competency": ["COMPETENCY", "EVAL_METRICS"],
            "secondary_competencies": [],
            "task_type": ["TASK_TYPE", task_type],
            "topics": [["TOPIC", "EVAL_CONFUSION_MATRIX"]],
            "prerequisites": [],
            "modalities": [["DATA_MODALITY", "NONE"]],
            "expected_minutes": 10,
            "resources": {
                "compute_tier": ["COMPUTE_TIER", "NONE"],
                "runtime_class": ["RUNTIME_CLASS", "INSTANT"],
                "cpu_cores": 0,
                "ram_mb": 0,
                "gpu_count": 0,
                "gpu_vram_mb": 0,
                "storage_mb": 0,
                "runtime_seconds": 0,
                "network_policy": "DENIED",
            },
        },
        "response": _response_configuration(task_type),
        "scoring": {
            "response_type": task_type,
            "pass_threshold": "1.0",
            "components": [
                {
                    "method": "RUBRIC_HUMAN" if human_scored else "EXACT_MATCH",
                    "weight": "1.0",
                    "configuration": _human_rubric() if human_scored else None,
                }
            ],
        },
    }


def _editorial_command(version: int, operation_id: str) -> dict[str, object]:
    return {
        "expected_version": version,
        "note": "System integration editorial decision.",
        "actor_context": "system-reviewer",
        "operation_id": operation_id,
    }


def _publish(client: TestClient, slug: str, task_type: str) -> PublishedProblem:
    created_response = client.post(
        "/api/v1/author/problems",
        json={},
        headers={"X-Request-ID": f"create-{slug}"},
    )
    assert created_response.status_code == 201
    assert created_response.headers["X-Request-ID"] == f"create-{slug}"
    created = created_response.json()

    saved_response = client.put(
        f"/api/v1/author/revisions/{created['revision_id']}",
        json=_draft_payload(created["problem_id"], created["version"], slug, task_type),
    )
    assert saved_response.status_code == 200
    assert saved_response.json()["version"] == 2

    validation = client.post(
        f"/api/v1/author/revisions/{created['revision_id']}/validate",
        json={"expected_version": 2},
    )
    assert validation.status_code == 200
    assert validation.json()["publication_eligible"] is True

    preview = client.post(
        f"/api/v1/author/revisions/{created['revision_id']}/preview",
        json={"expected_version": 2},
    )
    assert preview.status_code == 200
    assert preview.json()["marker"] == "Draft preview - not public"
    assert "correct_choice_id" not in preview.text
    assert "hidden_tests" not in preview.text

    submitted = client.post(
        f"/api/v1/author/revisions/{created['revision_id']}/submit-review",
        json=_editorial_command(2, f"review-{slug}"),
    )
    assert submitted.status_code == 200
    assert submitted.json()["editorial_status"] == "IN_REVIEW"

    approved = client.post(
        f"/api/v1/author/revisions/{created['revision_id']}/approve",
        json=_editorial_command(3, f"approve-{slug}"),
    )
    assert approved.status_code == 200
    assert approved.json()["editorial_status"] == "APPROVED"

    publication_request = {
        "expected_version": 4,
        "note": "Publish the verified system problem.",
        "actor_context": "system-reviewer",
        "idempotency_key": f"publish-{slug}",
    }
    published = client.post(
        f"/api/v1/author/revisions/{created['revision_id']}/publish",
        json=publication_request,
    )
    assert published.status_code == 200
    assert published.json()["slug"] == slug

    history = client.get(f"/api/v1/author/revisions/{created['revision_id']}/history")
    assert history.status_code == 200
    assert [item["target_status"] for item in history.json()["items"]] == [
        "IN_REVIEW",
        "APPROVED",
        "PUBLISHED",
    ]
    return PublishedProblem(
        problem_id=created["problem_id"],
        revision_id=created["revision_id"],
        snapshot_id=published.json()["snapshot_id"],
        slug=slug,
        publication_request=publication_request,
    )


@pytest.mark.parametrize(
    ("task_type", "answer", "expected_outcome"),
    [
        ("QUIZ_SINGLE", {"type": "QUIZ_SINGLE", "choice_id": "a"}, "ACCEPTED_RESULT"),
        (
            "QUIZ_MULTIPLE",
            {"type": "QUIZ_MULTIPLE", "choice_ids": ["a", "b"]},
            "ACCEPTED_RESULT",
        ),
        (
            "NUMERIC_ANSWER",
            {"type": "NUMERIC_ANSWER", "value": "0.3"},
            "ACCEPTED_RESULT",
        ),
        (
            "SHORT_ANSWER",
            {"type": "SHORT_ANSWER", "text": "Reasoned answer"},
            "PENDING_ASSESSMENT",
        ),
        (
            "CODE_FUNCTION",
            {"type": "CODE_FUNCTION", "code": "def solve(x):\n    return x"},
            "PENDING_ASSESSMENT",
        ),
    ],
)
def test_all_release_0_response_contracts_persist_once(
    api_system: ApiSystem,
    task_type: str,
    answer: dict[str, object],
    expected_outcome: str,
) -> None:
    slug = f"api-system-{task_type.lower().replace('_', '-')}"
    published = _publish(api_system.client, slug, task_type)
    receipt = f"private-receipt-{slug}"
    request = {
        "submission_key": f"submission-{slug}",
        "receipt": receipt,
        "response": answer,
    }

    first = api_system.client.post(f"/api/v1/problems/{slug}/submissions", json=request)
    replay = api_system.client.post(
        f"/api/v1/problems/{slug}/submissions", json=request
    )

    assert first.status_code == replay.status_code == 200
    assert first.json()["attempt_id"] == replay.json()["attempt_id"]
    assert first.json()["outcome"] == expected_outcome
    assert first.json()["receipt"] == receipt
    matching_events = [
        event
        for event in api_system.events
        if event.reference == slug
        and event.event in {"author.publication", "learner.submission"}
    ]
    assert {event.event for event in matching_events} == {
        "author.publication",
        "learner.submission",
    }
    submission_event = next(
        event for event in matching_events if event.event == "learner.submission"
    )
    assert submission_event.request_id == first.headers["x-request-id"]
    assert submission_event.operation_id.startswith("op_")
    assert request["submission_key"] not in repr(submission_event)
    assert receipt not in repr(submission_event)
    assert str(answer) not in repr(submission_event)
    with api_system.engine.connect() as connection:
        assert (
            connection.scalar(
                text(
                    """
                SELECT count(*) FROM learner_attempt
                WHERE snapshot_id = :snapshot_id
                """
                ),
                {"snapshot_id": published.snapshot_id},
            )
            == 1
        )


def test_vocabulary_proposal_public_queries_and_feedback_use_real_storage(
    api_system: ApiSystem,
) -> None:
    client = api_system.client
    vocabulary = client.get(
        "/api/v1/vocabulary",
        params={"vocabulary_type": "TOPIC", "search": "ma trận", "limit": 10},
    )
    assert vocabulary.status_code == 200
    assert any(
        item["identity"]["code"] == "EVAL_CONFUSION_MATRIX"
        for item in vocabulary.json()["items"]
    )

    proposal = client.post(
        "/api/v1/author/vocabulary/proposals",
        json={
            "vocabulary_type": "TOPIC",
            "note": "A system-verification proposal.",
        },
    )
    assert proposal.status_code == 201
    assert client.get("/api/v1/author/vocabulary/proposals").json()["count"] >= 1

    first = _publish(client, "api-system-list-a", "QUIZ_SINGLE")
    _publish(client, "api-system-list-b", "QUIZ_SINGLE")
    first_page = client.get(
        "/api/v1/problems",
        params={
            "stage": "AI_1_FOUNDATIONS",
            "q": "api-system-list",
            "sort": "TITLE",
            "page": 1,
            "page_size": 1,
        },
    )
    second_page = client.get(
        "/api/v1/problems",
        params={
            "stage": "AI_1_FOUNDATIONS",
            "q": "api-system-list",
            "sort": "TITLE",
            "page": 2,
            "page_size": 1,
        },
    )
    assert first_page.status_code == second_page.status_code == 200
    assert first_page.json()["total"] == second_page.json()["total"] == 2
    assert first_page.json()["items"] != second_page.json()["items"]

    detail = client.get(f"/api/v1/problems/{first.slug}")
    assert detail.status_code == 200
    assert detail.json()["permanent_url"] == f"/problems/{first.slug}"
    assert "correct_choice_id" not in detail.text

    recommendation = client.get(
        f"/api/v1/problems/{first.slug}/recommendation",
        params={"stage": "AI_1_FOUNDATIONS", "completed": first.slug},
    )
    assert recommendation.status_code == 200
    assert recommendation.json()["slug"] != first.slug

    feedback_request = {
        "feedback_key": "api-system-feedback",
        "category": "CONTENT_ISSUE",
        "message": "The verified prompt needs clarification.",
    }
    feedback = client.post(
        f"/api/v1/problems/{first.slug}/feedback", json=feedback_request
    )
    replay = client.post(
        f"/api/v1/problems/{first.slug}/feedback", json=feedback_request
    )
    conflict = client.post(
        f"/api/v1/problems/{first.slug}/feedback",
        json={**feedback_request, "message": "A different report."},
    )
    assert feedback.status_code == replay.status_code == 201
    assert feedback.json()["receipt_id"] == replay.json()["receipt_id"]
    assert conflict.status_code == 409
    feedback_events = [
        event
        for event in api_system.events
        if event.event == "learner.feedback" and event.reference == first.slug
    ]
    assert [event.outcome for event in feedback_events[-3:]] == [
        "success",
        "success",
        "failure",
    ]
    assert feedback_events[-3].request_id == feedback.headers["x-request-id"]
    assert feedback_request["message"] not in repr(feedback_events)
    assert feedback_request["feedback_key"] not in repr(feedback_events)
    with api_system.engine.connect() as connection:
        assert (
            connection.scalar(
                text(
                    """
                SELECT count(*) FROM problem_feedback
                WHERE snapshot_id = :snapshot_id
                """
                ),
                {"snapshot_id": first.snapshot_id},
            )
            == 1
        )


def test_manual_assessment_receipt_decision_and_correction_are_snapshot_bound(
    api_system: ApiSystem,
) -> None:
    client = api_system.client
    published = _publish(client, "api-system-manual", "SHORT_ANSWER")
    receipt = "private-receipt-api-system-manual"
    pending = client.post(
        f"/api/v1/problems/{published.slug}/submissions",
        json={
            "submission_key": "manual-submission",
            "receipt": receipt,
            "response": {"type": "SHORT_ANSWER", "text": "Reasoned answer"},
        },
    )
    assert pending.status_code == 200
    assert pending.json()["outcome"] == "PENDING_ASSESSMENT"
    attempt_id = pending.json()["attempt_id"]

    queue = client.get(
        "/api/v1/author/assessments",
        params={"status": "PENDING", "problem": published.slug, "limit": 1},
    )
    assert queue.status_code == 200
    assert [item["attempt_id"] for item in queue.json()["items"]] == [attempt_id]
    assert client.get(f"/api/v1/submissions/{attempt_id}").status_code == 422
    assert (
        client.get(
            f"/api/v1/submissions/{attempt_id}",
            headers={"X-Submission-Receipt": "wrong-private-receipt"},
        ).status_code
        == 404
    )

    selection = {
        "component_index": 0,
        "criterion_id": "correctness",
        "level_id": "complete",
        "feedback": "Correct reasoning.",
    }
    assessed = client.post(
        f"/api/v1/author/assessments/{attempt_id}/decisions",
        json={"selections": [selection], "overall_feedback": "Well done."},
    )
    assert assessed.status_code == 200
    first_decision_id = assessed.json()["latest_decision"]["decision_id"]

    result = client.get(
        f"/api/v1/submissions/{attempt_id}",
        headers={"X-Submission-Receipt": receipt},
    )
    assert result.status_code == 200
    assert result.json()["passed"] is True
    assert result.json()["submitted_response"] == {
        "type": "SHORT_ANSWER",
        "text": "Reasoned answer",
    }
    assert "Private reviewer guidance" not in result.text

    stale = client.post(
        f"/api/v1/author/assessments/{attempt_id}/decisions",
        json={
            "selections": [{**selection, "level_id": "not-yet"}],
            "expected_decision_id": "stale-decision",
            "correction_reason": "Correct the level.",
        },
    )
    assert stale.status_code == 409

    corrected = client.post(
        f"/api/v1/author/assessments/{attempt_id}/decisions",
        json={
            "selections": [{**selection, "level_id": "not-yet"}],
            "expected_decision_id": first_decision_id,
            "correction_reason": "Correct the level.",
        },
    )
    assert corrected.status_code == 200
    assert len(corrected.json()["decision_history"]) == 2
    assert corrected.json()["latest_decision"]["version"] == 2
    assert corrected.json()["latest_decision"]["result"]["passed"] is False
    operation_events = [
        event
        for event in api_system.events
        if event.reference == published.slug
        and event.event
        in {"author.publication", "learner.submission", "author.assessment"}
    ]
    assert {event.event for event in operation_events} == {
        "author.publication",
        "learner.submission",
        "author.assessment",
    }
    assert [
        event.outcome
        for event in operation_events
        if event.event == "author.assessment"
    ] == ["success", "failure", "success"]
    serialized_events = repr(operation_events)
    for private_value in (
        receipt,
        "Reasoned answer",
        "Correct reasoning.",
        "Well done.",
        "Private reviewer guidance.",
        attempt_id,
        published.revision_id,
        published.snapshot_id,
    ):
        assert private_value not in serialized_events


def test_rejected_requests_do_not_mutate_and_publication_replay_is_bounded(
    api_system: ApiSystem,
) -> None:
    client = api_system.client
    published = _publish(client, "api-system-rejections", "QUIZ_SINGLE")
    with api_system.engine.connect() as connection:
        before = {
            "attempts": connection.scalar(text("SELECT count(*) FROM learner_attempt")),
            "feedback": connection.scalar(
                text("SELECT count(*) FROM problem_feedback")
            ),
            "snapshots": connection.scalar(
                text("SELECT count(*) FROM published_snapshot")
            ),
        }

    malformed = client.post(
        f"/api/v1/problems/{published.slug}/submissions",
        json={
            "submission_key": "malformed-submission",
            "receipt": "private-malformed-receipt",
            "response": {"type": "QUIZ_SINGLE"},
        },
    )
    oversized = client.post(
        f"/api/v1/problems/{published.slug}/feedback",
        json={
            "feedback_key": "oversized-feedback",
            "category": "OTHER",
            "message": "x" * 2001,
        },
    )
    unknown_filter = client.get("/api/v1/problems?stage=NOT_A_STAGE")
    stale_transition = client.post(
        f"/api/v1/author/revisions/{published.revision_id}/approve",
        json=_editorial_command(4, "invalid-repeat-approval"),
    )
    replay = client.post(
        f"/api/v1/author/revisions/{published.revision_id}/publish",
        json=published.publication_request,
    )
    conflicting_replay = client.post(
        f"/api/v1/author/revisions/{published.revision_id}/publish",
        json={**published.publication_request, "note": "Different publish intent."},
    )

    assert malformed.status_code == 422
    assert oversized.status_code == 422
    assert unknown_filter.status_code == 422
    assert stale_transition.status_code == 409
    assert replay.status_code == 200
    assert replay.json()["snapshot_id"] == published.snapshot_id
    assert conflicting_replay.status_code == 409
    with api_system.engine.connect() as connection:
        after = {
            "attempts": connection.scalar(text("SELECT count(*) FROM learner_attempt")),
            "feedback": connection.scalar(
                text("SELECT count(*) FROM problem_feedback")
            ),
            "snapshots": connection.scalar(
                text("SELECT count(*) FROM published_snapshot")
            ),
        }
    assert after == before


def test_successor_revision_and_archive_preserve_snapshot_history(
    api_system: ApiSystem,
) -> None:
    client = api_system.client
    published = _publish(client, "api-system-archive", "QUIZ_SINGLE")
    successor = client.post(
        f"/api/v1/author/problems/{published.problem_id}/revisions",
        json={
            "source_revision_id": published.revision_id,
            "expected_version": 5,
            "operation_id": "successor-api-system-archive",
        },
    )
    assert successor.status_code == 201
    assert successor.json()["editorial_status"] == "DRAFT"
    assert client.get(f"/api/v1/problems/{published.slug}").status_code == 200

    archive = client.post(
        f"/api/v1/author/problems/{published.problem_id}/archive",
        json={
            "expected_version": 5,
            "note": "Archive after system verification.",
            "actor_context": "system-reviewer",
            "operation_id": "archive-api-system-archive",
        },
    )
    assert archive.status_code == 200
    assert client.get(f"/api/v1/problems/{published.slug}").status_code == 404
    with api_system.engine.connect() as connection:
        assert (
            connection.scalar(
                text(
                    """
                    SELECT count(*) FROM published_snapshot
                    WHERE snapshot_id = :identity
                    """
                ),
                {"identity": published.snapshot_id},
            )
            == 1
        )
        assert (
            connection.scalar(
                text(
                    """
                SELECT count(*) FROM problem_revision
                WHERE problem_id = :identity
                """
                ),
                {"identity": published.problem_id},
            )
            == 2
        )


def test_changes_requested_creates_a_private_successor_without_public_state(
    api_system: ApiSystem,
) -> None:
    client = api_system.client
    slug = "api-system-changes"
    created_response = client.post("/api/v1/author/problems", json={})
    assert created_response.status_code == 201
    created = created_response.json()
    saved = client.put(
        f"/api/v1/author/revisions/{created['revision_id']}",
        json=_draft_payload(
            created["problem_id"], created["version"], slug, "QUIZ_SINGLE"
        ),
    )
    assert saved.status_code == 200
    submitted = client.post(
        f"/api/v1/author/revisions/{created['revision_id']}/submit-review",
        json=_editorial_command(2, "review-api-system-changes"),
    )
    assert submitted.status_code == 200
    changes = client.post(
        f"/api/v1/author/revisions/{created['revision_id']}/request-changes",
        json=_editorial_command(3, "changes-api-system-changes"),
    )
    assert changes.status_code == 200
    assert changes.json()["editorial_status"] == "CHANGES_REQUESTED"

    successor = client.post(
        f"/api/v1/author/problems/{created['problem_id']}/revisions",
        json={
            "source_revision_id": created["revision_id"],
            "expected_version": 4,
            "operation_id": "successor-api-system-changes",
        },
    )
    assert successor.status_code == 201
    assert successor.json()["editorial_status"] == "DRAFT"
    assert successor.json()["revision_id"] != created["revision_id"]

    public = client.get("/api/v1/problems", params={"q": slug})
    assert public.status_code == 200
    assert public.json()["total"] == 0
    author = client.get(
        "/api/v1/author/problems",
        params={"search": created["problem_id"], "editorial_status": "DRAFT"},
    )
    assert author.status_code == 200
    assert author.json()["count"] == 1
