from __future__ import annotations

from typing import Protocol

from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder

from ioai.application.problems.authoring import AuthorDraftListItem
from ioai.application.problems.errors import DraftNotFoundError
from ioai.domain.problems.identity import ProblemId
from ioai.domain.problems.revision import ProblemRevision

from ..contracts.errors import ErrorResponse
from ..contracts.problems import (
    AuthorDraftListItemResponse,
    AuthorDraftListResponse,
    AuthorDraftResponse,
    CreateDraftRequest,
)


class AuthorProblemService(Protocol):
    def create(self) -> ProblemRevision: ...

    def list(self) -> tuple[AuthorDraftListItem, ...]: ...

    def get(self, problem_id: ProblemId) -> ProblemRevision: ...


def author_problem_router(service: AuthorProblemService) -> APIRouter:
    router = APIRouter(prefix="/author/problems", tags=["author-problems"])

    @router.post(
        "",
        response_model=AuthorDraftResponse,
        status_code=status.HTTP_201_CREATED,
        responses={422: {"model": ErrorResponse}},
    )
    def create_draft(request: CreateDraftRequest) -> AuthorDraftResponse:
        del request
        return _draft_response(service.create())

    @router.get("", response_model=AuthorDraftListResponse)
    def list_drafts() -> AuthorDraftListResponse:
        items = [_summary_response(item) for item in service.list()]
        return AuthorDraftListResponse(items=items, count=len(items))

    @router.get(
        "/{problem_id}",
        response_model=AuthorDraftResponse,
        responses={404: {"model": ErrorResponse}},
    )
    def read_draft(problem_id: str) -> AuthorDraftResponse:
        try:
            return _draft_response(service.get(ProblemId(problem_id)))
        except DraftNotFoundError as error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "DRAFT_NOT_FOUND", "message": "Draft not found."},
            ) from error

    return router


def _draft_response(revision: ProblemRevision) -> AuthorDraftResponse:
    encoded = jsonable_encoder(revision)
    return AuthorDraftResponse(
        problem_id=revision.problem_id.value,
        revision_id=revision.revision_id.value,
        version=revision.version,
        editorial_status=revision.status.value,
        slug=revision.slug.value if revision.slug else None,
        content=encoded.get("content"),
        metadata=encoded.get("metadata"),
        response=encoded.get("response"),
        scoring=encoded.get("scoring"),
    )


def _summary_response(item: AuthorDraftListItem) -> AuthorDraftListItemResponse:
    return AuthorDraftListItemResponse(
        problem_id=item.problem_id.value,
        revision_id=item.revision_id.value,
        version=item.version,
        editorial_status=item.status.value,
        last_saved_at=item.last_saved_at,
    )
