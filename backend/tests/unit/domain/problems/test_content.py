from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from ioai.domain.problems.content import (
    ContentBlock,
    ContentBlockKind,
    LearningObjective,
    LocalizedText,
    ProblemContent,
    TranslationState,
)
from ioai.domain.problems.errors import InvalidProblemContentError
from ioai.domain.problems.identity import ProblemId, RevisionId, StableSlug
from ioai.domain.problems.workflow import EditorialStatus


def test_problem_and_revision_ids_are_distinct_immutable_values() -> None:
    problem_id = ProblemId("problem-01")
    revision_id = RevisionId("revision-01")

    assert problem_id.value == "problem-01"
    assert revision_id.value == "revision-01"
    assert problem_id != revision_id

    with pytest.raises(FrozenInstanceError):
        problem_id.value = "changed"


@pytest.mark.parametrize("value", ["", " ", "contains spaces", "a" * 129])
def test_internal_ids_reject_invalid_values(value: str) -> None:
    with pytest.raises(InvalidProblemContentError):
        ProblemId(value)


def test_slug_is_normalized_once_and_rejects_invalid_public_shapes() -> None:
    assert StableSlug.from_title("  Confusion Matrix: Basics! ").value == (
        "confusion-matrix-basics"
    )
    assert StableSlug("confusion-matrix-basics").value == "confusion-matrix-basics"

    for value in ("Confusion Matrix", "-leading", "trailing-", "a--b", ""):
        with pytest.raises(InvalidProblemContentError):
            StableSlug(value)


def test_localized_text_preserves_both_languages_and_pending_state() -> None:
    text = LocalizedText(
        en=" Calculate a metric. ",
        vi="",
        vi_state=TranslationState.PENDING,
    )

    assert text.en == "Calculate a metric."
    assert text.vi == ""
    assert text.pending_languages == ("vi",)

    with pytest.raises(InvalidProblemContentError, match="marked pending"):
        LocalizedText(en="Calculate.", vi="")
    with pytest.raises(InvalidProblemContentError, match="cannot be pending"):
        LocalizedText(
            en="Calculate.",
            vi="Tính toán.",
            vi_state=TranslationState.PENDING,
        )


@pytest.mark.parametrize(
    "objective",
    [
        "Know precision and recall.",
        "Learn how classification works.",
        "Understand confusion matrices.",
        "Be familiar with F1-score.",
        "Precision and recall.",
    ],
)
def test_learning_objective_retains_vague_or_nonobservable_english_for_validation(
    objective: str,
) -> None:
    value = LearningObjective(LocalizedText(en=objective, vi="", vi_state="PENDING"))

    assert value.is_observable is False


def test_problem_content_keeps_structured_blocks_in_learner_reading_order() -> None:
    content = ProblemContent(
        title=LocalizedText(en="Metrics", vi="Độ đo"),
        summary=LocalizedText(en="Calculate metrics.", vi="Tính độ đo."),
        objectives=(
            LearningObjective(
                LocalizedText(
                    en="Calculate precision from a confusion matrix.",
                    vi="Tính precision từ ma trận nhầm lẫn.",
                )
            ),
        ),
        blocks=(
            ContentBlock(
                kind=ContentBlockKind.STATEMENT,
                content=LocalizedText(en="Given predictions...", vi="Cho dự đoán..."),
                order=1,
            ),
            ContentBlock(
                kind=ContentBlockKind.EXAMPLE,
                content=LocalizedText(en="Example one", vi="Ví dụ một"),
                order=2,
            ),
            ContentBlock(
                kind=ContentBlockKind.HINT,
                content=LocalizedText(en="Count positives", vi="Đếm mẫu dương"),
                order=3,
                reveal_order=1,
            ),
        ),
    )

    assert [block.kind for block in content.blocks] == [
        ContentBlockKind.STATEMENT,
        ContentBlockKind.EXAMPLE,
        ContentBlockKind.HINT,
    ]
    assert content.pending_translation_paths == ()


def test_content_rejects_duplicate_order_and_hint_without_reveal_order() -> None:
    title = LocalizedText(en="Metrics", vi="Độ đo")
    statement = ContentBlock(ContentBlockKind.STATEMENT, title, order=1)

    with pytest.raises(InvalidProblemContentError, match="unique"):
        ProblemContent(
            title=title,
            summary=title,
            objectives=(
                LearningObjective(
                    LocalizedText(en="Explain metrics.", vi="Giải thích độ đo.")
                ),
            ),
            blocks=(statement, ContentBlock(ContentBlockKind.EXAMPLE, title, order=1)),
        )
    with pytest.raises(InvalidProblemContentError, match="reveal_order"):
        ContentBlock(ContentBlockKind.HINT, title, order=1)


def test_editorial_status_is_not_learner_task_status() -> None:
    assert EditorialStatus.DRAFT.value == "DRAFT"
    assert {status.value for status in EditorialStatus} == {
        "DRAFT",
        "IN_REVIEW",
        "CHANGES_REQUESTED",
        "APPROVED",
        "PUBLISHED",
        "ARCHIVED",
    }
    assert "COMPLETED" not in {status.value for status in EditorialStatus}


def test_incomplete_pending_objective_can_be_saved_for_later_validation() -> None:
    pending = LocalizedText(
        en="",
        vi="",
        en_state=TranslationState.PENDING,
        vi_state=TranslationState.PENDING,
    )

    content = ProblemContent(
        title=pending,
        summary=pending,
        objectives=(LearningObjective(pending),),
        blocks=(),
    )

    assert content.pending_translation_paths
