from __future__ import annotations

import json
from pathlib import Path

from ioai.domain.vocabulary.validation import validate_vocabulary
from ioai.domain.vocabulary.values import (
    LocalizedLabels,
    VocabularyIdentity,
    VocabularyRecord,
    VocabularyStatus,
    VocabularyType,
)

from .artifact_contract import ARTIFACT_PATH, validate_artifact_contract


def load_generated_vocabulary(
    path: Path = ARTIFACT_PATH,
) -> tuple[VocabularyRecord, ...]:
    """Load generated runtime data through contract and domain validation."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = validate_artifact_contract(payload)
    domain_records = []
    for record in records:
        vocabulary_type = VocabularyType(record["vocabulary_type"])
        parent = (
            VocabularyIdentity(VocabularyType("TOPIC"), record["parent_code"])
            if record["parent_code"] is not None
            else None
        )
        domain_records.append(
            VocabularyRecord(
                identity=VocabularyIdentity(vocabulary_type, record["code"]),
                labels=LocalizedLabels(**record["labels"]),
                aliases=tuple(record["aliases"]),
                status=VocabularyStatus(record["status"]),
                parent=parent,
            )
        )
    return validate_vocabulary(domain_records)
