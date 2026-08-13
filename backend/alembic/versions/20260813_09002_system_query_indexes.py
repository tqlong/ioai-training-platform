"""add release 0 system query indexes

Revision ID: 20260813_09002
Revises: 20260811_08104
Create Date: 2026-08-13
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260813_09002"
down_revision: str | None = "20260811_08104"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_published_snapshot_slug",
        "published_snapshot",
        ["slug"],
    )
    op.create_index(
        "ix_learner_attempt_outcome_submitted",
        "learner_attempt",
        ["outcome", "submitted_at", "attempt_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_learner_attempt_outcome_submitted",
        table_name="learner_attempt",
    )
    op.drop_index("ix_published_snapshot_slug", table_name="published_snapshot")
