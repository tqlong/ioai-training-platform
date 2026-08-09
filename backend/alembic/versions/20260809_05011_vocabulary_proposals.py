"""create separately reviewable vocabulary proposals

Revision ID: 20260809_05011
Revises: 20260809_05008
Create Date: 2026-08-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260809_05011"
down_revision: str | None = "20260809_05008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "vocabulary_proposal",
        sa.Column("proposal_id", sa.String(length=64), nullable=False),
        sa.Column("vocabulary_type", sa.String(length=64), nullable=False),
        sa.Column("note", sa.String(length=1000), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "vocabulary_type ~ '^[A-Z][A-Z0-9_]*$'",
            name="ck_vocabulary_proposal_vocabulary_proposal_type_format",
        ),
        sa.CheckConstraint(
            "char_length(note) BETWEEN 1 AND 1000",
            name="ck_vocabulary_proposal_vocabulary_proposal_note_length",
        ),
        sa.CheckConstraint(
            "status = 'PENDING'",
            name="ck_vocabulary_proposal_vocabulary_proposal_pending_status",
        ),
        sa.PrimaryKeyConstraint("proposal_id", name="pk_vocabulary_proposal"),
    )
    op.create_index(
        "ix_vocabulary_proposal_review",
        "vocabulary_proposal",
        ["status", "created_at", "proposal_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_vocabulary_proposal_review", table_name="vocabulary_proposal")
    op.drop_table("vocabulary_proposal")
