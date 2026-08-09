from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from ioai.domain.vocabulary.availability import Release0AvailabilityPolicy
from ioai.domain.vocabulary.validation import validate_vocabulary
from ioai.domain.vocabulary.values import VocabularyRecord

from .ports import VocabularyUnitOfWork


@dataclass(frozen=True, slots=True)
class SynchronizationResult:
    added: int
    updated: int
    unchanged: int
    rejected: int
    policy_disabled: int


class SynchronizeVocabulary:
    def __init__(
        self,
        unit_of_work_factory: Callable[[], VocabularyUnitOfWork],
        policy: Release0AvailabilityPolicy | None = None,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._policy = policy or Release0AvailabilityPolicy()

    def __call__(
        self, source_records: Iterable[VocabularyRecord]
    ) -> SynchronizationResult:
        records = validate_vocabulary(source_records)
        policy_disabled = sum(
            not self._policy.evaluate(record.identity).is_available
            for record in records
        )
        added = 0
        updated = 0
        unchanged = 0

        with self._unit_of_work_factory() as unit_of_work:
            existing = {
                record.identity: record
                for record in unit_of_work.vocabulary.list_records()
            }
            for record in records:
                stored = existing.get(record.identity)
                if stored is None:
                    unit_of_work.vocabulary.add(record)
                    added += 1
                elif stored != record:
                    unit_of_work.vocabulary.update(record)
                    updated += 1
                else:
                    unchanged += 1

        return SynchronizationResult(
            added=added,
            updated=updated,
            unchanged=unchanged,
            rejected=0,
            policy_disabled=policy_disabled,
        )
