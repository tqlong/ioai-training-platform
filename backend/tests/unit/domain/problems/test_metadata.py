from __future__ import annotations

import pytest

from ioai.domain.problems.assessment import ResponseType
from ioai.domain.problems.errors import InvalidProblemMetadataError
from ioai.domain.problems.metadata import (
    CurriculumMetadata,
    ExpectedMinutes,
    LearningEvidence,
    NetworkPolicy,
    PrerequisiteReference,
    PrerequisiteRelationship,
    PrerequisiteTargetType,
    ResourceLimits,
)
from ioai.domain.vocabulary.availability import Release0AvailabilityPolicy
from ioai.domain.vocabulary.values import VocabularyIdentity, VocabularyType


def vid(vocabulary_type: str, code: str) -> VocabularyIdentity:
    return VocabularyIdentity(VocabularyType(vocabulary_type), code)


def valid_metadata(**overrides: object) -> CurriculumMetadata:
    values: dict[str, object] = {
        "stage": vid("PATHWAY_STAGE", "AI_1_FOUNDATIONS"),
        "difficulty": vid("DIFFICULTY", "EASY"),
        "primary_competency": vid("COMPETENCY", "EVAL_METRICS"),
        "secondary_competencies": (),
        "task_type": vid("TASK_TYPE", "QUIZ_SINGLE"),
        "topics": (vid("TOPIC", "ML_CONFUSION_MATRIX"),),
        "prerequisites": (),
        "modalities": (vid("DATA_MODALITY", "NONE"),),
        "expected_minutes": ExpectedMinutes(15),
        "resources": ResourceLimits(
            compute_tier=vid("COMPUTE_TIER", "NONE"),
            runtime_class=vid("RUNTIME_CLASS", "INSTANT"),
            cpu_cores=0,
            ram_mb=0,
            gpu_count=0,
            gpu_vram_mb=0,
            storage_mb=0,
            runtime_seconds=0,
            network_policy=NetworkPolicy.DENIED,
        ),
    }
    values.update(overrides)
    return CurriculumMetadata(**values)  # type: ignore[arg-type]


def test_metadata_preserves_canonical_composite_identities() -> None:
    metadata = valid_metadata(
        secondary_competencies=(vid("COMPETENCY", "MATH_STATISTICS"),),
        prerequisites=(
            PrerequisiteReference(
                relationship=PrerequisiteRelationship.REQUIRED,
                target_type=PrerequisiteTargetType.TOPIC,
                target_identity=vid("TOPIC", "ML_CONFUSION_MATRIX"),
                minimum_evidence=LearningEvidence.APPLIED,
            ),
        ),
    )

    assert metadata.stage.code == "AI_1_FOUNDATIONS"
    assert metadata.task_type.code == ResponseType.QUIZ_SINGLE.value
    assert metadata.prerequisites[0].target_identity.vocabulary_type.value == "TOPIC"


def test_metadata_enforces_vocabulary_types_and_secondary_limit() -> None:
    with pytest.raises(InvalidProblemMetadataError, match="stage"):
        valid_metadata(stage=vid("TOPIC", "AI_1_FOUNDATIONS"))
    with pytest.raises(InvalidProblemMetadataError, match="three"):
        valid_metadata(
            secondary_competencies=tuple(
                vid("COMPETENCY", f"COMP_{index}") for index in range(4)
            )
        )
    with pytest.raises(InvalidProblemMetadataError, match="duplicate"):
        valid_metadata(secondary_competencies=(vid("COMPETENCY", "EVAL_METRICS"),))


def test_prerequisite_target_type_must_match_canonical_identity() -> None:
    with pytest.raises(InvalidProblemMetadataError, match="target type"):
        PrerequisiteReference(
            relationship=PrerequisiteRelationship.REQUIRED,
            target_type=PrerequisiteTargetType.COMPETENCY,
            target_identity=vid("TOPIC", "ML_CONFUSION_MATRIX"),
        )


def test_task_and_learning_unit_prerequisites_use_bounded_stable_ids() -> None:
    prerequisite = PrerequisiteReference(
        relationship=PrerequisiteRelationship.RECOMMENDED,
        target_type=PrerequisiteTargetType.TASK,
        target_id="problem-01",
    )

    assert prerequisite.target_id == "problem-01"

    with pytest.raises(InvalidProblemMetadataError, match="canonical identity"):
        PrerequisiteReference(
            relationship=PrerequisiteRelationship.REQUIRED,
            target_type=PrerequisiteTargetType.TOPIC,
            target_id="free form tag",
        )


def test_expected_minutes_are_positive_and_category_is_derived() -> None:
    assert ExpectedMinutes(10).display_category == "MICRO"
    assert ExpectedMinutes(30).display_category == "SHORT"
    assert ExpectedMinutes(61).display_category == "EXTENDED"
    assert ExpectedMinutes(481).display_category == "PROJECT"

    with pytest.raises(InvalidProblemMetadataError, match="positive"):
        ExpectedMinutes(0)


def test_none_modality_is_mutually_exclusive() -> None:
    with pytest.raises(InvalidProblemMetadataError, match="NONE"):
        valid_metadata(
            modalities=(
                vid("DATA_MODALITY", "NONE"),
                vid("DATA_MODALITY", "TABULAR"),
            )
        )


def test_resources_reject_negative_or_inconsistent_gpu_values() -> None:
    with pytest.raises(InvalidProblemMetadataError, match="non-negative"):
        ResourceLimits(
            compute_tier=vid("COMPUTE_TIER", "CPU_LIGHT"),
            runtime_class=vid("RUNTIME_CLASS", "SHORT"),
            cpu_cores=-1,
            ram_mb=1024,
            gpu_count=0,
            gpu_vram_mb=0,
            storage_mb=100,
            runtime_seconds=30,
            network_policy=NetworkPolicy.DENIED,
        )
    with pytest.raises(InvalidProblemMetadataError, match="GPU VRAM"):
        ResourceLimits(
            compute_tier=vid("COMPUTE_TIER", "CPU_LIGHT"),
            runtime_class=vid("RUNTIME_CLASS", "SHORT"),
            cpu_cores=1,
            ram_mb=1024,
            gpu_count=0,
            gpu_vram_mb=1024,
            storage_mb=100,
            runtime_seconds=30,
            network_policy=NetworkPolicy.DENIED,
        )


def test_release_policy_blocks_unavailable_stage_compute_and_network() -> None:
    policy = Release0AvailabilityPolicy()

    assert valid_metadata().policy_blockers(policy) == ()
    blocked = valid_metadata(
        stage=vid("PATHWAY_STAGE", "AI_3_HIGHSCHOOL"),
        resources=ResourceLimits(
            compute_tier=vid("COMPUTE_TIER", "GPU_LIGHT"),
            runtime_class=vid("RUNTIME_CLASS", "SHORT"),
            cpu_cores=2,
            ram_mb=2048,
            gpu_count=1,
            gpu_vram_mb=2048,
            storage_mb=100,
            runtime_seconds=60,
            network_policy=NetworkPolicy.ALLOWED,
        ),
    )

    assert {blocker.field for blocker in blocked.policy_blockers(policy)} == {
        "stage",
        "resources.compute_tier",
        "resources.network_policy",
    }
