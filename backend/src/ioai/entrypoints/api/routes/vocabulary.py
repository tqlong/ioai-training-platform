from __future__ import annotations

from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Annotated

from fastapi import APIRouter, Query

from ioai.application.vocabulary.queries import (
    QueryVocabulary,
    VocabularyQuery,
    VocabularyQueryItem,
    VocabularyReader,
)
from ioai.domain.vocabulary.availability import Release0AvailabilityPolicy
from ioai.domain.vocabulary.values import VocabularyIdentity

from ..contracts.errors import ErrorResponse
from ..contracts.vocabulary import (
    AuthorVocabularyRecord,
    AuthorVocabularyResponse,
    AvailabilityResponse,
    LocalizedLabelsResponse,
    PublicVocabularyRecord,
    PublicVocabularyResponse,
    VocabularyIdentityResponse,
)

VocabularyReaderFactory = Callable[[], AbstractContextManager[VocabularyReader]]


def vocabulary_router(
    reader_factory: VocabularyReaderFactory,
    policy: Release0AvailabilityPolicy | None = None,
) -> APIRouter:
    router = APIRouter(tags=["vocabulary"])
    availability_policy = policy or Release0AvailabilityPolicy()

    @router.get(
        "/vocabulary",
        response_model=PublicVocabularyResponse,
        responses={422: {"model": ErrorResponse}},
    )
    def list_public_vocabulary(
        vocabulary_type: Annotated[str, Query(pattern=r"^[A-Z][A-Z0-9_]*$")],
        search: Annotated[str | None, Query(max_length=200)] = None,
        root_code: Annotated[str | None, Query(pattern=r"^[A-Z][A-Z0-9_]*$")] = None,
        include_descendants: bool = False,
        limit: Annotated[int, Query(ge=1, le=500)] = 100,
    ) -> PublicVocabularyResponse:
        query = VocabularyQuery(
            vocabulary_type=vocabulary_type,
            search=search,
            root_code=root_code,
            include_descendants=include_descendants,
            limit=limit,
        )
        with reader_factory() as reader:
            items = [
                _public_record(item, availability_policy)
                for item in QueryVocabulary(reader)(query, active_only=True)
            ]
        return PublicVocabularyResponse(items=items, count=len(items))

    @router.get(
        "/author/vocabulary",
        response_model=AuthorVocabularyResponse,
        responses={422: {"model": ErrorResponse}},
    )
    def list_author_vocabulary(
        vocabulary_type: Annotated[str, Query(pattern=r"^[A-Z][A-Z0-9_]*$")],
        search: Annotated[str | None, Query(max_length=200)] = None,
        root_code: Annotated[str | None, Query(pattern=r"^[A-Z][A-Z0-9_]*$")] = None,
        include_descendants: bool = False,
        limit: Annotated[int, Query(ge=1, le=500)] = 100,
    ) -> AuthorVocabularyResponse:
        query = VocabularyQuery(
            vocabulary_type=vocabulary_type,
            search=search,
            root_code=root_code,
            include_descendants=include_descendants,
            limit=limit,
        )
        with reader_factory() as reader:
            items = [
                _author_record(item, availability_policy)
                for item in QueryVocabulary(reader)(query, active_only=False)
            ]
        return AuthorVocabularyResponse(items=items, count=len(items))

    return router


def _public_record(
    item: VocabularyQueryItem,
    policy: Release0AvailabilityPolicy,
) -> PublicVocabularyRecord:
    record = item.record
    decision = policy.evaluate(record.identity)
    return PublicVocabularyRecord(
        identity=_identity(record.identity),
        labels=LocalizedLabelsResponse(en=record.labels.en, vi=record.labels.vi),
        aliases=list(record.aliases),
        parent_identity=_identity(record.parent) if record.parent else None,
        breadcrumbs=[_identity(ancestor.identity) for ancestor in item.breadcrumbs],
        availability=AvailabilityResponse(
            is_available=decision.is_available,
            reason_code=decision.reason_code,
            message=decision.message,
        ),
    )


def _author_record(
    item: VocabularyQueryItem,
    policy: Release0AvailabilityPolicy,
) -> AuthorVocabularyRecord:
    record = item.record
    public = _public_record(item, policy)
    return AuthorVocabularyRecord(
        **public.model_dump(),
        status=record.status.value,
    )


def _identity(identity: VocabularyIdentity) -> VocabularyIdentityResponse:
    return VocabularyIdentityResponse(
        vocabulary_type=identity.vocabulary_type.value,
        code=identity.code,
    )
