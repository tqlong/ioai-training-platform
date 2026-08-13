from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

DatabaseState = Literal["ready", "unavailable"]
SchemaState = Literal["current", "outdated", "unknown"]


@dataclass(frozen=True, slots=True)
class DependencyReadiness:
    """Safe operational state for required API dependencies."""

    database: DatabaseState
    schema: SchemaState

    @property
    def is_ready(self) -> bool:
        return self.database == "ready" and self.schema == "current"

    @classmethod
    def ready(cls) -> "DependencyReadiness":
        return cls(database="ready", schema="current")

    @classmethod
    def unavailable(cls) -> "DependencyReadiness":
        return cls(database="unavailable", schema="unknown")
