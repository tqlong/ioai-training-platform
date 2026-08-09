from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from datetime import datetime
from hashlib import sha256

from ioai.domain.problems.identity import RevisionId
from ioai.domain.problems.revision import ProblemRevision
from ioai.domain.problems.workflow import (
    ActorContext,
    EditorialStatus,
    transition_for_review,
)
from ioai.domain.vocabulary.availability import Release0AvailabilityPolicy

from .errors import DraftValidationError, RevisionConflictError, SuccessorRevisionError
from .ports import DraftUnitOfWork


class _ReviewCommand:
    source: EditorialStatus
    target: EditorialStatus
    requires_validation: bool

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], DraftUnitOfWork],
        policy: Release0AvailabilityPolicy,
        id_generator: Callable[[], str],
        clock: Callable[[], datetime],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._policy = policy
        self._id_generator = id_generator
        self._clock = clock

    def __call__(
        self,
        revision_id: RevisionId,
        *,
        expected_version: int,
        note: str,
        actor: ActorContext,
        operation_id: str,
    ) -> ProblemRevision:
        with self._unit_of_work_factory() as unit_of_work:
            current = unit_of_work.drafts.get(revision_id)
            if current.version != expected_version:
                raise RevisionConflictError(revision_id, current.version)
            transition = transition_for_review(
                revision_id=revision_id,
                source=current.status,
                target=self.target,
                note=note,
                actor=actor,
                occurred_at=self._clock(),
                operation_id=operation_id,
            )
            if self.requires_validation:
                report = current.validate(self._policy)
                if not report.publication_eligible:
                    raise DraftValidationError(report)
            return unit_of_work.editorial.transition(
                transition,
                expected_version=expected_version,
                transition_id=self._id_generator(),
            )


class SubmitForReview(_ReviewCommand):
    source = EditorialStatus.DRAFT
    target = EditorialStatus.IN_REVIEW
    requires_validation = True


class RequestChanges(_ReviewCommand):
    source = EditorialStatus.IN_REVIEW
    target = EditorialStatus.CHANGES_REQUESTED
    requires_validation = False


class ApproveRevision(_ReviewCommand):
    source = EditorialStatus.IN_REVIEW
    target = EditorialStatus.APPROVED
    requires_validation = True


class StartSuccessorDraft:
    """Create editable work while preserving the reviewed source revision."""

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

    def __call__(
        self,
        source_revision_id: RevisionId,
        *,
        expected_version: int,
        operation_id: str,
    ) -> ProblemRevision:
        with self._unit_of_work_factory() as unit_of_work:
            source = unit_of_work.drafts.get(source_revision_id)
            if source.version != expected_version:
                raise RevisionConflictError(source_revision_id, source.version)
            if source.status not in {
                EditorialStatus.CHANGES_REQUESTED,
                EditorialStatus.PUBLISHED,
            }:
                raise SuccessorRevisionError(
                    "only published or changes-requested work can start a successor"
                )
            successor = replace(
                source,
                revision_id=RevisionId(self._id_generator()),
                version=1,
                status=EditorialStatus.DRAFT,
            )
            digest = sha256(
                f"successor:{source.revision_id.value}".encode()
            ).hexdigest()
            return unit_of_work.editorial.create_successor(
                source,
                successor,
                operation_id=operation_id,
                request_digest=digest,
                created_at=self._clock(),
            )


class ListEditorialHistory:
    def __init__(self, unit_of_work_factory: Callable[[], DraftUnitOfWork]) -> None:
        self._unit_of_work_factory = unit_of_work_factory

    def __call__(self, revision_id: RevisionId):
        with self._unit_of_work_factory() as unit_of_work:
            unit_of_work.drafts.get(revision_id)
            return unit_of_work.editorial.list_history(revision_id)
