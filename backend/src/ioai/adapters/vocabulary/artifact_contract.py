from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

ARTIFACT_SCHEMA_VERSION = 1
ARTIFACT_PATH = Path("backend/generated/vocabulary.json")

_ROOT_FIELDS = {"schema_version", "source", "records"}
_RECORD_FIELDS = {
    "vocabulary_type",
    "code",
    "labels",
    "aliases",
    "parent_code",
    "status",
}
_LABEL_FIELDS = {"en", "vi"}


class ArtifactContractError(ValueError):
    """Raised when generated vocabulary data violates its stable contract."""


def validate_artifact_contract(payload: object) -> list[dict[str, Any]]:
    """Validate and return records from a generated vocabulary artifact."""
    root = _require_mapping(payload, "artifact")
    _require_exact_fields(root, _ROOT_FIELDS, "artifact")

    if root["schema_version"] != ARTIFACT_SCHEMA_VERSION:
        raise ArtifactContractError(f"schema_version must be {ARTIFACT_SCHEMA_VERSION}")
    if root["source"] != "vocab.md":
        raise ArtifactContractError("source must be vocab.md")

    raw_records = root["records"]
    if not isinstance(raw_records, list):
        raise ArtifactContractError("records must be a list")

    records = [
        _validate_record(record, index) for index, record in enumerate(raw_records)
    ]
    keys = [(record["vocabulary_type"], record["code"]) for record in records]
    if keys != sorted(keys):
        raise ArtifactContractError("records must use vocabulary_type/code ordering")
    return records


def _validate_record(payload: object, index: int) -> dict[str, Any]:
    path = f"records[{index}]"
    record = _require_mapping(payload, path)
    _require_exact_fields(record, _RECORD_FIELDS, path)

    for field in ("vocabulary_type", "code", "status"):
        if not isinstance(record[field], str) or not record[field].strip():
            raise ArtifactContractError(f"{path}.{field} must be a non-empty string")

    labels = _require_mapping(record["labels"], f"{path}.labels")
    _require_exact_fields(labels, _LABEL_FIELDS, f"{path}.labels")
    for language in sorted(_LABEL_FIELDS):
        if not isinstance(labels[language], str) or not labels[language].strip():
            raise ArtifactContractError(
                f"{path}.labels.{language} must be a non-empty string"
            )

    aliases = record["aliases"]
    if not isinstance(aliases, list) or not all(
        isinstance(alias, str) and alias.strip() for alias in aliases
    ):
        raise ArtifactContractError(f"{path}.aliases must contain non-empty strings")

    parent_code = record["parent_code"]
    if parent_code is not None and (
        not isinstance(parent_code, str) or not parent_code.strip()
    ):
        raise ArtifactContractError(
            f"{path}.parent_code must be null or a non-empty string"
        )

    return {
        "vocabulary_type": record["vocabulary_type"],
        "code": record["code"],
        "labels": {"en": labels["en"], "vi": labels["vi"]},
        "aliases": list(aliases),
        "parent_code": parent_code,
        "status": record["status"],
    }


def _require_mapping(payload: object, path: str) -> Mapping[str, Any]:
    if not isinstance(payload, Mapping):
        raise ArtifactContractError(f"{path} must be an object")
    if not all(isinstance(key, str) for key in payload):
        raise ArtifactContractError(f"{path} keys must be strings")
    return payload


def _require_exact_fields(
    payload: Mapping[str, Any], expected: set[str], path: str
) -> None:
    missing = expected - payload.keys()
    unknown = payload.keys() - expected
    if missing:
        raise ArtifactContractError(f"{path}.{sorted(missing)[0]} is required")
    if unknown:
        raise ArtifactContractError(f"{path}.{sorted(unknown)[0]} is not allowed")
