from __future__ import annotations

import pytest
from alembic import command
from alembic.script import ScriptDirectory
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError, ProgrammingError

from .test_vocabulary_migration import alembic_config, migrated_database

__all__ = ["migrated_database"]

EXPECTED_RELEASE_0_REVISIONS = (
    "20260809_05007",
    "20260809_05008",
    "20260809_05011",
    "20260809_06006",
    "20260809_07002",
    "20260809_08002",
    "20260811_08104",
    "20260813_09002",
)


def test_release_0_migration_chain_is_linear_and_at_expected_head(
    migrated_database,
) -> None:
    script = ScriptDirectory.from_config(alembic_config())
    revisions = tuple(
        revision.revision for revision in reversed(tuple(script.walk_revisions()))
    )

    assert revisions == EXPECTED_RELEASE_0_REVISIONS
    with migrated_database.connect() as connection:
        assert (
            connection.scalar(text("SELECT version_num FROM alembic_version"))
            == (EXPECTED_RELEASE_0_REVISIONS[-1])
        )


def test_problem_migration_creates_phase_6_tables(migrated_database) -> None:
    inspector = inspect(migrated_database)

    assert {
        "problem",
        "problem_revision",
        "revision_competency",
        "revision_topic",
        "prerequisite_reference",
        "response_configuration",
        "scoring_component",
        "editorial_transition",
        "published_snapshot",
        "idempotency_record",
        "learner_attempt",
        "problem_feedback",
    } <= set(inspector.get_table_names())

    problem_columns = {column["name"] for column in inspector.get_columns("problem")}
    assert "current_published_snapshot_id" in problem_columns


def test_problem_migration_enforces_unique_slug_and_positive_version(
    migrated_database,
) -> None:
    with migrated_database.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO problem (problem_id, slug, created_at)
                VALUES ('problem-1', 'stable-slug', now())
                """
            )
        )

    with pytest.raises(IntegrityError):
        with migrated_database.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO problem (problem_id, slug, created_at)
                    VALUES ('problem-2', 'stable-slug', now())
                    """
                )
            )

    with pytest.raises(IntegrityError):
        with migrated_database.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO problem_revision
                        (revision_id, problem_id, revision_number, lock_version,
                         editorial_status, content, created_at, updated_at)
                    VALUES
                        ('revision-1', 'problem-1', 0, 0, 'DRAFT', '{}', now(), now())
                    """
                )
            )


def test_editorial_publication_migration_up_and_down(migrated_database) -> None:
    command.downgrade(alembic_config(), "20260809_06006")

    inspector = inspect(migrated_database)
    assert not inspector.has_table("editorial_transition")
    assert not inspector.has_table("published_snapshot")
    assert not inspector.has_table("idempotency_record")
    assert "current_published_snapshot_id" not in {
        column["name"] for column in inspector.get_columns("problem")
    }

    command.upgrade(alembic_config(), "head")

    inspector = inspect(migrated_database)
    assert inspector.has_table("editorial_transition")
    assert inspector.has_table("published_snapshot")
    assert inspector.has_table("idempotency_record")


def test_learner_record_migration_up_and_down(migrated_database) -> None:
    command.downgrade(alembic_config(), "20260809_07002")

    inspector = inspect(migrated_database)
    assert not inspector.has_table("learner_attempt")
    assert not inspector.has_table("problem_feedback")

    command.upgrade(alembic_config(), "head")

    inspector = inspect(migrated_database)
    assert inspector.has_table("learner_attempt")
    assert inspector.has_table("problem_feedback")


def test_manual_assessment_migration_up_and_down(migrated_database) -> None:
    inspector = inspect(migrated_database)
    assert inspector.has_table("assessment_decision")
    assert {"receipt_digest", "response"} <= {
        column["name"] for column in inspector.get_columns("learner_attempt")
    }

    command.downgrade(alembic_config(), "20260809_08002")

    inspector = inspect(migrated_database)
    assert not inspector.has_table("assessment_decision")
    assert {"receipt_digest", "response"}.isdisjoint(
        column["name"] for column in inspector.get_columns("learner_attempt")
    )

    command.upgrade(alembic_config(), "head")

    inspector = inspect(migrated_database)
    assert inspector.has_table("assessment_decision")
    assert {"receipt_digest", "response"} <= {
        column["name"] for column in inspector.get_columns("learner_attempt")
    }


def test_public_and_assessment_queries_have_supporting_indexes(
    migrated_database,
) -> None:
    inspector = inspect(migrated_database)

    assert "ix_published_snapshot_slug" in {
        index["name"] for index in inspector.get_indexes("published_snapshot")
    }
    assert "ix_learner_attempt_outcome_submitted" in {
        index["name"] for index in inspector.get_indexes("learner_attempt")
    }
    assert "ix_assessment_decision_attempt" in {
        index["name"] for index in inspector.get_indexes("assessment_decision")
    }

    with migrated_database.begin() as connection:
        connection.execute(text("SET LOCAL enable_seqscan = off"))
        public_plan = "\n".join(
            row[0]
            for row in connection.execute(
                text(
                    """
                    EXPLAIN (COSTS OFF)
                    SELECT snapshot_id FROM published_snapshot WHERE slug = 'probe'
                    """
                )
            )
        )
        assessment_plan = "\n".join(
            row[0]
            for row in connection.execute(
                text(
                    """
                    EXPLAIN (COSTS OFF)
                    SELECT attempt_id FROM learner_attempt
                    WHERE outcome = 'PENDING_ASSESSMENT'
                    ORDER BY submitted_at, attempt_id
                    LIMIT 50
                    """
                )
            )
        )

    assert "ix_published_snapshot_slug" in public_plan
    assert "ix_learner_attempt_outcome_submitted" in assessment_plan


def test_postgresql_rolls_back_failed_migration_ddl(migrated_database) -> None:
    with pytest.raises(ProgrammingError, match="phase9_forced_migration_failure"):
        with migrated_database.begin() as connection:
            connection.execute(text("CREATE TABLE phase9_migration_probe (id integer)"))
            connection.execute(text("SELECT phase9_forced_migration_failure()"))

    assert not inspect(migrated_database).has_table("phase9_migration_probe")


def test_manual_assessment_constraints_preserve_append_only_history(
    migrated_database,
) -> None:
    with migrated_database.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO problem (problem_id, slug, created_at)
                VALUES ('assessment-problem', 'assessment-problem', now())
                """
            )
        )
        connection.execute(
            text(
                """
                INSERT INTO problem_revision
                    (revision_id, problem_id, revision_number, lock_version,
                     editorial_status, content, created_at, updated_at)
                VALUES ('assessment-revision', 'assessment-problem', 1, 1,
                        'PUBLISHED', '{}', now(), now())
                """
            )
        )
        connection.execute(
            text(
                """
                INSERT INTO published_snapshot
                    (snapshot_id, problem_id, revision_id, slug, public_payload,
                     published_at)
                VALUES ('assessment-snapshot', 'assessment-problem',
                        'assessment-revision', 'assessment-problem', '{}', now())
                """
            )
        )
        connection.execute(
            text(
                """
                INSERT INTO learner_attempt
                    (attempt_id, snapshot_id, submission_key, request_digest,
                     receipt_digest, response, outcome, result, submitted_at)
                VALUES ('assessment-attempt', 'assessment-snapshot', 'submission-1',
                        :digest, :digest, '{}', 'PENDING_ASSESSMENT', '{}', now())
                """
            ),
            {"digest": "a" * 64},
        )
        connection.execute(
            text(
                """
                INSERT INTO assessment_decision
                    (decision_id, attempt_id, version, selections, result, decided_at)
                VALUES ('decision-1', 'assessment-attempt', 1, '[]', '{}', now())
                """
            )
        )

    with pytest.raises(IntegrityError):
        with migrated_database.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO assessment_decision
                        (decision_id, attempt_id, version, selections, result,
                         correction_reason, decided_at)
                    VALUES ('decision-2', 'assessment-attempt', 1, '[]', '{}',
                            'duplicate version', now())
                    """
                )
            )

    with migrated_database.connect() as connection:
        assert (
            connection.scalar(
                text(
                    """
                SELECT count(*) FROM assessment_decision
                WHERE attempt_id = 'assessment-attempt'
                """
                )
            )
            == 1
        )


def test_editorial_storage_rejects_duplicate_operations_and_blank_notes(
    migrated_database,
) -> None:
    with migrated_database.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO problem (problem_id, slug, created_at)
                VALUES ('editorial-problem', 'editorial-problem', now())
                """
            )
        )
        connection.execute(
            text(
                """
                INSERT INTO problem_revision
                    (revision_id, problem_id, revision_number, lock_version,
                     editorial_status, content, created_at, updated_at)
                VALUES
                    ('editorial-revision', 'editorial-problem', 1, 1,
                     'DRAFT', '{}', now(), now())
                """
            )
        )
        connection.execute(
            text(
                """
                INSERT INTO editorial_transition
                    (transition_id, revision_id, source_status, target_status,
                     note, actor_context, occurred_at, operation_id)
                VALUES
                    ('transition-1', 'editorial-revision', 'DRAFT', 'IN_REVIEW',
                     'Ready for review', 'local-author', now(), 'operation-1')
                """
            )
        )

    with pytest.raises(IntegrityError):
        with migrated_database.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO editorial_transition
                        (transition_id, revision_id, source_status, target_status,
                         note, actor_context, occurred_at, operation_id)
                    VALUES
                        ('transition-2', 'editorial-revision', 'DRAFT', 'IN_REVIEW',
                         'Duplicate operation', 'local-author', now(), 'operation-1')
                    """
                )
            )

    with pytest.raises(IntegrityError):
        with migrated_database.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO editorial_transition
                        (transition_id, revision_id, source_status, target_status,
                         note, actor_context, occurred_at, operation_id)
                    VALUES
                        ('transition-3', 'editorial-revision', 'DRAFT', 'IN_REVIEW',
                         ' ', 'local-author', now(), 'operation-3')
                    """
                )
            )
