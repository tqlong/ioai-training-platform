from __future__ import annotations

from tests.fixtures.vocabulary import canonical_vocabulary_records


def test_vocabulary_fixture_comes_from_generated_canonical_artifact() -> None:
    records = canonical_vocabulary_records()

    assert len(records) == 343
    assert any(record.identity.code == "AI_1_FOUNDATIONS" for record in records)
