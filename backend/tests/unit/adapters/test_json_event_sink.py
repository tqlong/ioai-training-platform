from __future__ import annotations

import json
import logging

from ioai.adapters.observability.json_event_sink import JsonEventSink
from ioai.application.observability import ObservabilityEvent


def test_json_event_sink_emits_one_bounded_allowlisted_object(caplog) -> None:
    logger = logging.getLogger("ioai.tests.events")
    sink = JsonEventSink(logger)
    event = ObservabilityEvent(
        event="http.request.completed",
        outcome="client_error",
        environment="test",
        request_id="request-9",
        duration_ms=3,
        method="POST",
        route="/api/v1/problems/{slug}/submissions",
        status_code=422,
    )

    with caplog.at_level(logging.INFO, logger=logger.name):
        sink.emit(event)

    payload = json.loads(caplog.records[-1].message)
    assert payload == {
        "duration_ms": 3,
        "environment": "test",
        "event": "http.request.completed",
        "method": "POST",
        "outcome": "client_error",
        "request_id": "request-9",
        "route": "/api/v1/problems/{slug}/submissions",
        "status_code": 422,
    }
    assert set(payload) <= {
        "duration_ms",
        "environment",
        "event",
        "method",
        "operation_id",
        "outcome",
        "reference",
        "request_id",
        "route",
        "status_code",
    }
