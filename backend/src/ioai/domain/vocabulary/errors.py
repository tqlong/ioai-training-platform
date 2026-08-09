from __future__ import annotations


class VocabularyDomainError(ValueError):
    """Base error for invalid canonical vocabulary values."""


class InvalidVocabularyIdentityError(VocabularyDomainError):
    """A vocabulary type or code is not canonical."""


class InvalidVocabularyLabelError(VocabularyDomainError):
    """A required localized label is invalid."""


class InvalidVocabularyAliasError(VocabularyDomainError):
    """An approved alias is empty or ambiguous within one record."""


class InvalidVocabularyStatusError(VocabularyDomainError):
    """A canonical status code is invalid."""


class InvalidTopicParentError(VocabularyDomainError):
    """A topic parent reference has an invalid vocabulary type."""
