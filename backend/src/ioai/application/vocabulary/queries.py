from __future__ import annotations

from dataclasses import dataclass

from ioai.domain.vocabulary.values import VocabularyType


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
            from ioai.domain.vocabulary.values import VocabularyIdentity

            VocabularyIdentity(VocabularyType(self.vocabulary_type), self.root_code)
        if not 1 <= self.limit <= 500:
            raise ValueError("limit must be between 1 and 500")
