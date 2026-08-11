from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CreateDraftRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AuthorDraftResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    problem_id: str = Field(min_length=1, max_length=128)
    revision_id: str = Field(min_length=1, max_length=128)
    version: int = Field(ge=1)
    editorial_status: str
    slug: str | None
    content: dict[str, Any] | None
    metadata: dict[str, Any] | None
    response: dict[str, Any] | None
    scoring: dict[str, Any] | None


class AuthorDraftListItemResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    problem_id: str
    revision_id: str
    version: int = Field(ge=1)
    editorial_status: str
    last_saved_at: datetime
    validation_summary: dict[str, Any] | None


class AuthorDraftListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[AuthorDraftListItemResponse]
    count: int = Field(ge=0)


class SaveDraftRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    problem_id: str = Field(min_length=1, max_length=128)
    expected_version: int = Field(ge=1)
    client_save_key: str | None = Field(default=None, min_length=1, max_length=128)
    slug: str | None = Field(default=None, max_length=120)
    content: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    response: dict[str, Any] | None = None
    scoring: dict[str, Any] | None = None


class ValidateDraftRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_version: int = Field(ge=1)


class ValidationIssueResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: str
    section: str
    field_path: str
    message: str
    severity: str


class ValidationReportResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    revision_id: str
    revision_version: int = Field(ge=1)
    errors: list[ValidationIssueResponse]
    warnings: list[ValidationIssueResponse]
    publication_eligible: bool


class PreviewUnsavedState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    problem_id: str = Field(min_length=1, max_length=128)
    slug: str | None = Field(default=None, max_length=120)
    content: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    response: dict[str, Any] | None = None
    scoring: dict[str, Any] | None = None


class PreviewDraftRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_version: int = Field(ge=1)
    unsaved_state: PreviewUnsavedState | None = None


class PreviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    marker: str
    learner_problem: dict[str, Any]
    author_issues: list[ValidationIssueResponse]


class EditorialCommandRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_version: int = Field(ge=1)
    note: str = Field(min_length=1, max_length=2000)
    actor_context: str = Field(min_length=1, max_length=200)
    operation_id: str = Field(min_length=1, max_length=200)


class EditorialHistoryItemResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_status: str
    target_status: str
    note: str
    actor_context: str
    occurred_at: datetime
    operation_id: str


class EditorialHistoryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    items: list[EditorialHistoryItemResponse]


class PublishRevisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_version: int = Field(ge=1)
    note: str = Field(min_length=1, max_length=2000)
    actor_context: str = Field(min_length=1, max_length=200)
    idempotency_key: str = Field(min_length=1, max_length=200)


class PublicationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    snapshot_id: str
    slug: str
    public_url: str
    published_at: datetime


class StartRevisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_revision_id: str = Field(min_length=1, max_length=128)
    expected_version: int = Field(ge=1)
    operation_id: str = Field(min_length=1, max_length=200)


class ArchiveProblemRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_version: int = Field(ge=1)
    note: str = Field(min_length=1, max_length=2000)
    actor_context: str = Field(min_length=1, max_length=200)
    operation_id: str = Field(min_length=1, max_length=200)


class ArchiveProblemResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    problem_id: str
    slug: str
    archived_at: datetime


class AssessmentSelectionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    component_index: int = Field(ge=0)
    criterion_id: str = Field(min_length=1, max_length=64)
    level_id: str = Field(min_length=1, max_length=64)
    feedback: str | None = Field(default=None, max_length=2000)


class AssessmentDecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    selections: list[AssessmentSelectionRequest] = Field(min_length=1, max_length=100)
    expected_decision_id: str | None = Field(default=None, max_length=128)
    overall_feedback: str | None = Field(default=None, max_length=2000)
    correction_reason: str | None = Field(default=None, max_length=2000)


class AssessmentListItemResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    attempt_id: str
    slug: str
    title: dict[str, Any]
    status: str
    submitted_at: datetime
    score: str | None = None


class AssessmentListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    items: list[AssessmentListItemResponse]
    next_offset: int | None = None


class AssessmentDetailResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    attempt_id: str
    slug: str
    title: dict[str, Any]
    status: str
    submitted_at: datetime
    submitted_response: dict[str, Any]
    scoring: dict[str, Any]
    latest_decision: dict[str, Any] | None = None
    decision_history: list[dict[str, Any]] = Field(default_factory=list)
