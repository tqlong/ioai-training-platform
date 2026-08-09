from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from hashlib import sha256
from types import TracebackType
from typing import Protocol, Self

from .errors import IdempotencyConflictError, PublishedProblemNotFoundError
from .learner_records import LearnerAttempt, LearnerOutcome, LearnerRecordRepository
from .public_queries import PublishedProblemReader

ALLOWED_COMPUTE_TIERS = frozenset({"NONE", "BROWSER", "CPU_LIGHT"})


@dataclass(frozen=True, slots=True)
class SubmissionCommand:
    slug: str
    submission_key: str
    response: dict[str, object]

    def __post_init__(self) -> None:
        if not self.slug.strip() or len(self.slug) > 128:
            raise ValueError("slug must be bounded")
        if not self.submission_key.strip() or len(self.submission_key) > 200:
            raise ValueError("submission key must be bounded")
        if len(json.dumps(self.response, ensure_ascii=False).encode()) > 64_000:
            raise ValueError("response must be at most 64000 bytes")


class AssessmentUnitOfWork(Protocol):
    @property
    def published(self) -> PublishedProblemReader: ...

    @property
    def records(self) -> LearnerRecordRepository: ...

    def __enter__(self) -> Self: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...


class CodeEvaluator(Protocol):
    def score(
        self,
        code: str,
        response: dict[str, object],
        method: str,
        limits: dict[str, object],
    ) -> Decimal: ...


class AssessSubmission:
    def __init__(
        self,
        unit_of_work_factory: Callable[[], AssessmentUnitOfWork],
        id_generator: Callable[[], str],
        clock: Callable[[], datetime],
        code_evaluator: CodeEvaluator | None = None,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._id_generator = id_generator
        self._clock = clock
        self._code_evaluator = code_evaluator

    def __call__(self, command: SubmissionCommand) -> LearnerAttempt:
        digest = _digest(command)
        with self._unit_of_work_factory() as work:
            snapshot = work.published.get_current_by_slug(command.slug)
            if snapshot is None:
                raise PublishedProblemNotFoundError("published problem was not found")
            replay = work.records.replay_attempt(
                snapshot.snapshot_id, command.submission_key
            )
            if replay is not None:
                if replay.request_digest != digest:
                    raise IdempotencyConflictError("submission key was reused")
                return replay
            payload = snapshot.public_payload
            response = _mapping(payload.get("response"), "response configuration")
            scoring = _mapping(payload.get("scoring"), "scoring configuration")
            metadata = _mapping(payload.get("metadata"), "metadata")
            resources = _mapping(metadata.get("resources"), "resource limits")
            compute_tier = _identity_code(resources.get("compute_tier"))
            if compute_tier not in ALLOWED_COMPUTE_TIERS:
                raise ValueError("compute tier is unavailable for Release 0 assessment")
            _validate_boundary(command.response, str(response.get("type", "")))
            outcome, result = self._score(
                command.response, response, scoring, resources
            )
            attempt = LearnerAttempt(
                self._id_generator(),
                snapshot.snapshot_id,
                command.submission_key,
                digest,
                outcome,
                result,
                self._clock(),
            )
            work.records.add_attempt(attempt)
            return attempt

    def _score(
        self,
        submitted: dict[str, object],
        response: dict[str, object],
        scoring: dict[str, object],
        limits: dict[str, object],
    ) -> tuple[LearnerOutcome, dict[str, object]]:
        components = scoring.get("components")
        if not isinstance(components, list) or not components:
            raise ValueError("published scoring configuration is malformed")
        if any(
            isinstance(item, dict) and item.get("method") == "RUBRIC_HUMAN"
            for item in components
        ):
            return LearnerOutcome.PENDING_ASSESSMENT, {"status": "PENDING_ASSESSMENT"}
        results: list[dict[str, object]] = []
        total = Decimal("0")
        for raw in components:
            component = _mapping(raw, "scoring component")
            method = str(component.get("method", ""))
            weight = _decimal(component.get("weight"), "scoring weight")
            score = self._component_score(method, submitted, response, limits)
            total += score * weight
            results.append({"method": method, "score": _decimal_text(score)})
        return LearnerOutcome.ACCEPTED_RESULT, {
            "score": _decimal_text(total),
            "passed": total == Decimal("1"),
            "components": results,
        }

    def _component_score(
        self,
        method: str,
        submitted: dict[str, object],
        response: dict[str, object],
        limits: dict[str, object],
    ) -> Decimal:
        response_type = str(response.get("type", ""))
        if method == "EXACT_MATCH":
            return Decimal(int(_exact_match(response_type, submitted, response)))
        if (
            method in {"UNIT_TESTS", "PARTIAL_TESTS"}
            and response_type == "CODE_FUNCTION"
        ):
            if self._code_evaluator is None:
                raise RuntimeError("code assessment dependency is unavailable")
            return self._code_evaluator.score(
                str(submitted["code"]), response, method, limits
            )
        raise ValueError("published scoring method is unsupported")


def _validate_boundary(submitted: dict[str, object], expected_type: str) -> None:
    if submitted.get("type") != expected_type:
        raise ValueError("response type does not match the published problem")
    if expected_type == "QUIZ_SINGLE" and not isinstance(
        submitted.get("choice_id"), str
    ):
        raise ValueError("single choice response requires choice_id")
    if expected_type == "QUIZ_MULTIPLE" and (
        not isinstance(submitted.get("choice_ids"), list) or not submitted["choice_ids"]
    ):
        raise ValueError("multiple choice response requires choice_ids")
    field = {
        "NUMERIC_ANSWER": "value",
        "SHORT_ANSWER": "text",
        "CODE_FUNCTION": "code",
    }.get(expected_type)
    if field and (
        not isinstance(submitted.get(field), str) or not str(submitted[field]).strip()
    ):
        raise ValueError(f"{expected_type.lower()} response is required")


def _exact_match(
    response_type: str, submitted: dict[str, object], configured: dict[str, object]
) -> bool:
    if response_type == "QUIZ_SINGLE":
        return submitted["choice_id"] == configured.get("correct_choice_id")
    if response_type == "QUIZ_MULTIPLE":
        return set(_string_list(submitted.get("choice_ids"))) == set(
            _string_list(configured.get("correct_choice_ids"))
        )
    if response_type == "NUMERIC_ANSWER":
        value = _decimal(submitted["value"], "numeric answer")
        expected = _decimal(configured.get("expected"), "expected numeric answer")
        tolerance = _decimal(configured.get("absolute_tolerance"), "numeric tolerance")
        return abs(value - expected) <= tolerance
    if response_type == "SHORT_ANSWER":
        reference = _mapping(configured.get("reference_answer"), "reference answer")
        return (
            str(submitted["text"]).strip().casefold()
            == str(reference.get("en", "")).strip().casefold()
        )
    return False


def _digest(command: SubmissionCommand) -> str:
    canonical = json.dumps(
        {"slug": command.slug, "response": command.response},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256(canonical.encode()).hexdigest()


def _mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"published {label} is malformed")
    return value


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError("choice IDs must be a list of strings")
    return value


def _identity_code(value: object) -> str:
    if not isinstance(value, list) or len(value) != 2 or not isinstance(value[1], str):
        raise ValueError("published compute tier is malformed")
    return value[1]


def _decimal(value: object, label: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"{label} must be finite decimal") from error
    if not result.is_finite():
        raise ValueError(f"{label} must be finite decimal")
    return result


def _decimal_text(value: Decimal) -> str:
    text = format(value.quantize(Decimal("0.000001")).normalize(), "f")
    return text if "." in text else f"{text}.0"
