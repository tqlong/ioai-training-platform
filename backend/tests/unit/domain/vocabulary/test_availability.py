from __future__ import annotations

import pytest

from ioai.adapters.vocabulary.runtime import load_generated_vocabulary
from ioai.domain.vocabulary.availability import Release0AvailabilityPolicy
from ioai.domain.vocabulary.values import VocabularyIdentity, VocabularyType


def identity(vocabulary_type: str, code: str) -> VocabularyIdentity:
    return VocabularyIdentity(VocabularyType(vocabulary_type), code)


@pytest.mark.parametrize(
    ("vocabulary_type", "codes"),
    [
        ("PATHWAY_STAGE", {"AI_1_FOUNDATIONS", "AI_2_COMPETITION_FOUNDATIONS"}),
        (
            "TASK_TYPE",
            {
                "QUIZ_SINGLE",
                "QUIZ_MULTIPLE",
                "NUMERIC_ANSWER",
                "SHORT_ANSWER",
                "CODE_FUNCTION",
            },
        ),
        ("COMPUTE_TIER", {"NONE", "BROWSER", "CPU_LIGHT"}),
        (
            "SCORING_METHOD",
            {"EXACT_MATCH", "UNIT_TESTS", "PARTIAL_TESTS", "RUBRIC_HUMAN"},
        ),
    ],
)
def test_policy_allows_exact_release_zero_values(
    vocabulary_type: str, codes: set[str]
) -> None:
    policy = Release0AvailabilityPolicy()

    decisions = {
        code: policy.evaluate(identity(vocabulary_type, code)) for code in codes
    }

    assert all(decision.is_available for decision in decisions.values())
    assert {decision.reason_code for decision in decisions.values()} == {"AVAILABLE"}


@pytest.mark.parametrize(
    ("vocabulary_type", "code"),
    [
        ("PATHWAY_STAGE", "AI_3_HIGHSCHOOL"),
        ("TASK_TYPE", "MODEL_TRAINING"),
        ("COMPUTE_TIER", "GPU_LIGHT"),
        ("SCORING_METHOD", "RANK_BASED"),
    ],
)
def test_policy_blocks_future_canonical_values_without_removing_them(
    vocabulary_type: str, code: str
) -> None:
    records = load_generated_vocabulary()
    policy = Release0AvailabilityPolicy()

    assert any(record.identity == identity(vocabulary_type, code) for record in records)
    decision = policy.evaluate(identity(vocabulary_type, code))

    assert decision.is_available is False
    assert decision.reason_code == "UNAVAILABLE_IN_RELEASE_0"
    assert "Release 0" in decision.message


def test_policy_allows_unrestricted_canonical_dimensions() -> None:
    decision = Release0AvailabilityPolicy().evaluate(
        identity("TOPIC", "ML_LOGISTIC_REGRESSION")
    )

    assert decision.is_available is True
    assert decision.reason_code == "AVAILABLE"


def test_none_modality_is_mutually_exclusive_with_actual_modalities() -> None:
    policy = Release0AvailabilityPolicy()

    allowed_none = policy.evaluate_modalities((identity("DATA_MODALITY", "NONE"),))
    allowed_actual = policy.evaluate_modalities(
        (identity("DATA_MODALITY", "TEXT"), identity("DATA_MODALITY", "IMAGE"))
    )
    denied = policy.evaluate_modalities(
        (identity("DATA_MODALITY", "NONE"), identity("DATA_MODALITY", "TEXT"))
    )

    assert allowed_none.is_available is True
    assert allowed_actual.is_available is True
    assert denied.is_available is False
    assert denied.reason_code == "MODALITY_NONE_EXCLUSIVE"


def test_modality_policy_rejects_wrong_composite_type() -> None:
    decision = Release0AvailabilityPolicy().evaluate_modalities(
        (identity("TOPIC", "NONE"),)
    )

    assert decision.is_available is False
    assert decision.reason_code == "INVALID_POLICY_DIMENSION"
