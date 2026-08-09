from __future__ import annotations

from typing import Protocol

from fastapi import APIRouter, status

from ioai.domain.vocabulary.proposals import VocabularyProposal

from ..contracts.errors import ErrorResponse
from ..contracts.proposals import (
    RecordVocabularyProposalRequest,
    VocabularyProposalListResponse,
    VocabularyProposalResponse,
)


class ProposalService(Protocol):
    def __call__(self, *, vocabulary_type: str, note: str) -> VocabularyProposal: ...

    def list_pending(self) -> tuple[VocabularyProposal, ...]: ...


def proposal_router(service: ProposalService) -> APIRouter:
    router = APIRouter(prefix="/author/vocabulary/proposals", tags=["vocabulary"])

    @router.post(
        "",
        response_model=VocabularyProposalResponse,
        status_code=status.HTTP_201_CREATED,
        responses={422: {"model": ErrorResponse}},
    )
    def record_proposal(
        request: RecordVocabularyProposalRequest,
    ) -> VocabularyProposalResponse:
        return _response(
            service(vocabulary_type=request.vocabulary_type, note=request.note)
        )

    @router.get("", response_model=VocabularyProposalListResponse)
    def list_proposals() -> VocabularyProposalListResponse:
        items = [_response(proposal) for proposal in service.list_pending()]
        return VocabularyProposalListResponse(items=items, count=len(items))

    return router


def _response(proposal: VocabularyProposal) -> VocabularyProposalResponse:
    return VocabularyProposalResponse(
        proposal_id=proposal.proposal_id,
        vocabulary_type=proposal.vocabulary_type.value,
        note=proposal.note.value,
        status=proposal.status,
        created_at=proposal.created_at,
    )
