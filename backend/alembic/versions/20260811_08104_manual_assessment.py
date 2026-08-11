"""persist manual assessment records

Revision ID: 20260811_08104
Revises: 20260809_08002
Create Date: 2026-08-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260811_08104"
down_revision: str | None = "20260809_08002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "scoring_component",
        "configuration",
        existing_type=sa.Text(),
        type_=postgresql.JSONB(),
        postgresql_using="to_jsonb(configuration)",
    )
    op.add_column(
        "learner_attempt",
        sa.Column(
            "receipt_digest", sa.String(64), nullable=False, server_default="0" * 64
        ),
    )
    op.add_column(
        "learner_attempt",
        sa.Column(
            "response",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.alter_column("learner_attempt", "receipt_digest", server_default=None)
    op.alter_column("learner_attempt", "response", server_default=None)
    op.create_check_constraint(
        "ck_learner_attempt_receipt_digest",
        "learner_attempt",
        "length(receipt_digest) = 64",
    )
    op.create_check_constraint(
        "ck_learner_attempt_bounded_response",
        "learner_attempt",
        "jsonb_typeof(response) = 'object' AND octet_length(response::text) <= 64000",
    )
    op.create_table(
        "assessment_decision",
        sa.Column("decision_id", sa.String(128), nullable=False),
        sa.Column("attempt_id", sa.String(128), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("selections", postgresql.JSONB(), nullable=False),
        sa.Column("result", postgresql.JSONB(), nullable=False),
        sa.Column("overall_feedback", sa.Text()),
        sa.Column("correction_reason", sa.Text()),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "version >= 1", name="ck_assessment_decision_positive_version"
        ),
        sa.CheckConstraint(
            "jsonb_typeof(selections) = 'array'",
            name="ck_assessment_decision_selection_array",
        ),
        sa.CheckConstraint(
            "jsonb_typeof(result) = 'object'",
            name="ck_assessment_decision_result_object",
        ),
        sa.ForeignKeyConstraint(
            ["attempt_id"], ["learner_attempt.attempt_id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("decision_id", name="pk_assessment_decision"),
        sa.UniqueConstraint("attempt_id", "version", name="uq_assessment_version"),
    )
    op.create_index(
        "ix_assessment_decision_attempt",
        "assessment_decision",
        ["attempt_id", "version"],
    )


def downgrade() -> None:
    op.drop_index("ix_assessment_decision_attempt", table_name="assessment_decision")
    op.drop_table("assessment_decision")
    op.drop_constraint(
        "ck_learner_attempt_bounded_response", "learner_attempt", type_="check"
    )
    op.drop_constraint(
        "ck_learner_attempt_receipt_digest", "learner_attempt", type_="check"
    )
    op.drop_column("learner_attempt", "response")
    op.drop_column("learner_attempt", "receipt_digest")
    op.alter_column(
        "scoring_component",
        "configuration",
        existing_type=postgresql.JSONB(),
        type_=sa.Text(),
        postgresql_using="configuration #>> '{}'",
    )
