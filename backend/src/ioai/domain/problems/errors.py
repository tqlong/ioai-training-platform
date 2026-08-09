from __future__ import annotations


class ProblemDomainError(ValueError):
    """Base error for an invalid problem-domain value."""


class InvalidProblemContentError(ProblemDomainError):
    """Problem identity or authored content violates a domain invariant."""


class InvalidAssessmentConfigurationError(ProblemDomainError):
    """A response or scoring configuration violates an assessment invariant."""


class InvalidProblemMetadataError(ProblemDomainError):
    """Curriculum, prerequisite, or resource metadata is invalid."""


class InvalidEditorialTransitionError(ProblemDomainError):
    """An editorial state change is not part of the Release 0 workflow."""


class InvalidTransitionNoteError(ProblemDomainError):
    """An editorial decision note is missing or exceeds its safe bound."""
