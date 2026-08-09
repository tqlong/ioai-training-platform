from __future__ import annotations

from types import TracebackType
from typing import Self

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from ioai.domain.vocabulary.values import (
    LocalizedLabels,
    VocabularyIdentity,
    VocabularyRecord,
    VocabularyStatus,
    VocabularyType,
)

from .vocabulary_model import VocabularyRecordModel


class SqlAlchemyVocabularyRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_records(self) -> tuple[VocabularyRecord, ...]:
        statement = select(VocabularyRecordModel).order_by(
            VocabularyRecordModel.vocabulary_type,
            VocabularyRecordModel.code,
        )
        return tuple(_to_domain(row) for row in self._session.scalars(statement))

    def add(self, record: VocabularyRecord) -> None:
        self._session.add(_to_model(record))

    def update(self, record: VocabularyRecord) -> None:
        key = (record.identity.vocabulary_type.value, record.identity.code)
        stored = self._session.get(VocabularyRecordModel, key)
        if stored is None:
            raise LookupError(
                "cannot update missing vocabulary identity "
                f"{record.identity.vocabulary_type.value}:{record.identity.code}"
            )
        stored.label_en = record.labels.en
        stored.label_vi = record.labels.vi
        stored.aliases = list(record.aliases)
        stored.status = record.status.value
        stored.parent_vocabulary_type = (
            record.parent.vocabulary_type.value if record.parent else None
        )
        stored.parent_code = record.parent.code if record.parent else None


class SqlAlchemyVocabularyUnitOfWork:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None
        self._vocabulary: SqlAlchemyVocabularyRepository | None = None

    @property
    def vocabulary(self) -> SqlAlchemyVocabularyRepository:
        if self._vocabulary is None:
            raise RuntimeError("unit of work must be entered before repository access")
        return self._vocabulary

    def __enter__(self) -> Self:
        self._session = self._session_factory()
        self._vocabulary = SqlAlchemyVocabularyRepository(self._session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._session is None:
            return
        try:
            if exc_type is None:
                self._session.commit()
            else:
                self._session.rollback()
        finally:
            self._session.close()
            self._session = None
            self._vocabulary = None


def _to_domain(row: VocabularyRecordModel) -> VocabularyRecord:
    vocabulary_type = VocabularyType(row.vocabulary_type)
    parent = (
        VocabularyIdentity(VocabularyType(row.parent_vocabulary_type), row.parent_code)
        if row.parent_vocabulary_type is not None and row.parent_code is not None
        else None
    )
    return VocabularyRecord(
        identity=VocabularyIdentity(vocabulary_type, row.code),
        labels=LocalizedLabels(en=row.label_en, vi=row.label_vi),
        aliases=tuple(row.aliases),
        status=VocabularyStatus(row.status),
        parent=parent,
    )


def _to_model(record: VocabularyRecord) -> VocabularyRecordModel:
    return VocabularyRecordModel(
        vocabulary_type=record.identity.vocabulary_type.value,
        code=record.identity.code,
        label_en=record.labels.en,
        label_vi=record.labels.vi,
        aliases=list(record.aliases),
        status=record.status.value,
        parent_vocabulary_type=(
            record.parent.vocabulary_type.value if record.parent else None
        ),
        parent_code=record.parent.code if record.parent else None,
    )
