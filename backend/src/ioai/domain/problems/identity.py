from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from .errors import InvalidProblemContentError

_INTERNAL_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:._-]{0,127}$")
_STABLE_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _validate_internal_id(value: str, field: str) -> str:
    cleaned = value.strip()
    if not _INTERNAL_ID.fullmatch(cleaned):
        raise InvalidProblemContentError(
            f"{field} must be 1-128 URL-safe non-whitespace characters"
        )
    return cleaned


@dataclass(frozen=True, slots=True)
class ProblemId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "value", _validate_internal_id(self.value, "problem_id")
        )


@dataclass(frozen=True, slots=True)
class RevisionId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "value", _validate_internal_id(self.value, "revision_id")
        )


@dataclass(frozen=True, slots=True)
class StableSlug:
    value: str

    def __post_init__(self) -> None:
        if len(self.value) > 120 or not _STABLE_SLUG.fullmatch(self.value):
            raise InvalidProblemContentError(
                "slug must be a normalized lowercase hyphenated value"
            )

    @classmethod
    def from_title(cls, title: str) -> StableSlug:
        ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore")
        normalized = re.sub(r"[^a-z0-9]+", "-", ascii_title.decode().lower()).strip("-")
        return cls(normalized)
