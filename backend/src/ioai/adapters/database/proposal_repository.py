from __future__ import annotations

from types import TracebackType
from typing import Self

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from ioai.domain.vocabulary.proposals import ProposalNote, VocabularyProposal
from ioai.domain.vocabulary.values import VocabularyType

from .vocabulary_model import VocabularyProposalModel


class SqlAlchemyProposalRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, proposal: VocabularyProposal) -> None:
        self._session.add(
            VocabularyProposalModel(
                proposal_id=proposal.proposal_id,
                vocabulary_type=proposal.vocabulary_type.value,
                note=proposal.note.value,
                status=proposal.status,
                created_at=proposal.created_at,
            )
        )

    def list_pending(self) -> tuple[VocabularyProposal, ...]:
        statement = (
            select(VocabularyProposalModel)
            .where(VocabularyProposalModel.status == "PENDING")
            .order_by(
                VocabularyProposalModel.created_at,
                VocabularyProposalModel.proposal_id,
            )
        )
        return tuple(_to_domain(row) for row in self._session.scalars(statement))


class SqlAlchemyProposalUnitOfWork:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None
        self._proposals: SqlAlchemyProposalRepository | None = None

    @property
    def proposals(self) -> SqlAlchemyProposalRepository:
        if self._proposals is None:
            raise RuntimeError("unit of work must be entered before repository access")
        return self._proposals

    def __enter__(self) -> Self:
        self._session = self._session_factory()
        self._proposals = SqlAlchemyProposalRepository(self._session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._session is None:
            return
        try:
            if exc_type is None:
                self._session.commit()
            else:
                self._session.rollback()
        finally:
            self._session.close()
            self._session = None
            self._proposals = None


def _to_domain(row: VocabularyProposalModel) -> VocabularyProposal:
    return VocabularyProposal(
        proposal_id=row.proposal_id,
        vocabulary_type=VocabularyType(row.vocabulary_type),
        note=ProposalNote(row.note),
        status=row.status,
        created_at=row.created_at,
    )
