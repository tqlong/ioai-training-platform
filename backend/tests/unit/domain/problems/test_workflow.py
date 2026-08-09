from __future__ import annotations

from datetime import datetime, timezone

import pytest

from ioai.domain.problems.identity import RevisionId
from ioai.domain.problems.workflow import (
    ActorContext,
    EditorialStatus,
    EditorialTransition,
    InvalidEditorialTransitionError,
    InvalidTransitionNoteError,
    transition_for_review,
)

NOW = datetime(2026, 8, 9, 9, 30, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    ("source", "target"),
    (
        (EditorialStatus.DRAFT, EditorialStatus.IN_REVIEW),
        (EditorialStatus.IN_REVIEW, EditorialStatus.CHANGES_REQUESTED),
        (EditorialStatus.IN_REVIEW, EditorialStatus.APPROVED),
    ),
)
def test_review_transition_records_immutable_audit_context(
    source: EditorialStatus, target: EditorialStatus
) -> None:
    transition = transition_for_review(
        revision_id=RevisionId("revision-01"),
        source=source,
        target=target,
        note="Reviewed against the editorial checklist.",
        actor=ActorContext("local-reviewer"),
        occurred_at=NOW,
        operation_id="operation-01",
    )

    assert transition == EditorialTransition(
        revision_id=RevisionId("revision-01"),
        source=source,
        target=target,
        note="Reviewed against the editorial checklist.",
        actor=ActorContext("local-reviewer"),
        occurred_at=NOW,
        operation_id="operation-01",
    )


@pytest.mark.parametrize(
    ("source", "target"),
    (
        (EditorialStatus.DRAFT, EditorialStatus.APPROVED),
        (EditorialStatus.CHANGES_REQUESTED, EditorialStatus.IN_REVIEW),
        (EditorialStatus.APPROVED, EditorialStatus.PUBLISHED),
        (EditorialStatus.PUBLISHED, EditorialStatus.ARCHIVED),
        (EditorialStatus.IN_REVIEW, EditorialStatus.DRAFT),
    ),
)
def test_review_policy_rejects_every_non_review_transition(
    source: EditorialStatus, target: EditorialStatus
) -> None:
    with pytest.raises(InvalidEditorialTransitionError):
        transition_for_review(
            revision_id=RevisionId("revision-01"),
            source=source,
            target=target,
            note="A note",
            actor=ActorContext("local-reviewer"),
            occurred_at=NOW,
            operation_id="operation-01",
        )


@pytest.mark.parametrize("note", ("", "   ", "x" * 2001))
def test_transition_note_is_required_and_bounded(note: str) -> None:
    with pytest.raises(InvalidTransitionNoteError):
        transition_for_review(
            revision_id=RevisionId("revision-01"),
            source=EditorialStatus.DRAFT,
            target=EditorialStatus.IN_REVIEW,
            note=note,
            actor=ActorContext("local-author"),
            occurred_at=NOW,
            operation_id="operation-01",
        )


def test_actor_context_is_audit_context_not_an_authorization_claim() -> None:
    actor = ActorContext("local-reviewer")

    assert actor.label == "local-reviewer"
    assert not hasattr(actor, "is_authenticated")
