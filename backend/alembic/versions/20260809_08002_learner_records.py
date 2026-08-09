"""create snapshot-bound learner records

Revision ID: 20260809_08002
Revises: 20260809_07002
Create Date: 2026-08-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260809_08002"
down_revision: str | None = "20260809_07002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "learner_attempt",
        sa.Column("attempt_id", sa.String(128), nullable=False),
        sa.Column("snapshot_id", sa.String(128), nullable=False),
        sa.Column("submission_key", sa.String(200), nullable=False),
        sa.Column("request_digest", sa.String(64), nullable=False),
        sa.Column("outcome", sa.String(32), nullable=False),
        sa.Column("result", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "length(submission_key) BETWEEN 1 AND 200",
            name="ck_learner_attempt_bounded_submission_key",
        ),
        sa.CheckConstraint(
            "outcome IN ('ACCEPTED_RESULT', 'PENDING_ASSESSMENT')",
            name="ck_learner_attempt_outcome",
        ),
        sa.CheckConstraint(
            "jsonb_typeof(result) = 'object' AND octet_length(result::text) <= 16384",
            name="ck_learner_attempt_bounded_result",
        ),
        sa.ForeignKeyConstraint(
            ["snapshot_id"], ["published_snapshot.snapshot_id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("attempt_id", name="pk_learner_attempt"),
        sa.UniqueConstraint(
            "snapshot_id",
            "submission_key",
            name="uq_learner_attempt_snapshot_submission_key",
        ),
    )
    op.create_index(
        "ix_learner_attempt_snapshot_submitted",
        "learner_attempt",
        ["snapshot_id", "submitted_at"],
    )
    op.create_table(
        "problem_feedback",
        sa.Column("feedback_id", sa.String(128), nullable=False),
        sa.Column("snapshot_id", sa.String(128), nullable=False),
        sa.Column("feedback_key", sa.String(200), nullable=False),
        sa.Column("request_digest", sa.String(64), nullable=False),
        sa.Column("category", sa.String(32), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "length(feedback_key) BETWEEN 1 AND 200",
            name="ck_problem_feedback_bounded_feedback_key",
        ),
        sa.CheckConstraint(
            "length(btrim(message)) BETWEEN 1 AND 2000",
            name="ck_problem_feedback_bounded_message",
        ),
        sa.CheckConstraint(
            "category IN ('CONTENT_ISSUE', 'TYPO', 'SCORING_ISSUE', "
            "'ACCESSIBILITY', 'OTHER')",
            name="ck_problem_feedback_category",
        ),
        sa.ForeignKeyConstraint(
            ["snapshot_id"], ["published_snapshot.snapshot_id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("feedback_id", name="pk_problem_feedback"),
        sa.UniqueConstraint(
            "snapshot_id",
            "feedback_key",
            name="uq_problem_feedback_snapshot_feedback_key",
        ),
    )
    op.create_index(
        "ix_problem_feedback_snapshot_submitted",
        "problem_feedback",
        ["snapshot_id", "submitted_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_problem_feedback_snapshot_submitted", table_name="problem_feedback"
    )
    op.drop_table("problem_feedback")
    op.drop_index("ix_learner_attempt_snapshot_submitted", table_name="learner_attempt")
    op.drop_table("learner_attempt")
