from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.orm import Session

from ioai.adapters.database.problem_repository import SqlAlchemyPublishedProblemReader
from ioai.application.problems.public_queries import (
    PublicProblemQuery,
    PublicProblemSort,
)

from .test_vocabulary_migration import migrated_database

__all__ = ["migrated_database"]


NOW = datetime(2026, 8, 9, tzinfo=UTC)


def _payload(
    title_en: str,
    title_vi: str,
    *,
    stage: str = "AI_1_FOUNDATIONS",
    difficulty: str = "EASY",
    competency: str = "EVAL_METRICS",
    topic: str = "CONFUSION_MATRIX",
    task_type: str = "QUIZ_SINGLE",
    minutes: int = 10,
    compute_tier: str = "NONE",
    editorial_order: int = 1,
) -> dict[str, object]:
    return {
        "content": {
            "title": {"en": title_en, "vi": title_vi},
            "summary": {"en": "Calculate evaluation metrics", "vi": "Tính độ đo"},
            "objectives": [{"en": "Calculate metrics", "vi": "Tính độ đo"}],
        },
        "metadata": {
            "stage": ["PATHWAY_STAGE", stage],
            "difficulty": ["DIFFICULTY", difficulty],
            "primary_competency": ["COMPETENCY", competency],
            "secondary_competencies": [],
            "task_type": ["TASK_TYPE", task_type],
            "topics": [["TOPIC", topic]],
            "expected_minutes": minutes,
            "editorial_order": editorial_order,
            "resources": {"compute_tier": ["COMPUTE_TIER", compute_tier]},
        },
    }


def _seed_snapshot(
    database,
    identity: str,
    payload: dict[str, object],
    *,
    published_at: datetime,
    is_current: bool = True,
) -> None:
    with database.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO problem (problem_id, slug, created_at)
                VALUES (:identity, :identity, :published_at)
                """
            ),
            {"identity": identity, "published_at": published_at},
        )
        connection.execute(
            text(
                """
                INSERT INTO problem_revision
                    (revision_id, problem_id, revision_number, lock_version,
                     editorial_status, content, created_at, updated_at)
                VALUES (:revision_id, :identity, 1, 1, :status,
                        CAST(:payload AS jsonb), :published_at, :published_at)
                """
            ),
            {
                "revision_id": f"revision-{identity}",
                "identity": identity,
                "status": "PUBLISHED" if is_current else "DRAFT",
                "payload": json.dumps(payload),
                "published_at": published_at,
            },
        )
        if not is_current:
            return
        connection.execute(
            text(
                """
                INSERT INTO published_snapshot
                    (snapshot_id, problem_id, revision_id, slug, public_payload,
                     published_at)
                VALUES (:snapshot_id, :identity, :revision_id, :identity,
                        CAST(:payload AS jsonb), :published_at)
                """
            ),
            {
                "snapshot_id": f"snapshot-{identity}",
                "revision_id": f"revision-{identity}",
                "identity": identity,
                "payload": json.dumps(payload),
                "published_at": published_at,
            },
        )
        connection.execute(
            text(
                """
                UPDATE problem SET current_published_snapshot_id = :snapshot_id
                WHERE problem_id = :identity
                """
            ),
            {"snapshot_id": f"snapshot-{identity}", "identity": identity},
        )


def _seed_library(database) -> None:
    with database.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO vocabulary_record
                    (vocabulary_type, code, label_en, label_vi, aliases, status,
                     parent_vocabulary_type, parent_code)
                VALUES
                    ('TOPIC', 'EVALUATION', 'Evaluation', 'Đánh giá', '["eval"]',
                     'ACTIVE', NULL, NULL),
                    ('TOPIC', 'CONFUSION_MATRIX', 'Confusion matrix',
                     'Ma trận nhầm lẫn', '["error table"]', 'ACTIVE',
                     'TOPIC', 'EVALUATION'),
                    ('TOPIC', 'REGRESSION_METRICS', 'Regression metrics',
                     'Độ đo hồi quy', '[]', 'ACTIVE', 'TOPIC', 'EVALUATION'),
                    ('COMPETENCY', 'EVAL_METRICS', 'Evaluate models',
                     'Đánh giá mô hình', '["model assessment"]', 'ACTIVE',
                     NULL, NULL)
                """
            )
        )
    _seed_snapshot(
        database,
        "confusion-basics",
        _payload("Confusion basics", "Nhập môn ma trận", editorial_order=2),
        published_at=NOW,
    )
    _seed_snapshot(
        database,
        "regression-metrics",
        _payload(
            "Regression metrics",
            "Độ đo hồi quy",
            topic="REGRESSION_METRICS",
            minutes=25,
            compute_tier="BROWSER",
            editorial_order=1,
        ),
        published_at=NOW + timedelta(minutes=1),
    )
    _seed_snapshot(
        database,
        "private-draft",
        _payload("Private", "Riêng tư"),
        published_at=NOW,
        is_current=False,
    )


def test_filters_descendants_aliases_and_never_returns_drafts(
    migrated_database,
) -> None:
    _seed_library(migrated_database)
    with Session(migrated_database) as session:
        reader = SqlAlchemyPublishedProblemReader(session)

        descendants = reader.list_current(
            PublicProblemQuery(topic="EVALUATION", include_subtopics=True)
        )
        alias = reader.list_current(PublicProblemQuery(search="model assessment"))
        compute = reader.list_current(PublicProblemQuery(compute_tier="BROWSER"))
        metadata = reader.list_current(
            PublicProblemQuery(
                stage="AI_1_FOUNDATIONS",
                competency="EVAL_METRICS",
                difficulty="EASY",
                task_type="QUIZ_SINGLE",
                expected_minutes_min=20,
                expected_minutes_max=30,
            )
        )

    assert descendants.total == 2
    assert {item.slug.value for item in descendants.snapshots} == {
        "confusion-basics",
        "regression-metrics",
    }
    assert alias.total == 2
    assert [item.slug.value for item in compute.snapshots] == ["regression-metrics"]
    assert [item.slug.value for item in metadata.snapshots] == ["regression-metrics"]
    assert all(item.slug.value != "private-draft" for item in descendants.snapshots)


def test_sorts_counts_and_paginates_after_published_filtering(
    migrated_database,
) -> None:
    _seed_library(migrated_database)
    with Session(migrated_database) as session:
        reader = SqlAlchemyPublishedProblemReader(session)
        first = reader.list_current(PublicProblemQuery(page=1, page_size=1))
        second = reader.list_current(PublicProblemQuery(page=2, page_size=1))
        newest = reader.list_current(
            PublicProblemQuery(sort=PublicProblemSort.NEWEST, page_size=10)
        )

    assert first.total == second.total == 2
    assert [item.slug.value for item in first.snapshots] == ["regression-metrics"]
    assert [item.slug.value for item in second.snapshots] == ["confusion-basics"]
    assert [item.slug.value for item in newest.snapshots] == [
        "regression-metrics",
        "confusion-basics",
    ]
