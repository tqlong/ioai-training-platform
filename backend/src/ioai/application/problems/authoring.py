from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from ioai.domain.problems.identity import ProblemId, RevisionId
from ioai.domain.problems.revision import ProblemRevision, ValidationReport
from ioai.domain.problems.workflow import EditorialStatus
from ioai.domain.vocabulary.availability import Release0AvailabilityPolicy

from .ports import DraftUnitOfWork


@dataclass(frozen=True, slots=True)
class AuthorDraftListItem:
    problem_id: ProblemId
    revision_id: RevisionId
    version: int
    status: EditorialStatus
    last_saved_at: datetime


class CreateDraft:
    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], DraftUnitOfWork],
        id_generator: Callable[[], str],
        clock: Callable[[], datetime],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._id_generator = id_generator
        self._clock = clock

    def __call__(self) -> ProblemRevision:
        revision = ProblemRevision(
            problem_id=ProblemId(self._id_generator()),
            revision_id=RevisionId(self._id_generator()),
            version=1,
            slug=None,
            status=EditorialStatus.DRAFT,
            content=None,
            metadata=None,
            response=None,
            scoring=None,
        )
        with self._unit_of_work_factory() as unit_of_work:
            unit_of_work.drafts.create(revision, self._clock())
        return revision


class ListDrafts:
    def __init__(self, unit_of_work_factory: Callable[[], DraftUnitOfWork]) -> None:
        self._unit_of_work_factory = unit_of_work_factory

    def __call__(self) -> tuple[AuthorDraftListItem, ...]:
        with self._unit_of_work_factory() as unit_of_work:
            items = unit_of_work.drafts.list()
        return tuple(
            AuthorDraftListItem(
                problem_id=item.problem_id,
                revision_id=item.revision_id,
                version=item.version,
                status=item.status,
                last_saved_at=item.last_saved_at,
            )
            for item in items
        )


class GetDraft:
    def __init__(self, unit_of_work_factory: Callable[[], DraftUnitOfWork]) -> None:
        self._unit_of_work_factory = unit_of_work_factory

    def __call__(self, problem_id: ProblemId) -> ProblemRevision:
        with self._unit_of_work_factory() as unit_of_work:
            return unit_of_work.drafts.get_current(problem_id)


class GetRevisionDraft:
    def __init__(self, unit_of_work_factory: Callable[[], DraftUnitOfWork]) -> None:
        self._unit_of_work_factory = unit_of_work_factory

    def __call__(self, revision_id: RevisionId) -> ProblemRevision:
        with self._unit_of_work_factory() as unit_of_work:
            return unit_of_work.drafts.get(revision_id)


class SaveDraft:
    def __init__(
        self,
        unit_of_work_factory: Callable[[], DraftUnitOfWork],
        clock: Callable[[], datetime],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._clock = clock

    def __call__(
        self, revision: ProblemRevision, *, expected_version: int
    ) -> ProblemRevision:
        with self._unit_of_work_factory() as unit_of_work:
            return unit_of_work.drafts.save(
                revision,
                expected_version=expected_version,
                saved_at=self._clock(),
            )


class ValidateDraft:
    def __init__(
        self,
        unit_of_work_factory: Callable[[], DraftUnitOfWork],
        policy: Release0AvailabilityPolicy,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._policy = policy

    def __call__(
        self, revision_id: RevisionId, *, expected_version: int
    ) -> ValidationReport:
        with self._unit_of_work_factory() as unit_of_work:
            revision = unit_of_work.drafts.get(revision_id)
        if revision.version != expected_version:
            from .errors import RevisionConflictError

            raise RevisionConflictError(revision_id, revision.version)
        return revision.validate(self._policy)
