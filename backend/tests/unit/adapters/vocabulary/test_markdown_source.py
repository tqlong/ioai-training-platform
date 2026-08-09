from __future__ import annotations

from pathlib import Path

import pytest

from ioai.adapters.vocabulary.markdown_source import (
    VocabularySourceError,
    parse_vocabulary_markdown,
)


def test_parser_extracts_every_canonical_family_from_vocab_source() -> None:
    source = Path("vocab.md").read_text(encoding="utf-8")

    records = parse_vocabulary_markdown(source)
    identities = {
        (record.identity.vocabulary_type.value, record.identity.code): record
        for record in records
    }

    expected_types = {
        "PATHWAY_STAGE",
        "COMPETENCY",
        "DIFFICULTY",
        "TASK_STATUS",
        "TOPIC",
        "TASK_TYPE",
        "DATA_MODALITY",
        "DATA_ORIGIN",
        "PREREQUISITE_RELATIONSHIP",
        "PREREQUISITE_TARGET_TYPE",
        "LEARNING_EVIDENCE",
        "EXPECTED_TIME_CATEGORY",
        "COMPUTE_TIER",
        "RUNTIME_CLASS",
        "SCORING_METHOD",
    }
    assert {identity[0] for identity in identities} == expected_types
    assert identities[("TOPIC", "TOPIC_MATHEMATICS")].parent is None
    assert identities[("TOPIC", "MATH_VECTORS_MATRICES")].parent.code == (
        "MATH_LINEAR_ALGEBRA_TOPICS"
    )
    assert ("COMPETENCY", "DL_TRANSFORMERS") in identities
    assert ("TOPIC", "DL_TRANSFORMERS") in identities


def test_parser_uses_explicit_topic_parent_not_markdown_heading() -> None:
    source = """\
## 5. Topic taxonomy / Phan loai chu de

### Misleading visual group

- `TOPIC_CHILD` - Child - Con - Parent: `TOPIC_DECLARED_PARENT`
"""

    [record] = parse_vocabulary_markdown(source)

    assert record.parent is not None
    assert record.parent.code == "TOPIC_DECLARED_PARENT"


@pytest.mark.parametrize(
    ("source", "diagnostic"),
    [
        (
            """\
## 2. Pathway stage / Giai doan
| Code | English label | Vietnamese label |
|---|---|---|
| `AI_1_FOUNDATIONS` | | Nen tang AI |
""",
            "line 4.*English label",
        ),
        (
            """\
## 5. Topic taxonomy / Chu de
- `TOPIC_CHILD` - Child - Con
""",
            "line 2.*Parent",
        ),
        (
            """\
## 5. Topic taxonomy / Chu de
| Code | English label | Vietnamese label | Parent code | Status |
|---|---|---|---|---|
| `TOPIC_ROOT` | Root | Goc | `null` | `active` |
""",
            "line 4.*status",
        ),
    ],
)
def test_parser_reports_source_line_for_malformed_records(
    source: str, diagnostic: str
) -> None:
    with pytest.raises(VocabularySourceError, match=diagnostic):
        parse_vocabulary_markdown(source)
