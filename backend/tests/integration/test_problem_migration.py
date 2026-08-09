from __future__ import annotations

import pytest
from alembic import command
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError

from .test_vocabulary_migration import alembic_config, migrated_database

__all__ = ["migrated_database"]


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
