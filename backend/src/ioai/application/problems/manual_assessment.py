from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from hashlib import sha256
from types import TracebackType
from typing import Protocol, Self

from .learner_records import LearnerAttempt


class AssessmentNotFoundError(Exception):
    pass


class AssessmentConflictError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class AssessmentSelection:
    component_index: int
    criterion_id: str
    level_id: str
    feedback: str | None = None


@dataclass(frozen=True, slots=True)
class AssessmentDecision:
    decision_id: str
    attempt_id: str
    version: int
    selections: tuple[dict[str, object], ...]
    result: dict[str, object]
    overall_feedback: str | None
    correction_reason: str | None
    decided_at: datetime


@dataclass(frozen=True, slots=True)
class AssessmentRecord:
    attempt: LearnerAttempt
    slug: str
    title: dict[str, object]
    snapshot_payload: dict[str, object]
    latest_decision: AssessmentDecision | None = None
    decision_history: tuple[AssessmentDecision, ...] = ()


class ManualAssessmentRepository(Protocol):
    def list_records(
        self, *, status: str, problem: str | None, limit: int, offset: int
    ) -> tuple[AssessmentRecord, ...]: ...

    def get_record(
        self, attempt_id: str, *, lock: bool = False
    ) -> AssessmentRecord | None: ...

    def get_by_receipt(
        self, attempt_id: str, receipt_digest: str
    ) -> AssessmentRecord | None: ...

    def add_decision(self, decision: AssessmentDecision) -> None: ...

    def complete_attempt(self, attempt_id: str, result: dict[str, object]) -> None: ...


class ManualAssessmentUnitOfWork(Protocol):
    @property
    def assessments(self) -> ManualAssessmentRepository: ...

    def __enter__(self) -> Self: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...


class ListManualAssessments:
    def __init__(self, factory: Callable[[], ManualAssessmentUnitOfWork]) -> None:
        self._factory = factory

    def __call__(
        self,
        *,
        status: str = "PENDING",
        problem: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ):
        if status not in {"PENDING", "ASSESSED", "ALL"}:
            raise ValueError("assessment status is invalid")
        if limit < 1 or limit > 100 or offset < 0:
            raise ValueError("assessment pagination is invalid")
        with self._factory() as work:
            return work.assessments.list_records(
                status=status, problem=problem, limit=limit, offset=offset
            )


class GetManualAssessment:
    def __init__(self, factory: Callable[[], ManualAssessmentUnitOfWork]) -> None:
        self._factory = factory

    def __call__(self, attempt_id: str) -> AssessmentRecord:
        with self._factory() as work:
            record = work.assessments.get_record(attempt_id)
            if record is None:
                raise AssessmentNotFoundError("assessment was not found")
            return record


class GetLearnerSubmission:
    def __init__(self, factory: Callable[[], ManualAssessmentUnitOfWork]) -> None:
        self._factory = factory

    def __call__(self, attempt_id: str, receipt: str) -> AssessmentRecord:
        if not receipt or len(receipt) > 200:
            raise AssessmentNotFoundError("submission was not found")
        digest = sha256(receipt.encode()).hexdigest()
        with self._factory() as work:
            record = work.assessments.get_by_receipt(attempt_id, digest)
            if record is None:
                raise AssessmentNotFoundError("submission was not found")
            return record


class ResolveManualAssessment:
    def __init__(
        self,
        factory: Callable[[], ManualAssessmentUnitOfWork],
        id_generator: Callable[[], str],
        clock: Callable[[], datetime],
    ) -> None:
        self._factory = factory
        self._id_generator = id_generator
        self._clock = clock

    def __call__(
        self,
        attempt_id: str,
        selections: tuple[AssessmentSelection, ...],
        *,
        expected_decision_id: str | None = None,
        overall_feedback: str | None = None,
        correction_reason: str | None = None,
    ) -> AssessmentDecision:
        with self._factory() as work:
            record = work.assessments.get_record(attempt_id, lock=True)
            if record is None:
                raise AssessmentNotFoundError("assessment was not found")
            current = record.latest_decision
            if current is not None:
                if expected_decision_id != current.decision_id:
                    raise AssessmentConflictError("assessment decision is stale")
                if not correction_reason or not correction_reason.strip():
                    raise ValueError("a correction reason is required")
            elif expected_decision_id is not None:
                raise AssessmentConflictError("assessment decision is stale")
            result = _calculate_result(record, selections, overall_feedback)
            decision = AssessmentDecision(
                decision_id=self._id_generator(),
                attempt_id=attempt_id,
                version=1 if current is None else current.version + 1,
                selections=tuple(_selection_payload(item) for item in selections),
                result=result,
                overall_feedback=_bounded_optional(
                    overall_feedback, "overall feedback"
                ),
                correction_reason=_bounded_optional(
                    correction_reason, "correction reason"
                ),
                decided_at=self._clock(),
            )
            work.assessments.add_decision(decision)
            work.assessments.complete_attempt(attempt_id, result)
            return decision


def _calculate_result(
    record: AssessmentRecord,
    selections: tuple[AssessmentSelection, ...],
    overall_feedback: str | None,
) -> dict[str, object]:
    scoring = record.snapshot_payload.get("scoring")
    if not isinstance(scoring, dict) or not isinstance(scoring.get("components"), list):
        raise ValueError("published scoring configuration is malformed")
    supplied = {(item.component_index, item.criterion_id): item for item in selections}
    if len(supplied) != len(selections):
        raise ValueError("assessment selections must be unique")
    total = Decimal(str(record.attempt.result.get("automated_score", "0")))
    stored_components = record.attempt.result.get("components", [])
    if not isinstance(stored_components, list):
        raise ValueError("stored automated component results are malformed")
    component_results = list(stored_components)
    criterion_results: list[dict[str, object]] = []
    expected: set[tuple[int, str]] = set()
    for component_index, component in enumerate(scoring["components"]):
        if not isinstance(component, dict) or component.get("method") != "RUBRIC_HUMAN":
            continue
        configuration = component.get("configuration")
        if not isinstance(configuration, dict):
            raise ValueError("published human rubric is malformed")
        maximum = Decimal("0")
        awarded = Decimal("0")
        for criterion in configuration.get("criteria", []):
            criterion_id = str(criterion.get("id", ""))
            key = (component_index, criterion_id)
            expected.add(key)
            selected = supplied.get(key)
            if selected is None:
                raise ValueError("every rubric criterion requires a selection")
            levels = criterion.get("levels", [])
            level = next(
                (item for item in levels if str(item.get("id")) == selected.level_id),
                None,
            )
            if level is None:
                raise ValueError("selected rubric level is invalid")
            criterion_maximum = Decimal(str(criterion["maximum_points"]))
            points = Decimal(str(level["points"]))
            maximum += criterion_maximum
            awarded += points
            criterion_results.append(
                {
                    "component_index": component_index,
                    "criterion_id": criterion_id,
                    "title": criterion.get("title"),
                    "level_id": selected.level_id,
                    "level_label": level.get("label"),
                    "points": str(points),
                    "maximum_points": str(criterion_maximum),
                    "feedback": _bounded_optional(
                        selected.feedback, "criterion feedback"
                    ),
                }
            )
        component_score = awarded / maximum
        weight = Decimal(str(component["weight"]))
        total += component_score * weight
        component_results.append(
            {
                "method": "RUBRIC_HUMAN",
                "score": str(component_score),
                "weight": str(weight),
            }
        )
    if set(supplied) != expected:
        raise ValueError("assessment contains unknown rubric criteria")
    threshold = Decimal(str(scoring.get("pass_threshold", "1.0")))
    return {
        "score": str(total),
        "passed": total >= threshold,
        "components": component_results,
        "criteria": criterion_results,
        "overall_feedback": _bounded_optional(overall_feedback, "overall feedback"),
    }


def _selection_payload(value: AssessmentSelection) -> dict[str, object]:
    return {
        "component_index": value.component_index,
        "criterion_id": value.criterion_id,
        "level_id": value.level_id,
        "feedback": _bounded_optional(value.feedback, "criterion feedback"),
    }


def _bounded_optional(value: str | None, label: str) -> str | None:
    normalized = value.strip() if value else None
    if normalized is not None and len(normalized) > 2000:
        raise ValueError(f"{label} must be at most 2000 characters")
    return normalized
