from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from types import TracebackType
from typing import Self

from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.orm import Session, sessionmaker

from ioai.application.problems.assessment import AssessmentUnitOfWork
from ioai.application.problems.errors import (
    DraftNotFoundError,
    IdempotencyConflictError,
    RevisionConflictError,
    SlugConflictError,
    SuccessorRevisionError,
)
from ioai.application.problems.learner_records import (
    FeedbackCategory,
    LearnerAttempt,
    LearnerOutcome,
    ProblemFeedback,
)
from ioai.application.problems.payload import (
    decode_revision_payload,
    encode_revision_payload,
)
from ioai.application.problems.ports import (
    DraftRepository,
    DraftSummary,
    EditorialRepository,
    PublicationRepository,
)
from ioai.application.problems.public_queries import (
    PublicProblemPage,
    PublicProblemQuery,
    PublicProblemSort,
    PublishedProblemReader,
)
from ioai.application.problems.publication import ArchivedProblem, PublishedSnapshot
from ioai.domain.problems.identity import ProblemId, RevisionId, StableSlug
from ioai.domain.problems.revision import ProblemRevision, ValidationReport
from ioai.domain.problems.workflow import (
    ActorContext,
    EditorialStatus,
    EditorialTransition,
)
from ioai.domain.vocabulary.availability import Release0AvailabilityPolicy
from ioai.domain.vocabulary.values import VocabularyIdentity, VocabularyType

from .problem_model import (
    EditorialTransitionModel,
    IdempotencyRecordModel,
    LearnerAttemptModel,
    PrerequisiteReferenceModel,
    ProblemFeedbackModel,
    ProblemModel,
    ProblemRevisionModel,
    PublishedSnapshotModel,
    ResponseConfigurationModel,
    RevisionCompetencyModel,
    RevisionTopicModel,
    ScoringComponentModel,
)
from .vocabulary_model import VocabularyRecordModel

StoredDraftSummary = DraftSummary


class SqlAlchemyLearnerRecordRepository:
    """Persist bounded learner records without accepting revision identities."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add_attempt(self, attempt: LearnerAttempt) -> None:
        self._session.add(
            LearnerAttemptModel(
                attempt_id=attempt.attempt_id,
                snapshot_id=attempt.snapshot_id,
                submission_key=attempt.submission_key,
                request_digest=attempt.request_digest,
                outcome=attempt.outcome.value,
                result=attempt.result,
                submitted_at=attempt.submitted_at,
            )
        )

    def replay_attempt(
        self, snapshot_id: str, submission_key: str
    ) -> LearnerAttempt | None:
        row = self._session.scalar(
            select(LearnerAttemptModel).where(
                LearnerAttemptModel.snapshot_id == snapshot_id,
                LearnerAttemptModel.submission_key == submission_key,
            )
        )
        if row is None:
            return None
        return LearnerAttempt(
            attempt_id=row.attempt_id,
            snapshot_id=row.snapshot_id,
            submission_key=row.submission_key,
            request_digest=row.request_digest,
            outcome=LearnerOutcome(row.outcome),
            result=row.result,
            submitted_at=row.submitted_at,
        )

    def add_feedback(self, feedback: ProblemFeedback) -> None:
        self._session.add(
            ProblemFeedbackModel(
                feedback_id=feedback.feedback_id,
                snapshot_id=feedback.snapshot_id,
                feedback_key=feedback.feedback_key,
                request_digest=feedback.request_digest,
                category=feedback.category.value,
                message=feedback.message,
                submitted_at=feedback.submitted_at,
            )
        )

    def replay_feedback(
        self, snapshot_id: str, feedback_key: str
    ) -> ProblemFeedback | None:
        row = self._session.scalar(
            select(ProblemFeedbackModel).where(
                ProblemFeedbackModel.snapshot_id == snapshot_id,
                ProblemFeedbackModel.feedback_key == feedback_key,
            )
        )
        if row is None:
            return None
        return ProblemFeedback(
            feedback_id=row.feedback_id,
            snapshot_id=row.snapshot_id,
            feedback_key=row.feedback_key,
            request_digest=row.request_digest,
            category=FeedbackCategory(row.category),
            message=row.message,
            submitted_at=row.submitted_at,
        )


class SqlAlchemyAssessmentUnitOfWork(AssessmentUnitOfWork):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None
        self._published: SqlAlchemyPublishedProblemReader | None = None
        self._records: SqlAlchemyLearnerRecordRepository | None = None

    @property
    def published(self) -> PublishedProblemReader:
        if self._published is None:
            raise RuntimeError("unit of work must be entered before reader access")
        return self._published

    @property
    def records(self) -> SqlAlchemyLearnerRecordRepository:
        if self._records is None:
            raise RuntimeError("unit of work must be entered before repository access")
        return self._records

    def __enter__(self) -> Self:
        self._session = self._session_factory()
        self._published = SqlAlchemyPublishedProblemReader(self._session)
        self._records = SqlAlchemyLearnerRecordRepository(self._session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._session is None:
            return
        try:
            self._session.commit() if exc_type is None else self._session.rollback()
        finally:
            self._session.close()
            self._session = None
            self._published = None
            self._records = None


class SqlAlchemyPublishedProblemReader(PublishedProblemReader):
    """Read only current public pointers; never query revisions as candidates."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list_current(self, query: PublicProblemQuery) -> PublicProblemPage:
        statement = select(PublishedSnapshotModel).join(
            ProblemModel,
            ProblemModel.current_published_snapshot_id
            == PublishedSnapshotModel.snapshot_id,
        )
        rows = tuple(self._session.scalars(statement))
        vocabulary = tuple(
            self._session.scalars(
                select(VocabularyRecordModel).where(
                    VocabularyRecordModel.status == "ACTIVE"
                )
            )
        )
        matching = [
            row for row in rows if _matches_public_query(row, query, vocabulary)
        ]
        matching.sort(key=lambda row: _public_sort_key(row, query.sort))
        page_rows = matching[query.offset : query.offset + query.page_size]
        return PublicProblemPage(
            snapshots=tuple(_snapshot_domain(row) for row in page_rows),
            total=len(matching),
        )

    def get_current_by_slug(self, slug: str) -> PublishedSnapshot | None:
        row = self._session.scalar(
            select(PublishedSnapshotModel)
            .join(
                ProblemModel,
                ProblemModel.current_published_snapshot_id
                == PublishedSnapshotModel.snapshot_id,
            )
            .where(PublishedSnapshotModel.slug == slug)
        )
        return _snapshot_domain(row) if row is not None else None

    def recommendation_candidates(self, stage: str) -> tuple[PublishedSnapshot, ...]:
        return self.list_current(
            PublicProblemQuery(
                stage=stage,
                sort=PublicProblemSort.EDITORIAL,
                page_size=100,
            )
        ).snapshots


def _matches_public_query(
    row: PublishedSnapshotModel,
    query: PublicProblemQuery,
    vocabulary: tuple[VocabularyRecordModel, ...],
) -> bool:
    payload = row.public_payload
    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        return not any(
            (
                query.stage,
                query.competency,
                query.topic,
                query.difficulty,
                query.task_type,
                query.expected_minutes_min,
                query.expected_minutes_max,
                query.compute_tier,
                query.search,
            )
        )
    if not _is_release_eligible(metadata):
        return False
    scalar_filters = (
        (query.stage, _identity_code(metadata.get("stage"))),
        (query.competency, _identity_code(metadata.get("primary_competency"))),
        (query.difficulty, _identity_code(metadata.get("difficulty"))),
        (query.task_type, _identity_code(metadata.get("task_type"))),
        (query.compute_tier, _compute_tier_code(metadata)),
    )
    if any(
        expected is not None and expected != actual
        for expected, actual in scalar_filters
    ):
        return False
    minutes = metadata.get("expected_minutes")
    if not isinstance(minutes, int):
        return False
    if query.expected_minutes_min is not None and minutes < query.expected_minutes_min:
        return False
    if query.expected_minutes_max is not None and minutes > query.expected_minutes_max:
        return False
    if query.topic is not None:
        selected_topics = set(_identity_codes(metadata.get("topics")))
        accepted_topics = {query.topic}
        if query.include_subtopics:
            accepted_topics.update(_topic_descendants(query.topic, vocabulary))
        if selected_topics.isdisjoint(accepted_topics):
            return False
    if query.search is not None and not _matches_search(
        payload, query.search, vocabulary
    ):
        return False
    return True


def _is_release_eligible(metadata: dict[str, object]) -> bool:
    policy = Release0AvailabilityPolicy()
    selected = (
        ("PATHWAY_STAGE", _identity_code(metadata.get("stage"))),
        ("TASK_TYPE", _identity_code(metadata.get("task_type"))),
        ("COMPUTE_TIER", _compute_tier_code(metadata)),
    )
    return all(
        code is not None
        and policy.evaluate(
            VocabularyIdentity(VocabularyType(vocabulary_type), code)
        ).is_available
        for vocabulary_type, code in selected
    )


def _identity_code(value: object) -> str | None:
    if isinstance(value, list) and len(value) == 2 and isinstance(value[1], str):
        return value[1]
    return None


def _identity_codes(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(code for item in value if (code := _identity_code(item)) is not None)


def _compute_tier_code(metadata: dict[str, object]) -> str | None:
    resources = metadata.get("resources")
    if not isinstance(resources, dict):
        return None
    return _identity_code(resources.get("compute_tier"))


def _topic_descendants(
    parent_code: str, vocabulary: tuple[VocabularyRecordModel, ...]
) -> set[str]:
    children: dict[str, set[str]] = {}
    for record in vocabulary:
        if record.vocabulary_type == "TOPIC" and record.parent_code is not None:
            children.setdefault(record.parent_code, set()).add(record.code)
    descendants: set[str] = set()
    pending = list(children.get(parent_code, ()))
    while pending:
        code = pending.pop()
        if code in descendants:
            continue
        descendants.add(code)
        pending.extend(children.get(code, ()))
    return descendants


def _matches_search(
    payload: dict[str, object],
    search: str,
    vocabulary: tuple[VocabularyRecordModel, ...],
) -> bool:
    needle = search.casefold()
    content = payload.get("content")
    if any(needle in text.casefold() for text in _public_strings(content)):
        return True
    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        return False
    referenced_codes = {
        code
        for code in (
            _identity_code(metadata.get("primary_competency")),
            *_identity_codes(metadata.get("secondary_competencies")),
            *_identity_codes(metadata.get("topics")),
        )
        if code is not None
    }
    return any(
        record.code in referenced_codes
        and any(
            needle in candidate.casefold()
            for candidate in (record.label_en, record.label_vi, *record.aliases)
        )
        for record in vocabulary
    )


def _public_strings(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, dict):
        return tuple(
            text
            for key, item in value.items()
            if not str(key).endswith("_state")
            for text in _public_strings(item)
        )
    if isinstance(value, list):
        return tuple(text for item in value for text in _public_strings(item))
    return ()


def _public_sort_key(
    row: PublishedSnapshotModel, sort: PublicProblemSort
) -> tuple[object, ...]:
    payload = row.public_payload
    content = payload.get("content")
    metadata = payload.get("metadata")
    content_map = content if isinstance(content, dict) else {}
    metadata_map = metadata if isinstance(metadata, dict) else {}
    title = content_map.get("title")
    title_map = title if isinstance(title, dict) else {}
    title_en = str(title_map.get("en", "")).casefold()
    minutes = metadata_map.get("expected_minutes")
    expected_minutes = minutes if isinstance(minutes, int) else 2**31
    if sort is PublicProblemSort.NEWEST:
        return (-row.published_at.timestamp(), row.problem_id)
    if sort is PublicProblemSort.EXPECTED_TIME:
        return (expected_minutes, row.problem_id)
    if sort is PublicProblemSort.TITLE:
        return (title_en, row.problem_id)
    editorial_order = metadata_map.get("editorial_order")
    normalized_order = editorial_order if isinstance(editorial_order, int) else 2**31
    difficulty = _identity_code(metadata_map.get("difficulty")) or ""
    difficulty_rank = Release0AvailabilityPolicy().difficulty_rank(difficulty)
    return (normalized_order, difficulty_rank, row.problem_id)


class SqlAlchemyDraftRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, revision: ProblemRevision, created_at: datetime) -> None:
        self._session.add(
            ProblemModel(
                problem_id=revision.problem_id.value,
                slug=revision.slug.value if revision.slug else None,
                created_at=created_at,
            )
        )
        self._session.add(_revision_model(revision, created_at, created_at))
        _replace_associations(self._session, revision)

    def get(self, revision_id: RevisionId) -> ProblemRevision:
        row = self._session.get(ProblemRevisionModel, revision_id.value)
        if row is None:
            raise DraftNotFoundError(revision_id)
        problem = self._session.get(ProblemModel, row.problem_id)
        if problem is None:
            raise DraftNotFoundError(revision_id)
        return _revision_domain(problem, row)

    def get_current(self, problem_id: ProblemId) -> ProblemRevision:
        statement = (
            select(ProblemRevisionModel)
            .where(ProblemRevisionModel.problem_id == problem_id.value)
            .order_by(ProblemRevisionModel.revision_number.desc())
            .limit(1)
        )
        row = self._session.scalar(statement)
        if row is None:
            raise DraftNotFoundError(RevisionId(problem_id.value))
        problem = self._session.get(ProblemModel, problem_id.value)
        if problem is None:
            raise DraftNotFoundError(RevisionId(problem_id.value))
        return _revision_domain(problem, row)

    def list(
        self, *, search: str | None = None, status: EditorialStatus | None = None
    ) -> tuple[DraftSummary, ...]:
        statement = select(ProblemRevisionModel)
        if search:
            pattern = f"%{search.strip()}%"
            statement = statement.where(
                or_(
                    ProblemRevisionModel.problem_id.ilike(pattern),
                    ProblemRevisionModel.revision_id.ilike(pattern),
                )
            )
        if status is not None:
            statement = statement.where(
                ProblemRevisionModel.editorial_status == status.value
            )
        statement = statement.order_by(
            ProblemRevisionModel.updated_at.desc(),
            ProblemRevisionModel.revision_id,
        )
        return tuple(
            DraftSummary(
                problem_id=ProblemId(row.problem_id),
                revision_id=RevisionId(row.revision_id),
                version=row.lock_version,
                status=EditorialStatus(row.editorial_status),
                last_saved_at=row.updated_at,
                validation_summary=row.validation_summary,
            )
            for row in self._session.scalars(statement)
        )

    def save(
        self,
        revision: ProblemRevision,
        expected_version: int,
        saved_at: datetime,
    ) -> ProblemRevision:
        next_version = expected_version + 1
        payload = encode_revision_payload(
            revision.content,
            revision.metadata,
            revision.response,
            revision.scoring,
        )
        statement = (
            update(ProblemRevisionModel)
            .where(
                ProblemRevisionModel.revision_id == revision.revision_id.value,
                ProblemRevisionModel.lock_version == expected_version,
            )
            .values(
                lock_version=next_version,
                editorial_status=revision.status.value,
                content=payload,
                validation_summary=None,
                updated_at=saved_at,
            )
            .returning(ProblemRevisionModel.revision_id)
        )
        result = self._session.execute(statement)
        if result.scalar_one_or_none() is None:
            current = self._session.get(
                ProblemRevisionModel, revision.revision_id.value
            )
            if current is None:
                raise DraftNotFoundError(revision.revision_id)
            raise RevisionConflictError(revision.revision_id, current.lock_version)
        problem = self._session.get(ProblemModel, revision.problem_id.value)
        if problem is None:
            raise DraftNotFoundError(revision.revision_id)
        problem.slug = revision.slug.value if revision.slug else None
        _replace_associations(self._session, revision)
        return replace(revision, version=next_version)

    def record_validation(self, report: ValidationReport) -> None:
        row = self._session.get(ProblemRevisionModel, report.revision_id.value)
        if row is None:
            raise DraftNotFoundError(report.revision_id)
        row.validation_summary = {
            "revision_version": report.revision_version,
            "error_count": len(report.errors),
            "warning_count": len(report.warnings),
            "publication_eligible": report.publication_eligible,
        }


class SqlAlchemyEditorialRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_history(self, revision_id: RevisionId) -> tuple[EditorialTransition, ...]:
        rows = self._session.scalars(
            select(EditorialTransitionModel)
            .where(EditorialTransitionModel.revision_id == revision_id.value)
            .order_by(
                EditorialTransitionModel.occurred_at,
                EditorialTransitionModel.transition_id,
            )
        )
        return tuple(
            EditorialTransition(
                revision_id=revision_id,
                source=EditorialStatus(row.source_status),
                target=EditorialStatus(row.target_status),
                note=row.note,
                actor=ActorContext(row.actor_context),
                occurred_at=row.occurred_at,
                operation_id=row.operation_id,
            )
            for row in rows
        )

    def transition(
        self,
        transition: EditorialTransition,
        *,
        expected_version: int,
        transition_id: str,
    ) -> ProblemRevision:
        statement = (
            update(ProblemRevisionModel)
            .where(
                ProblemRevisionModel.revision_id == transition.revision_id.value,
                ProblemRevisionModel.lock_version == expected_version,
                ProblemRevisionModel.editorial_status == transition.source.value,
            )
            .values(
                lock_version=expected_version + 1,
                editorial_status=transition.target.value,
                validation_summary=None,
                updated_at=transition.occurred_at,
            )
            .returning(ProblemRevisionModel.problem_id)
        )
        problem_id = self._session.execute(statement).scalar_one_or_none()
        if problem_id is None:
            current = self._session.get(
                ProblemRevisionModel, transition.revision_id.value
            )
            if current is None:
                raise DraftNotFoundError(transition.revision_id)
            raise RevisionConflictError(transition.revision_id, current.lock_version)
        self._session.add(
            EditorialTransitionModel(
                transition_id=transition_id,
                revision_id=transition.revision_id.value,
                source_status=transition.source.value,
                target_status=transition.target.value,
                note=transition.note,
                actor_context=transition.actor.label,
                occurred_at=transition.occurred_at,
                operation_id=transition.operation_id,
            )
        )
        problem = self._session.get(ProblemModel, problem_id)
        row = self._session.get(ProblemRevisionModel, transition.revision_id.value)
        if problem is None or row is None:
            raise DraftNotFoundError(transition.revision_id)
        return _revision_domain(problem, row)

    def create_successor(
        self,
        source: ProblemRevision,
        successor: ProblemRevision,
        *,
        operation_id: str,
        request_digest: str,
        created_at: datetime,
    ) -> ProblemRevision:
        existing_operation = self._session.scalar(
            select(IdempotencyRecordModel).where(
                IdempotencyRecordModel.operation_type == "CREATE_SUCCESSOR",
                IdempotencyRecordModel.target_id == source.revision_id.value,
                IdempotencyRecordModel.idempotency_key == operation_id,
            )
        )
        if existing_operation is not None:
            if existing_operation.request_digest != request_digest:
                raise IdempotencyConflictError(
                    "successor operation key was reused for different intent"
                )
            existing = self._session.get(
                ProblemRevisionModel, existing_operation.result_reference
            )
            problem = self._session.get(ProblemModel, source.problem_id.value)
            if existing is None or problem is None:
                raise DraftNotFoundError(
                    RevisionId(existing_operation.result_reference)
                )
            return _revision_domain(problem, existing)

        persisted_source = self._session.get(
            ProblemRevisionModel, source.revision_id.value
        )
        if (
            persisted_source is None
            or persisted_source.editorial_status
            not in {
                EditorialStatus.CHANGES_REQUESTED.value,
                EditorialStatus.PUBLISHED.value,
                EditorialStatus.ARCHIVED.value,
            }
            or persisted_source.lock_version != source.version
        ):
            if persisted_source is None:
                raise DraftNotFoundError(source.revision_id)
            raise RevisionConflictError(
                source.revision_id, persisted_source.lock_version
            )
        existing_draft = self._session.scalar(
            select(ProblemRevisionModel).where(
                ProblemRevisionModel.problem_id == source.problem_id.value,
                ProblemRevisionModel.editorial_status == EditorialStatus.DRAFT.value,
            )
        )
        if existing_draft is not None:
            raise SuccessorRevisionError(
                "this problem already has an editable draft revision"
            )
        next_number = self._session.scalar(
            select(func.max(ProblemRevisionModel.revision_number)).where(
                ProblemRevisionModel.problem_id == source.problem_id.value
            )
        )
        row = _revision_model(successor, created_at, created_at)
        row.revision_number = (next_number or 0) + 1
        self._session.add(row)
        _replace_associations(self._session, successor)
        self._session.add(
            IdempotencyRecordModel(
                operation_type="CREATE_SUCCESSOR",
                target_id=source.revision_id.value,
                idempotency_key=operation_id,
                request_digest=request_digest,
                result_reference=successor.revision_id.value,
                created_at=created_at,
            )
        )
        return successor


class SqlAlchemyPublicationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def current_snapshot(self, problem_id: ProblemId) -> PublishedSnapshot | None:
        problem = self._session.get(ProblemModel, problem_id.value)
        if problem is None or problem.current_published_snapshot_id is None:
            return None
        row = self._session.get(
            PublishedSnapshotModel, problem.current_published_snapshot_id
        )
        return _snapshot_domain(row) if row is not None else None

    def replay(
        self,
        revision_id: RevisionId,
        *,
        idempotency_key: str,
        request_digest: str,
    ) -> PublishedSnapshot | None:
        record = self._session.scalar(
            select(IdempotencyRecordModel).where(
                IdempotencyRecordModel.operation_type == "PUBLISH",
                IdempotencyRecordModel.target_id == revision_id.value,
                IdempotencyRecordModel.idempotency_key == idempotency_key,
            )
        )
        if record is None:
            return None
        if record.request_digest != request_digest:
            raise IdempotencyConflictError(
                "publication key was reused for different intent"
            )
        row = self._session.get(PublishedSnapshotModel, record.result_reference)
        if row is None:
            raise RuntimeError("publication idempotency result is missing")
        return _snapshot_domain(row)

    def publish(
        self,
        *,
        snapshot: PublishedSnapshot,
        transition: EditorialTransition,
        expected_version: int,
        transition_id: str,
        idempotency_key: str,
        request_digest: str,
    ) -> PublishedSnapshot:
        revision = self._session.scalar(
            select(ProblemRevisionModel)
            .where(ProblemRevisionModel.revision_id == transition.revision_id.value)
            .with_for_update()
        )
        if revision is None:
            raise DraftNotFoundError(transition.revision_id)
        replay = self.replay(
            transition.revision_id,
            idempotency_key=idempotency_key,
            request_digest=request_digest,
        )
        if replay is not None:
            return replay
        if (
            revision.lock_version != expected_version
            or revision.editorial_status != EditorialStatus.APPROVED.value
        ):
            raise RevisionConflictError(transition.revision_id, revision.lock_version)
        problem = self._session.scalar(
            select(ProblemModel)
            .where(ProblemModel.problem_id == snapshot.problem_id.value)
            .with_for_update()
        )
        if problem is None:
            raise DraftNotFoundError(transition.revision_id)
        slug_owner = self._session.scalar(
            select(ProblemModel).where(
                ProblemModel.slug == snapshot.slug.value,
                ProblemModel.problem_id != snapshot.problem_id.value,
            )
        )
        if slug_owner is not None:
            raise SlugConflictError("the stable slug belongs to another problem")
        row = PublishedSnapshotModel(
            snapshot_id=snapshot.snapshot_id,
            problem_id=snapshot.problem_id.value,
            revision_id=snapshot.revision_id.value,
            slug=snapshot.slug.value,
            public_payload=snapshot.public_payload,
            published_at=snapshot.published_at,
        )
        self._session.add(row)
        self._session.flush([row])
        self._session.add(
            EditorialTransitionModel(
                transition_id=transition_id,
                revision_id=transition.revision_id.value,
                source_status=transition.source.value,
                target_status=transition.target.value,
                note=transition.note,
                actor_context=transition.actor.label,
                occurred_at=transition.occurred_at,
                operation_id=transition.operation_id,
            )
        )
        revision.editorial_status = EditorialStatus.PUBLISHED.value
        revision.lock_version = expected_version + 1
        revision.updated_at = transition.occurred_at
        problem.current_published_snapshot_id = snapshot.snapshot_id
        self._session.add(
            IdempotencyRecordModel(
                operation_type="PUBLISH",
                target_id=transition.revision_id.value,
                idempotency_key=idempotency_key,
                request_digest=request_digest,
                result_reference=snapshot.snapshot_id,
                created_at=transition.occurred_at,
            )
        )
        return snapshot

    def archive(
        self,
        *,
        problem_id: ProblemId,
        expected_version: int,
        transition: EditorialTransition,
        transition_id: str,
    ) -> ArchivedProblem:
        problem = self._session.scalar(
            select(ProblemModel)
            .where(ProblemModel.problem_id == problem_id.value)
            .with_for_update()
        )
        if problem is None or problem.current_published_snapshot_id is None:
            raise DraftNotFoundError(transition.revision_id)
        snapshot = self._session.get(
            PublishedSnapshotModel, problem.current_published_snapshot_id
        )
        revision = self._session.scalar(
            select(ProblemRevisionModel)
            .where(ProblemRevisionModel.revision_id == transition.revision_id.value)
            .with_for_update()
        )
        if snapshot is None or revision is None:
            raise DraftNotFoundError(transition.revision_id)
        if (
            snapshot.revision_id != revision.revision_id
            or revision.lock_version != expected_version
            or revision.editorial_status != EditorialStatus.PUBLISHED.value
        ):
            raise RevisionConflictError(transition.revision_id, revision.lock_version)
        self._session.add(
            EditorialTransitionModel(
                transition_id=transition_id,
                revision_id=transition.revision_id.value,
                source_status=transition.source.value,
                target_status=transition.target.value,
                note=transition.note,
                actor_context=transition.actor.label,
                occurred_at=transition.occurred_at,
                operation_id=transition.operation_id,
            )
        )
        revision.editorial_status = EditorialStatus.ARCHIVED.value
        revision.lock_version = expected_version + 1
        revision.updated_at = transition.occurred_at
        problem.current_published_snapshot_id = None
        return ArchivedProblem(
            problem_id, StableSlug(snapshot.slug), transition.occurred_at
        )


class SqlAlchemyDraftUnitOfWork:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None
        self._drafts: SqlAlchemyDraftRepository | None = None
        self._editorial: SqlAlchemyEditorialRepository | None = None
        self._publication: SqlAlchemyPublicationRepository | None = None

    @property
    def drafts(self) -> DraftRepository:
        if self._drafts is None:
            raise RuntimeError("unit of work must be entered before repository access")
        return self._drafts

    @property
    def editorial(self) -> EditorialRepository:
        if self._editorial is None:
            raise RuntimeError("unit of work must be entered before repository access")
        return self._editorial

    @property
    def publication(self) -> PublicationRepository:
        if self._publication is None:
            raise RuntimeError("unit of work must be entered before repository access")
        return self._publication

    def __enter__(self) -> Self:
        self._session = self._session_factory()
        self._drafts = SqlAlchemyDraftRepository(self._session)
        self._editorial = SqlAlchemyEditorialRepository(self._session)
        self._publication = SqlAlchemyPublicationRepository(self._session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._session is None:
            return
        try:
            if exc_type is None:
                self._session.commit()
            else:
                self._session.rollback()
        finally:
            self._session.close()
            self._session = None
            self._drafts = None
            self._editorial = None
            self._publication = None


def _revision_model(
    revision: ProblemRevision, created_at: datetime, updated_at: datetime
) -> ProblemRevisionModel:
    return ProblemRevisionModel(
        revision_id=revision.revision_id.value,
        problem_id=revision.problem_id.value,
        revision_number=1,
        lock_version=revision.version,
        editorial_status=revision.status.value,
        content=encode_revision_payload(
            revision.content,
            revision.metadata,
            revision.response,
            revision.scoring,
        ),
        validation_summary=None,
        created_at=created_at,
        updated_at=updated_at,
    )


def _revision_domain(
    problem: ProblemModel, row: ProblemRevisionModel
) -> ProblemRevision:
    content, metadata, response, scoring = decode_revision_payload(row.content)
    return ProblemRevision(
        problem_id=ProblemId(problem.problem_id),
        revision_id=RevisionId(row.revision_id),
        version=row.lock_version,
        slug=StableSlug(problem.slug) if problem.slug else None,
        status=EditorialStatus(row.editorial_status),
        content=content,
        metadata=metadata,
        response=response,
        scoring=scoring,
    )


def _snapshot_domain(row: PublishedSnapshotModel) -> PublishedSnapshot:
    return PublishedSnapshot(
        snapshot_id=row.snapshot_id,
        problem_id=ProblemId(row.problem_id),
        revision_id=RevisionId(row.revision_id),
        slug=StableSlug(row.slug),
        public_payload=row.public_payload,
        published_at=row.published_at,
    )


def _replace_associations(session: Session, revision: ProblemRevision) -> None:
    revision_id = revision.revision_id.value
    for model in (
        ScoringComponentModel,
        ResponseConfigurationModel,
        PrerequisiteReferenceModel,
        RevisionTopicModel,
        RevisionCompetencyModel,
    ):
        session.execute(delete(model).where(model.revision_id == revision_id))

    metadata = revision.metadata
    if metadata is not None:
        competencies = (
            (metadata.primary_competency, "PRIMARY", 0),
            *(
                (identity, "SECONDARY", position)
                for position, identity in enumerate(
                    metadata.secondary_competencies, start=1
                )
            ),
        )
        session.add_all(
            RevisionCompetencyModel(
                revision_id=revision_id,
                vocabulary_type=identity.vocabulary_type.value,
                code=identity.code,
                role=role,
                position=position,
            )
            for identity, role, position in competencies
        )
        session.add_all(
            RevisionTopicModel(
                revision_id=revision_id,
                vocabulary_type=identity.vocabulary_type.value,
                code=identity.code,
                position=position,
            )
            for position, identity in enumerate(metadata.topics)
        )
        session.add_all(
            PrerequisiteReferenceModel(
                revision_id=revision_id,
                relationship=item.relationship.value,
                target_type=item.target_type.value,
                target_id=(
                    item.target_identity.code
                    if item.target_identity is not None
                    else item.target_id
                ),
                minimum_evidence=(
                    item.minimum_evidence.value if item.minimum_evidence else None
                ),
            )
            for item in metadata.prerequisites
        )

    if revision.response is not None:
        response_payload = encode_revision_payload(None, None, revision.response, None)[
            "response"
        ]
        if response_payload is None:
            raise RuntimeError("response encoding unexpectedly returned no payload")
        session.add(
            ResponseConfigurationModel(
                revision_id=revision_id,
                task_type=revision.response.response_type.value,
                configuration=response_payload,
            )
        )
    if revision.scoring is not None:
        session.add_all(
            ScoringComponentModel(
                revision_id=revision_id,
                method=item.method.value,
                weight=item.weight,
                position=position,
                configuration=item.configuration,
            )
            for position, item in enumerate(revision.scoring.components)
        )
