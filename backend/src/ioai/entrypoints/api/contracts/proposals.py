from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RecordVocabularyProposalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vocabulary_type: str = Field(pattern=r"^[A-Z][A-Z0-9_]*$")
    note: str = Field(min_length=1, max_length=1000)


class VocabularyProposalResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    proposal_id: str
    vocabulary_type: str
    note: str
    status: str
    created_at: datetime


class VocabularyProposalListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[VocabularyProposalResponse]
    count: int
