from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

import pytest
from tests.unit.domain.problems.test_revision import revision

from ioai.application.problems.errors import DraftValidationError
from ioai.application.problems.publication import (
    ArchivedProblem,
    ArchiveProblem,
    PublishedSnapshot,
    PublishRevision,
)
from ioai.domain.problems.identity import ProblemId, RevisionId, StableSlug
from ioai.domain.problems.workflow import ActorContext, EditorialStatus
from ioai.domain.vocabulary.availability import Release0AvailabilityPolicy

NOW = datetime(2026, 8, 9, 11, tzinfo=UTC)


class FakePublicationRepository:
    def __init__(self) -> None:
        self.calls = []
        self.replay_result = None

    def replay(self, revision_id, *, idempotency_key, request_digest):
        del revision_id, idempotency_key, request_digest
        return self.replay_result

    def current_snapshot(self, problem_id):
        return PublishedSnapshot(
            "snapshot-current",
            problem_id,
            RevisionId("revision-01"),
            StableSlug("metrics-basics"),
            {},
            NOW,
        )

    def publish(self, **kwargs):
        self.calls.append(kwargs)
        return kwargs["snapshot"]

    def archive(self, **kwargs):
        self.calls.append(kwargs)
        return ArchivedProblem(
            problem_id=kwargs["problem_id"],
            slug=StableSlug("metrics-basics"),
            archived_at=kwargs["transition"].occurred_at,
        )


class FakeWork:
    def __init__(self, current):
        self.current = current
        self.drafts = self
        self.publication = FakePublicationRepository()

    def get(self, revision_id):
        assert revision_id == self.current.revision_id
        return self.current

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return None


def publisher(current):
    work = FakeWork(current)
    ids = iter(("snapshot-01", "transition-01"))
    use_case = PublishRevision(
        unit_of_work_factory=lambda: work,
        policy=Release0AvailabilityPolicy(),
        id_generator=lambda: next(ids),
        clock=lambda: NOW,
    )
    return work, use_case


def test_approved_valid_revision_builds_snapshot_and_publication_transition() -> None:
    approved = revision(status=EditorialStatus.APPROVED, version=4)
    work, publish = publisher(approved)

    result = publish(
        approved.revision_id,
        expected_version=4,
        note="Publish approved learner content.",
        actor=ActorContext("local-reviewer"),
        idempotency_key="publish-01",
    )

    assert result.snapshot_id == "snapshot-01"
    assert result.slug.value == "metrics-basics"
    assert result.published_at == NOW
    call = work.publication.calls[0]
    assert call["transition"].target is EditorialStatus.PUBLISHED
    assert call["request_digest"]
    assert "editorial_status" not in result.public_payload
    assert "revision_id" not in result.public_payload


@pytest.mark.parametrize(
    "status",
    (
        EditorialStatus.DRAFT,
        EditorialStatus.IN_REVIEW,
        EditorialStatus.CHANGES_REQUESTED,
    ),
)
def test_nonapproved_revision_cannot_publish(status: EditorialStatus) -> None:
    current = revision(status=status)
    work, publish = publisher(current)

    with pytest.raises(ValueError):
        publish(
            current.revision_id,
            expected_version=1,
            note="Publish.",
            actor=ActorContext("local-reviewer"),
            idempotency_key="publish-01",
        )

    assert work.publication.calls == []


def test_approved_revision_is_revalidated_against_current_policy() -> None:
    invalid = replace(
        revision(status=EditorialStatus.APPROVED),
        slug=None,
    )
    work, publish = publisher(invalid)

    with pytest.raises(DraftValidationError):
        publish(
            invalid.revision_id,
            expected_version=1,
            note="Publish.",
            actor=ActorContext("local-reviewer"),
            idempotency_key="publish-01",
        )

    assert work.publication.calls == []


def test_identical_publication_retry_returns_original_snapshot() -> None:
    approved = revision(status=EditorialStatus.PUBLISHED, version=5)
    work, publish = publisher(approved)
    original = PublishedSnapshot(
        "snapshot-existing",
        ProblemId("problem-01"),
        RevisionId("revision-01"),
        StableSlug("metrics-basics"),
        {},
        NOW,
    )
    work.publication.replay_result = original

    result = publish(
        approved.revision_id,
        expected_version=4,
        note="Publish approved learner content.",
        actor=ActorContext("local-reviewer"),
        idempotency_key="publish-01",
    )

    assert result is original
    assert work.publication.calls == []


def test_archive_is_a_distinct_versioned_transition() -> None:
    published = revision(status=EditorialStatus.PUBLISHED, version=5)
    work = FakeWork(published)
    archive = ArchiveProblem(
        unit_of_work_factory=lambda: work,
        id_generator=lambda: "transition-archive",
        clock=lambda: NOW,
    )

    result = archive(
        published.problem_id,
        expected_version=5,
        note="Retire outdated learner content.",
        actor=ActorContext("local-reviewer"),
        operation_id="archive-01",
    )

    assert result.slug == StableSlug("metrics-basics")
    assert work.publication.calls[0]["transition"].target is EditorialStatus.ARCHIVED
