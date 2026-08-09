from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
    String,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class VocabularyRecordModel(Base):
    """Persistence mapping for canonical vocabulary; not a domain entity."""

    __tablename__ = "vocabulary_record"
    __table_args__ = (
        ForeignKeyConstraint(
            ["parent_vocabulary_type", "parent_code"],
            ["vocabulary_record.vocabulary_type", "vocabulary_record.code"],
            name="fk_vocabulary_parent",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
            deferrable=True,
            initially="DEFERRED",
        ),
        CheckConstraint(
            "vocabulary_type ~ '^[A-Z][A-Z0-9_]*$' AND code ~ '^[A-Z][A-Z0-9_]*$'",
            name="vocabulary_identity_format",
        ),
        CheckConstraint(
            "status ~ '^[A-Z][A-Z0-9_]*$'",
            name="vocabulary_status_format",
        ),
        CheckConstraint(
            "(parent_vocabulary_type IS NULL) = (parent_code IS NULL)",
            name="vocabulary_parent_pair",
        ),
        CheckConstraint(
            "parent_code IS NULL OR "
            "(vocabulary_type = 'TOPIC' AND parent_vocabulary_type = 'TOPIC')",
            name="vocabulary_topic_parent_type",
        ),
        CheckConstraint(
            "parent_code IS NULL OR code <> parent_code",
            name="vocabulary_not_self_parent",
        ),
        Index(
            "ix_vocabulary_type_parent",
            "vocabulary_type",
            "parent_vocabulary_type",
            "parent_code",
        ),
        Index("ix_vocabulary_label_en_normalized", func.lower(text("label_en"))),
        Index("ix_vocabulary_label_vi_normalized", func.lower(text("label_vi"))),
        Index("ix_vocabulary_aliases_gin", "aliases", postgresql_using="gin"),
    )

    vocabulary_type: Mapped[str] = mapped_column(String(64), primary_key=True)
    code: Mapped[str] = mapped_column(String(128), primary_key=True)
    label_en: Mapped[str] = mapped_column(String(255), nullable=False)
    label_vi: Mapped[str] = mapped_column(String(255), nullable=False)
    aliases: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb")
    )
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    parent_vocabulary_type: Mapped[str | None] = mapped_column(String(64))
    parent_code: Mapped[str | None] = mapped_column(String(128))


class VocabularyProposalModel(Base):
    """Author proposal persistence, deliberately separate from canonical records."""

    __tablename__ = "vocabulary_proposal"
    __table_args__ = (
        CheckConstraint(
            "vocabulary_type ~ '^[A-Z][A-Z0-9_]*$'",
            name="vocabulary_proposal_type_format",
        ),
        CheckConstraint(
            "char_length(note) BETWEEN 1 AND 1000",
            name="vocabulary_proposal_note_length",
        ),
        CheckConstraint(
            "status = 'PENDING'",
            name="vocabulary_proposal_pending_status",
        ),
        Index("ix_vocabulary_proposal_review", "status", "created_at", "proposal_id"),
    )

    proposal_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    vocabulary_type: Mapped[str] = mapped_column(String(64), nullable=False)
    note: Mapped[str] = mapped_column(String(1000), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
