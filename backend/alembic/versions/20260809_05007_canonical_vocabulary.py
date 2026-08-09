"""create canonical vocabulary records

Revision ID: 20260809_05007
Revises:
Create Date: 2026-08-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260809_05007"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "vocabulary_record",
        sa.Column("vocabulary_type", sa.String(length=64), nullable=False),
        sa.Column("code", sa.String(length=128), nullable=False),
        sa.Column("label_en", sa.String(length=255), nullable=False),
        sa.Column("label_vi", sa.String(length=255), nullable=False),
        sa.Column(
            "aliases",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("parent_vocabulary_type", sa.String(length=64), nullable=True),
        sa.Column("parent_code", sa.String(length=128), nullable=True),
        sa.CheckConstraint(
            "vocabulary_type ~ '^[A-Z][A-Z0-9_]*$' AND code ~ '^[A-Z][A-Z0-9_]*$'",
            name="ck_vocabulary_record_vocabulary_identity_format",
        ),
        sa.CheckConstraint(
            "status ~ '^[A-Z][A-Z0-9_]*$'",
            name="ck_vocabulary_record_vocabulary_status_format",
        ),
        sa.CheckConstraint(
            "(parent_vocabulary_type IS NULL) = (parent_code IS NULL)",
            name="ck_vocabulary_record_vocabulary_parent_pair",
        ),
        sa.CheckConstraint(
            "parent_code IS NULL OR "
            "(vocabulary_type = 'TOPIC' AND parent_vocabulary_type = 'TOPIC')",
            name="ck_vocabulary_record_vocabulary_topic_parent_type",
        ),
        sa.CheckConstraint(
            "parent_code IS NULL OR code <> parent_code",
            name="ck_vocabulary_record_vocabulary_not_self_parent",
        ),
        sa.ForeignKeyConstraint(
            ["parent_vocabulary_type", "parent_code"],
            ["vocabulary_record.vocabulary_type", "vocabulary_record.code"],
            name="fk_vocabulary_parent",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("vocabulary_type", "code", name="pk_vocabulary_record"),
    )
    op.create_index(
        "ix_vocabulary_type_parent",
        "vocabulary_record",
        ["vocabulary_type", "parent_vocabulary_type", "parent_code"],
    )
    op.create_index(
        "ix_vocabulary_label_en_normalized",
        "vocabulary_record",
        [sa.literal_column("lower(label_en)")],
    )
    op.create_index(
        "ix_vocabulary_label_vi_normalized",
        "vocabulary_record",
        [sa.literal_column("lower(label_vi)")],
    )
    op.create_index(
        "ix_vocabulary_aliases_gin",
        "vocabulary_record",
        ["aliases"],
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index("ix_vocabulary_aliases_gin", table_name="vocabulary_record")
    op.drop_index("ix_vocabulary_label_vi_normalized", table_name="vocabulary_record")
    op.drop_index("ix_vocabulary_label_en_normalized", table_name="vocabulary_record")
    op.drop_index("ix_vocabulary_type_parent", table_name="vocabulary_record")
    op.drop_table("vocabulary_record")
