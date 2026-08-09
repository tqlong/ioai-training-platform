from __future__ import annotations

from sqlalchemy import CheckConstraint, ForeignKeyConstraint

from ioai.adapters.database.base import Base
from ioai.adapters.database.vocabulary_model import VocabularyRecordModel


def test_vocabulary_mapping_uses_composite_identity_and_explicit_parent() -> None:
    table = VocabularyRecordModel.__table__

    assert table.primary_key.columns.keys() == ["vocabulary_type", "code"]
    assert {
        "label_en",
        "label_vi",
        "aliases",
        "status",
        "parent_vocabulary_type",
        "parent_code",
    }.issubset(table.columns.keys())

    parent_keys = [
        constraint
        for constraint in table.constraints
        if isinstance(constraint, ForeignKeyConstraint)
    ]
    assert len(parent_keys) == 1
    assert [element.parent.name for element in parent_keys[0].elements] == [
        "parent_vocabulary_type",
        "parent_code",
    ]
    assert [element.column.name for element in parent_keys[0].elements] == [
        "vocabulary_type",
        "code",
    ]
    assert parent_keys[0].deferrable is True
    assert parent_keys[0].initially == "DEFERRED"


def test_vocabulary_mapping_declares_database_invariant_constraints_and_indexes() -> (
    None
):
    table = VocabularyRecordModel.__table__
    check_names = {
        constraint.name
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    }
    index_names = {index.name for index in table.indexes}

    assert {
        "ck_vocabulary_record_vocabulary_identity_format",
        "ck_vocabulary_record_vocabulary_status_format",
        "ck_vocabulary_record_vocabulary_parent_pair",
        "ck_vocabulary_record_vocabulary_topic_parent_type",
        "ck_vocabulary_record_vocabulary_not_self_parent",
    }.issubset(check_names)
    assert {
        "ix_vocabulary_type_parent",
        "ix_vocabulary_label_en_normalized",
        "ix_vocabulary_label_vi_normalized",
        "ix_vocabulary_aliases_gin",
    }.issubset(index_names)
    assert Base.metadata.tables["vocabulary_record"] is table
