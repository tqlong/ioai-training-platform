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
        CheckConstraint(
            "slug IS NULL OR slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'",
            name="slug_format",
        ),
    )

    problem_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    slug: Mapped[str | None] = mapped_column(String(120))
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
    configuration: Mapped[str | None] = mapped_column(Text)
