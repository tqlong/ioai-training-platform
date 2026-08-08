from __future__ import annotations

from datetime import datetime, timezone


class DeterministicClock:
    """A simple deterministic clock for tests that cannot rely on wall clock time."""

    def __init__(self, now: datetime | None = None) -> None:
        self._now = now or datetime(2026, 1, 1, tzinfo=timezone.utc)

    def now(self) -> datetime:
        current = self._now
        self._now = self._now.replace(second=(self._now.second + 1) % 60)
        return current
