from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from .content import LocalizedText
from .errors import InvalidAssessmentConfigurationError

_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class ResponseType(StrEnum):
    QUIZ_SINGLE = "QUIZ_SINGLE"
    QUIZ_MULTIPLE = "QUIZ_MULTIPLE"
    NUMERIC_ANSWER = "NUMERIC_ANSWER"
    SHORT_ANSWER = "SHORT_ANSWER"
    CODE_FUNCTION = "CODE_FUNCTION"


@dataclass(frozen=True, slots=True)
class Choice:
    id: str
    content: LocalizedText

    def __post_init__(self) -> None:
        if not _IDENTIFIER.fullmatch(self.id):
            raise InvalidAssessmentConfigurationError(
                "choice id must be a bounded stable identifier"
            )


def _choice_ids(choices: tuple[Choice, ...]) -> frozenset[str]:
    if len(choices) < 2:
        raise InvalidAssessmentConfigurationError(
            "a quiz requires at least two choices"
        )
    ids = frozenset(choice.id for choice in choices)
    if len(ids) != len(choices):
        raise InvalidAssessmentConfigurationError("choice ids must be unique")
    return ids


@dataclass(frozen=True, slots=True)
class QuizSingleResponse:
    choices: tuple[Choice, ...]
    correct_choice_id: str
    response_type: ResponseType = ResponseType.QUIZ_SINGLE

    def __post_init__(self) -> None:
        if self.correct_choice_id not in _choice_ids(self.choices):
            raise InvalidAssessmentConfigurationError(
                "correct_choice_id must identify a known choice"
            )


@dataclass(frozen=True, slots=True)
class QuizMultipleResponse:
    choices: tuple[Choice, ...]
    correct_choice_ids: frozenset[str]
    response_type: ResponseType = ResponseType.QUIZ_MULTIPLE

    def __post_init__(self) -> None:
        ids = _choice_ids(self.choices)
        if not self.correct_choice_ids:
            raise InvalidAssessmentConfigurationError(
                "multiple choice requires at least one correct choice"
            )
        if not self.correct_choice_ids <= ids:
            raise InvalidAssessmentConfigurationError(
                "correct_choice_ids must identify known choices"
            )


@dataclass(frozen=True, slots=True)
class NumericResponse:
    expected: Decimal
    absolute_tolerance: Decimal
    unit: str | None = None
    response_type: ResponseType = ResponseType.NUMERIC_ANSWER

    def __post_init__(self) -> None:
        if not self.expected.is_finite():
            raise InvalidAssessmentConfigurationError("expected value must be finite")
        if not self.absolute_tolerance.is_finite() or self.absolute_tolerance < 0:
            raise InvalidAssessmentConfigurationError(
                "absolute tolerance must be finite and non-negative"
            )
        if self.unit is not None:
            unit = self.unit.strip()
            if not unit or len(unit) > 64:
                raise InvalidAssessmentConfigurationError(
                    "unit must be a bounded non-empty value"
                )
            object.__setattr__(self, "unit", unit)


@dataclass(frozen=True, slots=True)
class ShortAnswerResponse:
    reference_answer: LocalizedText
    accepted_keywords: tuple[str, ...]
    rubric_guidance: str | None
    response_type: ResponseType = ResponseType.SHORT_ANSWER

    def __post_init__(self) -> None:
        keywords = tuple(keyword.strip() for keyword in self.accepted_keywords)
        if any(not keyword for keyword in keywords) or len(set(keywords)) != len(
            keywords
        ):
            raise InvalidAssessmentConfigurationError(
                "accepted keywords must be non-empty and unique"
            )
        guidance = self.rubric_guidance.strip() if self.rubric_guidance else None
        if not keywords and not guidance:
            raise InvalidAssessmentConfigurationError(
                "short answer requires keyword or rubric guidance"
            )
        object.__setattr__(self, "accepted_keywords", keywords)
        object.__setattr__(self, "rubric_guidance", guidance)


@dataclass(frozen=True, slots=True)
class CodeTestCase:
    id: str
    invocation: str
    expected: str

    def __post_init__(self) -> None:
        if not _IDENTIFIER.fullmatch(self.id):
            raise InvalidAssessmentConfigurationError(
                "test id must be a bounded stable identifier"
            )


@dataclass(frozen=True, slots=True)
class CodeFunctionResponse:
    language: str
    signature: str
    starter_code: str
    public_tests: tuple[CodeTestCase, ...]
    hidden_tests: tuple[CodeTestCase, ...]
    rubric_guidance: str | None = None
    response_type: ResponseType = ResponseType.CODE_FUNCTION

    def __post_init__(self) -> None:
        if self.language != "PYTHON":
            raise InvalidAssessmentConfigurationError(
                "Release 0 code functions require PYTHON"
            )
        tests = self.public_tests + self.hidden_tests
        ids = [test.id for test in tests]
        if len(ids) != len(set(ids)):
            raise InvalidAssessmentConfigurationError("test ids must be unique")


ResponseConfiguration = (
    QuizSingleResponse
    | QuizMultipleResponse
    | NumericResponse
    | ShortAnswerResponse
    | CodeFunctionResponse
)


class ScoringMethod(StrEnum):
    EXACT_MATCH = "EXACT_MATCH"
    UNIT_TESTS = "UNIT_TESTS"
    PARTIAL_TESTS = "PARTIAL_TESTS"
    RUBRIC_HUMAN = "RUBRIC_HUMAN"


@dataclass(frozen=True, slots=True)
class ScoringComponent:
    method: ScoringMethod
    weight: Decimal
    configuration: str | None = None

    def __post_init__(self) -> None:
        if not self.weight.is_finite() or self.weight <= 0:
            raise InvalidAssessmentConfigurationError(
                "scoring component weight must be finite and positive"
            )


_METHODS_BY_RESPONSE: dict[ResponseType, frozenset[ScoringMethod]] = {
    ResponseType.QUIZ_SINGLE: frozenset(
        {ScoringMethod.EXACT_MATCH, ScoringMethod.RUBRIC_HUMAN}
    ),
    ResponseType.QUIZ_MULTIPLE: frozenset(
        {ScoringMethod.EXACT_MATCH, ScoringMethod.RUBRIC_HUMAN}
    ),
    ResponseType.NUMERIC_ANSWER: frozenset(
        {ScoringMethod.EXACT_MATCH, ScoringMethod.RUBRIC_HUMAN}
    ),
    ResponseType.SHORT_ANSWER: frozenset(
        {ScoringMethod.EXACT_MATCH, ScoringMethod.RUBRIC_HUMAN}
    ),
    ResponseType.CODE_FUNCTION: frozenset(
        {
            ScoringMethod.UNIT_TESTS,
            ScoringMethod.PARTIAL_TESTS,
            ScoringMethod.RUBRIC_HUMAN,
        }
    ),
}


@dataclass(frozen=True, slots=True)
class ScoringScheme:
    response_type: ResponseType
    components: tuple[ScoringComponent, ...]

    def __post_init__(self) -> None:
        if not self.components:
            raise InvalidAssessmentConfigurationError(
                "scoring requires at least one component"
            )
        invalid = [
            component.method
            for component in self.components
            if component.method not in _METHODS_BY_RESPONSE[self.response_type]
        ]
        if invalid:
            raise InvalidAssessmentConfigurationError(
                f"scoring method {invalid[0]} is not valid for {self.response_type}"
            )
        if self.total_weight != Decimal("1.0"):
            raise InvalidAssessmentConfigurationError(
                "scoring component weights must total exactly 1.0"
            )

    @property
    def total_weight(self) -> Decimal:
        return sum(
            (component.weight for component in self.components), start=Decimal("0")
        )
