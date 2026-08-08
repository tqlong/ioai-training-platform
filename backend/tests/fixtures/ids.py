from __future__ import annotations

import uuid


def deterministic_id(namespace: str, key: str) -> str:
    """Return deterministic but stable IDs for fixture reuse and snapshot stability."""

    return f"{namespace}:{key}:{uuid.uuid5(uuid.NAMESPACE_URL, f'{namespace}:{key}')!s}"
