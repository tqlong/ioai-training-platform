from __future__ import annotations

from typing import Protocol

from fastapi import APIRouter, HTTPException, status

from ioai.application.problems.authoring import AuthorDraftListItem
from ioai.application.problems.errors import (
    DraftNotFoundError,
    RevisionConflictError,
)
from ioai.application.problems.payload import encode_revision_payload
from ioai.domain.problems.identity import ProblemId, RevisionId
from ioai.domain.problems.revision import ProblemRevision, ValidationReport

from ..contracts.errors import ErrorResponse
from ..contracts.problems import (
    AuthorDraftListItemResponse,
    AuthorDraftListResponse,
    AuthorDraftResponse,
    CreateDraftRequest,
    SaveDraftRequest,
    ValidateDraftRequest,
    ValidationIssueResponse,
    ValidationReportResponse,
)


class AuthorProblemService(Protocol):
    def create(self) -> ProblemRevision: ...

    def list(self) -> tuple[AuthorDraftListItem, ...]: ...

    def get(self, problem_id: ProblemId) -> ProblemRevision: ...

    def save(
        self, revision_id: RevisionId, request: SaveDraftRequest
    ) -> ProblemRevision: ...

    def validate(
        self, revision_id: RevisionId, expected_version: int
    ) -> ValidationReport: ...


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

    @router.put(
        "/revisions/{revision_id}",
        response_model=AuthorDraftResponse,
        responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
    )
    def save_draft(revision_id: str, request: SaveDraftRequest) -> AuthorDraftResponse:
        try:
            return _draft_response(service.save(RevisionId(revision_id), request))
        except RevisionConflictError as error:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "REVISION_CONFLICT",
                    "message": "A newer draft version exists.",
                    "current_version": error.current_version,
                },
            ) from error
        except DraftNotFoundError as error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "DRAFT_NOT_FOUND", "message": "Draft not found."},
            ) from error

    return router


def author_revision_router(service: AuthorProblemService) -> APIRouter:
    router = APIRouter(prefix="/author/revisions", tags=["author-revisions"])

    @router.post(
        "/{revision_id}/validate",
        response_model=ValidationReportResponse,
        responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
    )
    def validate_draft(
        revision_id: str, request: ValidateDraftRequest
    ) -> ValidationReportResponse:
        identity = RevisionId(revision_id)
        try:
            return _validation_response(
                service.validate(identity, request.expected_version)
            )
        except RevisionConflictError as error:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "REVISION_CONFLICT",
                    "message": "A newer draft version exists.",
                    "current_version": error.current_version,
                },
            ) from error
        except DraftNotFoundError as error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "DRAFT_NOT_FOUND", "message": "Draft not found."},
            ) from error

    return router


def _validation_response(report: ValidationReport) -> ValidationReportResponse:
    def issue(value):
        return ValidationIssueResponse(
            code=value.code,
            section=value.section.value,
            field_path=value.field_path,
            message=value.message,
            severity=value.severity.value,
        )

    return ValidationReportResponse(
        revision_id=report.revision_id.value,
        revision_version=report.revision_version,
        errors=[issue(value) for value in report.errors],
        warnings=[issue(value) for value in report.warnings],
        publication_eligible=report.publication_eligible,
    )


def _draft_response(revision: ProblemRevision) -> AuthorDraftResponse:
    encoded = encode_revision_payload(
        revision.content, revision.metadata, revision.response, revision.scoring
    )
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
