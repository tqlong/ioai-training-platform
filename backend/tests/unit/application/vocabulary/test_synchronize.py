from __future__ import annotations

from dataclasses import replace

import pytest

from ioai.application.vocabulary.ports import VocabularyRepository, VocabularyUnitOfWork
from ioai.application.vocabulary.synchronize import SynchronizeVocabulary
from ioai.domain.vocabulary.validation import VocabularyValidationError
from ioai.domain.vocabulary.values import (
    LocalizedLabels,
    VocabularyIdentity,
    VocabularyRecord,
    VocabularyStatus,
    VocabularyType,
)


def record(
    code: str,
    *,
    vocabulary_type: str = "TOPIC",
    en: str | None = None,
) -> VocabularyRecord:
    return VocabularyRecord(
        identity=VocabularyIdentity(VocabularyType(vocabulary_type), code),
        labels=LocalizedLabels(en=en or code, vi=f"VI {code}"),
        aliases=(),
        status=VocabularyStatus("ACTIVE"),
    )


class FakeRepository(VocabularyRepository):
    def __init__(self, initial: tuple[VocabularyRecord, ...] = ()) -> None:
        self.records = {item.identity: item for item in initial}
        self.added: list[VocabularyIdentity] = []
        self.updated: list[VocabularyIdentity] = []

    def list_records(self) -> tuple[VocabularyRecord, ...]:
        return tuple(self.records.values())

    def add(self, item: VocabularyRecord) -> None:
        self.records[item.identity] = item
        self.added.append(item.identity)

    def update(self, item: VocabularyRecord) -> None:
        self.records[item.identity] = item
        self.updated.append(item.identity)


class FakeUnitOfWork(VocabularyUnitOfWork):
    def __init__(self, repository: FakeRepository) -> None:
        self.vocabulary = repository
        self.entries = 0
        self.commits = 0
        self.rollbacks = 0

    def __enter__(self):
        self.entries += 1
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        if exc_type is None:
            self.commits += 1
        else:
            self.rollbacks += 1


def test_sync_adds_then_reports_unchanged_on_repeated_input() -> None:
    repository = FakeRepository()
    unit_of_work = FakeUnitOfWork(repository)
    synchronize = SynchronizeVocabulary(lambda: unit_of_work)
    records = (
        record("AI_1_FOUNDATIONS", vocabulary_type="PATHWAY_STAGE"),
        record("AI_3_HIGHSCHOOL", vocabulary_type="PATHWAY_STAGE"),
    )

    first = synchronize(records)
    second = synchronize(records)

    assert (first.added, first.updated, first.unchanged, first.rejected) == (2, 0, 0, 0)
    assert first.policy_disabled == 1
    assert (second.added, second.updated, second.unchanged) == (0, 0, 2)
    assert unit_of_work.commits == 2


def test_sync_updates_mutable_fields_without_repurposing_identity() -> None:
    original = record("TOPIC_OLD", en="Old label")
    repository = FakeRepository((original,))
    synchronize = SynchronizeVocabulary(lambda: FakeUnitOfWork(repository))
    changed_label = replace(original, labels=LocalizedLabels(en="New label", vi="Moi"))

    updated = synchronize((changed_label,))
    changed_identity = synchronize((record("TOPIC_NEW", en="New label"),))

    assert updated.updated == 1
    assert repository.records[original.identity].labels.en == "New label"
    assert changed_identity.added == 1
    assert original.identity in repository.records
    assert (
        VocabularyIdentity(VocabularyType("TOPIC"), "TOPIC_NEW") in repository.records
    )


def test_sync_validates_complete_input_before_opening_transaction() -> None:
    duplicate = record("TOPIC_DUPLICATE")
    unit_of_work = FakeUnitOfWork(FakeRepository())
    synchronize = SynchronizeVocabulary(lambda: unit_of_work)

    with pytest.raises(VocabularyValidationError, match="duplicate_identity"):
        synchronize((duplicate, duplicate))

    assert unit_of_work.entries == 0
