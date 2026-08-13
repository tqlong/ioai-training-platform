from __future__ import annotations

import re
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Literal, Protocol, TypeVar

EventOutcome = Literal["success", "client_error", "failure"]
Result = TypeVar("Result")

_request_id: ContextVar[str | None] = ContextVar("ioai_request_id", default=None)


@dataclass(frozen=True, slots=True)
class ObservabilityEvent:
    """Allowlisted metadata for one safe structured system event."""

    event: str
    outcome: EventOutcome
    environment: str
    request_id: str
    duration_ms: int
    operation_id: str | None = None
    reference: str | None = None
    method: str | None = None
    route: str | None = None
    status_code: int | None = None

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[a-z][a-z0-9.]{0,63}", self.event):
            raise ValueError("event name must be a bounded canonical label")
        if self.outcome not in {"success", "client_error", "failure"}:
            raise ValueError("event outcome is invalid")
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", self.environment):
            raise ValueError("event environment must be a bounded label")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", self.request_id):
            raise ValueError("event request ID must be bounded")
        if not 0 <= self.duration_ms <= 86_400_000:
            raise ValueError("event duration must be bounded")
        if self.operation_id is not None and not re.fullmatch(
            r"op_[a-f0-9]{20}", self.operation_id
        ):
            raise ValueError("event operation ID must be opaque")
        if self.reference is not None and not re.fullmatch(
            r"[a-z0-9][a-z0-9-]{0,127}", self.reference
        ):
            raise ValueError("event reference must be a canonical slug")
        if self.method is not None and not re.fullmatch(r"[A-Z]{3,10}", self.method):
            raise ValueError("event method is invalid")
        if self.route is not None and (
            len(self.route) > 200
            or (self.route != "unmatched" and not self.route.startswith("/"))
        ):
            raise ValueError("event route template is invalid")
        if self.status_code is not None and not 100 <= self.status_code <= 599:
            raise ValueError("event status is invalid")

    def as_payload(self) -> dict[str, str | int]:
        return {key: value for key, value in asdict(self).items() if value is not None}


class EventSink(Protocol):
    def emit(self, event: ObservabilityEvent) -> None: ...


@contextmanager
def bind_request_id(request_id: str) -> Iterator[None]:
    token = _request_id.set(request_id)
    try:
        yield
    finally:
        _request_id.reset(token)


def current_request_id() -> str | None:
    return _request_id.get()


def observe_operation(
    *,
    sink: EventSink,
    event_name: str,
    environment: str,
    raw_operation_id: str,
    reference: str,
    action: Callable[[], Result],
    clock: Callable[[], float],
) -> Result:
    """Run an application operation and emit bounded success/failure metadata."""

    started = clock()
    outcome: EventOutcome = "success"
    try:
        return action()
    except Exception:
        outcome = "failure"
        raise
    finally:
        sink.emit(
            ObservabilityEvent(
                event=event_name,
                outcome=outcome,
                environment=environment,
                request_id=current_request_id() or "unbound",
                duration_ms=_duration_ms(started, clock()),
                operation_id=_opaque_operation_id(raw_operation_id),
                reference=reference,
            )
        )


def _opaque_operation_id(value: str) -> str:
    return f"op_{sha256(value.encode('utf-8')).hexdigest()[:20]}"


def _duration_ms(started: float, finished: float) -> int:
    return max(0, min(86_400_000, round((finished - started) * 1000)))
