from __future__ import annotations

import os
from dataclasses import replace

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from ioai.adapters.database.vocabulary_model import VocabularyRecordModel
from ioai.adapters.database.vocabulary_repository import (
    SqlAlchemyVocabularyUnitOfWork,
)
from ioai.adapters.vocabulary.runtime import load_generated_vocabulary
from ioai.application.vocabulary.synchronize import SynchronizeVocabulary
from ioai.domain.vocabulary.values import LocalizedLabels

DATABASE_URL = os.getenv(
    "IOAI_TEST_DATABASE_URL",
    "postgresql+psycopg://ioai:ioai@127.0.0.1:5432/ioai",
)


@pytest.fixture
def session_factory():
    engine = create_engine(DATABASE_URL)
    try:
        with engine.connect():
            pass
    except Exception as error:
        pytest.skip(f"PostgreSQL is unavailable: {error}")
    config = Config("backend/alembic.ini")
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    yield factory
    command.downgrade(config, "base")
    engine.dispose()


def test_generated_artifact_sync_is_idempotent_and_updates_labels(
    session_factory,
) -> None:
    synchronize = SynchronizeVocabulary(
        lambda: SqlAlchemyVocabularyUnitOfWork(session_factory)
    )
    records = load_generated_vocabulary()

    first = synchronize(records)
    second = synchronize(records)
    changed = list(records)
    changed[0] = replace(
        changed[0], labels=LocalizedLabels(en="Updated label", vi="Nhan moi")
    )
    third = synchronize(changed)

    assert (first.added, first.updated, first.unchanged) == (343, 0, 0)
    assert (second.added, second.updated, second.unchanged) == (0, 0, 343)
    assert (third.added, third.updated, third.unchanged) == (0, 1, 342)
    with session_factory() as session:
        assert (
            session.scalar(select(func.count()).select_from(VocabularyRecordModel))
            == 343
        )


def test_unit_of_work_rolls_back_all_writes_on_failure(session_factory) -> None:
    record = load_generated_vocabulary()[0]

    with pytest.raises(RuntimeError, match="force rollback"):
        with SqlAlchemyVocabularyUnitOfWork(session_factory) as unit_of_work:
            unit_of_work.vocabulary.add(record)
            raise RuntimeError("force rollback")

    with session_factory() as session:
        assert (
            session.scalar(select(func.count()).select_from(VocabularyRecordModel)) == 0
        )
