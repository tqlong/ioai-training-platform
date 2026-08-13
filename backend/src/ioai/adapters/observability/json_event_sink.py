from __future__ import annotations

import json
import logging

from ioai.application.observability import ObservabilityEvent


class JsonEventSink:
    """Write one compact JSON object for each allowlisted system event."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._logger = logger or logging.getLogger("uvicorn.error")

    def emit(self, event: ObservabilityEvent) -> None:
        self._logger.info(
            json.dumps(event.as_payload(), ensure_ascii=True, sort_keys=True)
        )
