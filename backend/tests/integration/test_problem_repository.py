from __future__ import annotations

import os
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from ioai.adapters.database.problem_model import ProblemModel, ProblemRevisionModel
from ioai.adapters.database.problem_repository import (
    SqlAlchemyDraftUnitOfWork,
)
from ioai.application.problems.errors import RevisionConflictError
from ioai.domain.problems.assessment import (
    Choice,
    QuizSingleResponse,
    ResponseType,
    ScoringComponent,
    ScoringMethod,
    ScoringScheme,
)
from ioai.domain.problems.content import (
    ContentBlock,
    ContentBlockKind,
    LearningObjective,
    LocalizedText,
    ProblemContent,
)
from ioai.domain.problems.identity import ProblemId, RevisionId, StableSlug
from ioai.domain.problems.revision import ProblemRevision
from ioai.domain.problems.workflow import EditorialStatus

DATABASE_URL = os.getenv(
    "IOAI_TEST_DATABASE_URL",
    "postgresql+psycopg://ioai:ioai@127.0.0.1:5432/ioai",
)
NOW = datetime(2026, 8, 9, 8, 0, tzinfo=timezone.utc)


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


def empty_revision(*, version: int = 1, slug: str | None = None) -> ProblemRevision:
    return ProblemRevision(
        problem_id=ProblemId("problem-01"),
        revision_id=RevisionId("revision-01"),
        version=version,
        slug=StableSlug(slug) if slug else None,
        status=EditorialStatus.DRAFT,
        content=None,
        metadata=None,
        response=None,
        scoring=None,
    )


def test_create_read_list_and_normalized_round_trip(session_factory) -> None:
    bilingual = LocalizedText(en="Metrics", vi="Độ đo")
    authored = empty_revision(slug="first-problem")
    authored = ProblemRevision(
        problem_id=authored.problem_id,
        revision_id=authored.revision_id,
        version=authored.version,
        slug=authored.slug,
        status=authored.status,
        content=ProblemContent(
            title=bilingual,
            summary=bilingual,
            objectives=(
                LearningObjective(
                    LocalizedText(en="Explain metrics.", vi="Giải thích độ đo.")
                ),
            ),
            blocks=(ContentBlock(ContentBlockKind.STATEMENT, bilingual, 1),),
        ),
        metadata=None,
        response=QuizSingleResponse(
            (Choice("A", bilingual), Choice("B", bilingual)), "A"
        ),
        scoring=ScoringScheme(
            ResponseType.QUIZ_SINGLE,
            (ScoringComponent(ScoringMethod.EXACT_MATCH, Decimal("1.0")),),
        ),
    )
    with SqlAlchemyDraftUnitOfWork(session_factory) as work:
        work.drafts.create(authored, NOW)

    with SqlAlchemyDraftUnitOfWork(session_factory) as work:
        stored = work.drafts.get(RevisionId("revision-01"))
        listed = work.drafts.list()

    assert stored == authored
    assert len(listed) == 1
    assert listed[0].problem_id == ProblemId("problem-01")
    assert listed[0].revision_id == RevisionId("revision-01")
    assert listed[0].status is EditorialStatus.DRAFT
    assert listed[0].last_saved_at == NOW


def test_unit_of_work_rolls_back_problem_and_revision_together(session_factory) -> None:
    with pytest.raises(RuntimeError, match="rollback"):
        with SqlAlchemyDraftUnitOfWork(session_factory) as work:
            work.drafts.create(empty_revision(), NOW)
            raise RuntimeError("rollback")

    with session_factory() as session:
        assert session.scalar(select(func.count()).select_from(ProblemModel)) == 0
        assert (
            session.scalar(select(func.count()).select_from(ProblemRevisionModel)) == 0
        )


def test_compare_and_increment_save_rejects_stale_write(session_factory) -> None:
    with SqlAlchemyDraftUnitOfWork(session_factory) as work:
        work.drafts.create(empty_revision(), NOW)

    changed = empty_revision(version=1, slug="saved-slug")
    with SqlAlchemyDraftUnitOfWork(session_factory) as work:
        saved = work.drafts.save(changed, expected_version=1, saved_at=NOW)

    assert saved.version == 2
    assert saved.slug == StableSlug("saved-slug")

    with pytest.raises(RevisionConflictError) as conflict:
        with SqlAlchemyDraftUnitOfWork(session_factory) as work:
            work.drafts.save(changed, expected_version=1, saved_at=NOW)

    assert conflict.value.current_version == 2
    with SqlAlchemyDraftUnitOfWork(session_factory) as work:
        assert work.drafts.get(RevisionId("revision-01")) == saved
