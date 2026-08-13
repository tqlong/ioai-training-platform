from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ProblemModel(Base):
    """Stable internal identity shared by every revision."""

    __tablename__ = "problem"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_problem_slug"),
        UniqueConstraint(
            "current_published_snapshot_id",
            name="uq_problem_current_published_snapshot_id",
        ),
        CheckConstraint(
            "slug IS NULL OR slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'",
            name="slug_format",
        ),
    )

    problem_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    slug: Mapped[str | None] = mapped_column(String(120))
    current_published_snapshot_id: Mapped[str | None] = mapped_column(
        ForeignKey(
            "published_snapshot.snapshot_id",
            name="fk_problem_current_snapshot",
            use_alter=True,
            ondelete="SET NULL",
        )
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class ProblemRevisionModel(Base):
    """Editable author revision; never a public projection."""

    __tablename__ = "problem_revision"
    __table_args__ = (
        UniqueConstraint(
            "problem_id", "revision_number", name="uq_problem_revision_problem_number"
        ),
        CheckConstraint(
            "revision_number >= 1 AND lock_version >= 1",
            name="positive_versions",
        ),
        CheckConstraint(
            "editorial_status IN ('DRAFT', 'IN_REVIEW', 'CHANGES_REQUESTED', "
            "'APPROVED', 'PUBLISHED', 'ARCHIVED')",
            name="editorial_status",
        ),
        Index(
            "ix_problem_revision_problem_status_version",
            "problem_id",
            "editorial_status",
            "revision_number",
        ),
    )

    revision_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    problem_id: Mapped[str] = mapped_column(
        ForeignKey("problem.problem_id", ondelete="CASCADE"), nullable=False
    )
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False)
    lock_version: Mapped[int] = mapped_column(Integer, nullable=False)
    editorial_status: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    validation_summary: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class RevisionCompetencyModel(Base):
    __tablename__ = "revision_competency"
    __table_args__ = (
        ForeignKeyConstraint(
            ["vocabulary_type", "code"],
            ["vocabulary_record.vocabulary_type", "vocabulary_record.code"],
            ondelete="RESTRICT",
        ),
        CheckConstraint("vocabulary_type = 'COMPETENCY'", name="competency_type"),
        CheckConstraint("role IN ('PRIMARY', 'SECONDARY')", name="competency_role"),
        UniqueConstraint("revision_id", "role", "code", name="uq_revision_competency"),
    )

    revision_id: Mapped[str] = mapped_column(
        ForeignKey("problem_revision.revision_id", ondelete="CASCADE"),
        primary_key=True,
    )
    vocabulary_type: Mapped[str] = mapped_column(String(64), primary_key=True)
    code: Mapped[str] = mapped_column(String(128), primary_key=True)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)


class RevisionTopicModel(Base):
    __tablename__ = "revision_topic"
    __table_args__ = (
        ForeignKeyConstraint(
            ["vocabulary_type", "code"],
            ["vocabulary_record.vocabulary_type", "vocabulary_record.code"],
            ondelete="RESTRICT",
        ),
        CheckConstraint("vocabulary_type = 'TOPIC'", name="topic_type"),
        UniqueConstraint("revision_id", "code", name="uq_revision_topic"),
    )

    revision_id: Mapped[str] = mapped_column(
        ForeignKey("problem_revision.revision_id", ondelete="CASCADE"),
        primary_key=True,
    )
    vocabulary_type: Mapped[str] = mapped_column(String(64), primary_key=True)
    code: Mapped[str] = mapped_column(String(128), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)


class PrerequisiteReferenceModel(Base):
    __tablename__ = "prerequisite_reference"
    __table_args__ = (
        CheckConstraint(
            "relationship IN ('REQUIRED', 'RECOMMENDED', 'CO_REQUISITE', "
            "'UNLOCKED_BY')",
            name="prerequisite_relationship",
        ),
        CheckConstraint(
            "target_type IN ('COMPETENCY', 'TOPIC', 'TASK', 'LEARNING_UNIT')",
            name="prerequisite_target_type",
        ),
        CheckConstraint(
            "minimum_evidence IS NULL OR minimum_evidence IN "
            "('INTRODUCED', 'PRACTICED', 'APPLIED', 'PROFICIENT')",
            name="prerequisite_evidence",
        ),
        UniqueConstraint(
            "revision_id",
            "relationship",
            "target_type",
            "target_id",
            name="uq_prerequisite_reference",
        ),
    )

    prerequisite_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    revision_id: Mapped[str] = mapped_column(
        ForeignKey("problem_revision.revision_id", ondelete="CASCADE"), nullable=False
    )
    relationship: Mapped[str] = mapped_column(String(32), nullable=False)
    target_type: Mapped[str] = mapped_column(String(32), nullable=False)
    target_id: Mapped[str] = mapped_column(String(128), nullable=False)
    minimum_evidence: Mapped[str | None] = mapped_column(String(32))


class ResponseConfigurationModel(Base):
    __tablename__ = "response_configuration"
    __table_args__ = (
        CheckConstraint(
            "task_type IN ('QUIZ_SINGLE', 'QUIZ_MULTIPLE', 'NUMERIC_ANSWER', "
            "'SHORT_ANSWER', 'CODE_FUNCTION')",
            name="release_0_task_type",
        ),
    )

    revision_id: Mapped[str] = mapped_column(
        ForeignKey("problem_revision.revision_id", ondelete="CASCADE"),
        primary_key=True,
    )
    task_type: Mapped[str] = mapped_column(String(32), nullable=False)
    configuration: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)


class ScoringComponentModel(Base):
    __tablename__ = "scoring_component"
    __table_args__ = (
        CheckConstraint("weight > 0 AND weight <= 1", name="scoring_weight"),
        CheckConstraint(
            "method IN ('EXACT_MATCH', 'UNIT_TESTS', 'PARTIAL_TESTS', 'RUBRIC_HUMAN')",
            name="release_0_scoring_method",
        ),
        UniqueConstraint("revision_id", "position", name="uq_scoring_position"),
    )

    component_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    revision_id: Mapped[str] = mapped_column(
        ForeignKey("response_configuration.revision_id", ondelete="CASCADE"),
        nullable=False,
    )
    method: Mapped[str] = mapped_column(String(32), nullable=False)
    weight: Mapped[Decimal] = mapped_column(Numeric(8, 7), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    configuration: Mapped[dict[str, object] | str | None] = mapped_column(JSONB)


class EditorialTransitionModel(Base):
    """Append-only audit history for an accepted editorial decision."""

    __tablename__ = "editorial_transition"
    __table_args__ = (
        CheckConstraint(
            "source_status IN ('DRAFT', 'IN_REVIEW', 'CHANGES_REQUESTED', "
            "'APPROVED', 'PUBLISHED', 'ARCHIVED')",
            name="source_status",
        ),
        CheckConstraint(
            "target_status IN ('DRAFT', 'IN_REVIEW', 'CHANGES_REQUESTED', "
            "'APPROVED', 'PUBLISHED', 'ARCHIVED')",
            name="target_status",
        ),
        CheckConstraint("source_status <> target_status", name="status_changes"),
        CheckConstraint("length(btrim(note)) BETWEEN 1 AND 2000", name="bounded_note"),
        UniqueConstraint("operation_id", name="uq_editorial_transition_operation_id"),
        Index(
            "ix_editorial_transition_revision_occurred",
            "revision_id",
            "occurred_at",
        ),
    )

    transition_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    revision_id: Mapped[str] = mapped_column(
        ForeignKey("problem_revision.revision_id", ondelete="RESTRICT"), nullable=False
    )
    source_status: Mapped[str] = mapped_column(String(32), nullable=False)
    target_status: Mapped[str] = mapped_column(String(32), nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=False)
    actor_context: Mapped[str] = mapped_column(String(200), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    operation_id: Mapped[str] = mapped_column(String(200), nullable=False)


class PublishedSnapshotModel(Base):
    """Immutable learner-safe projection of one approved revision."""

    __tablename__ = "published_snapshot"
    __table_args__ = (
        UniqueConstraint("revision_id", name="uq_published_snapshot_revision_id"),
        Index("ix_published_snapshot_slug", "slug"),
        Index("ix_published_snapshot_problem_published", "problem_id", "published_at"),
    )

    snapshot_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    problem_id: Mapped[str] = mapped_column(
        ForeignKey("problem.problem_id", ondelete="RESTRICT"), nullable=False
    )
    revision_id: Mapped[str] = mapped_column(
        ForeignKey("problem_revision.revision_id", ondelete="RESTRICT"), nullable=False
    )
    slug: Mapped[str] = mapped_column(String(120), nullable=False)
    public_payload: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class IdempotencyRecordModel(Base):
    """Safe result reference for a retriable externally visible command."""

    __tablename__ = "idempotency_record"
    __table_args__ = (
        UniqueConstraint(
            "operation_type",
            "target_id",
            "idempotency_key",
            name="uq_idempotency_operation_target_key",
        ),
        Index("ix_idempotency_created_at", "created_at"),
    )

    idempotency_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    operation_type: Mapped[str] = mapped_column(String(64), nullable=False)
    target_id: Mapped[str] = mapped_column(String(128), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(200), nullable=False)
    request_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    result_reference: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class LearnerAttemptModel(Base):
    """Bounded anonymous assessment record tied to a public snapshot."""

    __tablename__ = "learner_attempt"
    __table_args__ = (
        CheckConstraint(
            "outcome IN ('ACCEPTED_RESULT', 'PENDING_ASSESSMENT')",
            name="outcome",
        ),
        CheckConstraint(
            "length(submission_key) BETWEEN 1 AND 200",
            name="bounded_submission_key",
        ),
        CheckConstraint(
            "jsonb_typeof(result) = 'object' AND octet_length(result::text) <= 16384",
            name="bounded_result",
        ),
        CheckConstraint(
            "jsonb_typeof(response) = 'object' "
            "AND octet_length(response::text) <= 64000",
            name="bounded_response",
        ),
        CheckConstraint("length(receipt_digest) = 64", name="receipt_digest"),
        UniqueConstraint(
            "snapshot_id",
            "submission_key",
            name="uq_learner_attempt_snapshot_submission_key",
        ),
        Index("ix_learner_attempt_snapshot_submitted", "snapshot_id", "submitted_at"),
        Index(
            "ix_learner_attempt_outcome_submitted",
            "outcome",
            "submitted_at",
            "attempt_id",
        ),
    )

    attempt_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    snapshot_id: Mapped[str] = mapped_column(
        ForeignKey("published_snapshot.snapshot_id", ondelete="RESTRICT"),
        nullable=False,
    )
    submission_key: Mapped[str] = mapped_column(String(200), nullable=False)
    request_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    receipt_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    response: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    outcome: Mapped[str] = mapped_column(String(32), nullable=False)
    result: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class AssessmentDecisionModel(Base):
    """Append-only human assessment result and correction history."""

    __tablename__ = "assessment_decision"
    __table_args__ = (
        CheckConstraint("version >= 1", name="positive_version"),
        CheckConstraint("jsonb_typeof(selections) = 'array'", name="selection_array"),
        CheckConstraint("jsonb_typeof(result) = 'object'", name="result_object"),
        UniqueConstraint("attempt_id", "version", name="uq_assessment_version"),
        Index("ix_assessment_decision_attempt", "attempt_id", "version"),
    )

    decision_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    attempt_id: Mapped[str] = mapped_column(
        ForeignKey("learner_attempt.attempt_id", ondelete="RESTRICT"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    selections: Mapped[list[dict[str, object]]] = mapped_column(JSONB, nullable=False)
    result: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    overall_feedback: Mapped[str | None] = mapped_column(Text)
    correction_reason: Mapped[str | None] = mapped_column(Text)
    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class ProblemFeedbackModel(Base):
    """Bounded anonymous feedback tied to the content the learner saw."""

    __tablename__ = "problem_feedback"
    __table_args__ = (
        CheckConstraint(
            "category IN ('CONTENT_ISSUE', 'TYPO', 'SCORING_ISSUE', "
            "'ACCESSIBILITY', 'OTHER')",
            name="category",
        ),
        CheckConstraint(
            "length(btrim(message)) BETWEEN 1 AND 2000",
            name="bounded_message",
        ),
        CheckConstraint(
            "length(feedback_key) BETWEEN 1 AND 200",
            name="bounded_feedback_key",
        ),
        UniqueConstraint(
            "snapshot_id",
            "feedback_key",
            name="uq_problem_feedback_snapshot_feedback_key",
        ),
        Index("ix_problem_feedback_snapshot_submitted", "snapshot_id", "submitted_at"),
    )

    feedback_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    snapshot_id: Mapped[str] = mapped_column(
        ForeignKey("published_snapshot.snapshot_id", ondelete="RESTRICT"),
        nullable=False,
    )
    feedback_key: Mapped[str] = mapped_column(String(200), nullable=False)
    request_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    category: Mapped[str] = mapped_column(String(32), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
