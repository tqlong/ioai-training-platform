from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from hashlib import sha256
from typing import Protocol

from .assessment import AssessmentUnitOfWork
from .errors import IdempotencyConflictError, PublishedProblemNotFoundError
from .learner_records import FeedbackCategory, ProblemFeedback


class FeedbackThrottle(Protocol):
    def allow(self, token: str) -> bool: ...


@dataclass(frozen=True, slots=True)
class SubmitFeedbackCommand:
    slug: str
    feedback_key: str
    category: FeedbackCategory
    message: str
    abuse_token: str

    def __post_init__(self) -> None:
        for value, label, maximum in (
            (self.slug, "slug", 128),
            (self.feedback_key, "feedback key", 200),
            (self.abuse_token, "abuse token", 128),
        ):
            if not value.strip() or len(value) > maximum:
                raise ValueError(f"{label} must be bounded")
        message = self.message.strip()
        if not message or len(message) > 2000:
            raise ValueError("message must contain between 1 and 2000 characters")
        object.__setattr__(self, "message", message)


class RecordProblemFeedback:
    def __init__(
        self,
        unit_of_work_factory: Callable[[], AssessmentUnitOfWork],
        id_generator: Callable[[], str],
        clock: Callable[[], datetime],
        throttle: FeedbackThrottle,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._id_generator = id_generator
        self._clock = clock
        self._throttle = throttle

    def __call__(self, command: SubmitFeedbackCommand) -> ProblemFeedback:
        digest = _feedback_digest(command)
        with self._unit_of_work_factory() as work:
            snapshot = work.published.get_current_by_slug(command.slug)
            if snapshot is None:
                raise PublishedProblemNotFoundError("published problem was not found")
            replay = work.records.replay_feedback(
                snapshot.snapshot_id, command.feedback_key
            )
            if replay is not None:
                if replay.request_digest != digest:
                    raise IdempotencyConflictError("feedback key was reused")
                return replay
            if not self._throttle.allow(command.abuse_token):
                raise PermissionError("anonymous feedback rate limit exceeded")
            feedback = ProblemFeedback(
                self._id_generator(),
                snapshot.snapshot_id,
                command.feedback_key,
                digest,
                command.category,
                command.message,
                self._clock(),
            )
            work.records.add_feedback(feedback)
            return feedback


class FixedWindowFeedbackThrottle:
    """Small process-local pilot throttle; tokens are already one-way digests."""

    def __init__(
        self,
        clock: Callable[[], datetime],
        limit: int = 5,
        window: timedelta = timedelta(minutes=10),
        maximum_tokens: int = 10_000,
    ) -> None:
        self._clock = clock
        self._limit = limit
        self._window = window
        self._maximum_tokens = maximum_tokens
        self._events: dict[str, list[datetime]] = {}

    def allow(self, token: str) -> bool:
        now = self._clock()
        cutoff = now - self._window
        events = [value for value in self._events.get(token, []) if value > cutoff]
        if len(events) >= self._limit:
            self._events[token] = events
            return False
        if token not in self._events and len(self._events) >= self._maximum_tokens:
            oldest = min(self._events, key=lambda item: self._events[item][-1])
            self._events.pop(oldest, None)
        self._events[token] = [*events, now]
        return True


def anonymous_abuse_token(value: str) -> str:
    return sha256(value.encode()).hexdigest()


def _feedback_digest(command: SubmitFeedbackCommand) -> str:
    payload = json.dumps(
        {
            "slug": command.slug,
            "category": command.category.value,
            "message": command.message,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256(payload.encode()).hexdigest()
