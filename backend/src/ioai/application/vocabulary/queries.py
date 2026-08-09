from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ioai.domain.vocabulary.values import (
    VocabularyIdentity,
    VocabularyRecord,
    VocabularyType,
)


@dataclass(frozen=True, slots=True)
class VocabularyQuery:
    vocabulary_type: str
    search: str | None = None
    root_code: str | None = None
    include_descendants: bool = False
    limit: int = 100

    def __post_init__(self) -> None:
        VocabularyType(self.vocabulary_type)
        if self.search is not None and len(self.search.strip()) > 200:
            raise ValueError("search must be at most 200 characters")
        if self.root_code is not None:
            VocabularyIdentity(VocabularyType(self.vocabulary_type), self.root_code)
        if not 1 <= self.limit <= 500:
            raise ValueError("limit must be between 1 and 500")


class VocabularyReader(Protocol):
    def query(self, query: VocabularyQuery) -> tuple[VocabularyRecord, ...]: ...

    def breadcrumbs(
        self, identity: VocabularyIdentity
    ) -> tuple[VocabularyRecord, ...]: ...


@dataclass(frozen=True, slots=True)
class VocabularyQueryItem:
    record: VocabularyRecord
    breadcrumbs: tuple[VocabularyRecord, ...]


class QueryVocabulary:
    def __init__(self, reader: VocabularyReader) -> None:
        self._reader = reader

    def __call__(
        self, query: VocabularyQuery, *, active_only: bool
    ) -> tuple[VocabularyQueryItem, ...]:
        records = self._reader.query(query)
        if active_only:
            records = tuple(
                record for record in records if record.status.value == "ACTIVE"
            )
        return tuple(
            VocabularyQueryItem(
                record=record,
                breadcrumbs=self._reader.breadcrumbs(record.identity),
            )
            for record in records
        )
