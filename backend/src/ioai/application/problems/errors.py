from __future__ import annotations

from ioai.domain.problems.identity import RevisionId


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
