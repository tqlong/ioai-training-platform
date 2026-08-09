from __future__ import annotations

from datetime import UTC, datetime

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker
from tests.integration.database_environment import require_test_database_url

from ioai.adapters.database.proposal_repository import SqlAlchemyProposalUnitOfWork
from ioai.adapters.database.vocabulary_model import (
    VocabularyProposalModel,
    VocabularyRecordModel,
)
from ioai.application.vocabulary.proposals import RecordVocabularyProposal

DATABASE_URL = require_test_database_url()


@pytest.fixture
def proposal_session_factory():
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


def test_proposal_persists_separately_and_is_reviewable(
    proposal_session_factory,
) -> None:
    record = RecordVocabularyProposal(
        unit_of_work_factory=lambda: SqlAlchemyProposalUnitOfWork(
            proposal_session_factory
        ),
        id_generator=lambda: "proposal-fixed",
        clock=lambda: datetime(2026, 8, 9, tzinfo=UTC),
    )

    created = record(vocabulary_type="TOPIC", note="Add causal inference")
    pending = record.list_pending()

    assert pending == (created,)
    with proposal_session_factory() as session:
        assert (
            session.scalar(select(func.count()).select_from(VocabularyProposalModel))
            == 1
        )
        assert (
            session.scalar(select(func.count()).select_from(VocabularyRecordModel)) == 0
        )
