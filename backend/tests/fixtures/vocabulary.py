from __future__ import annotations

from ioai.adapters.vocabulary.runtime import load_generated_vocabulary
from ioai.domain.vocabulary.values import VocabularyRecord


def canonical_vocabulary_records() -> tuple[VocabularyRecord, ...]:
    """Return deterministic canonical records from the generated artifact."""
    return load_generated_vocabulary()
