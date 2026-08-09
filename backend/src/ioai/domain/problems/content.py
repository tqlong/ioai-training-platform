from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

from .errors import InvalidProblemContentError

_MAX_TEXT_LENGTH = 100_000
_OBSERVABLE_VERBS = frozenset(
    {
        "define",
        "describe",
        "explain",
        "calculate",
        "implement",
        "apply",
        "compare",
        "select",
        "interpret",
        "diagnose",
        "evaluate",
        "design",
        "optimize",
        "justify",
        "reproduce",
        "defend",
    }
)
_VAGUE_OBJECTIVE = re.compile(r"^(know|learn|understand|be familiar with)\b", re.I)


class TranslationState(StrEnum):
    COMPLETE = "COMPLETE"
    PENDING = "PENDING"


@dataclass(frozen=True, slots=True)
class LocalizedText:
    en: str
    vi: str
    en_state: TranslationState | str = TranslationState.COMPLETE
    vi_state: TranslationState | str = TranslationState.COMPLETE

    def __post_init__(self) -> None:
        en_state = TranslationState(self.en_state)
        vi_state = TranslationState(self.vi_state)
        en = self.en.strip()
        vi = self.vi.strip()
        for language, value, state in (
            ("en", en, en_state),
            ("vi", vi, vi_state),
        ):
            if len(value) > _MAX_TEXT_LENGTH:
                raise InvalidProblemContentError(f"{language} content is too long")
            if not value and state is not TranslationState.PENDING:
                raise InvalidProblemContentError(
                    f"missing {language} content must be marked pending"
                )
            if value and state is TranslationState.PENDING:
                raise InvalidProblemContentError(
                    f"completed {language} content cannot be pending"
                )
        object.__setattr__(self, "en", en)
        object.__setattr__(self, "vi", vi)
        object.__setattr__(self, "en_state", en_state)
        object.__setattr__(self, "vi_state", vi_state)

    @property
    def pending_languages(self) -> tuple[str, ...]:
        return tuple(
            language
            for language, state in (("en", self.en_state), ("vi", self.vi_state))
            if state is TranslationState.PENDING
        )


@dataclass(frozen=True, slots=True)
class LearningObjective:
    content: LocalizedText

    def __post_init__(self) -> None:
        english = self.content.en.strip()
        if not english and self.content.en_state is TranslationState.PENDING:
            return
        first_word = english.split(maxsplit=1)[0].lower() if english else ""
        if _VAGUE_OBJECTIVE.match(english) or first_word not in _OBSERVABLE_VERBS:
            raise InvalidProblemContentError(
                "learning objective must begin with an observable verb"
            )


class ContentBlockKind(StrEnum):
    STATEMENT = "STATEMENT"
    PROVIDED_INFORMATION = "PROVIDED_INFORMATION"
    EXAMPLE = "EXAMPLE"
    CONSTRAINT = "CONSTRAINT"
    HINT = "HINT"
    EXPLANATION = "EXPLANATION"
    RECOMMENDED_NEXT = "RECOMMENDED_NEXT"
    FEEDBACK = "FEEDBACK"


@dataclass(frozen=True, slots=True)
class ContentBlock:
    kind: ContentBlockKind
    content: LocalizedText
    order: int
    reveal_order: int | None = None

    def __post_init__(self) -> None:
        if self.order < 1:
            raise InvalidProblemContentError("content block order must be positive")
        if self.kind is ContentBlockKind.HINT:
            if self.reveal_order is None or self.reveal_order < 1:
                raise InvalidProblemContentError(
                    "hint blocks require a positive reveal_order"
                )
        elif self.reveal_order is not None:
            raise InvalidProblemContentError(
                "reveal_order is only valid for hint blocks"
            )


@dataclass(frozen=True, slots=True)
class ProblemContent:
    title: LocalizedText
    summary: LocalizedText
    objectives: tuple[LearningObjective, ...]
    blocks: tuple[ContentBlock, ...]

    def __post_init__(self) -> None:
        orders = [block.order for block in self.blocks]
        if len(orders) != len(set(orders)):
            raise InvalidProblemContentError("content block orders must be unique")
        if orders != sorted(orders):
            raise InvalidProblemContentError(
                "content blocks must be supplied in learner reading order"
            )
        reveal_orders = [
            block.reveal_order
            for block in self.blocks
            if block.kind is ContentBlockKind.HINT
        ]
        if len(reveal_orders) != len(set(reveal_orders)):
            raise InvalidProblemContentError("hint reveal orders must be unique")

    @property
    def pending_translation_paths(self) -> tuple[str, ...]:
        paths: list[str] = []
        for language in self.title.pending_languages:
            paths.append(f"title.{language}")
        for language in self.summary.pending_languages:
            paths.append(f"summary.{language}")
        for index, objective in enumerate(self.objectives):
            for language in objective.content.pending_languages:
                paths.append(f"objectives.{index}.{language}")
        for index, block in enumerate(self.blocks):
            for language in block.content.pending_languages:
                paths.append(f"blocks.{index}.content.{language}")
        return tuple(paths)
