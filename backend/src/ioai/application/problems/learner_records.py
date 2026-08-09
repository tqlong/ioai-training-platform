from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol

MAX_KEY_LENGTH = 200
MAX_RESULT_FIELDS = 32
MAX_RESULT_BYTES = 16_384
MAX_FEEDBACK_LENGTH = 2000


class LearnerOutcome(StrEnum):
    ACCEPTED_RESULT = "ACCEPTED_RESULT"
    PENDING_ASSESSMENT = "PENDING_ASSESSMENT"


class FeedbackCategory(StrEnum):
    CONTENT_ISSUE = "CONTENT_ISSUE"
    TYPO = "TYPO"
    SCORING_ISSUE = "SCORING_ISSUE"
    ACCESSIBILITY = "ACCESSIBILITY"
    OTHER = "OTHER"


def _require_identifier(value: str, label: str, maximum: int = 128) -> str:
    normalized = value.strip()
    if not normalized or len(normalized) > maximum:
        raise ValueError(f"{label} must contain between 1 and {maximum} characters")
    return normalized


def _require_digest(value: str) -> str:
    if len(value) != 64 or any(
        character not in "0123456789abcdef" for character in value
    ):
        raise ValueError("request digest must be 64 lowercase hexadecimal characters")
    return value


@dataclass(frozen=True, slots=True)
class LearnerAttempt:
    attempt_id: str
    snapshot_id: str
    submission_key: str
    request_digest: str
    outcome: LearnerOutcome
    result: dict[str, object]
    submitted_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "attempt_id", _require_identifier(self.attempt_id, "attempt ID")
        )
        object.__setattr__(
            self, "snapshot_id", _require_identifier(self.snapshot_id, "snapshot ID")
        )
        object.__setattr__(
            self,
            "submission_key",
            _require_identifier(self.submission_key, "submission key", MAX_KEY_LENGTH),
        )
        object.__setattr__(self, "request_digest", _require_digest(self.request_digest))
        if len(self.result) > MAX_RESULT_FIELDS:
            raise ValueError(f"result must contain at most {MAX_RESULT_FIELDS} fields")
        encoded_result = json.dumps(
            self.result, ensure_ascii=False, separators=(",", ":")
        ).encode()
        if len(encoded_result) > MAX_RESULT_BYTES:
            raise ValueError(f"result must be at most {MAX_RESULT_BYTES} bytes")
        if self.submitted_at.tzinfo is None:
            raise ValueError("submitted time must include a timezone")


@dataclass(frozen=True, slots=True)
class ProblemFeedback:
    feedback_id: str
    snapshot_id: str
    feedback_key: str
    request_digest: str
    category: FeedbackCategory
    message: str
    submitted_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "feedback_id", _require_identifier(self.feedback_id, "feedback ID")
        )
        object.__setattr__(
            self, "snapshot_id", _require_identifier(self.snapshot_id, "snapshot ID")
        )
        object.__setattr__(
            self,
            "feedback_key",
            _require_identifier(self.feedback_key, "feedback key", MAX_KEY_LENGTH),
        )
        object.__setattr__(self, "request_digest", _require_digest(self.request_digest))
        message = self.message.strip()
        if not message or len(message) > MAX_FEEDBACK_LENGTH:
            raise ValueError(
                f"message must contain between 1 and {MAX_FEEDBACK_LENGTH} characters"
            )
        object.__setattr__(self, "message", message)
        if self.submitted_at.tzinfo is None:
            raise ValueError("submitted time must include a timezone")


class LearnerRecordRepository(Protocol):
    def add_attempt(self, attempt: LearnerAttempt) -> None: ...

    def replay_attempt(
        self, snapshot_id: str, submission_key: str
    ) -> LearnerAttempt | None: ...

    def add_feedback(self, feedback: ProblemFeedback) -> None: ...

    def replay_feedback(
        self, snapshot_id: str, feedback_key: str
    ) -> ProblemFeedback | None: ...
