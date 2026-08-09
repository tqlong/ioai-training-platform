from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol, cast

from .errors import PublishedProblemNotFoundError
from .publication import PublishedSnapshot


@dataclass(frozen=True, slots=True)
class PublicProblemProjection:
    slug: str
    content: dict[str, object]
    metadata: dict[str, object]
    response_schema: dict[str, object]
    published_at: datetime


class PublicProblemSort(StrEnum):
    EDITORIAL = "EDITORIAL"
    NEWEST = "NEWEST"
    EXPECTED_TIME = "EXPECTED_TIME"
    TITLE = "TITLE"


@dataclass(frozen=True, slots=True)
class PublicProblemQuery:
    stage: str | None = None
    competency: str | None = None
    topic: str | None = None
    include_subtopics: bool = False
    difficulty: str | None = None
    task_type: str | None = None
    expected_minutes_min: int | None = None
    expected_minutes_max: int | None = None
    compute_tier: str | None = None
    search: str | None = None
    sort: PublicProblemSort = PublicProblemSort.EDITORIAL
    page: int = 1
    page_size: int = 25

    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValueError("page must be positive")
        if self.page_size < 1 or self.page_size > 100:
            raise ValueError("page size must be between 1 and 100")
        if self.search is not None:
            normalized_search = self.search.strip()
            if not normalized_search or len(normalized_search) > 128:
                raise ValueError("search must contain between 1 and 128 characters")
            object.__setattr__(self, "search", normalized_search)
        if self.expected_minutes_min is not None and self.expected_minutes_min < 1:
            raise ValueError("minimum expected minutes must be positive")
        if self.expected_minutes_max is not None and self.expected_minutes_max < 1:
            raise ValueError("maximum expected minutes must be positive")
        if (
            self.expected_minutes_min is not None
            and self.expected_minutes_max is not None
            and self.expected_minutes_min > self.expected_minutes_max
        ):
            raise ValueError("expected minutes minimum cannot exceed maximum")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


@dataclass(frozen=True, slots=True)
class PublicProblemPage:
    snapshots: tuple[PublishedSnapshot, ...]
    total: int


@dataclass(frozen=True, slots=True)
class PublicProblemProjectionPage:
    items: tuple[PublicProblemProjection, ...]
    total: int
    page: int
    page_size: int


class PublishedProblemReader(Protocol):
    def list_current(self, query: PublicProblemQuery) -> PublicProblemPage: ...

    def get_current_by_slug(self, slug: str) -> PublishedSnapshot | None: ...


class ListPublishedProblems:
    def __init__(self, reader: PublishedProblemReader) -> None:
        self._reader = reader

    def __call__(self, query: PublicProblemQuery) -> PublicProblemProjectionPage:
        page = self._reader.list_current(query)
        return PublicProblemProjectionPage(
            items=tuple(
                project_public_snapshot(snapshot) for snapshot in page.snapshots
            ),
            total=page.total,
            page=query.page,
            page_size=query.page_size,
        )


class GetPublishedProblem:
    def __init__(self, reader: PublishedProblemReader) -> None:
        self._reader = reader

    def __call__(self, slug: str) -> PublicProblemProjection:
        snapshot = self._reader.get_current_by_slug(slug)
        if snapshot is None:
            raise PublishedProblemNotFoundError("published problem was not found")
        return project_public_snapshot(snapshot)


def project_public_snapshot(snapshot: PublishedSnapshot) -> PublicProblemProjection:
    payload = snapshot.public_payload
    content = _safe_mapping(payload.get("content"))
    metadata = _safe_mapping(payload.get("metadata"))
    response = _safe_mapping(payload.get("response"))
    allowed_response = {
        "type",
        "choices",
        "unit",
        "absolute_tolerance",
        "language",
        "signature",
        "starter_code",
        "public_tests",
    }
    response_schema = {
        key: _strip_workflow_fields(value)
        for key, value in response.items()
        if key in allowed_response
    }
    return PublicProblemProjection(
        slug=snapshot.slug.value,
        content=_strip_mapping(content),
        metadata=_strip_mapping(metadata),
        response_schema=response_schema,
        published_at=snapshot.published_at,
    )


def _safe_mapping(value: object) -> dict[str, object]:
    return dict(value) if isinstance(value, dict) else {}


def _strip_mapping(value: dict[str, object]) -> dict[str, object]:
    return cast(dict[str, object], _strip_workflow_fields(value))


def _strip_workflow_fields(value: object) -> object:
    if isinstance(value, dict):
        return {
            str(key): _strip_workflow_fields(item)
            for key, item in value.items()
            if not str(key).endswith("_state")
            and str(key)
            not in {
                "revision_id",
                "editorial_status",
                "validation_summary",
                "author_issues",
                "internal_notes",
                "object_key",
            }
        }
    if isinstance(value, list):
        return [_strip_workflow_fields(item) for item in value]
    return value
