from __future__ import annotations

from datetime import UTC, datetime

import pytest

from ioai.domain.vocabulary.proposals import ProposalNote, VocabularyProposal
from ioai.domain.vocabulary.values import VocabularyType


def test_proposal_is_pending_and_keeps_vocabulary_context_separate() -> None:
    proposal = VocabularyProposal.create(
        proposal_id="proposal-1",
        vocabulary_type=VocabularyType("TOPIC"),
        note=ProposalNote("Add causal inference"),
        created_at=datetime(2026, 8, 9, tzinfo=UTC),
    )

    assert proposal.status == "PENDING"
    assert proposal.vocabulary_type.value == "TOPIC"
    assert proposal.note.value == "Add causal inference"


@pytest.mark.parametrize("note", ["", " ", "x" * 1001])
def test_proposal_note_is_required_and_bounded(note: str) -> None:
    with pytest.raises(ValueError, match="note"):
        ProposalNote(note)
