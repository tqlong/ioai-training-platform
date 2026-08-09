from __future__ import annotations

from dataclasses import dataclass

from .values import VocabularyIdentity


@dataclass(frozen=True, slots=True)
class AvailabilityDecision:
    is_available: bool
    reason_code: str
    message: str


class Release0AvailabilityPolicy:
    """Central Release 0 publication availability for canonical values."""

    _RESTRICTED_VALUES = {
        "PATHWAY_STAGE": frozenset(
            {"AI_1_FOUNDATIONS", "AI_2_COMPETITION_FOUNDATIONS"}
        ),
        "TASK_TYPE": frozenset(
            {
                "QUIZ_SINGLE",
                "QUIZ_MULTIPLE",
                "NUMERIC_ANSWER",
                "SHORT_ANSWER",
                "CODE_FUNCTION",
            }
        ),
        "COMPUTE_TIER": frozenset({"NONE", "BROWSER", "CPU_LIGHT"}),
        "SCORING_METHOD": frozenset(
            {"EXACT_MATCH", "UNIT_TESTS", "PARTIAL_TESTS", "RUBRIC_HUMAN"}
        ),
    }
    _DIFFICULTY_ORDER = (
        "INTRODUCTORY",
        "EASY",
        "MEDIUM",
        "HARD",
        "CHALLENGE",
    )

    def evaluate(self, identity: VocabularyIdentity) -> AvailabilityDecision:
        vocabulary_type = identity.vocabulary_type.value
        enabled = self._RESTRICTED_VALUES.get(vocabulary_type)
        if enabled is not None and identity.code not in enabled:
            return AvailabilityDecision(
                is_available=False,
                reason_code="UNAVAILABLE_IN_RELEASE_0",
                message=f"{identity.code} is canonical but unavailable in Release 0.",
            )
        return _available()

    def evaluate_modalities(
        self, identities: tuple[VocabularyIdentity, ...]
    ) -> AvailabilityDecision:
        if not identities:
            return AvailabilityDecision(
                is_available=False,
                reason_code="EMPTY_MODALITY_SELECTION",
                message="Select NONE or at least one actual data modality.",
            )
        if any(
            identity.vocabulary_type.value != "DATA_MODALITY" for identity in identities
        ):
            return AvailabilityDecision(
                is_available=False,
                reason_code="INVALID_POLICY_DIMENSION",
                message="Modality policy accepts DATA_MODALITY identities only.",
            )

        codes = {identity.code for identity in identities}
        if "NONE" in codes and len(codes) > 1:
            return AvailabilityDecision(
                is_available=False,
                reason_code="MODALITY_NONE_EXCLUSIVE",
                message="NONE cannot be combined with an actual data modality.",
            )
        return _available()

    def difficulty_rank(self, code: str) -> int:
        """Return the Release 0 curriculum order for a canonical difficulty."""
        try:
            return self._DIFFICULTY_ORDER.index(code)
        except ValueError:
            return len(self._DIFFICULTY_ORDER)


def _available() -> AvailabilityDecision:
    return AvailabilityDecision(
        is_available=True,
        reason_code="AVAILABLE",
        message="Available for Release 0.",
    )
