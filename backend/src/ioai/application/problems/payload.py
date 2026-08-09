from __future__ import annotations

from decimal import Decimal
from typing import Any

from ioai.domain.problems.assessment import (
    Choice,
    CodeFunctionResponse,
    CodeTestCase,
    NumericResponse,
    QuizMultipleResponse,
    QuizSingleResponse,
    ResponseConfiguration,
    ResponseType,
    ScoringComponent,
    ScoringMethod,
    ScoringScheme,
    ShortAnswerResponse,
)
from ioai.domain.problems.content import (
    ContentBlock,
    ContentBlockKind,
    LearningObjective,
    LocalizedText,
    ProblemContent,
    TranslationState,
)
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
from ioai.domain.vocabulary.values import VocabularyIdentity, VocabularyType


def encode_revision_payload(
    content: ProblemContent | None,
    metadata: CurriculumMetadata | None,
    response: ResponseConfiguration | None,
    scoring: ScoringScheme | None,
) -> dict[str, Any]:
    return {
        "content": _encode_content(content),
        "metadata": _encode_metadata(metadata),
        "response": _encode_response(response),
        "scoring": _encode_scoring(scoring),
    }


def decode_revision_payload(
    payload: dict[str, object],
) -> tuple[
    ProblemContent | None,
    CurriculumMetadata | None,
    ResponseConfiguration | None,
    ScoringScheme | None,
]:
    return (
        _decode_content(_mapping_or_none(payload.get("content"))),
        _decode_metadata(_mapping_or_none(payload.get("metadata"))),
        _decode_response(_mapping_or_none(payload.get("response"))),
        _decode_scoring(_mapping_or_none(payload.get("scoring"))),
    )


def _encode_localized(value: LocalizedText) -> dict[str, str]:
    return {
        "en": value.en,
        "vi": value.vi,
        "en_state": str(value.en_state),
        "vi_state": str(value.vi_state),
    }


def _decode_localized(value: dict[str, Any]) -> LocalizedText:
    return LocalizedText(
        en=str(value["en"]),
        vi=str(value["vi"]),
        en_state=TranslationState(str(value["en_state"])),
        vi_state=TranslationState(str(value["vi_state"])),
    )


def _encode_content(value: ProblemContent | None) -> dict[str, object] | None:
    if value is None:
        return None
    return {
        "title": _encode_localized(value.title),
        "summary": _encode_localized(value.summary),
        "objectives": [_encode_localized(item.content) for item in value.objectives],
        "blocks": [
            {
                "kind": block.kind.value,
                "content": _encode_localized(block.content),
                "order": block.order,
                "reveal_order": block.reveal_order,
            }
            for block in value.blocks
        ],
    }


def _decode_content(value: dict[str, Any] | None) -> ProblemContent | None:
    if value is None:
        return None
    return ProblemContent(
        title=_decode_localized(value["title"]),
        summary=_decode_localized(value["summary"]),
        objectives=tuple(
            LearningObjective(_decode_localized(item)) for item in value["objectives"]
        ),
        blocks=tuple(
            ContentBlock(
                kind=ContentBlockKind(item["kind"]),
                content=_decode_localized(item["content"]),
                order=int(item["order"]),
                reveal_order=(
                    int(item["reveal_order"])
                    if item.get("reveal_order") is not None
                    else None
                ),
            )
            for item in value["blocks"]
        ),
    )


def _vid(value: VocabularyIdentity) -> list[str]:
    return [value.vocabulary_type.value, value.code]


def _decode_vid(value: list[str]) -> VocabularyIdentity:
    return VocabularyIdentity(VocabularyType(value[0]), value[1])


def _encode_metadata(value: CurriculumMetadata | None) -> dict[str, object] | None:
    if value is None:
        return None
    return {
        "stage": _vid(value.stage),
        "difficulty": _vid(value.difficulty),
        "primary_competency": _vid(value.primary_competency),
        "secondary_competencies": [_vid(item) for item in value.secondary_competencies],
        "task_type": _vid(value.task_type),
        "topics": [_vid(item) for item in value.topics],
        "prerequisites": [
            {
                "relationship": item.relationship.value,
                "target_type": item.target_type.value,
                "target_identity": _vid(item.target_identity)
                if item.target_identity
                else None,
                "target_id": item.target_id,
                "minimum_evidence": item.minimum_evidence.value
                if item.minimum_evidence
                else None,
            }
            for item in value.prerequisites
        ],
        "modalities": [_vid(item) for item in value.modalities],
        "expected_minutes": value.expected_minutes.value,
        "resources": {
            "compute_tier": _vid(value.resources.compute_tier),
            "runtime_class": _vid(value.resources.runtime_class),
            "cpu_cores": value.resources.cpu_cores,
            "ram_mb": value.resources.ram_mb,
            "gpu_count": value.resources.gpu_count,
            "gpu_vram_mb": value.resources.gpu_vram_mb,
            "storage_mb": value.resources.storage_mb,
            "runtime_seconds": value.resources.runtime_seconds,
            "network_policy": value.resources.network_policy.value,
        },
    }


def _decode_metadata(value: dict[str, Any] | None) -> CurriculumMetadata | None:
    if value is None:
        return None
    resources = value["resources"]
    return CurriculumMetadata(
        stage=_decode_vid(value["stage"]),
        difficulty=_decode_vid(value["difficulty"]),
        primary_competency=_decode_vid(value["primary_competency"]),
        secondary_competencies=tuple(
            _decode_vid(item) for item in value["secondary_competencies"]
        ),
        task_type=_decode_vid(value["task_type"]),
        topics=tuple(_decode_vid(item) for item in value["topics"]),
        prerequisites=tuple(
            PrerequisiteReference(
                relationship=PrerequisiteRelationship(item["relationship"]),
                target_type=PrerequisiteTargetType(item["target_type"]),
                target_identity=_decode_vid(item["target_identity"])
                if item.get("target_identity")
                else None,
                target_id=item.get("target_id"),
                minimum_evidence=LearningEvidence(item["minimum_evidence"])
                if item.get("minimum_evidence")
                else None,
            )
            for item in value["prerequisites"]
        ),
        modalities=tuple(_decode_vid(item) for item in value["modalities"]),
        expected_minutes=ExpectedMinutes(int(value["expected_minutes"])),
        resources=ResourceLimits(
            compute_tier=_decode_vid(resources["compute_tier"]),
            runtime_class=_decode_vid(resources["runtime_class"]),
            cpu_cores=int(resources["cpu_cores"]),
            ram_mb=int(resources["ram_mb"]),
            gpu_count=int(resources["gpu_count"]),
            gpu_vram_mb=int(resources["gpu_vram_mb"]),
            storage_mb=int(resources["storage_mb"]),
            runtime_seconds=int(resources["runtime_seconds"]),
            network_policy=NetworkPolicy(resources["network_policy"]),
        ),
    )


def _encode_response(value: ResponseConfiguration | None) -> dict[str, object] | None:
    if value is None:
        return None
    result: dict[str, object] = {"type": value.response_type.value}
    if isinstance(value, (QuizSingleResponse, QuizMultipleResponse)):
        result["choices"] = [
            {"id": item.id, "content": _encode_localized(item.content)}
            for item in value.choices
        ]
        if isinstance(value, QuizSingleResponse):
            result["correct_choice_id"] = value.correct_choice_id
        else:
            result["correct_choice_ids"] = sorted(value.correct_choice_ids)
    elif isinstance(value, NumericResponse):
        result.update(
            expected=str(value.expected),
            absolute_tolerance=str(value.absolute_tolerance),
            unit=value.unit,
        )
    elif isinstance(value, ShortAnswerResponse):
        result.update(
            reference_answer=_encode_localized(value.reference_answer),
            accepted_keywords=list(value.accepted_keywords),
            rubric_guidance=value.rubric_guidance,
        )
    else:
        result.update(
            language=value.language,
            signature=value.signature,
            starter_code=value.starter_code,
            public_tests=[_encode_test(item) for item in value.public_tests],
            hidden_tests=[_encode_test(item) for item in value.hidden_tests],
            rubric_guidance=value.rubric_guidance,
        )
    return result


def _decode_response(value: dict[str, Any] | None) -> ResponseConfiguration | None:
    if value is None:
        return None
    response_type = ResponseType(value["type"])
    if response_type in {ResponseType.QUIZ_SINGLE, ResponseType.QUIZ_MULTIPLE}:
        choices = tuple(
            Choice(item["id"], _decode_localized(item["content"]))
            for item in value["choices"]
        )
        if response_type is ResponseType.QUIZ_SINGLE:
            return QuizSingleResponse(choices, value["correct_choice_id"])
        return QuizMultipleResponse(choices, frozenset(value["correct_choice_ids"]))
    if response_type is ResponseType.NUMERIC_ANSWER:
        return NumericResponse(
            Decimal(value["expected"]),
            Decimal(value["absolute_tolerance"]),
            value.get("unit"),
        )
    if response_type is ResponseType.SHORT_ANSWER:
        return ShortAnswerResponse(
            _decode_localized(value["reference_answer"]),
            tuple(value["accepted_keywords"]),
            value.get("rubric_guidance"),
        )
    return CodeFunctionResponse(
        language=value["language"],
        signature=value["signature"],
        starter_code=value["starter_code"],
        public_tests=tuple(_decode_test(item) for item in value["public_tests"]),
        hidden_tests=tuple(_decode_test(item) for item in value["hidden_tests"]),
        rubric_guidance=value.get("rubric_guidance"),
    )


def _encode_test(value: CodeTestCase) -> dict[str, str]:
    return {"id": value.id, "invocation": value.invocation, "expected": value.expected}


def _decode_test(value: dict[str, Any]) -> CodeTestCase:
    return CodeTestCase(value["id"], value["invocation"], value["expected"])


def _encode_scoring(value: ScoringScheme | None) -> dict[str, object] | None:
    if value is None:
        return None
    return {
        "response_type": value.response_type.value,
        "components": [
            {
                "method": item.method.value,
                "weight": str(item.weight),
                "configuration": item.configuration,
            }
            for item in value.components
        ],
    }


def _decode_scoring(value: dict[str, Any] | None) -> ScoringScheme | None:
    if value is None:
        return None
    return ScoringScheme(
        ResponseType(value["response_type"]),
        tuple(
            ScoringComponent(
                ScoringMethod(item["method"]),
                Decimal(item["weight"]),
                item.get("configuration"),
            )
            for item in value["components"]
        ),
    )


def _mapping_or_none(value: object) -> dict[str, Any] | None:
    return value if isinstance(value, dict) else None
