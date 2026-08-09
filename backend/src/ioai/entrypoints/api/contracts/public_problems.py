from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PublicLocalizedTextResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    en: str = Field(min_length=1)
    vi: str = Field(min_length=1)


class PublicProblemListItemResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: str
    public_short_id: str
    title: PublicLocalizedTextResponse
    objective: PublicLocalizedTextResponse
    stage_code: str
    difficulty_code: str
    primary_competency_code: str
    topic_codes: list[str] = Field(max_length=2)
    remaining_topic_count: int = Field(ge=0)
    task_type_code: str
    expected_minutes: int = Field(gt=0)
    compute_tier_code: str
    published_at: datetime


class PublicProblemListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[PublicProblemListItemResponse]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    active_filters: dict[str, str | bool | int]


class PublicContentBlockResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: str
    content: PublicLocalizedTextResponse
    order: int = Field(gt=0)
    reveal_order: int | None = Field(default=None, gt=0)


class PublicPrerequisiteResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    relationship: str
    target_type: str
    target_code: str | None = None
    target_id: str | None = None
    minimum_evidence: str | None = None


class PublicResourceLimitsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    compute_tier_code: str
    runtime_class_code: str
    cpu_cores: int = Field(ge=0)
    ram_mb: int = Field(ge=0)
    gpu_count: int = Field(ge=0)
    gpu_vram_mb: int = Field(ge=0)
    storage_mb: int = Field(ge=0)
    runtime_seconds: int = Field(ge=0)
    network_policy: str


class PublicResponseSchemaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    choices: list[dict[str, object]] | None = None
    unit: str | None = None
    absolute_tolerance: str | None = None
    language: str | None = None
    signature: str | None = None
    starter_code: str | None = None
    public_tests: list[dict[str, object]] | None = None


class PublicProblemDetailResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: str
    public_short_id: str
    permanent_url: str
    title: PublicLocalizedTextResponse
    summary: PublicLocalizedTextResponse
    objective: PublicLocalizedTextResponse
    blocks: list[PublicContentBlockResponse]
    stage_code: str
    difficulty_code: str
    primary_competency_code: str
    secondary_competency_codes: list[str]
    topic_codes: list[str]
    prerequisite_codes: list[str]
    prerequisites: list[PublicPrerequisiteResponse]
    modality_codes: list[str]
    task_type_code: str
    expected_minutes: int = Field(gt=0)
    resources: PublicResourceLimitsResponse
    response_schema: PublicResponseSchemaResponse
    feedback_available: bool
    recommendation_url: str
    published_at: datetime


class PublicProblemRecommendationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: str
    permanent_url: str
    title: PublicLocalizedTextResponse
    stage_code: str
    difficulty_code: str
    expected_minutes: int = Field(gt=0)
    compute_tier_code: str
    label: str
    reason: str
