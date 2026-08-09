from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ErrorDetailResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error: ErrorDetailResponse
    request_id: str | None = None
