from __future__ import annotations

from datetime import datetime
from types import TracebackType
from typing import Protocol, Self

from ioai.domain.problems.identity import ProblemId, RevisionId
from ioai.domain.problems.revision import ProblemRevision
from ioai.domain.problems.workflow import EditorialStatus


class DraftSummary(Protocol):
    problem_id: ProblemId
    revision_id: RevisionId
    version: int
    status: EditorialStatus
    last_saved_at: datetime


class DraftRepository(Protocol):
    def create(self, revision: ProblemRevision, created_at: datetime) -> None: ...

    def get(self, revision_id: RevisionId) -> ProblemRevision: ...

    def list(self) -> tuple[DraftSummary, ...]: ...

    def save(
        self,
        revision: ProblemRevision,
        expected_version: int,
        saved_at: datetime,
    ) -> ProblemRevision: ...


class DraftUnitOfWork(Protocol):
    drafts: DraftRepository

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...


class PublishedRevisionSource(Protocol):
    """Phase 7 boundary for starting an edit without mutating a live snapshot."""

    def revision_base(self, problem_id: ProblemId) -> ProblemRevision: ...
