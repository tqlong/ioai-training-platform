from __future__ import annotations

from datetime import UTC, datetime

from ioai.application.vocabulary.proposals import RecordVocabularyProposal
from ioai.domain.vocabulary.proposals import VocabularyProposal


class FakeProposalRepository:
    def __init__(self) -> None:
        self.items: list[VocabularyProposal] = []

    def add(self, proposal: VocabularyProposal) -> None:
        self.items.append(proposal)

    def list_pending(self) -> tuple[VocabularyProposal, ...]:
        return tuple(self.items)


class FakeProposalUnitOfWork:
    def __init__(self, repository: FakeProposalRepository) -> None:
        self.proposals = repository
        self.commits = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        if exc_type is None:
            self.commits += 1


def test_record_proposal_uses_injected_id_and_clock() -> None:
    repository = FakeProposalRepository()
    unit_of_work = FakeProposalUnitOfWork(repository)
    now = datetime(2026, 8, 9, tzinfo=UTC)
    record = RecordVocabularyProposal(
        unit_of_work_factory=lambda: unit_of_work,
        id_generator=lambda: "proposal-fixed",
        clock=lambda: now,
    )

    proposal = record(vocabulary_type="TOPIC", note="Add causal inference")

    assert proposal.proposal_id == "proposal-fixed"
    assert proposal.created_at == now
    assert repository.items == [proposal]
    assert unit_of_work.commits == 1


def test_pending_proposals_are_reviewable_in_stable_order() -> None:
    repository = FakeProposalRepository()
    unit_of_work = FakeProposalUnitOfWork(repository)
    moments = iter(
        [
            datetime(2026, 8, 9, 2, tzinfo=UTC),
            datetime(2026, 8, 9, 1, tzinfo=UTC),
        ]
    )
    ids = iter(["proposal-2", "proposal-1"])
    record = RecordVocabularyProposal(
        unit_of_work_factory=lambda: unit_of_work,
        id_generator=lambda: next(ids),
        clock=lambda: next(moments),
    )
    record(vocabulary_type="TOPIC", note="Second")
    record(vocabulary_type="COMPETENCY", note="First")

    proposals = record.list_pending()

    assert [proposal.proposal_id for proposal in proposals] == [
        "proposal-1",
        "proposal-2",
    ]
