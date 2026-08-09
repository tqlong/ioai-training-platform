from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256

from ioai.domain.problems.identity import ProblemId, RevisionId, StableSlug
from ioai.domain.problems.workflow import (
    ActorContext,
    transition_for_publication,
)
from ioai.domain.vocabulary.availability import Release0AvailabilityPolicy

from .errors import DraftValidationError, RevisionConflictError
from .payload import encode_revision_payload
from .ports import DraftUnitOfWork


@dataclass(frozen=True, slots=True)
class PublishedSnapshot:
    snapshot_id: str
    problem_id: ProblemId
    revision_id: RevisionId
    slug: StableSlug
    public_payload: dict[str, object]
    published_at: datetime


class PublishRevision:
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
        idempotency_key: str,
    ) -> PublishedSnapshot:
        digest = _publication_digest(
            revision_id, expected_version, note, actor, idempotency_key
        )
        with self._unit_of_work_factory() as unit_of_work:
            replay = unit_of_work.publication.replay(
                revision_id,
                idempotency_key=idempotency_key,
                request_digest=digest,
            )
            if replay is not None:
                return replay
            current = unit_of_work.drafts.get(revision_id)
            if current.version != expected_version:
                raise RevisionConflictError(revision_id, current.version)
            report = current.validate(self._policy)
            if not report.publication_eligible:
                raise DraftValidationError(report)
            if current.slug is None:
                raise DraftValidationError(report)
            occurred_at = self._clock()
            operation_id = f"publication-{sha256(digest.encode()).hexdigest()}"
            transition = transition_for_publication(
                revision_id=revision_id,
                source=current.status,
                note=note,
                actor=actor,
                occurred_at=occurred_at,
                operation_id=operation_id,
            )
            snapshot = PublishedSnapshot(
                snapshot_id=self._id_generator(),
                problem_id=current.problem_id,
                revision_id=current.revision_id,
                slug=current.slug,
                public_payload=encode_revision_payload(
                    current.content,
                    current.metadata,
                    current.response,
                    current.scoring,
                ),
                published_at=occurred_at,
            )
            return unit_of_work.publication.publish(
                snapshot=snapshot,
                transition=transition,
                expected_version=expected_version,
                transition_id=self._id_generator(),
                idempotency_key=idempotency_key,
                request_digest=digest,
            )


def _publication_digest(
    revision_id: RevisionId,
    expected_version: int,
    note: str,
    actor: ActorContext,
    idempotency_key: str,
) -> str:
    canonical = json.dumps(
        {
            "revision_id": revision_id.value,
            "expected_version": expected_version,
            "note": note.strip(),
            "actor": actor.label,
            "idempotency_key": idempotency_key,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256(canonical.encode()).hexdigest()
