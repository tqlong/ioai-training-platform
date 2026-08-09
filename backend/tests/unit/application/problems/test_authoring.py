from __future__ import annotations

from datetime import UTC, datetime

import pytest

from ioai.adapters.database.problem_repository import StoredDraftSummary
from ioai.application.problems.authoring import (
    CreateDraft,
    GetDraft,
    ListDrafts,
)
from ioai.application.problems.errors import DraftNotFoundError
from ioai.domain.problems.identity import ProblemId, RevisionId
from ioai.domain.problems.revision import ProblemRevision
from ioai.domain.problems.workflow import EditorialStatus


class FakeDraftRepository:
    def __init__(self) -> None:
        self.items: dict[RevisionId, ProblemRevision] = {}
        self.summaries: tuple[StoredDraftSummary, ...] = ()
        self.created_at: datetime | None = None

    def create(self, revision: ProblemRevision, created_at: datetime) -> None:
        self.items[revision.revision_id] = revision
        self.created_at = created_at

    def get(self, revision_id: RevisionId) -> ProblemRevision:
        try:
            return self.items[revision_id]
        except KeyError:
            raise DraftNotFoundError(revision_id) from None

    def list(self) -> tuple[StoredDraftSummary, ...]:
        return self.summaries

    def save(self, revision, expected_version, saved_at):
        raise NotImplementedError


class FakeUnitOfWork:
    def __init__(self, repository: FakeDraftRepository) -> None:
        self.drafts = repository
        self.commits = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        if exc_type is None:
            self.commits += 1


def test_create_draft_allocates_both_identities_atomically() -> None:
    repository = FakeDraftRepository()
    work = FakeUnitOfWork(repository)
    now = datetime(2026, 8, 9, tzinfo=UTC)
    ids = iter(["problem-fixed", "revision-fixed"])
    create = CreateDraft(
        unit_of_work_factory=lambda: work,
        id_generator=lambda: next(ids),
        clock=lambda: now,
    )

    created = create()

    assert created.problem_id == ProblemId("problem-fixed")
    assert created.revision_id == RevisionId("revision-fixed")
    assert created.version == 1
    assert created.status is EditorialStatus.DRAFT
    assert created.slug is None
    assert created.content is None
    assert repository.created_at == now
    assert work.commits == 1


def test_list_drafts_returns_stable_author_projection() -> None:
    repository = FakeDraftRepository()
    work = FakeUnitOfWork(repository)
    first = datetime(2026, 8, 9, 1, tzinfo=UTC)
    second = datetime(2026, 8, 9, 2, tzinfo=UTC)
    repository.summaries = (
        StoredDraftSummary(
            ProblemId("problem-2"),
            RevisionId("revision-2"),
            3,
            EditorialStatus.CHANGES_REQUESTED,
            second,
        ),
        StoredDraftSummary(
            ProblemId("problem-1"),
            RevisionId("revision-1"),
            1,
            EditorialStatus.DRAFT,
            first,
        ),
    )

    result = ListDrafts(lambda: work)()

    assert [item.revision_id.value for item in result] == [
        "revision-2",
        "revision-1",
    ]
    assert result[0].last_saved_at == second


def test_get_draft_returns_author_aggregate_and_preserves_not_found() -> None:
    repository = FakeDraftRepository()
    work = FakeUnitOfWork(repository)
    draft = ProblemRevision(
        ProblemId("problem-1"),
        RevisionId("revision-1"),
        1,
        None,
        EditorialStatus.DRAFT,
        None,
        None,
        None,
        None,
    )
    repository.items[draft.revision_id] = draft

    assert GetDraft(lambda: work)(draft.revision_id) == draft
    with pytest.raises(DraftNotFoundError):
        GetDraft(lambda: work)(RevisionId("missing"))
