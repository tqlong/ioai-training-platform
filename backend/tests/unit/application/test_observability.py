from __future__ import annotations

import pytest

from ioai.application.observability import (
    ObservabilityEvent,
    bind_request_id,
    observe_operation,
)


class RecordingSink:
    def __init__(self) -> None:
        self.events: list[ObservabilityEvent] = []

    def emit(self, event: ObservabilityEvent) -> None:
        self.events.append(event)


def test_observed_operation_propagates_safe_context_and_hashes_retry_key() -> None:
    sink = RecordingSink()
    times = iter((10.0, 10.025))

    with bind_request_id("request-7"):
        result = observe_operation(
            sink=sink,
            event_name="learner.submission",
            environment="test",
            raw_operation_id="private-receipt-and-answer",
            reference="canonical-problem-slug",
            action=lambda: "accepted",
            clock=lambda: next(times),
        )

    assert result == "accepted"
    assert sink.events == [
        ObservabilityEvent(
            event="learner.submission",
            outcome="success",
            environment="test",
            request_id="request-7",
            duration_ms=25,
            operation_id=sink.events[0].operation_id,
            reference="canonical-problem-slug",
        )
    ]
    assert sink.events[0].operation_id.startswith("op_")
    assert "private" not in sink.events[0].operation_id


def test_observed_operation_emits_failure_without_recording_exception_details() -> None:
    sink = RecordingSink()
    times = iter((4.0, 4.001))

    with bind_request_id("request-8"):
        with pytest.raises(RuntimeError, match="secret SQL and filesystem path"):
            observe_operation(
                sink=sink,
                event_name="author.publication",
                environment="test",
                raw_operation_id="publish-key",
                reference="safe-slug",
                action=lambda: (_ for _ in ()).throw(
                    RuntimeError("secret SQL and filesystem path")
                ),
                clock=lambda: next(times),
            )

    assert sink.events[0].outcome == "failure"
    assert "secret" not in repr(sink.events[0])


def test_event_rejects_free_form_reference_data() -> None:
    with pytest.raises(ValueError, match="canonical slug"):
        ObservabilityEvent(
            event="learner.submission",
            outcome="success",
            environment="test",
            request_id="request-10",
            duration_ms=1,
            reference="answer text must not be logged",
        )
