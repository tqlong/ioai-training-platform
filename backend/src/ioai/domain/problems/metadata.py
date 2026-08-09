from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

from ioai.domain.vocabulary.availability import Release0AvailabilityPolicy
from ioai.domain.vocabulary.values import VocabularyIdentity

from .errors import InvalidProblemMetadataError

_REFERENCE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:._-]{0,127}$")


class PrerequisiteRelationship(StrEnum):
    REQUIRED = "REQUIRED"
    RECOMMENDED = "RECOMMENDED"
    CO_REQUISITE = "CO_REQUISITE"
    UNLOCKED_BY = "UNLOCKED_BY"


class PrerequisiteTargetType(StrEnum):
    COMPETENCY = "COMPETENCY"
    TOPIC = "TOPIC"
    TASK = "TASK"
    LEARNING_UNIT = "LEARNING_UNIT"


class LearningEvidence(StrEnum):
    INTRODUCED = "INTRODUCED"
    PRACTICED = "PRACTICED"
    APPLIED = "APPLIED"
    PROFICIENT = "PROFICIENT"


@dataclass(frozen=True, slots=True)
class PrerequisiteReference:
    relationship: PrerequisiteRelationship
    target_type: PrerequisiteTargetType
    target_identity: VocabularyIdentity | None = None
    target_id: str | None = None
    minimum_evidence: LearningEvidence | None = None

    def __post_init__(self) -> None:
        canonical_target = self.target_type in {
            PrerequisiteTargetType.COMPETENCY,
            PrerequisiteTargetType.TOPIC,
        }
        if canonical_target:
            if self.target_identity is None or self.target_id is not None:
                raise InvalidProblemMetadataError(
                    "competency/topic prerequisite requires a canonical identity"
                )
            if self.target_identity.vocabulary_type.value != self.target_type.value:
                raise InvalidProblemMetadataError(
                    "prerequisite target type must match canonical identity"
                )
        else:
            if self.target_identity is not None or not self.target_id:
                raise InvalidProblemMetadataError(
                    "task/unit prerequisite requires a stable target id"
                )
            if not _REFERENCE_ID.fullmatch(self.target_id):
                raise InvalidProblemMetadataError(
                    "prerequisite target id must be a bounded stable identifier"
                )


@dataclass(frozen=True, slots=True)
class ExpectedMinutes:
    value: int

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or self.value < 1:
            raise InvalidProblemMetadataError("expected_minutes must be positive")

    @property
    def display_category(self) -> str:
        if self.value <= 10:
            return "MICRO"
        if self.value <= 30:
            return "SHORT"
        if self.value <= 60:
            return "STANDARD"
        if self.value <= 180:
            return "EXTENDED"
        if self.value <= 480:
            return "LONG"
        return "PROJECT"


class NetworkPolicy(StrEnum):
    DENIED = "DENIED"
    ALLOWED = "ALLOWED"


@dataclass(frozen=True, slots=True)
class ResourceLimits:
    compute_tier: VocabularyIdentity
    runtime_class: VocabularyIdentity
    cpu_cores: int
    ram_mb: int
    gpu_count: int
    gpu_vram_mb: int
    storage_mb: int
    runtime_seconds: int
    network_policy: NetworkPolicy

    def __post_init__(self) -> None:
        _require_type("resources.compute_tier", self.compute_tier, "COMPUTE_TIER")
        _require_type("resources.runtime_class", self.runtime_class, "RUNTIME_CLASS")
        numeric = {
            "cpu_cores": self.cpu_cores,
            "ram_mb": self.ram_mb,
            "gpu_count": self.gpu_count,
            "gpu_vram_mb": self.gpu_vram_mb,
            "storage_mb": self.storage_mb,
            "runtime_seconds": self.runtime_seconds,
        }
        if any(isinstance(value, bool) or value < 0 for value in numeric.values()):
            raise InvalidProblemMetadataError("resource limits must be non-negative")
        if self.gpu_count == 0 and self.gpu_vram_mb != 0:
            raise InvalidProblemMetadataError("GPU VRAM requires a positive GPU count")


@dataclass(frozen=True, slots=True)
class PolicyBlocker:
    field: str
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class CurriculumMetadata:
    stage: VocabularyIdentity
    difficulty: VocabularyIdentity
    primary_competency: VocabularyIdentity
    secondary_competencies: tuple[VocabularyIdentity, ...]
    task_type: VocabularyIdentity
    topics: tuple[VocabularyIdentity, ...]
    prerequisites: tuple[PrerequisiteReference, ...]
    modalities: tuple[VocabularyIdentity, ...]
    expected_minutes: ExpectedMinutes
    resources: ResourceLimits

    def __post_init__(self) -> None:
        _require_type("stage", self.stage, "PATHWAY_STAGE")
        _require_type("difficulty", self.difficulty, "DIFFICULTY")
        _require_type("primary_competency", self.primary_competency, "COMPETENCY")
        _require_type("task_type", self.task_type, "TASK_TYPE")
        if len(self.secondary_competencies) > 3:
            raise InvalidProblemMetadataError(
                "a problem may have at most three secondary competencies"
            )
        for competency in self.secondary_competencies:
            _require_type("secondary_competencies", competency, "COMPETENCY")
        competency_codes = {
            self.primary_competency.code,
            *(item.code for item in self.secondary_competencies),
        }
        if len(competency_codes) != 1 + len(self.secondary_competencies):
            raise InvalidProblemMetadataError("competencies cannot contain duplicates")
        if not self.topics:
            raise InvalidProblemMetadataError("a problem requires at least one topic")
        for topic in self.topics:
            _require_type("topics", topic, "TOPIC")
        if len(set(self.topics)) != len(self.topics):
            raise InvalidProblemMetadataError("topics cannot contain duplicates")
        if not self.modalities:
            raise InvalidProblemMetadataError("select at least one data modality")
        for modality in self.modalities:
            _require_type("modalities", modality, "DATA_MODALITY")
        modality_codes = {modality.code for modality in self.modalities}
        if "NONE" in modality_codes and len(modality_codes) > 1:
            raise InvalidProblemMetadataError(
                "NONE data modality cannot be combined with actual modalities"
            )

    def policy_blockers(
        self, policy: Release0AvailabilityPolicy
    ) -> tuple[PolicyBlocker, ...]:
        blockers: list[PolicyBlocker] = []
        for field, identity in (
            ("stage", self.stage),
            ("task_type", self.task_type),
            ("resources.compute_tier", self.resources.compute_tier),
        ):
            decision = policy.evaluate(identity)
            if not decision.is_available:
                blockers.append(
                    PolicyBlocker(field, decision.reason_code, decision.message)
                )
        modality_decision = policy.evaluate_modalities(self.modalities)
        if not modality_decision.is_available:
            blockers.append(
                PolicyBlocker(
                    "modalities",
                    modality_decision.reason_code,
                    modality_decision.message,
                )
            )
        if self.resources.network_policy is NetworkPolicy.ALLOWED:
            blockers.append(
                PolicyBlocker(
                    "resources.network_policy",
                    "NETWORK_UNAVAILABLE_IN_RELEASE_0",
                    "Network access is unavailable for Release 0 assessment.",
                )
            )
        return tuple(blockers)


def _require_type(field: str, identity: VocabularyIdentity, expected_type: str) -> None:
    if identity.vocabulary_type.value != expected_type:
        raise InvalidProblemMetadataError(
            f"{field} must use a {expected_type} canonical identity"
        )
