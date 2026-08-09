from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class VocabularyIdentityResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vocabulary_type: str
    code: str


class LocalizedLabelsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    en: str
    vi: str


class AvailabilityResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_available: bool
    reason_code: str
    message: str


class PublicVocabularyRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identity: VocabularyIdentityResponse
    labels: LocalizedLabelsResponse
    aliases: list[str]
    parent_identity: VocabularyIdentityResponse | None
    breadcrumbs: list[VocabularyIdentityResponse]


class AuthorVocabularyRecord(PublicVocabularyRecord):
    status: str
    availability: AvailabilityResponse


class PublicVocabularyResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[PublicVocabularyRecord]
    count: int


class AuthorVocabularyResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[AuthorVocabularyRecord]
    count: int
