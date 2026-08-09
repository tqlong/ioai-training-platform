from __future__ import annotations

import pytest

from ioai.domain.vocabulary.validation import (
    VocabularyValidationError,
    validate_vocabulary,
)
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
    vi: str | None = None,
    aliases: tuple[str, ...] = (),
    parent_code: str | None = None,
) -> VocabularyRecord:
    identity = VocabularyIdentity(VocabularyType(vocabulary_type), code)
    parent = (
        VocabularyIdentity(VocabularyType("TOPIC"), parent_code)
        if parent_code is not None
        else None
    )
    return VocabularyRecord(
        identity=identity,
        labels=LocalizedLabels(en=en or code, vi=vi or f"VI {code}"),
        aliases=aliases,
        status=VocabularyStatus("ACTIVE"),
        parent=parent,
    )


def test_validator_returns_records_in_stable_composite_identity_order() -> None:
    records = [
        record("TOPIC_CHILD", parent_code="TOPIC_ROOT"),
        record("COMPETENCY_A", vocabulary_type="COMPETENCY"),
        record("TOPIC_ROOT"),
    ]

    validated = validate_vocabulary(records)

    assert [
        (item.identity.vocabulary_type.value, item.identity.code) for item in validated
    ] == [
        ("COMPETENCY", "COMPETENCY_A"),
        ("TOPIC", "TOPIC_CHILD"),
        ("TOPIC", "TOPIC_ROOT"),
    ]


def test_validator_rejects_duplicate_composite_identity() -> None:
    with pytest.raises(VocabularyValidationError, match="duplicate_identity"):
        validate_vocabulary([record("SAME"), record("SAME", en="Different")])


def test_validator_allows_same_code_and_label_across_vocabulary_types() -> None:
    records = [
        record("DL_TRANSFORMERS", vocabulary_type="COMPETENCY", en="Transformers"),
        record("DL_TRANSFORMERS", vocabulary_type="TOPIC", en="Transformers"),
    ]

    assert len(validate_vocabulary(records)) == 2


def test_validator_rejects_missing_and_self_parent() -> None:
    with pytest.raises(VocabularyValidationError, match="missing_parent"):
        validate_vocabulary([record("TOPIC_CHILD", parent_code="TOPIC_MISSING")])
    with pytest.raises(VocabularyValidationError, match="self_parent"):
        validate_vocabulary([record("TOPIC_SELF", parent_code="TOPIC_SELF")])


def test_validator_rejects_topic_cycle_with_actionable_path() -> None:
    records = [
        record("TOPIC_A", parent_code="TOPIC_C"),
        record("TOPIC_B", parent_code="TOPIC_A"),
        record("TOPIC_C", parent_code="TOPIC_B"),
    ]

    with pytest.raises(
        VocabularyValidationError, match=r"topic_cycle.*TOPIC_A.*TOPIC_C"
    ):
        validate_vocabulary(records)


@pytest.mark.parametrize(
    "second",
    [
        record("TOPIC_TWO", en=" classification ", parent_code="TOPIC_ROOT"),
        record(
            "TOPIC_TWO",
            en="Different",
            aliases=("CLASSIFICATION",),
            parent_code="TOPIC_ROOT",
        ),
    ],
)
def test_validator_rejects_normalized_label_or_alias_ambiguity_within_branch(
    second: VocabularyRecord,
) -> None:
    records = [
        record("TOPIC_ROOT"),
        record("TOPIC_ONE", en="Classification", parent_code="TOPIC_ROOT"),
        second,
    ]

    with pytest.raises(VocabularyValidationError, match="ambiguous_branch_label"):
        validate_vocabulary(records)


def test_validator_allows_same_label_in_different_parent_branches() -> None:
    records = [
        record("TOPIC_ROOT_A"),
        record("TOPIC_ROOT_B"),
        record("TOPIC_CHILD_A", en="Shared", parent_code="TOPIC_ROOT_A"),
        record("TOPIC_CHILD_B", en="Shared", parent_code="TOPIC_ROOT_B"),
    ]

    assert len(validate_vocabulary(records)) == 4
