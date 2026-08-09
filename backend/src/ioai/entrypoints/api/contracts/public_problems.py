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
