from __future__ import annotations

from types import TracebackType
from typing import Self

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from ioai.application.vocabulary.queries import VocabularyQuery
from ioai.domain.vocabulary.normalization import normalize_vocabulary_text
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
        self._records: tuple[VocabularyRecord, ...] | None = None

    def list_records(self) -> tuple[VocabularyRecord, ...]:
        if self._records is not None:
            return self._records
        statement = select(VocabularyRecordModel).order_by(
            VocabularyRecordModel.vocabulary_type,
            VocabularyRecordModel.code,
        )
        self._records = tuple(
            _to_domain(row) for row in self._session.scalars(statement)
        )
        return self._records

    def get(self, identity: VocabularyIdentity) -> VocabularyRecord | None:
        key = (identity.vocabulary_type.value, identity.code)
        row = self._session.get(VocabularyRecordModel, key)
        return _to_domain(row) if row is not None else None

    def query(self, query: VocabularyQuery) -> tuple[VocabularyRecord, ...]:
        records = tuple(
            record
            for record in self.list_records()
            if record.identity.vocabulary_type.value == query.vocabulary_type
        )
        if query.root_code is not None:
            records = _select_hierarchy(records, query)
        if query.search and query.search.strip():
            needle = normalize_vocabulary_text(query.search)
            records = tuple(
                record
                for record in records
                if any(
                    needle in normalize_vocabulary_text(term)
                    for term in (record.labels.en, record.labels.vi, *record.aliases)
                )
            )
        return records[: query.limit]

    def breadcrumbs(self, identity: VocabularyIdentity) -> tuple[VocabularyRecord, ...]:
        by_identity = {record.identity: record for record in self.list_records()}
        current = by_identity.get(identity)
        path: list[VocabularyRecord] = []
        while current is not None:
            path.append(current)
            current = by_identity.get(current.parent) if current.parent else None
        return tuple(reversed(path))

    def add(self, record: VocabularyRecord) -> None:
        self._session.add(_to_model(record))
        self._records = None

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
        self._records = None


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


def _select_hierarchy(
    records: tuple[VocabularyRecord, ...], query: VocabularyQuery
) -> tuple[VocabularyRecord, ...]:
    root_identity = VocabularyIdentity(
        VocabularyType(query.vocabulary_type), query.root_code or ""
    )
    by_identity = {record.identity: record for record in records}
    root = by_identity.get(root_identity)
    if root is None:
        return ()
    if not query.include_descendants:
        return (root,)

    children: dict[VocabularyIdentity, list[VocabularyRecord]] = {}
    for record in records:
        if record.parent is not None:
            children.setdefault(record.parent, []).append(record)
    for siblings in children.values():
        siblings.sort(key=lambda record: record.identity.code)

    ordered = [root]
    pending = [root]
    while pending:
        parent = pending.pop(0)
        descendants = children.get(parent.identity, [])
        ordered.extend(descendants)
        pending.extend(descendants)
    return tuple(ordered)
