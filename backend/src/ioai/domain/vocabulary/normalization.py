from __future__ import annotations

import unicodedata


def normalize_vocabulary_text(value: str) -> str:
    """Normalize labels and aliases consistently for comparison and search."""
    return unicodedata.normalize("NFKC", value).casefold().strip()
