from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from ioai.domain.vocabulary.errors import (
    InvalidTopicParentError,
    InvalidVocabularyAliasError,
    InvalidVocabularyIdentityError,
    InvalidVocabularyLabelError,
    InvalidVocabularyStatusError,
)
from ioai.domain.vocabulary.values import (
    LocalizedLabels,
    VocabularyIdentity,
    VocabularyRecord,
    VocabularyStatus,
    VocabularyType,
)


def identity(vocabulary_type: str = "TOPIC", code: str = "ML_CLASSIFICATION"):
    return VocabularyIdentity(VocabularyType(vocabulary_type), code)


def test_identity_is_composite_and_allows_the_same_code_across_types() -> None:
    competency = identity("COMPETENCY", "DL_TRANSFORMERS")
    topic = identity("TOPIC", "DL_TRANSFORMERS")

    assert competency != topic
    assert {competency, topic} == {competency, topic}
    assert competency.code == topic.code


def test_vocabulary_record_preserves_bilingual_labels_aliases_status_and_parent() -> (
    None
):
    parent = identity(code="TOPIC_MACHINE_LEARNING")
    record = VocabularyRecord(
        identity=identity(code="ML_CLASSIFICATION"),
        labels=LocalizedLabels(en="Classification", vi="Phân loại"),
        aliases=("Classifier",),
        status=VocabularyStatus("ACTIVE"),
        parent=parent,
    )

    assert record.labels.en == "Classification"
    assert record.labels.vi == "Phân loại"
    assert record.aliases == ("Classifier",)
    assert record.status.value == "ACTIVE"
    assert record.parent == parent

    with pytest.raises(FrozenInstanceError):
        record.aliases = ()


@pytest.mark.parametrize(
    ("vocabulary_type", "code"),
    [("topic", "ML_CLASSIFICATION"), ("TOPIC", "ml_classification"), ("", "CODE")],
)
def test_identity_rejects_noncanonical_type_or_code(
    vocabulary_type: str, code: str
) -> None:
    with pytest.raises(InvalidVocabularyIdentityError):
        identity(vocabulary_type, code)


@pytest.mark.parametrize(("en", "vi"), [("", "Phân loại"), ("Classification", " ")])
def test_labels_require_nonempty_english_and_vietnamese(en: str, vi: str) -> None:
    with pytest.raises(InvalidVocabularyLabelError):
        LocalizedLabels(en=en, vi=vi)


def test_aliases_reject_empty_and_normalized_duplicates() -> None:
    base = {
        "identity": identity(),
        "labels": LocalizedLabels(en="Classification", vi="Phân loại"),
        "status": VocabularyStatus("ACTIVE"),
    }

    with pytest.raises(InvalidVocabularyAliasError, match="non-empty"):
        VocabularyRecord(**base, aliases=("",))
    with pytest.raises(InvalidVocabularyAliasError, match="duplicate"):
        VocabularyRecord(**base, aliases=("Classifier", " classifier "))


def test_status_requires_a_canonical_uppercase_code() -> None:
    with pytest.raises(InvalidVocabularyStatusError):
        VocabularyStatus("active")


def test_only_topics_can_have_topic_parents() -> None:
    parent = identity(code="TOPIC_MACHINE_LEARNING")
    labels = LocalizedLabels(en="Classification", vi="Phân loại")

    with pytest.raises(InvalidTopicParentError, match="only TOPIC"):
        VocabularyRecord(
            identity=identity("COMPETENCY", "ML_CLASSIFICATION"),
            labels=labels,
            aliases=(),
            status=VocabularyStatus("ACTIVE"),
            parent=parent,
        )
    with pytest.raises(InvalidTopicParentError, match="must be TOPIC"):
        VocabularyRecord(
            identity=identity(),
            labels=labels,
            aliases=(),
            status=VocabularyStatus("ACTIVE"),
            parent=identity("COMPETENCY", "ML_CLASSIFICATION"),
        )
