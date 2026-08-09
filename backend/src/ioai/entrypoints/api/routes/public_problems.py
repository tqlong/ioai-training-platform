from __future__ import annotations

from typing import Protocol

from fastapi import APIRouter, HTTPException, Query, Request, Response, status

from ioai.application.problems.assessment import SubmissionCommand
from ioai.application.problems.errors import (
    IdempotencyConflictError,
    PublishedProblemNotFoundError,
)
from ioai.application.problems.learner_records import LearnerAttempt, LearnerOutcome
from ioai.application.problems.public_queries import (
    PublicProblemProjection,
    PublicProblemProjectionPage,
    PublicProblemQuery,
    PublicProblemSort,
)
from ioai.application.problems.recommendations import (
    LearningEvidenceContext,
    ProblemRecommendation,
    RecommendationContext,
)
from ioai.domain.vocabulary.availability import Release0AvailabilityPolicy
from ioai.domain.vocabulary.values import (
    VocabularyIdentity,
    VocabularyRecord,
    VocabularyType,
)

from ..contracts.errors import ErrorResponse
from ..contracts.public_problems import (
    PublicContentBlockResponse,
    PublicLocalizedTextResponse,
    PublicPrerequisiteResponse,
    PublicProblemDetailResponse,
    PublicProblemListItemResponse,
    PublicProblemListResponse,
    PublicProblemRecommendationResponse,
    PublicResourceLimitsResponse,
    PublicResponseSchemaResponse,
    PublicSubmissionRequest,
    PublicSubmissionResponse,
)


class PublicProblemService(Protocol):
    def list(self, query: PublicProblemQuery) -> PublicProblemProjectionPage: ...

    def get(self, slug: str) -> PublicProblemProjection: ...

    def assess(self, command: SubmissionCommand) -> LearnerAttempt: ...

    def recommend(
        self, context: RecommendationContext
    ) -> ProblemRecommendation | None: ...


_QUERY_PARAMETERS = {
    "stage",
    "competency",
    "topic",
    "include_subtopics",
    "difficulty",
    "task_type",
    "expected_minutes_min",
    "expected_minutes_max",
    "compute_tier",
    "q",
    "sort",
    "page",
    "page_size",
}


def public_problem_router(
    service: PublicProblemService,
    vocabulary: tuple[VocabularyRecord, ...],
) -> APIRouter:
    router = APIRouter(prefix="/problems", tags=["public-problems"])
    known = {record.identity for record in vocabulary}
    policy = Release0AvailabilityPolicy()

    @router.get(
        "",
        response_model=PublicProblemListResponse,
        responses={422: {"model": ErrorResponse}},
    )
    def list_problems(
        request: Request,
        stage: str | None = None,
        competency: str | None = None,
        topic: str | None = None,
        include_subtopics: bool = False,
        difficulty: str | None = None,
        task_type: str | None = None,
        expected_minutes_min: int | None = Query(default=None, gt=0),
        expected_minutes_max: int | None = Query(default=None, gt=0),
        compute_tier: str | None = None,
        q: str | None = Query(default=None, min_length=1, max_length=128),
        sort: PublicProblemSort = PublicProblemSort.EDITORIAL,
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=25, ge=1, le=100),
    ) -> PublicProblemListResponse:
        unknown_parameters = set(request.query_params) - _QUERY_PARAMETERS
        if unknown_parameters:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={
                    "code": "UNKNOWN_QUERY_PARAMETER",
                    "message": "The request contains an unsupported query parameter.",
                },
            )
        selected = (
            ("PATHWAY_STAGE", stage),
            ("COMPETENCY", competency),
            ("TOPIC", topic),
            ("DIFFICULTY", difficulty),
            ("TASK_TYPE", task_type),
            ("COMPUTE_TIER", compute_tier),
        )
        for vocabulary_type, code in selected:
            if code is None:
                continue
            identity = VocabularyIdentity(VocabularyType(vocabulary_type), code)
            if identity not in known:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail={
                        "code": "UNKNOWN_VOCABULARY_VALUE",
                        "message": "A selected filter value is not canonical.",
                    },
                )
            decision = policy.evaluate(identity)
            if not decision.is_available:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail={"code": "POLICY_DISALLOWED", "message": decision.message},
                )
        try:
            query = PublicProblemQuery(
                stage=stage,
                competency=competency,
                topic=topic,
                include_subtopics=include_subtopics,
                difficulty=difficulty,
                task_type=task_type,
                expected_minutes_min=expected_minutes_min,
                expected_minutes_max=expected_minutes_max,
                compute_tier=compute_tier,
                search=q,
                sort=sort,
                page=page,
                page_size=page_size,
            )
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={"code": "INVALID_FILTER", "message": str(error)},
            ) from error
        result = service.list(query)
        return PublicProblemListResponse(
            items=[_list_item(item) for item in result.items],
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            active_filters=_active_filters(query),
        )

    @router.get(
        "/{slug}/recommendation",
        response_model=PublicProblemRecommendationResponse,
        responses={204: {"description": "No eligible recommendation"}},
    )
    def recommend_problem(
        slug: str,
        stage: str,
        completed: list[str] = Query(default_factory=list, max_length=50),
        evidence: list[str] = Query(default_factory=list, max_length=100),
    ) -> PublicProblemRecommendationResponse | Response:
        _validate_identity(known, policy, "PATHWAY_STAGE", stage)
        try:
            context = RecommendationContext(
                stage=stage,
                current_slug=slug,
                completed_slugs=tuple(completed),
                evidence=tuple(_evidence_context(value) for value in evidence),
            )
            recommendation = service.recommend(context)
        except PublishedProblemNotFoundError as error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "PUBLIC_NOT_FOUND", "message": "Problem not found."},
            ) from error
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={
                    "code": "INVALID_RECOMMENDATION_CONTEXT",
                    "message": str(error),
                },
            ) from error
        if recommendation is None:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        return _recommendation_response(recommendation)

    @router.get(
        "/{slug}",
        response_model=PublicProblemDetailResponse,
        responses={404: {"model": ErrorResponse}},
    )
    def get_problem(slug: str) -> PublicProblemDetailResponse:
        try:
            return _detail_response(service.get(slug))
        except PublishedProblemNotFoundError as error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "PUBLIC_NOT_FOUND", "message": "Problem not found."},
            ) from error

    @router.post(
        "/{slug}/submissions",
        response_model=PublicSubmissionResponse,
        response_model_exclude_none=True,
        responses={
            404: {"model": ErrorResponse},
            409: {"model": ErrorResponse},
            422: {"model": ErrorResponse},
            503: {"model": ErrorResponse},
        },
    )
    def submit_problem(
        slug: str, request: PublicSubmissionRequest
    ) -> PublicSubmissionResponse:
        try:
            attempt = service.assess(
                SubmissionCommand(
                    slug, request.submission_key, request.response.model_dump()
                )
            )
        except PublishedProblemNotFoundError as error:
            raise HTTPException(
                status_code=404,
                detail={"code": "PUBLIC_NOT_FOUND", "message": "Problem not found."},
            ) from error
        except IdempotencyConflictError as error:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "SUBMISSION_KEY_CONFLICT",
                    "message": (
                        "This submission key was already used for a different answer."
                    ),
                },
            ) from error
        except ValueError as error:
            raise HTTPException(
                status_code=422,
                detail={"code": "INVALID_SUBMISSION", "message": str(error)},
            ) from error
        except RuntimeError as error:
            raise HTTPException(
                status_code=503,
                detail={
                    "code": "ASSESSMENT_UNAVAILABLE",
                    "message": (
                        "Assessment is temporarily unavailable. Retry with the same "
                        "submission key."
                    ),
                },
            ) from error
        return _submission_response(attempt)

    return router


def _list_item(item: PublicProblemProjection) -> PublicProblemListItemResponse:
    metadata = item.metadata
    topics = _identity_codes(metadata.get("topics"))
    objectives = item.content.get("objectives")
    objective = objectives[0] if isinstance(objectives, list) and objectives else None
    resources = metadata.get("resources")
    resources_map = resources if isinstance(resources, dict) else {}
    return PublicProblemListItemResponse(
        slug=item.slug,
        public_short_id=item.slug,
        title=_localized(item.content.get("title")),
        objective=_localized(objective),
        stage_code=_identity_code(metadata.get("stage")),
        difficulty_code=_identity_code(metadata.get("difficulty")),
        primary_competency_code=_identity_code(metadata.get("primary_competency")),
        topic_codes=list(topics[:2]),
        remaining_topic_count=max(0, len(topics) - 2),
        task_type_code=_identity_code(metadata.get("task_type")),
        expected_minutes=_positive_int(metadata.get("expected_minutes")),
        compute_tier_code=_identity_code(resources_map.get("compute_tier")),
        published_at=item.published_at,
    )


def _detail_response(item: PublicProblemProjection) -> PublicProblemDetailResponse:
    metadata = item.metadata
    content = item.content
    resources = metadata.get("resources")
    resources_map = resources if isinstance(resources, dict) else {}
    prerequisites = metadata.get("prerequisites")
    prerequisite_items = prerequisites if isinstance(prerequisites, list) else []
    blocks = content.get("blocks")
    block_items = blocks if isinstance(blocks, list) else []
    objectives = content.get("objectives")
    objective = objectives[0] if isinstance(objectives, list) and objectives else None
    response_schema = dict(item.response_schema)
    return PublicProblemDetailResponse(
        slug=item.slug,
        public_short_id=item.slug,
        permanent_url=f"/problems/{item.slug}",
        title=_localized(content.get("title")),
        summary=_localized(content.get("summary")),
        objective=_localized(objective),
        blocks=[_content_block(value) for value in block_items],
        stage_code=_identity_code(metadata.get("stage")),
        difficulty_code=_identity_code(metadata.get("difficulty")),
        primary_competency_code=_identity_code(metadata.get("primary_competency")),
        secondary_competency_codes=list(
            _identity_codes(metadata.get("secondary_competencies"))
        ),
        topic_codes=list(_identity_codes(metadata.get("topics"))),
        prerequisite_codes=[
            value.target_code
            for value in map(_prerequisite, prerequisite_items)
            if value.target_code is not None
        ],
        prerequisites=[_prerequisite(value) for value in prerequisite_items],
        modality_codes=list(_identity_codes(metadata.get("modalities"))),
        task_type_code=_identity_code(metadata.get("task_type")),
        expected_minutes=_positive_int(metadata.get("expected_minutes")),
        resources=PublicResourceLimitsResponse(
            compute_tier_code=_identity_code(resources_map.get("compute_tier")),
            runtime_class_code=_identity_code(resources_map.get("runtime_class")),
            cpu_cores=_non_negative_int(resources_map.get("cpu_cores")),
            ram_mb=_non_negative_int(resources_map.get("ram_mb")),
            gpu_count=_non_negative_int(resources_map.get("gpu_count")),
            gpu_vram_mb=_non_negative_int(resources_map.get("gpu_vram_mb")),
            storage_mb=_non_negative_int(resources_map.get("storage_mb")),
            runtime_seconds=_non_negative_int(resources_map.get("runtime_seconds")),
            network_policy=str(resources_map.get("network_policy", "DENIED")),
        ),
        response_schema=PublicResponseSchemaResponse.model_validate(response_schema),
        feedback_available=True,
        recommendation_url=f"/api/v1/problems/{item.slug}/recommendation",
        published_at=item.published_at,
    )


def _content_block(value: object) -> PublicContentBlockResponse:
    if not isinstance(value, dict):
        raise ValueError("published content block is malformed")
    return PublicContentBlockResponse(
        kind=str(value.get("kind", "")),
        content=_localized(value.get("content")),
        order=_positive_int(value.get("order")),
        reveal_order=(
            _positive_int(value.get("reveal_order"))
            if value.get("reveal_order") is not None
            else None
        ),
    )


def _prerequisite(value: object) -> PublicPrerequisiteResponse:
    if not isinstance(value, dict):
        raise ValueError("published prerequisite is malformed")
    target_identity = value.get("target_identity")
    return PublicPrerequisiteResponse(
        relationship=str(value.get("relationship", "")),
        target_type=str(value.get("target_type", "")),
        target_code=_identity_code(target_identity) if target_identity else None,
        target_id=str(value["target_id"]) if value.get("target_id") else None,
        minimum_evidence=(
            str(value["minimum_evidence"]) if value.get("minimum_evidence") else None
        ),
    )


def _localized(value: object) -> PublicLocalizedTextResponse:
    if not isinstance(value, dict):
        raise ValueError("published localized content is malformed")
    return PublicLocalizedTextResponse(
        en=str(value.get("en", "")), vi=str(value.get("vi", ""))
    )


def _identity_code(value: object) -> str:
    if not isinstance(value, list) or len(value) != 2 or not isinstance(value[1], str):
        raise ValueError("published vocabulary identity is malformed")
    return value[1]


def _identity_codes(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(_identity_code(item) for item in value)


def _positive_int(value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ValueError("published expected minutes is malformed")
    return value


def _non_negative_int(value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError("published resource limit is malformed")
    return value


def _active_filters(query: PublicProblemQuery) -> dict[str, str | bool | int]:
    values: tuple[tuple[str, str | bool | int | None], ...] = (
        ("stage", query.stage),
        ("competency", query.competency),
        ("topic", query.topic),
        ("include_subtopics", query.include_subtopics if query.topic else None),
        ("difficulty", query.difficulty),
        ("task_type", query.task_type),
        ("expected_minutes_min", query.expected_minutes_min),
        ("expected_minutes_max", query.expected_minutes_max),
        ("compute_tier", query.compute_tier),
        ("q", query.search),
        (
            "sort",
            query.sort.value if query.sort is not PublicProblemSort.EDITORIAL else None,
        ),
    )
    return {key: value for key, value in values if value is not None}


def _validate_identity(
    known: set[VocabularyIdentity],
    policy: Release0AvailabilityPolicy,
    vocabulary_type: str,
    code: str,
) -> None:
    identity = VocabularyIdentity(VocabularyType(vocabulary_type), code)
    if identity not in known:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "code": "UNKNOWN_VOCABULARY_VALUE",
                "message": "A selected value is not canonical.",
            },
        )
    decision = policy.evaluate(identity)
    if not decision.is_available:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={"code": "POLICY_DISALLOWED", "message": decision.message},
        )


def _evidence_context(value: str) -> LearningEvidenceContext:
    parts = value.split(":")
    if len(parts) != 3:
        raise ValueError("evidence must use VOCABULARY_TYPE:CODE:LEVEL format")
    return LearningEvidenceContext(parts[0], parts[1], parts[2])


def _recommendation_response(
    value: ProblemRecommendation,
) -> PublicProblemRecommendationResponse:
    return PublicProblemRecommendationResponse(
        slug=value.slug,
        permanent_url=value.permanent_url,
        title=PublicLocalizedTextResponse(**value.title),
        stage_code=value.stage_code,
        difficulty_code=value.difficulty_code,
        expected_minutes=value.expected_minutes,
        compute_tier_code=value.compute_tier_code,
        label=value.label,
        reason=value.reason,
    )


def _submission_response(attempt: LearnerAttempt) -> PublicSubmissionResponse:
    if attempt.outcome is LearnerOutcome.PENDING_ASSESSMENT:
        return PublicSubmissionResponse(
            attempt_id=attempt.attempt_id,
            outcome=attempt.outcome.value,
            message="Your answer is waiting for assessment.",
        )
    score = attempt.result.get("score")
    passed = attempt.result.get("passed")
    components = attempt.result.get("components")
    if (
        not isinstance(score, str)
        or not isinstance(passed, bool)
        or not isinstance(components, list)
    ):
        raise ValueError("stored assessment result is malformed")
    return PublicSubmissionResponse.model_validate(
        {
            "attempt_id": attempt.attempt_id,
            "outcome": attempt.outcome.value,
            "score": score,
            "passed": passed,
            "components": components,
            "message": "Your answer was assessed.",
        }
    )
