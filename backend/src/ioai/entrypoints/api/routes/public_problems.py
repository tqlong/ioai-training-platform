from __future__ import annotations

from typing import Protocol

from fastapi import APIRouter, HTTPException, Query, Request, status

from ioai.application.problems.public_queries import (
    PublicProblemProjection,
    PublicProblemProjectionPage,
    PublicProblemQuery,
    PublicProblemSort,
)
from ioai.domain.vocabulary.availability import Release0AvailabilityPolicy
from ioai.domain.vocabulary.values import (
    VocabularyIdentity,
    VocabularyRecord,
    VocabularyType,
)

from ..contracts.errors import ErrorResponse
from ..contracts.public_problems import (
    PublicLocalizedTextResponse,
    PublicProblemListItemResponse,
    PublicProblemListResponse,
)


class PublicProblemService(Protocol):
    def list(self, query: PublicProblemQuery) -> PublicProblemProjectionPage: ...


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
