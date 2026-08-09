from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from types import TracebackType
from typing import Protocol, Self

from ioai.domain.vocabulary.proposals import ProposalNote, VocabularyProposal
from ioai.domain.vocabulary.values import VocabularyType


class ProposalRepository(Protocol):
    def add(self, proposal: VocabularyProposal) -> None: ...

    def list_pending(self) -> tuple[VocabularyProposal, ...]: ...


class ProposalUnitOfWork(Protocol):
    @property
    def proposals(self) -> ProposalRepository: ...

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...


class RecordVocabularyProposal:
    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], ProposalUnitOfWork],
        id_generator: Callable[[], str],
        clock: Callable[[], datetime],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._id_generator = id_generator
        self._clock = clock

    def __call__(self, *, vocabulary_type: str, note: str) -> VocabularyProposal:
        proposal = VocabularyProposal.create(
            proposal_id=self._id_generator(),
            vocabulary_type=VocabularyType(vocabulary_type),
            note=ProposalNote(note),
            created_at=self._clock(),
        )
        with self._unit_of_work_factory() as unit_of_work:
            unit_of_work.proposals.add(proposal)
        return proposal

    def list_pending(self) -> tuple[VocabularyProposal, ...]:
        with self._unit_of_work_factory() as unit_of_work:
            proposals = unit_of_work.proposals.list_pending()
        return tuple(
            sorted(
                proposals,
                key=lambda proposal: (proposal.created_at, proposal.proposal_id),
            )
        )
