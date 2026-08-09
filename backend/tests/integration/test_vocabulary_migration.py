from __future__ import annotations

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError
from tests.integration.database_environment import require_test_database_url

DATABASE_URL = require_test_database_url()


def alembic_config() -> Config:
    config = Config("backend/alembic.ini")
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
    return config


@pytest.fixture
def migrated_database():
    engine = create_engine(DATABASE_URL)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as error:
        pytest.skip(f"PostgreSQL is unavailable: {error}")

    command.downgrade(alembic_config(), "base")
    command.upgrade(alembic_config(), "head")
    yield engine
    command.downgrade(alembic_config(), "base")
    engine.dispose()


def test_vocabulary_migration_up_and_down(migrated_database) -> None:
    assert inspect(migrated_database).has_table("vocabulary_record")

    command.downgrade(alembic_config(), "base")

    assert not inspect(migrated_database).has_table("vocabulary_record")


def test_database_rejects_invalid_parent_and_rolls_back(migrated_database) -> None:
    with migrated_database.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO vocabulary_record
                    (vocabulary_type, code, label_en, label_vi, aliases, status)
                VALUES
                    ('TOPIC', 'TOPIC_ROOT', 'Root', 'Gốc', '[]', 'ACTIVE')
                """
            )
        )

    with pytest.raises(IntegrityError):
        with migrated_database.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO vocabulary_record
                        (vocabulary_type, code, label_en, label_vi, aliases, status,
                         parent_vocabulary_type, parent_code)
                    VALUES
                        ('TOPIC', 'TOPIC_CHILD', 'Child', 'Chủ đề con', '[]', 'ACTIVE',
                         'TOPIC', 'TOPIC_MISSING')
                    """
                )
            )

    with migrated_database.connect() as connection:
        count = connection.scalar(
            text("SELECT count(*) FROM vocabulary_record WHERE code = 'TOPIC_CHILD'")
        )
    assert count == 0
