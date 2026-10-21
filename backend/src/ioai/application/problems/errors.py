from __future__ import annotations

from ioai.domain.problems.identity import RevisionId
from ioai.domain.problems.revision import ValidationReport
from ioai.domain.problems.workflow import EditorialStatus


class ProblemApplicationError(RuntimeError):
    """Base application error for author problem commands."""


class DraftNotFoundError(ProblemApplicationError):
    def __init__(self, revision_id: RevisionId) -> None:
        self.revision_id = revision_id
        super().__init__(f"draft revision {revision_id.value} was not found")


class RevisionConflictError(ProblemApplicationError):
    def __init__(self, revision_id: RevisionId, current_version: int) -> None:
        self.revision_id = revision_id
        self.current_version = current_version
        super().__init__(
            f"revision {revision_id.value} has current version {current_version}"
        )


class DraftNotEditableError(ProblemApplicationError):
    def __init__(self, revision_id: RevisionId, status: EditorialStatus) -> None:
        self.revision_id = revision_id
        self.status = status
        super().__init__(
            f"revision {revision_id.value} is in {status.value} "
            "status and cannot be edited"
        )


class DraftValidationError(ProblemApplicationError):
    def __init__(self, report: ValidationReport) -> None:
        self.report = report
        super().__init__("draft has publication-blocking validation errors")


class SuccessorRevisionError(ProblemApplicationError):
    """A new editable revision cannot be created from the requested source."""


class IdempotencyConflictError(ProblemApplicationError):
    """An idempotency key was reused for different command intent."""


class SlugConflictError(ProblemApplicationError):
    """A stable public slug belongs to a different problem."""


class PublishedProblemNotFoundError(ProblemApplicationError):
    """A problem has no current published snapshot for a lifecycle command."""
