"""defer vocabulary parent constraint for atomic synchronization

Revision ID: 20260809_05008
Revises: 20260809_05007
Create Date: 2026-08-09
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260809_05008"
down_revision: str | None = "20260809_05007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("fk_vocabulary_parent", "vocabulary_record", type_="foreignkey")
    op.create_foreign_key(
        "fk_vocabulary_parent",
        "vocabulary_record",
        "vocabulary_record",
        ["parent_vocabulary_type", "parent_code"],
        ["vocabulary_type", "code"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
        deferrable=True,
        initially="DEFERRED",
    )


def downgrade() -> None:
    op.drop_constraint("fk_vocabulary_parent", "vocabulary_record", type_="foreignkey")
    op.create_foreign_key(
        "fk_vocabulary_parent",
        "vocabulary_record",
        "vocabulary_record",
        ["parent_vocabulary_type", "parent_code"],
        ["vocabulary_type", "code"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
