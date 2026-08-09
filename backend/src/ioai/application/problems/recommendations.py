from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ioai.domain.vocabulary.availability import Release0AvailabilityPolicy
from ioai.domain.vocabulary.values import VocabularyIdentity, VocabularyType

from .publication import PublishedSnapshot

_EVIDENCE_ORDER = ("INTRODUCED", "PRACTICED", "APPLIED", "PROFICIENT")
_MAX_HISTORY = 50
_MAX_EVIDENCE = 100


@dataclass(frozen=True, slots=True)
class LearningEvidenceContext:
    vocabulary_type: str
    code: str
    level: str

    def __post_init__(self) -> None:
        VocabularyIdentity(VocabularyType(self.vocabulary_type), self.code)
        if self.level not in _EVIDENCE_ORDER:
            raise ValueError("learning evidence level is invalid")


@dataclass(frozen=True, slots=True)
class RecommendationContext:
    stage: str
    current_slug: str | None = None
    completed_slugs: tuple[str, ...] = ()
    evidence: tuple[LearningEvidenceContext, ...] = ()

    def __post_init__(self) -> None:
        VocabularyIdentity(VocabularyType("PATHWAY_STAGE"), self.stage)
        if len(self.completed_slugs) > _MAX_HISTORY:
            raise ValueError(
                f"completed history must contain at most {_MAX_HISTORY} items"
            )
        if len(self.evidence) > _MAX_EVIDENCE:
            raise ValueError(f"evidence must contain at most {_MAX_EVIDENCE} items")
        normalized = tuple(dict.fromkeys(slug.strip() for slug in self.completed_slugs))
        if any(not slug or len(slug) > 120 for slug in normalized):
            raise ValueError("completed history contains an invalid public slug")
        object.__setattr__(self, "completed_slugs", normalized)
        if self.current_slug is not None:
            current = self.current_slug.strip()
            if not current or len(current) > 120:
                raise ValueError("current public slug is invalid")
            object.__setattr__(self, "current_slug", current)


@dataclass(frozen=True, slots=True)
class ProblemRecommendation:
    slug: str
    title: dict[str, str]
    stage_code: str
    difficulty_code: str
    expected_minutes: int
    compute_tier_code: str
    label: str
    reason: str

    @property
    def permanent_url(self) -> str:
        return f"/problems/{self.slug}"


class RecommendationCandidateReader(Protocol):
    def recommendation_candidates(
        self, stage: str
    ) -> tuple[PublishedSnapshot, ...]: ...


class RecommendNextProblem:
    def __init__(self, reader: RecommendationCandidateReader) -> None:
        self._reader = reader

    def __call__(self, context: RecommendationContext) -> ProblemRecommendation | None:
        candidates = sorted(
            self._reader.recommendation_candidates(context.stage),
            key=_candidate_order,
        )
        has_history = bool(context.completed_slugs or context.evidence)
        for candidate in candidates:
            slug = candidate.slug.value
            if has_history and slug in context.completed_slugs:
                continue
            if context.current_slug is not None and slug == context.current_slug:
                continue
            if has_history and not _prerequisites_satisfied(candidate, context):
                continue
            return _recommendation(candidate, has_history=has_history)
        return None


def _candidate_order(snapshot: PublishedSnapshot) -> tuple[int, int, str]:
    metadata = _mapping(snapshot.public_payload.get("metadata"))
    editorial_order = metadata.get("editorial_order")
    normalized_order = editorial_order if isinstance(editorial_order, int) else 2**31
    difficulty = _identity_code(metadata.get("difficulty")) or ""
    return (
        normalized_order,
        Release0AvailabilityPolicy().difficulty_rank(difficulty),
        snapshot.problem_id.value,
    )


def _prerequisites_satisfied(
    snapshot: PublishedSnapshot, context: RecommendationContext
) -> bool:
    metadata = _mapping(snapshot.public_payload.get("metadata"))
    prerequisites = metadata.get("prerequisites")
    if not isinstance(prerequisites, list):
        return True
    evidence = {
        (item.vocabulary_type, item.code): _EVIDENCE_ORDER.index(item.level)
        for item in context.evidence
    }
    for value in prerequisites:
        prerequisite = _mapping(value)
        if prerequisite.get("relationship") != "REQUIRED":
            continue
        target_type = prerequisite.get("target_type")
        if target_type == "TASK":
            target_id = prerequisite.get("target_id")
            if (
                not isinstance(target_id, str)
                or target_id not in context.completed_slugs
            ):
                return False
            continue
        target = prerequisite.get("target_identity")
        if not isinstance(target, list) or len(target) != 2:
            return False
        vocabulary_type, code = target
        if not isinstance(vocabulary_type, str) or not isinstance(code, str):
            return False
        minimum = prerequisite.get("minimum_evidence") or "INTRODUCED"
        if not isinstance(minimum, str) or minimum not in _EVIDENCE_ORDER:
            return False
        if evidence.get((vocabulary_type, code), -1) < _EVIDENCE_ORDER.index(minimum):
            return False
    return True


def _recommendation(
    snapshot: PublishedSnapshot, *, has_history: bool
) -> ProblemRecommendation:
    content = _mapping(snapshot.public_payload.get("content"))
    metadata = _mapping(snapshot.public_payload.get("metadata"))
    resources = _mapping(metadata.get("resources"))
    title = _mapping(content.get("title"))
    title_en = title.get("en")
    title_vi = title.get("vi")
    minutes = metadata.get("expected_minutes")
    if not isinstance(title_en, str) or not isinstance(title_vi, str):
        raise ValueError("published recommendation title is malformed")
    if not isinstance(minutes, int) or minutes < 1:
        raise ValueError("published recommendation time is malformed")
    return ProblemRecommendation(
        slug=snapshot.slug.value,
        title={"en": title_en, "vi": title_vi},
        stage_code=_required_identity_code(metadata.get("stage")),
        difficulty_code=_required_identity_code(metadata.get("difficulty")),
        expected_minutes=minutes,
        compute_tier_code=_required_identity_code(resources.get("compute_tier")),
        label="Recommended next" if has_history else "Recommended start",
        reason=(
            "Matches your stage and editorial path with available prerequisites."
            if has_history
            else "First published problem in this stage."
        ),
    )


def _mapping(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def _identity_code(value: object) -> str | None:
    if isinstance(value, list) and len(value) == 2 and isinstance(value[1], str):
        return value[1]
    return None


def _required_identity_code(value: object) -> str:
    code = _identity_code(value)
    if code is None:
        raise ValueError("published recommendation metadata is malformed")
    return code
