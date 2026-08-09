from __future__ import annotations

import re

from ioai.domain.vocabulary.errors import VocabularyDomainError
from ioai.domain.vocabulary.values import (
    LocalizedLabels,
    VocabularyIdentity,
    VocabularyRecord,
    VocabularyStatus,
    VocabularyType,
)

_SECTION_TYPES: dict[int, str | None] = {
    2: "PATHWAY_STAGE",
    3: "COMPETENCY",
    4: "DIFFICULTY",
    5: "TOPIC",
    6: "TASK_TYPE",
    7: "DATA_MODALITY",
    8: None,
    9: "EXPECTED_TIME_CATEGORY",
    10: None,
    11: "SCORING_METHOD",
}
_SUBSECTION_TYPES = {
    "task status": "TASK_STATUS",
    "relationship type": "PREREQUISITE_RELATIONSHIP",
    "target type": "PREREQUISITE_TARGET_TYPE",
    "learning evidence level": "LEARNING_EVIDENCE",
    "compute tier": "COMPUTE_TIER",
    "runtime class": "RUNTIME_CLASS",
}
_SECTION_PATTERN = re.compile(r"^##\s+(\d+)\.")
_LEAF_PATTERN = re.compile(
    r"^-\s+`(?P<code>[A-Z][A-Z0-9_]*)`\s+(?:—|-)\s+"
    r"(?P<en>.+?)\s+(?:—|-)\s+(?P<vi>.+?)\s+(?:—|-)\s+"
    r"Parent:\s+`(?P<parent>[A-Z][A-Z0-9_]*)`\s*$"
)


class VocabularySourceError(ValueError):
    """A canonical Markdown source record cannot be parsed safely."""


def parse_vocabulary_markdown(source: str) -> list[VocabularyRecord]:
    """Parse canonical records while requiring explicit topic parent fields."""
    records: list[VocabularyRecord] = []
    current_type: str | None = None
    current_section: int | None = None

    for line_number, raw_line in enumerate(source.splitlines(), start=1):
        line = raw_line.strip()
        section_match = _SECTION_PATTERN.match(line)
        if section_match:
            current_section = int(section_match.group(1))
            current_type = _SECTION_TYPES.get(current_section)
            continue

        if current_section not in _SECTION_TYPES:
            continue

        if line.startswith("### "):
            heading = line[4:].split("/")[0].strip().casefold()
            current_type = _SUBSECTION_TYPES.get(
                heading, _SECTION_TYPES.get(current_section)
            )
            continue

        if current_section == 7 and line.startswith("Store data origin separately"):
            current_type = "DATA_ORIGIN"
            continue

        if current_section == 5 and line.startswith("- `"):
            records.append(_parse_topic_leaf(line, line_number))
            continue

        if current_type is not None and line.startswith("| `"):
            records.append(_parse_table_record(line, line_number, current_type))

    return records


def _parse_table_record(
    line: str, line_number: int, vocabulary_type: str
) -> VocabularyRecord:
    cells = [cell.strip() for cell in line.strip("|").split("|")]
    minimum_cells = 5 if vocabulary_type == "TOPIC" else 3
    if len(cells) < minimum_cells:
        detail = (
            "explicit Parent code and Status"
            if vocabulary_type == "TOPIC"
            else "labels"
        )
        raise VocabularySourceError(f"line {line_number}: record is missing {detail}")

    code = _strip_code(cells[0])
    en = cells[1].strip()
    vi = cells[2].strip()
    if not en:
        raise VocabularySourceError(f"line {line_number}: English label is required")
    if not vi:
        raise VocabularySourceError(f"line {line_number}: Vietnamese label is required")

    parent_code: str | None = None
    status = "ACTIVE"
    if vocabulary_type == "TOPIC":
        parent_value = _strip_code(cells[3])
        parent_code = None if parent_value == "null" else parent_value
        status = _strip_code(cells[4])

    return _build_record(
        line_number=line_number,
        vocabulary_type=vocabulary_type,
        code=code,
        en=en,
        vi=vi,
        parent_code=parent_code,
        status=status,
    )


def _parse_topic_leaf(line: str, line_number: int) -> VocabularyRecord:
    match = _LEAF_PATTERN.match(line)
    if match is None:
        raise VocabularySourceError(
            f"line {line_number}: topic leaf requires an explicit Parent code"
        )
    return _build_record(
        line_number=line_number,
        vocabulary_type="TOPIC",
        code=match.group("code"),
        en=match.group("en"),
        vi=match.group("vi"),
        parent_code=match.group("parent"),
        status="ACTIVE",
    )


def _build_record(
    *,
    line_number: int,
    vocabulary_type: str,
    code: str,
    en: str,
    vi: str,
    parent_code: str | None,
    status: str,
) -> VocabularyRecord:
    try:
        record_type = VocabularyType(vocabulary_type)
        parent = (
            VocabularyIdentity(VocabularyType("TOPIC"), parent_code)
            if parent_code is not None
            else None
        )
        return VocabularyRecord(
            identity=VocabularyIdentity(record_type, code),
            labels=LocalizedLabels(en=en, vi=vi),
            aliases=(),
            status=VocabularyStatus(status),
            parent=parent,
        )
    except VocabularyDomainError as error:
        raise VocabularySourceError(f"line {line_number}: {error}") from error


def _strip_code(value: str) -> str:
    return value.strip().strip("`").strip()
