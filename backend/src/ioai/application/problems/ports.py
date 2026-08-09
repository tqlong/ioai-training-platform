from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from types import TracebackType
from typing import Protocol, Self

from ioai.domain.problems.identity import ProblemId, RevisionId
from ioai.domain.problems.revision import ProblemRevision, ValidationReport
from ioai.domain.problems.workflow import EditorialStatus


@dataclass(frozen=True, slots=True)
class DraftSummary:
    problem_id: ProblemId
    revision_id: RevisionId
    version: int
    status: EditorialStatus
    last_saved_at: datetime
    validation_summary: dict[str, object] | None = None


class DraftRepository(Protocol):
    def create(self, revision: ProblemRevision, created_at: datetime) -> None: ...

    def get(self, revision_id: RevisionId) -> ProblemRevision: ...

    def get_current(self, problem_id: ProblemId) -> ProblemRevision: ...

    def list(
        self, *, search: str | None = None, status: EditorialStatus | None = None
    ) -> tuple[DraftSummary, ...]: ...

    def save(
        self,
        revision: ProblemRevision,
        expected_version: int,
        saved_at: datetime,
    ) -> ProblemRevision: ...

    def record_validation(self, report: ValidationReport) -> None: ...


class DraftUnitOfWork(Protocol):
    @property
    def drafts(self) -> DraftRepository: ...

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
