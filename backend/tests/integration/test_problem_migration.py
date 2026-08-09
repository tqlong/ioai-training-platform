from __future__ import annotations

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError

from .test_vocabulary_migration import migrated_database

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
    } <= set(inspector.get_table_names())


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
