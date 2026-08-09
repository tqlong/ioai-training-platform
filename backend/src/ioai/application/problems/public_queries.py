from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
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


class PublishedProblemReader(Protocol):
    def list_current(
        self, *, offset: int, limit: int
    ) -> tuple[PublishedSnapshot, ...]: ...

    def get_current_by_slug(self, slug: str) -> PublishedSnapshot | None: ...


class ListPublishedProblems:
    def __init__(self, reader: PublishedProblemReader) -> None:
        self._reader = reader

    def __call__(self, *, offset: int = 0, limit: int = 50):
        return tuple(
            project_public_snapshot(snapshot)
            for snapshot in self._reader.list_current(offset=offset, limit=limit)
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
