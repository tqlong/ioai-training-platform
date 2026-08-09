"""create editorial publication storage

Revision ID: 20260809_07002
Revises: 20260809_06006
Create Date: 2026-08-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260809_07002"
down_revision: str | None = "20260809_06006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "editorial_transition",
        sa.Column("transition_id", sa.String(128), nullable=False),
        sa.Column("revision_id", sa.String(128), nullable=False),
        sa.Column("source_status", sa.String(32), nullable=False),
        sa.Column("target_status", sa.String(32), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("actor_context", sa.String(200), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("operation_id", sa.String(200), nullable=False),
        sa.CheckConstraint(
            "length(btrim(note)) BETWEEN 1 AND 2000",
            name="ck_editorial_transition_bounded_note",
        ),
        sa.CheckConstraint(
            "source_status IN ('DRAFT', 'IN_REVIEW', 'CHANGES_REQUESTED', "
            "'APPROVED', 'PUBLISHED', 'ARCHIVED')",
            name="ck_editorial_transition_source_status",
        ),
        sa.CheckConstraint(
            "target_status IN ('DRAFT', 'IN_REVIEW', 'CHANGES_REQUESTED', "
            "'APPROVED', 'PUBLISHED', 'ARCHIVED')",
            name="ck_editorial_transition_target_status",
        ),
        sa.CheckConstraint(
            "source_status <> target_status",
            name="ck_editorial_transition_status_changes",
        ),
        sa.ForeignKeyConstraint(
            ["revision_id"], ["problem_revision.revision_id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("transition_id", name="pk_editorial_transition"),
        sa.UniqueConstraint(
            "operation_id", name="uq_editorial_transition_operation_id"
        ),
    )
    op.create_index(
        "ix_editorial_transition_revision_occurred",
        "editorial_transition",
        ["revision_id", "occurred_at"],
    )
    op.create_table(
        "published_snapshot",
        sa.Column("snapshot_id", sa.String(128), nullable=False),
        sa.Column("problem_id", sa.String(128), nullable=False),
        sa.Column("revision_id", sa.String(128), nullable=False),
        sa.Column("slug", sa.String(120), nullable=False),
        sa.Column(
            "public_payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["problem_id"], ["problem.problem_id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["revision_id"], ["problem_revision.revision_id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("snapshot_id", name="pk_published_snapshot"),
        sa.UniqueConstraint("revision_id", name="uq_published_snapshot_revision_id"),
    )
    op.create_index(
        "ix_published_snapshot_problem_published",
        "published_snapshot",
        ["problem_id", "published_at"],
    )
    op.add_column(
        "problem",
        sa.Column("current_published_snapshot_id", sa.String(128), nullable=True),
    )
    op.create_foreign_key(
        "fk_problem_current_snapshot",
        "problem",
        "published_snapshot",
        ["current_published_snapshot_id"],
        ["snapshot_id"],
        ondelete="SET NULL",
    )
    op.create_unique_constraint(
        "uq_problem_current_published_snapshot_id",
        "problem",
        ["current_published_snapshot_id"],
    )
    op.create_table(
        "idempotency_record",
        sa.Column("idempotency_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("operation_type", sa.String(64), nullable=False),
        sa.Column("target_id", sa.String(128), nullable=False),
        sa.Column("idempotency_key", sa.String(200), nullable=False),
        sa.Column("request_digest", sa.String(64), nullable=False),
        sa.Column("result_reference", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("idempotency_id", name="pk_idempotency_record"),
        sa.UniqueConstraint(
            "operation_type",
            "target_id",
            "idempotency_key",
            name="uq_idempotency_operation_target_key",
        ),
    )
    op.create_index("ix_idempotency_created_at", "idempotency_record", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_idempotency_created_at", table_name="idempotency_record")
    op.drop_table("idempotency_record")
    op.drop_constraint("fk_problem_current_snapshot", "problem", type_="foreignkey")
    op.drop_constraint(
        "uq_problem_current_published_snapshot_id", "problem", type_="unique"
    )
    op.drop_column("problem", "current_published_snapshot_id")
    op.drop_index(
        "ix_published_snapshot_problem_published", table_name="published_snapshot"
    )
    op.drop_table("published_snapshot")
    op.drop_index(
        "ix_editorial_transition_revision_occurred",
        table_name="editorial_transition",
    )
    op.drop_table("editorial_transition")
