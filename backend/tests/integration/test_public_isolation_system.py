from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from ioai.entrypoints.api.factory import create_app

from .database_environment import require_test_database_url
from .test_vocabulary_migration import alembic_config

PUBLIC_SLUG = "phase9-isolation-public"
PUBLIC_PROBLEM_ID = "phase9-isolation-problem"
PUBLIC_REVISION_ID = "phase9-isolation-revision"
PUBLIC_SNAPSHOT_ID = "phase9-isolation-snapshot"
PRIVATE_REVISION_ID = "phase9-private-successor"
ARCHIVED_SLUG = "phase9-archived-only"
PRIVATE_VALUES = (
    "PRIVATE_AUTHOR_NOTE_09004",
    "PRIVATE_REVIEWER_GUIDANCE_09004",
    "PRIVATE_EXEMPLAR_09004",
    "PRIVATE_HIDDEN_EXPECTED_09004",
    "PRIVATE_OBJECT_KEY_09004",
    PRIVATE_REVISION_ID,
)


@pytest.fixture
def isolation_system() -> Iterator[tuple[TestClient, Engine]]:
    engine = create_engine(require_test_database_url())
    command.downgrade(alembic_config(), "base")
    command.upgrade(alembic_config(), "head")
    _seed_adversarial_records(engine)
    with TestClient(create_app()) as client:
        yield client, engine
    command.downgrade(alembic_config(), "base")
    engine.dispose()


def _localized(en: str, vi: str) -> dict[str, str]:
    return {
        "en": en,
        "vi": vi,
        "en_state": "COMPLETE",
        "vi_state": "COMPLETE",
    }


def _public_payload() -> dict[str, object]:
    return {
        "content": {
            "title": _localized("Isolation problem", "Bài toán cô lập"),
            "summary": _localized("Verify safe projections.", "Xác minh phép chiếu."),
            "objectives": [
                _localized(
                    "Calculate the correct response.",
                    "Tính đáp án đúng.",
                )
            ],
            "blocks": [
                {
                    "kind": "STATEMENT",
                    "content": _localized("Choose the answer.", "Chọn đáp án."),
                    "order": 1,
                    "reveal_order": None,
                }
            ],
            "internal_notes": "PRIVATE_AUTHOR_NOTE_09004",
        },
        "metadata": {
            "stage": ["PATHWAY_STAGE", "AI_1_FOUNDATIONS"],
            "difficulty": ["DIFFICULTY", "EASY"],
            "primary_competency": ["COMPETENCY", "EVAL_METRICS"],
            "secondary_competencies": [],
            "task_type": ["TASK_TYPE", "QUIZ_SINGLE"],
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
                "object_key": "PRIVATE_OBJECT_KEY_09004",
            },
        },
        "response": {
            "type": "QUIZ_SINGLE",
            "choices": [
                {"id": "a", "content": _localized("Correct", "Đúng")},
                {"id": "b", "content": _localized("Wrong", "Sai")},
            ],
            "correct_choice_id": "a",
            "hidden_tests": [{"expected": "PRIVATE_HIDDEN_EXPECTED_09004"}],
        },
        "scoring": {
            "response_type": "QUIZ_SINGLE",
            "pass_threshold": "1.0",
            "components": [
                {
                    "method": "EXACT_MATCH",
                    "weight": "1.0",
                    "configuration": {
                        "reviewer_guidance": "PRIVATE_REVIEWER_GUIDANCE_09004",
                        "exemplar": "PRIVATE_EXEMPLAR_09004",
                    },
                }
            ],
        },
        "revision_id": PUBLIC_REVISION_ID,
        "editorial_status": "PUBLISHED",
    }


def _seed_adversarial_records(engine: Engine) -> None:
    payload = json.dumps(_public_payload(), ensure_ascii=False)
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO problem (problem_id, slug, created_at)
                VALUES (:problem_id, :slug, now()),
                       ('phase9-private-only', 'phase9-private-only', now()),
                       ('phase9-archived-problem', :archived_slug, now())
                """
            ),
            {
                "problem_id": PUBLIC_PROBLEM_ID,
                "slug": PUBLIC_SLUG,
                "archived_slug": ARCHIVED_SLUG,
            },
        )
        connection.execute(
            text(
                """
                INSERT INTO problem_revision
                    (revision_id, problem_id, revision_number, lock_version,
                     editorial_status, content, created_at, updated_at)
                VALUES
                    (:revision_id, :problem_id, 1, 1, 'PUBLISHED',
                     CAST(:payload AS jsonb), now(), now()),
                    (:private_revision, :problem_id, 2, 1, 'APPROVED',
                     CAST(:private_payload AS jsonb), now(), now()),
                    ('phase9-private-only-revision', 'phase9-private-only', 1, 1,
                     'DRAFT', CAST(:private_payload AS jsonb), now(), now()),
                    ('phase9-archived-revision', 'phase9-archived-problem', 1, 1,
                     'ARCHIVED', CAST(:payload AS jsonb), now(), now())
                """
            ),
            {
                "revision_id": PUBLIC_REVISION_ID,
                "problem_id": PUBLIC_PROBLEM_ID,
                "payload": payload,
                "private_revision": PRIVATE_REVISION_ID,
                "private_payload": json.dumps({"private": "PRIVATE_AUTHOR_NOTE_09004"}),
            },
        )
        connection.execute(
            text(
                """
                INSERT INTO published_snapshot
                    (snapshot_id, problem_id, revision_id, slug, public_payload,
                     published_at)
                VALUES
                    (:snapshot_id, :problem_id, :revision_id, :slug,
                     CAST(:payload AS jsonb), now()),
                    ('phase9-archived-snapshot', 'phase9-archived-problem',
                     'phase9-archived-revision', :archived_slug,
                     CAST(:payload AS jsonb), now())
                """
            ),
            {
                "snapshot_id": PUBLIC_SNAPSHOT_ID,
                "problem_id": PUBLIC_PROBLEM_ID,
                "revision_id": PUBLIC_REVISION_ID,
                "slug": PUBLIC_SLUG,
                "archived_slug": ARCHIVED_SLUG,
                "payload": payload,
            },
        )
        connection.execute(
            text(
                """
                UPDATE problem SET current_published_snapshot_id = :snapshot_id
                WHERE problem_id = :problem_id
                """
            ),
            {"snapshot_id": PUBLIC_SNAPSHOT_ID, "problem_id": PUBLIC_PROBLEM_ID},
        )
        connection.execute(
            text(
                """
                INSERT INTO editorial_transition
                    (transition_id, revision_id, source_status, target_status,
                     note, actor_context, occurred_at, operation_id)
                VALUES ('phase9-private-transition', :revision_id, 'APPROVED',
                        'PUBLISHED', 'PRIVATE_AUTHOR_NOTE_09004', 'private-author',
                        now(), 'phase9-private-operation')
                """
            ),
            {"revision_id": PUBLIC_REVISION_ID},
        )


def _assert_no_private_values(serialized: str) -> None:
    for value in PRIVATE_VALUES:
        assert value not in serialized


def test_public_routes_project_only_current_eligible_snapshot(
    isolation_system: tuple[TestClient, Engine],
) -> None:
    client, _ = isolation_system
    listing = client.get("/api/v1/problems", params={"q": "Isolation problem"})
    detail = client.get(f"/api/v1/problems/{PUBLIC_SLUG}")
    draft = client.get("/api/v1/problems/phase9-private-only")
    archived = client.get(f"/api/v1/problems/{ARCHIVED_SLUG}")
    recommendation = client.get(
        f"/api/v1/problems/{PUBLIC_SLUG}/recommendation",
        params={"stage": "AI_1_FOUNDATIONS"},
    )

    assert listing.status_code == 200
    assert [item["slug"] for item in listing.json()["items"]] == [PUBLIC_SLUG]
    assert detail.status_code == 200
    assert detail.json()["response_schema"]["type"] == "QUIZ_SINGLE"
    assert draft.status_code == archived.status_code == 404
    assert recommendation.status_code == 204
    for response in (listing, detail, draft, archived, recommendation):
        _assert_no_private_values(response.text)
    for forbidden_key in (
        "correct_choice_id",
        "hidden_tests",
        "reviewer_guidance",
        "exemplar",
        "object_key",
        "revision_id",
        "editorial_status",
        "internal_notes",
    ):
        assert forbidden_key not in detail.text


def test_submission_result_and_feedback_use_private_data_without_exposing_it(
    isolation_system: tuple[TestClient, Engine],
) -> None:
    client, engine = isolation_system
    receipt = "phase9-private-result-receipt"
    submission = client.post(
        f"/api/v1/problems/{PUBLIC_SLUG}/submissions",
        json={
            "submission_key": "phase9-isolation-submission",
            "receipt": receipt,
            "response": {"type": "QUIZ_SINGLE", "choice_id": "a"},
        },
    )
    assert submission.status_code == 200
    assert submission.json()["passed"] is True
    _assert_no_private_values(submission.text)

    attempt_id = submission.json()["attempt_id"]
    invalid_receipt = client.get(
        f"/api/v1/submissions/{attempt_id}",
        headers={"X-Submission-Receipt": "another-private-receipt"},
    )
    result = client.get(
        f"/api/v1/submissions/{attempt_id}",
        headers={"X-Submission-Receipt": receipt},
    )
    feedback = client.post(
        f"/api/v1/problems/{PUBLIC_SLUG}/feedback",
        json={
            "feedback_key": "phase9-isolation-feedback",
            "category": "OTHER",
            "message": "A safe learner report.",
        },
    )
    assert invalid_receipt.status_code == 404
    assert result.status_code == 200
    assert result.json()["submitted_response"] == {
        "type": "QUIZ_SINGLE",
        "choice_id": "a",
    }
    assert feedback.status_code == 201
    for response in (invalid_receipt, result, feedback):
        _assert_no_private_values(response.text)

    with engine.connect() as connection:
        assert (
            connection.scalar(
                text(
                    """
                SELECT count(*) FROM learner_attempt
                WHERE snapshot_id = :snapshot_id
                """
                ),
                {"snapshot_id": PUBLIC_SNAPSHOT_ID},
            )
            == 1
        )
        assert (
            connection.scalar(
                text(
                    """
                SELECT count(*) FROM problem_feedback
                WHERE snapshot_id = :snapshot_id
                """
                ),
                {"snapshot_id": PUBLIC_SNAPSHOT_ID},
            )
            == 1
        )


def test_alternate_identifiers_and_query_parameters_reveal_nothing(
    isolation_system: tuple[TestClient, Engine],
) -> None:
    client, _ = isolation_system
    responses = (
        client.get(f"/api/v1/problems/{PRIVATE_REVISION_ID}"),
        client.get(
            "/api/v1/problems",
            params={"preview": PRIVATE_REVISION_ID},
        ),
        client.get(
            "/api/v1/problems",
            params={"editorial_status": "APPROVED"},
        ),
        client.get(
            f"/api/v1/problems/{PUBLIC_SLUG}/recommendation",
            params={
                "stage": "AI_1_FOUNDATIONS",
                "evidence": f"TOPIC:{PRIVATE_REVISION_ID}:PRACTICED",
            },
        ),
    )
    assert [response.status_code for response in responses] == [404, 422, 422, 422]
    for response in responses:
        _assert_no_private_values(response.text)


def test_archive_removes_every_public_operation_but_retains_history(
    isolation_system: tuple[TestClient, Engine],
) -> None:
    client, engine = isolation_system
    archive = client.post(
        f"/api/v1/author/problems/{PUBLIC_PROBLEM_ID}/archive",
        json={
            "expected_version": 1,
            "note": "Archive after isolation verification.",
            "actor_context": "system-reviewer",
            "operation_id": "phase9-isolation-archive",
        },
    )
    assert archive.status_code == 200

    listing = client.get("/api/v1/problems", params={"q": "Isolation problem"})
    detail = client.get(f"/api/v1/problems/{PUBLIC_SLUG}")
    recommendation = client.get(
        f"/api/v1/problems/{PUBLIC_SLUG}/recommendation",
        params={"stage": "AI_1_FOUNDATIONS"},
    )
    submission = client.post(
        f"/api/v1/problems/{PUBLIC_SLUG}/submissions",
        json={
            "submission_key": "phase9-after-archive",
            "receipt": "phase9-after-archive-receipt",
            "response": {"type": "QUIZ_SINGLE", "choice_id": "a"},
        },
    )
    feedback = client.post(
        f"/api/v1/problems/{PUBLIC_SLUG}/feedback",
        json={
            "feedback_key": "phase9-after-archive",
            "category": "OTHER",
            "message": "This must not target archived content.",
        },
    )

    assert listing.status_code == 200
    assert listing.json()["total"] == 0
    assert [detail.status_code, recommendation.status_code] == [404, 404]
    assert [submission.status_code, feedback.status_code] == [404, 404]
    for response in (listing, detail, recommendation, submission, feedback):
        _assert_no_private_values(response.text)

    with engine.connect() as connection:
        assert (
            connection.scalar(
                text(
                    """
                SELECT count(*) FROM published_snapshot
                WHERE snapshot_id = :snapshot_id
                """
                ),
                {"snapshot_id": PUBLIC_SNAPSHOT_ID},
            )
            == 1
        )
        assert (
            connection.scalar(
                text(
                    """
                SELECT count(*) FROM editorial_transition
                WHERE revision_id = :revision_id
                """
                ),
                {"revision_id": PUBLIC_REVISION_ID},
            )
            == 2
        )


def test_openapi_public_operations_do_not_reference_private_author_shapes(
    isolation_system: tuple[TestClient, Engine],
) -> None:
    client, _ = isolation_system
    schema = client.get("/api/v1/openapi.json").json()
    forbidden = (
        "AuthorDraftResponse",
        "EditorialHistoryResponse",
        "AssessmentDetailResponse",
        "correct_choice_id",
        "hidden_tests",
        "reviewer_guidance",
        "revision_id",
        "editorial_status",
        "object_key",
    )

    for path, operations in schema["paths"].items():
        if path.startswith("/api/v1/author/"):
            continue
        serialized = json.dumps(operations, sort_keys=True)
        for private_name in forbidden:
            assert private_name not in serialized, path


def test_learner_source_does_not_import_studio_or_author_contract_paths() -> None:
    source_roots = (
        Path("frontend/apps/learn/app"),
        Path("frontend/apps/learn/src"),
    )
    forbidden = (
        "frontend/apps/studio",
        "@ioai/studio",
        "/api/v1/author/",
        "Draft preview - not public",
        "PRIVATE_REVIEWER_GUIDANCE_09004",
    )
    for root in source_roots:
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in {".ts", ".tsx"}:
                continue
            content = path.read_text()
            for marker in forbidden:
                assert marker not in content, f"{path} contains {marker}"
