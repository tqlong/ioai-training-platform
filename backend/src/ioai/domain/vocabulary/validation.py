from __future__ import annotations

from collections.abc import Iterable

from .errors import VocabularyValidationError
from .normalization import normalize_vocabulary_text
from .values import VocabularyIdentity, VocabularyRecord


def validate_vocabulary(
    records: Iterable[VocabularyRecord],
) -> tuple[VocabularyRecord, ...]:
    """Validate collection invariants and return stable identity ordering."""
    ordered = tuple(
        sorted(
            records,
            key=lambda record: (
                record.identity.vocabulary_type.value,
                record.identity.code,
            ),
        )
    )
    by_identity = _index_unique_identities(ordered)
    _validate_topic_parents(ordered, by_identity)
    _validate_topic_cycles(ordered, by_identity)
    _validate_branch_labels(ordered)
    return ordered


def _index_unique_identities(
    records: tuple[VocabularyRecord, ...],
) -> dict[VocabularyIdentity, VocabularyRecord]:
    indexed: dict[VocabularyIdentity, VocabularyRecord] = {}
    for record in records:
        if record.identity in indexed:
            raise VocabularyValidationError(
                f"duplicate_identity: {_display_identity(record.identity)}"
            )
        indexed[record.identity] = record
    return indexed


def _validate_topic_parents(
    records: tuple[VocabularyRecord, ...],
    by_identity: dict[VocabularyIdentity, VocabularyRecord],
) -> None:
    for record in records:
        if record.parent is None:
            continue
        if record.parent == record.identity:
            raise VocabularyValidationError(
                f"self_parent: {_display_identity(record.identity)}"
            )
        if record.parent not in by_identity:
            raise VocabularyValidationError(
                "missing_parent: "
                f"{_display_identity(record.identity)} -> "
                f"{_display_identity(record.parent)}"
            )


def _validate_topic_cycles(
    records: tuple[VocabularyRecord, ...],
    by_identity: dict[VocabularyIdentity, VocabularyRecord],
) -> None:
    for record in records:
        if record.identity.vocabulary_type.value != "TOPIC":
            continue
        chain: list[VocabularyIdentity] = []
        positions: dict[VocabularyIdentity, int] = {}
        current: VocabularyRecord | None = record
        while current is not None:
            identity = current.identity
            if identity in positions:
                cycle = chain[positions[identity] :] + [identity]
                path = " -> ".join(item.code for item in cycle)
                raise VocabularyValidationError(f"topic_cycle: {path}")
            positions[identity] = len(chain)
            chain.append(identity)
            current = by_identity.get(current.parent) if current.parent else None


def _validate_branch_labels(records: tuple[VocabularyRecord, ...]) -> None:
    seen: dict[tuple[str, VocabularyIdentity | None, str], VocabularyIdentity] = {}
    for record in records:
        branch = (record.identity.vocabulary_type.value, record.parent)
        terms = (record.labels.en, record.labels.vi, *record.aliases)
        for term in terms:
            normalized = normalize_vocabulary_text(term)
            key = (*branch, normalized)
            owner = seen.get(key)
            if owner is not None and owner != record.identity:
                raise VocabularyValidationError(
                    "ambiguous_branch_label: "
                    f"{term!r} is shared by {_display_identity(owner)} and "
                    f"{_display_identity(record.identity)}"
                )
            seen[key] = record.identity


def _display_identity(identity: VocabularyIdentity) -> str:
    return f"{identity.vocabulary_type.value}:{identity.code}"
