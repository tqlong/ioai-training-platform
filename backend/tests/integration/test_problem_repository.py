from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, func, select, text
from sqlalchemy.orm import sessionmaker
from tests.integration.database_environment import require_test_database_url

from ioai.adapters.database.problem_model import (
    EditorialTransitionModel,
    IdempotencyRecordModel,
    ProblemModel,
    ProblemRevisionModel,
    PublishedSnapshotModel,
)
from ioai.adapters.database.problem_repository import (
    SqlAlchemyDraftUnitOfWork,
    SqlAlchemyPublishedProblemReader,
)
from ioai.application.problems.editorial import StartSuccessorDraft
from ioai.application.problems.errors import RevisionConflictError
from ioai.application.problems.public_queries import PublicProblemQuery
from ioai.application.problems.publication import ArchiveProblem, PublishedSnapshot
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
from ioai.domain.problems.metadata import (
    CurriculumMetadata,
    ExpectedMinutes,
    NetworkPolicy,
    PrerequisiteReference,
    PrerequisiteRelationship,
    PrerequisiteTargetType,
    ResourceLimits,
)
from ioai.domain.problems.revision import ProblemRevision
from ioai.domain.problems.workflow import (
    ActorContext,
    EditorialStatus,
    transition_for_publication,
    transition_for_review,
)
from ioai.domain.vocabulary.availability import Release0AvailabilityPolicy
from ioai.domain.vocabulary.values import VocabularyIdentity, VocabularyType

DATABASE_URL = require_test_database_url()
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


def test_editorial_transition_updates_version_and_history_atomically(
    session_factory,
) -> None:
    with SqlAlchemyDraftUnitOfWork(session_factory) as work:
        work.drafts.create(empty_revision(), NOW)

    transition = transition_for_review(
        revision_id=RevisionId("revision-01"),
        source=EditorialStatus.DRAFT,
        target=EditorialStatus.IN_REVIEW,
        note="Ready for review.",
        actor=ActorContext("local-author"),
        occurred_at=NOW,
        operation_id="submit-01",
    )
    with SqlAlchemyDraftUnitOfWork(session_factory) as work:
        reviewed = work.editorial.transition(
            transition,
            expected_version=1,
            transition_id="transition-01",
        )

    assert reviewed.status is EditorialStatus.IN_REVIEW
    assert reviewed.version == 2
    with SqlAlchemyDraftUnitOfWork(session_factory) as work:
        projected_history = work.editorial.list_history(RevisionId("revision-01"))
    assert projected_history == (transition,)
    with session_factory() as session:
        history = session.scalars(select(EditorialTransitionModel)).all()
        assert len(history) == 1
        assert history[0].note == "Ready for review."

    with pytest.raises(RevisionConflictError):
        with SqlAlchemyDraftUnitOfWork(session_factory) as work:
            work.editorial.transition(
                transition,
                expected_version=1,
                transition_id="transition-stale",
            )


def test_editorial_unit_of_work_rolls_back_state_and_history(session_factory) -> None:
    with SqlAlchemyDraftUnitOfWork(session_factory) as work:
        work.drafts.create(empty_revision(), NOW)
    transition = transition_for_review(
        revision_id=RevisionId("revision-01"),
        source=EditorialStatus.DRAFT,
        target=EditorialStatus.IN_REVIEW,
        note="Ready for review.",
        actor=ActorContext("local-author"),
        occurred_at=NOW,
        operation_id="submit-rollback",
    )

    with pytest.raises(RuntimeError, match="rollback"):
        with SqlAlchemyDraftUnitOfWork(session_factory) as work:
            work.editorial.transition(
                transition,
                expected_version=1,
                transition_id="transition-rollback",
            )
            raise RuntimeError("rollback")

    with SqlAlchemyDraftUnitOfWork(session_factory) as work:
        assert (
            work.drafts.get(RevisionId("revision-01")).status is EditorialStatus.DRAFT
        )
    with session_factory() as session:
        assert (
            session.scalar(select(func.count()).select_from(EditorialTransitionModel))
            == 0
        )


def test_changes_requested_successor_is_idempotent_and_preserves_source(
    session_factory,
) -> None:
    source = replace(empty_revision(), status=EditorialStatus.CHANGES_REQUESTED)
    with SqlAlchemyDraftUnitOfWork(session_factory) as work:
        work.drafts.create(source, NOW)
    generated = iter(("revision-02", "revision-03"))
    start = StartSuccessorDraft(
        unit_of_work_factory=lambda: SqlAlchemyDraftUnitOfWork(session_factory),
        id_generator=lambda: next(generated),
        clock=lambda: NOW,
    )

    first = start(source.revision_id, expected_version=1, operation_id="revise-01")
    replay = start(source.revision_id, expected_version=1, operation_id="revise-01")

    assert first.revision_id == RevisionId("revision-02")
    assert replay.revision_id == first.revision_id
    with session_factory() as session:
        revisions = session.scalars(
            select(ProblemRevisionModel).order_by(ProblemRevisionModel.revision_number)
        ).all()
    assert [(row.revision_id, row.editorial_status) for row in revisions] == [
        ("revision-01", "CHANGES_REQUESTED"),
        ("revision-02", "DRAFT"),
    ]


def test_publication_switches_snapshot_status_history_and_idempotency_atomically(
    session_factory,
) -> None:
    approved = replace(
        empty_revision(slug="stable-public-url"),
        status=EditorialStatus.APPROVED,
    )
    with SqlAlchemyDraftUnitOfWork(session_factory) as work:
        work.drafts.create(approved, NOW)
    snapshot = PublishedSnapshot(
        snapshot_id="snapshot-01",
        problem_id=approved.problem_id,
        revision_id=approved.revision_id,
        slug=StableSlug("stable-public-url"),
        public_payload={"content": {"title": {"en": "Public"}}},
        published_at=NOW,
    )
    transition = transition_for_publication(
        revision_id=approved.revision_id,
        source=EditorialStatus.APPROVED,
        note="Publish approved content.",
        actor=ActorContext("local-reviewer"),
        occurred_at=NOW,
        operation_id="publication-operation-01",
    )
    with SqlAlchemyDraftUnitOfWork(session_factory) as work:
        result = work.publication.publish(
            snapshot=snapshot,
            transition=transition,
            expected_version=1,
            transition_id="transition-publication-01",
            idempotency_key="publish-01",
            request_digest="digest-01",
        )

    assert result == snapshot
    with session_factory() as session:
        problem = session.get(ProblemModel, "problem-01")
        revision_row = session.get(ProblemRevisionModel, "revision-01")
        assert problem is not None
        assert revision_row is not None
        assert problem.current_published_snapshot_id == "snapshot-01"
        assert revision_row.editorial_status == "PUBLISHED"
        assert revision_row.lock_version == 2
        assert (
            session.scalar(select(func.count()).select_from(PublishedSnapshotModel))
            == 1
        )

    start = StartSuccessorDraft(
        unit_of_work_factory=lambda: SqlAlchemyDraftUnitOfWork(session_factory),
        id_generator=lambda: "revision-02",
        clock=lambda: NOW,
    )
    successor = start(
        approved.revision_id,
        expected_version=2,
        operation_id="revise-published-01",
    )
    assert successor.status is EditorialStatus.DRAFT
    with session_factory() as session:
        problem = session.get(ProblemModel, "problem-01")
        assert problem is not None
        assert problem.current_published_snapshot_id == "snapshot-01"
        reader = SqlAlchemyPublishedProblemReader(session)
        assert [
            item.slug.value
            for item in reader.list_current(PublicProblemQuery(page_size=10)).snapshots
        ] == ["stable-public-url"]
        assert reader.get_current_by_slug("stable-public-url") == snapshot

    archive = ArchiveProblem(
        unit_of_work_factory=lambda: SqlAlchemyDraftUnitOfWork(session_factory),
        id_generator=lambda: "transition-archive-01",
        clock=lambda: NOW,
    )
    archived = archive(
        approved.problem_id,
        expected_version=2,
        note="Archive obsolete public content.",
        actor=ActorContext("local-reviewer"),
        operation_id="archive-01",
    )
    assert archived.slug == StableSlug("stable-public-url")
    with session_factory() as session:
        problem = session.get(ProblemModel, "problem-01")
        published_revision = session.get(ProblemRevisionModel, "revision-01")
        draft_revision = session.get(ProblemRevisionModel, "revision-02")
        assert problem is not None and problem.current_published_snapshot_id is None
        assert published_revision is not None
        assert published_revision.editorial_status == "ARCHIVED"
        assert draft_revision is not None and draft_revision.editorial_status == "DRAFT"
        assert (
            session.scalar(select(func.count()).select_from(PublishedSnapshotModel))
            == 1
        )
        assert (
            session.scalar(select(func.count()).select_from(EditorialTransitionModel))
            == 2
        )
        assert (
            session.scalar(select(func.count()).select_from(IdempotencyRecordModel))
            == 2
        )
        reader = SqlAlchemyPublishedProblemReader(session)
        assert reader.list_current(PublicProblemQuery(page_size=10)).snapshots == ()
        assert reader.get_current_by_slug("stable-public-url") is None

    with SqlAlchemyDraftUnitOfWork(session_factory) as work:
        replay = work.publication.replay(
            approved.revision_id,
            idempotency_key="publish-01",
            request_digest="digest-01",
        )
    assert replay == snapshot


def test_publication_rolls_back_every_visible_effect_on_failure(
    session_factory,
) -> None:
    approved = replace(
        empty_revision(slug="rollback-publication"),
        status=EditorialStatus.APPROVED,
    )
    with SqlAlchemyDraftUnitOfWork(session_factory) as work:
        work.drafts.create(approved, NOW)
    snapshot = PublishedSnapshot(
        "snapshot-rollback",
        approved.problem_id,
        approved.revision_id,
        StableSlug("rollback-publication"),
        {},
        NOW,
    )
    transition = transition_for_publication(
        revision_id=approved.revision_id,
        source=EditorialStatus.APPROVED,
        note="Publish then fail.",
        actor=ActorContext("local-reviewer"),
        occurred_at=NOW,
        operation_id="publication-rollback",
    )

    with pytest.raises(RuntimeError, match="injected"):
        with SqlAlchemyDraftUnitOfWork(session_factory) as work:
            work.publication.publish(
                snapshot=snapshot,
                transition=transition,
                expected_version=1,
                transition_id="transition-rollback",
                idempotency_key="publish-rollback",
                request_digest="digest-rollback",
            )
            raise RuntimeError("injected publication failure")

    with session_factory() as session:
        problem = session.get(ProblemModel, "problem-01")
        revision_row = session.get(ProblemRevisionModel, "revision-01")
        assert problem is not None and problem.current_published_snapshot_id is None
        assert revision_row is not None and revision_row.editorial_status == "APPROVED"
        assert (
            session.scalar(select(func.count()).select_from(PublishedSnapshotModel))
            == 0
        )
        assert (
            session.scalar(select(func.count()).select_from(EditorialTransitionModel))
            == 0
        )


def test_create_persists_normalized_curriculum_response_and_scoring(
    session_factory,
) -> None:
    with session_factory.begin() as session:
        session.execute(
            text("""
            INSERT INTO vocabulary_record
              (vocabulary_type, code, label_en, label_vi, aliases, status)
            VALUES
              ('COMPETENCY', 'EVAL_METRICS', 'Metrics', 'Độ đo', '[]', 'ACTIVE'),
              ('COMPETENCY', 'MATH_STATISTICS', 'Statistics', 'Thống kê',
               '[]', 'ACTIVE'),
              ('TOPIC', 'ML_EVALUATION', 'Evaluation', 'Đánh giá', '[]', 'ACTIVE')
        """)
        )

    def vid(type_: str, code: str) -> VocabularyIdentity:
        return VocabularyIdentity(VocabularyType(type_), code)

    metadata = CurriculumMetadata(
        stage=vid("PATHWAY_STAGE", "AI_1_FOUNDATIONS"),
        difficulty=vid("DIFFICULTY", "EASY"),
        primary_competency=vid("COMPETENCY", "EVAL_METRICS"),
        secondary_competencies=(vid("COMPETENCY", "MATH_STATISTICS"),),
        task_type=vid("TASK_TYPE", "QUIZ_SINGLE"),
        topics=(vid("TOPIC", "ML_EVALUATION"),),
        prerequisites=(
            PrerequisiteReference(
                PrerequisiteRelationship.RECOMMENDED,
                PrerequisiteTargetType.TOPIC,
                target_identity=vid("TOPIC", "ML_EVALUATION"),
            ),
        ),
        modalities=(vid("DATA_MODALITY", "NONE"),),
        expected_minutes=ExpectedMinutes(15),
        resources=ResourceLimits(
            vid("COMPUTE_TIER", "NONE"),
            vid("RUNTIME_CLASS", "INSTANT"),
            0,
            0,
            0,
            0,
            0,
            0,
            NetworkPolicy.DENIED,
        ),
    )
    bilingual = LocalizedText(en="Metrics", vi="Độ đo")
    revision = ProblemRevision(
        problem_id=ProblemId("problem-normalized"),
        revision_id=RevisionId("revision-normalized"),
        version=1,
        slug=None,
        status=EditorialStatus.DRAFT,
        content=None,
        metadata=metadata,
        response=QuizSingleResponse(
            (Choice("A", bilingual), Choice("B", bilingual)), "A"
        ),
        scoring=ScoringScheme(
            ResponseType.QUIZ_SINGLE,
            (ScoringComponent(ScoringMethod.EXACT_MATCH, Decimal("1.0")),),
        ),
    )
    with SqlAlchemyDraftUnitOfWork(session_factory) as work:
        work.drafts.create(revision, NOW)
        work.drafts.record_validation(revision.validate(Release0AvailabilityPolicy()))
    with SqlAlchemyDraftUnitOfWork(session_factory) as work:
        summary = work.drafts.list()[0].validation_summary
    assert summary is not None
    assert summary["revision_version"] == 1
    expected_counts = {
        "revision_competency": 2,
        "revision_topic": 1,
        "prerequisite_reference": 1,
        "response_configuration": 1,
        "scoring_component": 1,
    }
    with session_factory() as session:
        for table, expected in expected_counts.items():
            count = session.scalar(
                text(f"SELECT count(*) FROM {table} WHERE revision_id=:revision_id"),
                {"revision_id": "revision-normalized"},
            )
            assert count == expected

    cleared = ProblemRevision(
        problem_id=revision.problem_id,
        revision_id=revision.revision_id,
        version=1,
        slug=None,
        status=revision.status,
        content=None,
        metadata=None,
        response=None,
        scoring=None,
    )
    with SqlAlchemyDraftUnitOfWork(session_factory) as work:
        work.drafts.save(cleared, expected_version=1, saved_at=NOW)
    with SqlAlchemyDraftUnitOfWork(session_factory) as work:
        assert work.drafts.list()[0].validation_summary is None
    with session_factory() as session:
        for table in expected_counts:
            count = session.scalar(
                text(f"SELECT count(*) FROM {table} WHERE revision_id=:revision_id"),
                {"revision_id": "revision-normalized"},
            )
            assert count == 0
