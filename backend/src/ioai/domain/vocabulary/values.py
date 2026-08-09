from __future__ import annotations

import re
from dataclasses import dataclass

from .errors import (
    InvalidTopicParentError,
    InvalidVocabularyAliasError,
    InvalidVocabularyIdentityError,
    InvalidVocabularyLabelError,
    InvalidVocabularyStatusError,
)
from .normalization import normalize_vocabulary_text

_CANONICAL_CODE = re.compile(r"^[A-Z][A-Z0-9_]*$")


@dataclass(frozen=True, slots=True)
class VocabularyType:
    value: str

    def __post_init__(self) -> None:
        if not _CANONICAL_CODE.fullmatch(self.value):
            raise InvalidVocabularyIdentityError(
                "vocabulary_type must be a non-empty uppercase canonical code"
            )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class VocabularyIdentity:
    vocabulary_type: VocabularyType
    code: str

    def __post_init__(self) -> None:
        if not _CANONICAL_CODE.fullmatch(self.code):
            raise InvalidVocabularyIdentityError(
                "code must be a non-empty uppercase canonical code"
            )


@dataclass(frozen=True, slots=True)
class LocalizedLabels:
    en: str
    vi: str

    def __post_init__(self) -> None:
        for language, label in (("en", self.en), ("vi", self.vi)):
            if not label.strip():
                raise InvalidVocabularyLabelError(
                    f"labels.{language} must be a non-empty string"
                )
        object.__setattr__(self, "en", self.en.strip())
        object.__setattr__(self, "vi", self.vi.strip())


@dataclass(frozen=True, slots=True)
class VocabularyStatus:
    value: str

    def __post_init__(self) -> None:
        if not _CANONICAL_CODE.fullmatch(self.value):
            raise InvalidVocabularyStatusError(
                "status must be a non-empty uppercase canonical code"
            )


@dataclass(frozen=True, slots=True)
class VocabularyRecord:
    identity: VocabularyIdentity
    labels: LocalizedLabels
    aliases: tuple[str, ...]
    status: VocabularyStatus
    parent: VocabularyIdentity | None = None

    def __post_init__(self) -> None:
        normalized_aliases: set[str] = set()
        cleaned_aliases: list[str] = []
        for alias in self.aliases:
            cleaned = alias.strip()
            if not cleaned:
                raise InvalidVocabularyAliasError("aliases must be non-empty strings")
            normalized = normalize_vocabulary_text(cleaned)
            if normalized in normalized_aliases:
                raise InvalidVocabularyAliasError(
                    f"duplicate normalized alias: {cleaned}"
                )
            normalized_aliases.add(normalized)
            cleaned_aliases.append(cleaned)

        object.__setattr__(self, "aliases", tuple(cleaned_aliases))

        if self.parent is None:
            return
        if self.identity.vocabulary_type.value != "TOPIC":
            raise InvalidTopicParentError("only TOPIC records can have a parent")
        if self.parent.vocabulary_type.value != "TOPIC":
            raise InvalidTopicParentError("topic parent identity must be TOPIC")
