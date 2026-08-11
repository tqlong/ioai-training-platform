from __future__ import annotations

from typing import Protocol

from fastapi import APIRouter, Header, HTTPException, Query

from ioai.application.problems.manual_assessment import (
    AssessmentConflictError,
    AssessmentDecision,
    AssessmentNotFoundError,
    AssessmentRecord,
)

from ..contracts.errors import ErrorResponse
from ..contracts.problems import (
    AssessmentDecisionRequest,
    AssessmentDetailResponse,
    AssessmentListItemResponse,
    AssessmentListResponse,
)
from ..contracts.public_problems import PublicSubmissionResponse
from .public_problems import _submission_response


class ManualAssessmentService(Protocol):
    def list_assessments(
        self, *, status: str, problem: str | None, limit: int, offset: int
    ) -> tuple[AssessmentRecord, ...]: ...

    def get_assessment(self, attempt_id: str) -> AssessmentRecord: ...

    def decide(
        self, attempt_id: str, request: AssessmentDecisionRequest
    ) -> AssessmentDecision: ...

    def get_submission(self, attempt_id: str, receipt: str) -> AssessmentRecord: ...


def public_submission_router(service: ManualAssessmentService) -> APIRouter:
    router = APIRouter(prefix="/submissions", tags=["public-submissions"])

    @router.get(
        "/{attempt_id}",
        response_model=PublicSubmissionResponse,
        response_model_exclude_none=True,
        responses={404: {"model": ErrorResponse}},
    )
    def get_submission(
        attempt_id: str,
        x_submission_receipt: str = Header(min_length=16, max_length=200),
    ) -> PublicSubmissionResponse:
        try:
            record = service.get_submission(attempt_id, x_submission_receipt)
        except AssessmentNotFoundError as error:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "SUBMISSION_NOT_FOUND",
                    "message": "Submission not found.",
                },
            ) from error
        return _submission_response(record.attempt, include_submitted_response=True)

    return router


def author_assessment_router(service: ManualAssessmentService) -> APIRouter:
    router = APIRouter(prefix="/author/assessments", tags=["author-assessments"])

    @router.get("", response_model=AssessmentListResponse)
    def list_assessments(
        status: str = Query(default="PENDING", pattern="^(PENDING|ASSESSED|ALL)$"),
        problem: str | None = Query(default=None, min_length=1, max_length=120),
        limit: int = Query(default=50, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
    ) -> AssessmentListResponse:
        records = service.list_assessments(
            status=status, problem=problem, limit=limit, offset=offset
        )
        return AssessmentListResponse(
            items=[_list_item(record) for record in records],
            next_offset=offset + len(records) if len(records) == limit else None,
        )

    @router.get(
        "/{attempt_id}",
        response_model=AssessmentDetailResponse,
        responses={404: {"model": ErrorResponse}},
    )
    def get_assessment(attempt_id: str) -> AssessmentDetailResponse:
        try:
            return _detail(service.get_assessment(attempt_id))
        except AssessmentNotFoundError as error:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "ASSESSMENT_NOT_FOUND",
                    "message": "Assessment not found.",
                },
            ) from error

    @router.post(
        "/{attempt_id}/decisions",
        response_model=AssessmentDetailResponse,
        responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
    )
    def decide(
        attempt_id: str, request: AssessmentDecisionRequest
    ) -> AssessmentDetailResponse:
        try:
            service.decide(attempt_id, request)
            return _detail(service.get_assessment(attempt_id))
        except AssessmentNotFoundError as error:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "ASSESSMENT_NOT_FOUND",
                    "message": "Assessment not found.",
                },
            ) from error
        except AssessmentConflictError as error:
            raise HTTPException(
                status_code=409,
                detail={"code": "ASSESSMENT_CONFLICT", "message": str(error)},
            ) from error
        except ValueError as error:
            raise HTTPException(
                status_code=422,
                detail={"code": "ASSESSMENT_INVALID", "message": str(error)},
            ) from error

    return router


def _list_item(record: AssessmentRecord) -> AssessmentListItemResponse:
    score = record.attempt.result.get("score")
    return AssessmentListItemResponse(
        attempt_id=record.attempt.attempt_id,
        slug=record.slug,
        title=record.title,
        status="PENDING" if record.latest_decision is None else "ASSESSED",
        submitted_at=record.attempt.submitted_at,
        score=score if isinstance(score, str) else None,
    )


def _detail(record: AssessmentRecord) -> AssessmentDetailResponse:
    scoring = record.snapshot_payload.get("scoring")
    return AssessmentDetailResponse(
        attempt_id=record.attempt.attempt_id,
        slug=record.slug,
        title=record.title,
        status="PENDING" if record.latest_decision is None else "ASSESSED",
        submitted_at=record.attempt.submitted_at,
        submitted_response=record.attempt.response,
        scoring=scoring if isinstance(scoring, dict) else {},
        latest_decision=(
            {
                "decision_id": record.latest_decision.decision_id,
                "version": record.latest_decision.version,
                "result": record.latest_decision.result,
                "overall_feedback": record.latest_decision.overall_feedback,
                "correction_reason": record.latest_decision.correction_reason,
                "decided_at": record.latest_decision.decided_at,
            }
            if record.latest_decision
            else None
        ),
        decision_history=[
            {
                "decision_id": item.decision_id,
                "version": item.version,
                "result": item.result,
                "overall_feedback": item.overall_feedback,
                "correction_reason": item.correction_reason,
                "decided_at": item.decided_at,
            }
            for item in record.decision_history
        ],
    )
