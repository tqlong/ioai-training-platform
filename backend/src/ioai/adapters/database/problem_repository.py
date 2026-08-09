from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from types import TracebackType
from typing import Self

from sqlalchemy import select, update
from sqlalchemy.orm import Session, sessionmaker

from ioai.application.problems.errors import (
    DraftNotFoundError,
    RevisionConflictError,
)
from ioai.domain.problems.identity import ProblemId, RevisionId, StableSlug
from ioai.domain.problems.revision import ProblemRevision
from ioai.domain.problems.workflow import EditorialStatus

from .problem_codec import decode_revision_payload, encode_revision_payload
from .problem_model import ProblemModel, ProblemRevisionModel


@dataclass(frozen=True, slots=True)
class StoredDraftSummary:
    problem_id: ProblemId
    revision_id: RevisionId
    version: int
    status: EditorialStatus
    last_saved_at: datetime


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

    def get(self, revision_id: RevisionId) -> ProblemRevision:
        row = self._session.get(ProblemRevisionModel, revision_id.value)
        if row is None:
            raise DraftNotFoundError(revision_id)
        problem = self._session.get(ProblemModel, row.problem_id)
        if problem is None:
            raise DraftNotFoundError(revision_id)
        return _revision_domain(problem, row)

    def list(self) -> tuple[StoredDraftSummary, ...]:
        statement = select(ProblemRevisionModel).order_by(
            ProblemRevisionModel.updated_at.desc(),
            ProblemRevisionModel.revision_id,
        )
        return tuple(
            StoredDraftSummary(
                problem_id=ProblemId(row.problem_id),
                revision_id=RevisionId(row.revision_id),
                version=row.lock_version,
                status=EditorialStatus(row.editorial_status),
                last_saved_at=row.updated_at,
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
        return replace(revision, version=next_version)


class SqlAlchemyDraftUnitOfWork:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None
        self._drafts: SqlAlchemyDraftRepository | None = None

    @property
    def drafts(self) -> SqlAlchemyDraftRepository:
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
