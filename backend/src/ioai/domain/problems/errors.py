from __future__ import annotations


class ProblemDomainError(ValueError):
    """Base error for an invalid problem-domain value."""


class InvalidProblemContentError(ProblemDomainError):
    """Problem identity or authored content violates a domain invariant."""


class InvalidAssessmentConfigurationError(ProblemDomainError):
    """A response or scoring configuration violates an assessment invariant."""
