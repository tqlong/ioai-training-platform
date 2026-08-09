from __future__ import annotations

import json
from pathlib import Path

import pytest

from ioai.adapters.vocabulary.artifact_contract import (
    ARTIFACT_PATH,
    ArtifactContractError,
    validate_artifact_contract,
)

FIXTURE_ROOT = Path("backend/tests/fixtures/vocabulary")


def test_representative_source_fixture_covers_declared_vocabulary_shapes() -> None:
    source = (FIXTURE_ROOT / "source_shapes.md").read_text(encoding="utf-8")

    assert "| Code | English label | Vietnamese label |" in source
    assert "| Definition |" in source
    assert "| Parent code | Status |" in source
    assert "Parent: `MATH_LINEAR_ALGEBRA_TOPICS`" in source
    assert '"aliases": ["logit"]' in source


def test_artifact_contract_accepts_nested_labels_aliases_and_explicit_parent() -> None:
    payload = json.loads(
        (FIXTURE_ROOT / "artifact_records.json").read_text(encoding="utf-8")
    )

    records = validate_artifact_contract(payload)

    assert ARTIFACT_PATH.as_posix() == "backend/generated/vocabulary.json"
    assert [record["code"] for record in records] == [
        "AI_1_FOUNDATIONS",
        "ML_LOGISTIC_REGRESSION",
    ]
    assert records[1]["labels"] == {
        "en": "Logistic Regression",
        "vi": "Hồi quy logistic",
    }
    assert records[1]["aliases"] == ["logit"]
    assert records[1]["parent_code"] == "ML_CLASSIFICATION_METHODS"


@pytest.mark.parametrize(
    ("mutation", "diagnostic"),
    [
        (lambda payload: payload.pop("schema_version"), "schema_version"),
        (lambda payload: payload["records"][0]["labels"].pop("vi"), "labels.vi"),
        (lambda payload: payload["records"][0].pop("parent_code"), "parent_code"),
        (lambda payload: payload["records"][0].update(extra="value"), "extra"),
    ],
)
def test_artifact_contract_rejects_missing_or_unknown_fields(
    mutation, diagnostic
) -> None:
    payload = json.loads(
        (FIXTURE_ROOT / "artifact_records.json").read_text(encoding="utf-8")
    )
    mutation(payload)

    with pytest.raises(ArtifactContractError, match=diagnostic):
        validate_artifact_contract(payload)
