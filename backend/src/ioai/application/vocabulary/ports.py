from __future__ import annotations

from types import TracebackType
from typing import Protocol, Self

from ioai.domain.vocabulary.values import VocabularyRecord


class VocabularyRepository(Protocol):
    def list_records(self) -> tuple[VocabularyRecord, ...]: ...

    def add(self, record: VocabularyRecord) -> None: ...

    def update(self, record: VocabularyRecord) -> None: ...


class VocabularyUnitOfWork(Protocol):
    vocabulary: VocabularyRepository

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...
