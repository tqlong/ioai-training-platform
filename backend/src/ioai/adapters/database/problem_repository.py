from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from types import TracebackType
from typing import Self

from sqlalchemy import delete, or_, select, update
from sqlalchemy.orm import Session, sessionmaker

from ioai.application.problems.errors import (
    DraftNotFoundError,
    RevisionConflictError,
)
from ioai.application.problems.payload import (
    decode_revision_payload,
    encode_revision_payload,
)
from ioai.application.problems.ports import DraftRepository, DraftSummary
from ioai.domain.problems.identity import ProblemId, RevisionId, StableSlug
from ioai.domain.problems.revision import ProblemRevision, ValidationReport
from ioai.domain.problems.workflow import EditorialStatus

from .problem_model import (
    PrerequisiteReferenceModel,
    ProblemModel,
    ProblemRevisionModel,
    ResponseConfigurationModel,
    RevisionCompetencyModel,
    RevisionTopicModel,
    ScoringComponentModel,
)

StoredDraftSummary = DraftSummary


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


class SqlAlchemyDraftUnitOfWork:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None
        self._drafts: SqlAlchemyDraftRepository | None = None

    @property
    def drafts(self) -> DraftRepository:
        if self._drafts is None:
            raise RuntimeError("unit of work must be entered before repository access")
        return self._drafts

    def __enter__(self) -> Self:
        self._session = self._session_factory()
        self._drafts = SqlAlchemyDraftRepository(self._session)
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
