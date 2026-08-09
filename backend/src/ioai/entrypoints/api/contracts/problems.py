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
