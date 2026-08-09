from __future__ import annotations

from typing import Protocol

from fastapi import APIRouter, HTTPException, Query, status

from ioai.application.problems.authoring import AuthorDraftListItem, PreviewResult
from ioai.application.problems.errors import (
    DraftNotFoundError,
    RevisionConflictError,
)
from ioai.application.problems.payload import encode_revision_payload
from ioai.domain.problems.identity import ProblemId, RevisionId
from ioai.domain.problems.revision import ProblemRevision, ValidationReport
from ioai.domain.problems.workflow import EditorialStatus

from ..contracts.errors import ErrorResponse
from ..contracts.problems import (
    AuthorDraftListItemResponse,
    AuthorDraftListResponse,
    AuthorDraftResponse,
    CreateDraftRequest,
    PreviewDraftRequest,
    PreviewResponse,
    SaveDraftRequest,
    ValidateDraftRequest,
    ValidationIssueResponse,
    ValidationReportResponse,
)


class AuthorProblemService(Protocol):
    def create(self) -> ProblemRevision: ...

    def list(
        self, *, search: str | None = None, status: EditorialStatus | None = None
    ) -> tuple[AuthorDraftListItem, ...]: ...

    def get(self, problem_id: ProblemId) -> ProblemRevision: ...

    def save(
        self, revision_id: RevisionId, request: SaveDraftRequest
    ) -> ProblemRevision: ...

    def validate(
        self, revision_id: RevisionId, expected_version: int
    ) -> ValidationReport: ...

    def preview(
        self, revision_id: RevisionId, request: PreviewDraftRequest
    ) -> PreviewResult: ...


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
    def list_drafts(
        search: str | None = Query(default=None, min_length=1, max_length=128),
        editorial_status: EditorialStatus | None = None,
    ) -> AuthorDraftListResponse:
        items = [
            _summary_response(item)
            for item in service.list(search=search, status=editorial_status)
        ]
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


def author_revision_router(service: AuthorProblemService) -> APIRouter:
    router = APIRouter(prefix="/author/revisions", tags=["author-revisions"])

    @router.put(
        "/{revision_id}",
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

    @router.post(
        "/{revision_id}/preview",
        response_model=PreviewResponse,
        responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
    )
    def preview_draft(
        revision_id: str, request: PreviewDraftRequest
    ) -> PreviewResponse:
        identity = RevisionId(revision_id)
        try:
            return _preview_response(service.preview(identity, request))
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


def _preview_response(result: PreviewResult) -> PreviewResponse:
    revision = result.revision
    encoded = encode_revision_payload(
        revision.content, revision.metadata, revision.response, revision.scoring
    )
    content = encoded["content"] or {}
    metadata = encoded["metadata"] or {}
    response = encoded["response"] or None
    issues = [*result.report.errors, *result.report.warnings]
    return PreviewResponse(
        marker="Draft preview - not public",
        learner_problem={
            "slug": revision.slug.value if revision.slug else None,
            "title": _learner_localized(content.get("title")),
            "summary": _learner_localized(content.get("summary")),
            "objectives": [
                _learner_localized(item) for item in content.get("objectives", [])
            ],
            "blocks": [
                {
                    "kind": item.get("kind"),
                    "content": _learner_localized(item.get("content")),
                    "order": item.get("order"),
                    "reveal_order": item.get("reveal_order"),
                }
                for item in content.get("blocks", [])
                if isinstance(item, dict)
            ],
            "stage": metadata.get("stage"),
            "difficulty": metadata.get("difficulty"),
            "topics": metadata.get("topics", []),
            "prerequisites": metadata.get("prerequisites", []),
            "task_type": metadata.get("task_type"),
            "expected_minutes": metadata.get("expected_minutes"),
            "resources": metadata.get("resources"),
            "response_schema": _safe_response_schema(response),
        },
        author_issues=[
            ValidationIssueResponse(
                code=item.code,
                section=item.section.value,
                field_path=item.field_path,
                message=item.message,
                severity=item.severity.value,
            )
            for item in issues
        ],
    )


def _safe_response_schema(
    response: dict[str, object] | None,
) -> dict[str, object] | None:
    if response is None:
        return None
    allowed = {
        "type",
        "choices",
        "unit",
        "language",
        "signature",
        "starter_code",
        "public_tests",
    }
    safe = {key: value for key, value in response.items() if key in allowed}
    choices = safe.get("choices")
    if isinstance(choices, list):
        safe["choices"] = [
            {
                "id": choice.get("id"),
                "content": _learner_localized(choice.get("content")),
            }
            for choice in choices
            if isinstance(choice, dict)
        ]
    return safe


def _learner_localized(value: object) -> dict[str, object] | None:
    if not isinstance(value, dict):
        return None
    return {"en": value.get("en"), "vi": value.get("vi")}


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
        validation_summary=item.validation_summary,
    )
