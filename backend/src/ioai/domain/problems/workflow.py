from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .errors import InvalidEditorialTransitionError, InvalidTransitionNoteError
from .identity import RevisionId

MAX_TRANSITION_NOTE_LENGTH = 2000
MAX_ACTOR_LABEL_LENGTH = 200
MAX_OPERATION_ID_LENGTH = 200


class EditorialStatus(StrEnum):
    DRAFT = "DRAFT"
    IN_REVIEW = "IN_REVIEW"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    APPROVED = "APPROVED"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


@dataclass(frozen=True, slots=True)
class ActorContext:
    """Best available local audit label; it is not an authentication claim."""

    label: str

    def __post_init__(self) -> None:
        normalized = self.label.strip()
        if not normalized or len(normalized) > MAX_ACTOR_LABEL_LENGTH:
            raise InvalidEditorialTransitionError(
                "actor context must be present and at most "
                f"{MAX_ACTOR_LABEL_LENGTH} characters"
            )
        object.__setattr__(self, "label", normalized)


@dataclass(frozen=True, slots=True)
class EditorialTransition:
    revision_id: RevisionId
    source: EditorialStatus
    target: EditorialStatus
    note: str
    actor: ActorContext
    occurred_at: datetime
    operation_id: str


_REVIEW_TRANSITIONS = frozenset(
    {
        (EditorialStatus.DRAFT, EditorialStatus.IN_REVIEW),
        (EditorialStatus.IN_REVIEW, EditorialStatus.CHANGES_REQUESTED),
        (EditorialStatus.IN_REVIEW, EditorialStatus.APPROVED),
    }
)


def transition_for_review(
    *,
    revision_id: RevisionId,
    source: EditorialStatus,
    target: EditorialStatus,
    note: str,
    actor: ActorContext,
    occurred_at: datetime,
    operation_id: str,
) -> EditorialTransition:
    if (source, target) not in _REVIEW_TRANSITIONS:
        raise InvalidEditorialTransitionError(
            f"editorial transition {source.value} -> {target.value} is not allowed"
        )
    return _transition(
        revision_id=revision_id,
        source=source,
        target=target,
        note=note,
        actor=actor,
        occurred_at=occurred_at,
        operation_id=operation_id,
    )


def transition_for_publication(
    *,
    revision_id: RevisionId,
    source: EditorialStatus,
    note: str,
    actor: ActorContext,
    occurred_at: datetime,
    operation_id: str,
) -> EditorialTransition:
    if source is not EditorialStatus.APPROVED:
        raise InvalidEditorialTransitionError(
            f"editorial transition {source.value} -> PUBLISHED is not allowed"
        )
    return _transition(
        revision_id=revision_id,
        source=source,
        target=EditorialStatus.PUBLISHED,
        note=note,
        actor=actor,
        occurred_at=occurred_at,
        operation_id=operation_id,
    )


def transition_for_archive(
    *,
    revision_id: RevisionId,
    source: EditorialStatus,
    note: str,
    actor: ActorContext,
    occurred_at: datetime,
    operation_id: str,
) -> EditorialTransition:
    if source is not EditorialStatus.PUBLISHED:
        raise InvalidEditorialTransitionError(
            f"editorial transition {source.value} -> ARCHIVED is not allowed"
        )
    return _transition(
        revision_id=revision_id,
        source=source,
        target=EditorialStatus.ARCHIVED,
        note=note,
        actor=actor,
        occurred_at=occurred_at,
        operation_id=operation_id,
    )


def _transition(
    *,
    revision_id: RevisionId,
    source: EditorialStatus,
    target: EditorialStatus,
    note: str,
    actor: ActorContext,
    occurred_at: datetime,
    operation_id: str,
) -> EditorialTransition:
    normalized_note = note.strip()
    if not normalized_note or len(normalized_note) > MAX_TRANSITION_NOTE_LENGTH:
        raise InvalidTransitionNoteError(
            "editorial note must be present and at most "
            f"{MAX_TRANSITION_NOTE_LENGTH} characters"
        )
    normalized_operation_id = operation_id.strip()
    if (
        not normalized_operation_id
        or len(normalized_operation_id) > MAX_OPERATION_ID_LENGTH
    ):
        raise InvalidEditorialTransitionError(
            "operation id must be present and at most "
            f"{MAX_OPERATION_ID_LENGTH} characters"
        )
    if occurred_at.tzinfo is None or occurred_at.utcoffset() is None:
        raise InvalidEditorialTransitionError(
            "transition timestamp must be timezone-aware"
        )
    return EditorialTransition(
        revision_id=revision_id,
        source=source,
        target=target,
        note=normalized_note,
        actor=actor,
        occurred_at=occurred_at,
        operation_id=normalized_operation_id,
    )
