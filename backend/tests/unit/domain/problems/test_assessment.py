from __future__ import annotations

from decimal import Decimal

import pytest

from ioai.domain.problems.assessment import (
    Choice,
    CodeFunctionResponse,
    CodeTestCase,
    HumanRubric,
    NumericResponse,
    QuizMultipleResponse,
    QuizSingleResponse,
    ResponseType,
    RubricCriterion,
    RubricLevel,
    ScoringComponent,
    ScoringMethod,
    ScoringScheme,
    ShortAnswerResponse,
)
from ioai.domain.problems.content import LocalizedText
from ioai.domain.problems.errors import InvalidAssessmentConfigurationError


def choice(code: str) -> Choice:
    return Choice(code, LocalizedText(en=f"Choice {code}", vi=f"Lựa chọn {code}"))


def test_single_choice_requires_one_known_correct_choice() -> None:
    response = QuizSingleResponse(
        choices=(choice("A"), choice("B")), correct_choice_id="A"
    )

    assert response.response_type is ResponseType.QUIZ_SINGLE

    with pytest.raises(InvalidAssessmentConfigurationError, match="known choice"):
        QuizSingleResponse(choices=(choice("A"), choice("B")), correct_choice_id="C")


def test_multiple_choice_requires_a_nonempty_known_subset() -> None:
    response = QuizMultipleResponse(
        choices=(choice("A"), choice("B"), choice("C")),
        correct_choice_ids=frozenset({"A", "C"}),
    )

    assert response.response_type is ResponseType.QUIZ_MULTIPLE

    with pytest.raises(InvalidAssessmentConfigurationError, match="at least one"):
        QuizMultipleResponse(
            choices=(choice("A"), choice("B")), correct_choice_ids=frozenset()
        )


def test_choices_require_unique_ids_and_at_least_two_options() -> None:
    with pytest.raises(InvalidAssessmentConfigurationError, match="at least two"):
        QuizSingleResponse(choices=(choice("A"),), correct_choice_id="A")
    with pytest.raises(InvalidAssessmentConfigurationError, match="unique"):
        QuizSingleResponse(choices=(choice("A"), choice("A")), correct_choice_id="A")


def test_numeric_response_uses_exact_decimal_values_and_tolerance() -> None:
    response = NumericResponse(
        expected=Decimal("0.333333"),
        absolute_tolerance=Decimal("0.000001"),
        unit="ratio",
    )

    assert response.response_type is ResponseType.NUMERIC_ANSWER
    assert response.absolute_tolerance == Decimal("0.000001")

    with pytest.raises(InvalidAssessmentConfigurationError, match="non-negative"):
        NumericResponse(Decimal("1"), Decimal("-0.1"))


def test_short_answer_requires_reference_and_assessment_guidance() -> None:
    response = ShortAnswerResponse(
        reference_answer=LocalizedText(en="Precision", vi="Độ chính xác"),
        accepted_keywords=("precision",),
        rubric_guidance=None,
    )

    assert response.response_type is ResponseType.SHORT_ANSWER

    with pytest.raises(InvalidAssessmentConfigurationError, match="guidance"):
        ShortAnswerResponse(
            reference_answer=LocalizedText(en="Precision", vi="Độ chính xác"),
            accepted_keywords=(),
            rubric_guidance=None,
        )


def test_code_function_requires_python_signature_starter_and_tests() -> None:
    response = CodeFunctionResponse(
        language="PYTHON",
        signature="def f1_score(tp: int, fp: int, fn: int) -> float:",
        starter_code="def f1_score(tp, fp, fn):\n    pass",
        public_tests=(CodeTestCase("public-1", "f1_score(1, 0, 0)", "1.0"),),
        hidden_tests=(CodeTestCase("hidden-1", "f1_score(0, 1, 1)", "0.0"),),
        rubric_guidance="Return a finite float.",
    )

    assert response.response_type is ResponseType.CODE_FUNCTION
    assert response.language == "PYTHON"

    with pytest.raises(InvalidAssessmentConfigurationError, match="PYTHON"):
        CodeFunctionResponse(
            language="JAVASCRIPT",
            signature="function score()",
            starter_code="function score() {}",
            public_tests=(CodeTestCase("one", "score()", "1"),),
            hidden_tests=(),
        )


def test_scoring_weights_total_exactly_one() -> None:
    scheme = ScoringScheme(
        ResponseType.CODE_FUNCTION,
        (
            ScoringComponent(ScoringMethod.UNIT_TESTS, Decimal("0.7")),
            ScoringComponent(ScoringMethod.PARTIAL_TESTS, Decimal("0.3")),
        ),
    )

    assert scheme.total_weight == Decimal("1.0")

    with pytest.raises(InvalidAssessmentConfigurationError, match="exactly 1.0"):
        ScoringScheme(
            ResponseType.CODE_FUNCTION,
            (ScoringComponent(ScoringMethod.UNIT_TESTS, Decimal("0.99")),),
        )


def test_scoring_method_must_apply_to_response_type() -> None:
    with pytest.raises(InvalidAssessmentConfigurationError, match="not valid"):
        ScoringScheme(
            ResponseType.QUIZ_SINGLE,
            (ScoringComponent(ScoringMethod.UNIT_TESTS, Decimal("1.0")),),
        )
    with pytest.raises(InvalidAssessmentConfigurationError, match="positive"):
        ScoringComponent(ScoringMethod.EXACT_MATCH, Decimal("0"))


def test_human_scoring_requires_a_structured_point_level_rubric() -> None:
    criterion = RubricCriterion(
        id="reasoning",
        title=LocalizedText(en="Reasoning", vi="", vi_state="PENDING"),
        description=LocalizedText(
            en="Explains why precision uses predicted positives.",
            vi="",
            vi_state="PENDING",
        ),
        maximum_points=Decimal("2"),
        levels=(
            RubricLevel(
                "not-yet",
                LocalizedText(en="Not yet", vi="", vi_state="PENDING"),
                LocalizedText(
                    en="Does not explain the denominator.",
                    vi="",
                    vi_state="PENDING",
                ),
                Decimal("0"),
            ),
            RubricLevel(
                "complete",
                LocalizedText(en="Complete", vi="", vi_state="PENDING"),
                LocalizedText(
                    en="Correctly explains the denominator.",
                    vi="",
                    vi_state="PENDING",
                ),
                Decimal("2"),
            ),
        ),
    )
    rubric = HumanRubric((criterion,), reviewer_guidance="Check the reasoning.")
    component = ScoringComponent(ScoringMethod.RUBRIC_HUMAN, Decimal("1.0"), rubric)

    assert rubric.maximum_points == Decimal("2")
    assert component.configuration is rubric

    with pytest.raises(InvalidAssessmentConfigurationError, match="structured rubric"):
        ScoringComponent(ScoringMethod.RUBRIC_HUMAN, Decimal("1.0"), None)


def test_rubric_levels_include_unique_zero_and_maximum_points() -> None:
    text = LocalizedText(en="Observable result", vi="", vi_state="PENDING")

    with pytest.raises(InvalidAssessmentConfigurationError, match="zero and maximum"):
        RubricCriterion(
            "criterion",
            text,
            text,
            Decimal("2"),
            (
                RubricLevel("partial", text, text, Decimal("1")),
                RubricLevel("full", text, text, Decimal("2")),
            ),
        )


def test_scoring_threshold_defaults_to_one_and_accepts_decimal_boundary() -> None:
    component = ScoringComponent(ScoringMethod.EXACT_MATCH, Decimal("1.0"))

    assert ScoringScheme(
        ResponseType.QUIZ_SINGLE, (component,)
    ).pass_threshold == Decimal("1.0")
    assert ScoringScheme(
        ResponseType.QUIZ_SINGLE, (component,), Decimal("0.75")
    ).pass_threshold == Decimal("0.75")

    with pytest.raises(InvalidAssessmentConfigurationError, match="pass threshold"):
        ScoringScheme(ResponseType.QUIZ_SINGLE, (component,), Decimal("1.01"))
