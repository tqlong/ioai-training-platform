from __future__ import annotations

import json
from pathlib import Path

import pytest

from ioai.adapters.vocabulary.artifact_contract import ARTIFACT_PATH
from ioai.adapters.vocabulary.generation import (
    VocabularyDriftError,
    build_vocabulary_artifact,
    check_vocabulary_drift,
    render_vocabulary_artifact,
)
from ioai.adapters.vocabulary.runtime import load_generated_vocabulary

SOURCE_PATH = Path("vocab.md")


def test_generation_is_deterministic_and_contains_no_environment_metadata() -> None:
    source = SOURCE_PATH.read_text(encoding="utf-8")

    first = render_vocabulary_artifact(build_vocabulary_artifact(source))
    second = render_vocabulary_artifact(build_vocabulary_artifact(source))

    assert first == second
    assert '"schema_version": 1' in first
    assert '"source": "vocab.md"' in first
    assert "generated_at" not in first
    assert str(Path.cwd()) not in first


def test_checked_in_artifact_matches_canonical_source() -> None:
    source = SOURCE_PATH.read_text(encoding="utf-8")
    checked_in = ARTIFACT_PATH.read_text(encoding="utf-8")

    check_vocabulary_drift(source, checked_in)


def test_drift_error_reports_the_changed_field_path() -> None:
    source = SOURCE_PATH.read_text(encoding="utf-8")
    payload = build_vocabulary_artifact(source)
    payload["records"][0]["labels"]["en"] = "Changed label"
    changed = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"

    with pytest.raises(VocabularyDriftError, match=r"records\[0\]\.labels\.en"):
        check_vocabulary_drift(source, changed)


def test_runtime_loader_consumes_validated_generated_artifact() -> None:
    records = load_generated_vocabulary()

    assert len(records) == 343
    assert (
        records[0].identity.vocabulary_type.value
        <= records[-1].identity.vocabulary_type.value
    )
    assert any(record.labels.vi == "Nền tảng AI" for record in records)
