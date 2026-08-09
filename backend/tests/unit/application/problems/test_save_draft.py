from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

from ioai.application.problems.authoring import SaveDraft
from ioai.application.problems.errors import RevisionConflictError
from ioai.domain.problems.identity import ProblemId, RevisionId, StableSlug
from ioai.domain.problems.revision import ProblemRevision
from ioai.domain.problems.workflow import EditorialStatus


class FakeRepository:
    def __init__(self, current: ProblemRevision) -> None:
        self.current = current
        self.saved_at: datetime | None = None

    def save(self, revision, expected_version, saved_at):
        if expected_version != self.current.version:
            raise RevisionConflictError(revision.revision_id, self.current.version)
        self.current = replace(revision, version=expected_version + 1)
        self.saved_at = saved_at
        return self.current


class FakeWork:
    def __init__(self, repository: FakeRepository) -> None:
        self.drafts = repository

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return None


def draft(version: int = 1) -> ProblemRevision:
    return ProblemRevision(
        ProblemId("problem-1"),
        RevisionId("revision-1"),
        version,
        None,
        EditorialStatus.DRAFT,
        None,
        None,
        None,
        None,
    )


def test_save_draft_uses_expected_version_and_injected_clock() -> None:
    repository = FakeRepository(draft())
    now = datetime(2026, 8, 9, tzinfo=UTC)
    save = SaveDraft(lambda: FakeWork(repository), lambda: now)

    saved = save(replace(draft(), slug=StableSlug("new-slug")), expected_version=1)

    assert saved.version == 2
    assert saved.slug == StableSlug("new-slug")
    assert repository.saved_at == now


def test_save_draft_preserves_conflict_outcome() -> None:
    repository = FakeRepository(draft(version=2))
    save = SaveDraft(lambda: FakeWork(repository), lambda: datetime.now(UTC))

    try:
        save(draft(), expected_version=1)
    except RevisionConflictError as error:
        assert error.current_version == 2
    else:
        raise AssertionError("stale save should fail")
