"""create problem draft and revision storage

Revision ID: 20260809_06006
Revises: 20260809_05011
Create Date: 2026-08-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260809_06006"
down_revision: str | None = "20260809_05011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "problem",
        sa.Column("problem_id", sa.String(128), nullable=False),
        sa.Column("slug", sa.String(120)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "slug IS NULL OR slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'",
            name="ck_problem_slug_format",
        ),
        sa.PrimaryKeyConstraint("problem_id", name="pk_problem"),
        sa.UniqueConstraint("slug", name="uq_problem_slug"),
    )
    op.create_table(
        "problem_revision",
        sa.Column("revision_id", sa.String(128), nullable=False),
        sa.Column("problem_id", sa.String(128), nullable=False),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("lock_version", sa.Integer(), nullable=False),
        sa.Column("editorial_status", sa.String(32), nullable=False),
        sa.Column(
            "content",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("validation_summary", postgresql.JSONB(astext_type=sa.Text())),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "editorial_status IN ('DRAFT', 'IN_REVIEW', 'CHANGES_REQUESTED', "
            "'APPROVED', 'PUBLISHED', 'ARCHIVED')",
            name="ck_problem_revision_editorial_status",
        ),
        sa.CheckConstraint(
            "revision_number >= 1 AND lock_version >= 1",
            name="ck_problem_revision_positive_versions",
        ),
        sa.ForeignKeyConstraint(
            ["problem_id"], ["problem.problem_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("revision_id", name="pk_problem_revision"),
        sa.UniqueConstraint(
            "problem_id",
            "revision_number",
            name="uq_problem_revision_problem_number",
        ),
    )
    op.create_index(
        "ix_problem_revision_problem_status_version",
        "problem_revision",
        ["problem_id", "editorial_status", "revision_number"],
    )
    _create_metadata_tables()


def _create_metadata_tables() -> None:
    op.create_table(
        "revision_competency",
        sa.Column("revision_id", sa.String(128), nullable=False),
        sa.Column("vocabulary_type", sa.String(64), nullable=False),
        sa.Column("code", sa.String(128), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.CheckConstraint("vocabulary_type = 'COMPETENCY'", name="competency_type"),
        sa.CheckConstraint("role IN ('PRIMARY', 'SECONDARY')", name="competency_role"),
        sa.ForeignKeyConstraint(
            ["revision_id"], ["problem_revision.revision_id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["vocabulary_type", "code"],
            ["vocabulary_record.vocabulary_type", "vocabulary_record.code"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("revision_id", "vocabulary_type", "code"),
        sa.UniqueConstraint("revision_id", "role", "code"),
    )
    op.create_table(
        "revision_topic",
        sa.Column("revision_id", sa.String(128), nullable=False),
        sa.Column("vocabulary_type", sa.String(64), nullable=False),
        sa.Column("code", sa.String(128), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.CheckConstraint("vocabulary_type = 'TOPIC'", name="topic_type"),
        sa.ForeignKeyConstraint(
            ["revision_id"], ["problem_revision.revision_id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["vocabulary_type", "code"],
            ["vocabulary_record.vocabulary_type", "vocabulary_record.code"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("revision_id", "vocabulary_type", "code"),
        sa.UniqueConstraint("revision_id", "code"),
    )
    op.create_table(
        "prerequisite_reference",
        sa.Column("prerequisite_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("revision_id", sa.String(128), nullable=False),
        sa.Column("relationship", sa.String(32), nullable=False),
        sa.Column("target_type", sa.String(32), nullable=False),
        sa.Column("target_id", sa.String(128), nullable=False),
        sa.Column("minimum_evidence", sa.String(32)),
        sa.CheckConstraint(
            "relationship IN "
            "('REQUIRED', 'RECOMMENDED', 'CO_REQUISITE', 'UNLOCKED_BY')",
            name="prerequisite_relationship",
        ),
        sa.CheckConstraint(
            "target_type IN ('COMPETENCY', 'TOPIC', 'TASK', 'LEARNING_UNIT')",
            name="prerequisite_target_type",
        ),
        sa.CheckConstraint(
            "minimum_evidence IS NULL OR minimum_evidence IN "
            "('INTRODUCED', 'PRACTICED', 'APPLIED', 'PROFICIENT')",
            name="prerequisite_evidence",
        ),
        sa.ForeignKeyConstraint(
            ["revision_id"], ["problem_revision.revision_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("prerequisite_id"),
        sa.UniqueConstraint("revision_id", "relationship", "target_type", "target_id"),
    )
    op.create_table(
        "response_configuration",
        sa.Column("revision_id", sa.String(128), nullable=False),
        sa.Column("task_type", sa.String(32), nullable=False),
        sa.Column("configuration", postgresql.JSONB(), nullable=False),
        sa.CheckConstraint(
            "task_type IN ('QUIZ_SINGLE', 'QUIZ_MULTIPLE', 'NUMERIC_ANSWER', "
            "'SHORT_ANSWER', 'CODE_FUNCTION')",
            name="release_0_task_type",
        ),
        sa.ForeignKeyConstraint(
            ["revision_id"], ["problem_revision.revision_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("revision_id"),
    )
    op.create_table(
        "scoring_component",
        sa.Column("component_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("revision_id", sa.String(128), nullable=False),
        sa.Column("method", sa.String(32), nullable=False),
        sa.Column("weight", sa.Numeric(8, 7), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("configuration", sa.Text()),
        sa.CheckConstraint("weight > 0 AND weight <= 1", name="scoring_weight"),
        sa.CheckConstraint(
            "method IN ('EXACT_MATCH', 'UNIT_TESTS', 'PARTIAL_TESTS', 'RUBRIC_HUMAN')",
            name="release_0_scoring_method",
        ),
        sa.ForeignKeyConstraint(
            ["revision_id"], ["response_configuration.revision_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("component_id"),
        sa.UniqueConstraint("revision_id", "position"),
    )


def downgrade() -> None:
    op.drop_table("scoring_component")
    op.drop_table("response_configuration")
    op.drop_table("prerequisite_reference")
    op.drop_table("revision_topic")
    op.drop_table("revision_competency")
    op.drop_index(
        "ix_problem_revision_problem_status_version", table_name="problem_revision"
    )
    op.drop_table("problem_revision")
    op.drop_table("problem")
