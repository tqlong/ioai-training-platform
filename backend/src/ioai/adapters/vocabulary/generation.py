from __future__ import annotations

import json
from typing import Any

from ioai.domain.vocabulary.validation import validate_vocabulary
from ioai.domain.vocabulary.values import VocabularyRecord

from .artifact_contract import ARTIFACT_SCHEMA_VERSION, validate_artifact_contract
from .markdown_source import parse_vocabulary_markdown


class VocabularyDriftError(ValueError):
    """The checked-in artifact differs from the canonical source."""


def build_vocabulary_artifact(source: str) -> dict[str, Any]:
    """Parse and fully validate source before building stable artifact data."""
    records = validate_vocabulary(parse_vocabulary_markdown(source))
    payload = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "source": "vocab.md",
        "records": [_serialize_record(record) for record in records],
    }
    validate_artifact_contract(payload)
    return payload


def render_vocabulary_artifact(payload: dict[str, Any]) -> str:
    """Render deterministic UTF-8 JSON with one trailing newline."""
    validate_artifact_contract(payload)
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def check_vocabulary_drift(source: str, checked_in: str) -> None:
    """Raise with field paths when checked-in data differs from source."""
    expected = build_vocabulary_artifact(source)
    try:
        actual = json.loads(checked_in)
    except json.JSONDecodeError as error:
        raise VocabularyDriftError(f"artifact is not valid JSON: {error}") from error

    differences = _find_differences(expected, actual)
    if differences:
        raise VocabularyDriftError(
            "vocabulary artifact drift:\n" + "\n".join(differences)
        )


def _serialize_record(record: VocabularyRecord) -> dict[str, Any]:
    return {
        "vocabulary_type": record.identity.vocabulary_type.value,
        "code": record.identity.code,
        "labels": {"en": record.labels.en, "vi": record.labels.vi},
        "aliases": list(record.aliases),
        "parent_code": record.parent.code if record.parent else None,
        "status": record.status.value,
    }


def _find_differences(expected: object, actual: object, path: str = "") -> list[str]:
    if isinstance(expected, dict) and isinstance(actual, dict):
        differences: list[str] = []
        for key in sorted(expected.keys() | actual.keys()):
            child_path = f"{path}.{key}" if path else key
            if key not in expected:
                differences.append(f"{child_path}: unexpected field")
            elif key not in actual:
                differences.append(f"{child_path}: missing field")
            else:
                differences.extend(
                    _find_differences(expected[key], actual[key], child_path)
                )
        return differences
    if isinstance(expected, list) and isinstance(actual, list):
        differences = []
        for index in range(max(len(expected), len(actual))):
            child_path = f"{path}[{index}]"
            if index >= len(expected):
                differences.append(f"{child_path}: unexpected item")
            elif index >= len(actual):
                differences.append(f"{child_path}: missing item")
            else:
                differences.extend(
                    _find_differences(expected[index], actual[index], child_path)
                )
        return differences
    if expected != actual:
        return [f"{path}: expected {expected!r}, found {actual!r}"]
    return []
