from __future__ import annotations

from collections.abc import Callable
from contextlib import contextmanager
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from ...adapters.database.problem_repository import SqlAlchemyDraftUnitOfWork
from ...adapters.database.proposal_repository import SqlAlchemyProposalUnitOfWork
from ...adapters.database.session import (
    build_engine,
    build_session_factory,
    check_connection,
)
from ...adapters.database.settings import DatabaseSettings
from ...adapters.database.vocabulary_repository import SqlAlchemyVocabularyRepository
from ...application.problems.authoring import CreateDraft, GetDraft, ListDrafts
from ...application.vocabulary.proposals import RecordVocabularyProposal
from .errors import install_error_handlers
from .routes.health import health_router
from .routes.problems import AuthorProblemService, author_problem_router
from .routes.proposals import ProposalService, proposal_router
from .routes.vocabulary import VocabularyReaderFactory, vocabulary_router
from .settings import ApiSettings

ReadinessProbe = Callable[[], bool]


def create_app(
    *,
    settings: ApiSettings | None = None,
    readiness_probe: ReadinessProbe | None = None,
    vocabulary_reader_factory: VocabularyReaderFactory | None = None,
    proposal_service: ProposalService | None = None,
    author_problem_service: AuthorProblemService | None = None,
) -> FastAPI:
    resolved_settings = settings or ApiSettings.from_env()
    resolved_probe = readiness_probe
    resolved_reader_factory = vocabulary_reader_factory
    resolved_proposal_service = proposal_service
    resolved_author_problem_service = author_problem_service
    db_settings = DatabaseSettings.from_env()
    engine = build_engine(db_settings)
    session_factory = build_session_factory(engine)
    if readiness_probe is None:

        def default_probe() -> bool:
            try:
                return check_connection(db_settings.url)
            except Exception:
                return False

        resolved_probe = default_probe

    if resolved_reader_factory is None:

        @contextmanager
        def default_reader():
            with session_factory() as session:
                yield SqlAlchemyVocabularyRepository(session)

        resolved_reader_factory = default_reader

    if resolved_proposal_service is None:
        resolved_proposal_service = RecordVocabularyProposal(
            unit_of_work_factory=lambda: SqlAlchemyProposalUnitOfWork(session_factory),
            id_generator=lambda: str(uuid4()),
            clock=lambda: datetime.now(UTC),
        )

    if resolved_author_problem_service is None:

        def draft_uow() -> SqlAlchemyDraftUnitOfWork:
            return SqlAlchemyDraftUnitOfWork(session_factory)

        resolved_author_problem_service = _DefaultAuthorProblemService(
            create=CreateDraft(
                unit_of_work_factory=draft_uow,
                id_generator=lambda: str(uuid4()),
                clock=lambda: datetime.now(UTC),
            ),
            list_drafts=ListDrafts(draft_uow),
            get=GetDraft(draft_uow),
        )

    app = FastAPI(
        title=resolved_settings.project_name,
        debug=resolved_settings.debug,
        openapi_url=f"{resolved_settings.api_prefix}/openapi.json",
        redoc_url=None,
        docs_url="/api/docs",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router(is_ready=resolved_probe), prefix="")
    app.include_router(
        vocabulary_router(resolved_reader_factory), prefix=resolved_settings.api_prefix
    )
    app.include_router(
        proposal_router(resolved_proposal_service), prefix=resolved_settings.api_prefix
    )
    app.include_router(
        author_problem_router(resolved_author_problem_service),
        prefix=resolved_settings.api_prefix,
    )
    install_error_handlers(app, request_id_header=resolved_settings.request_id_header)
    app.add_middleware(
        _RequestIdMiddleware,
        header_name=resolved_settings.request_id_header,
    )

    @app.get("/health", include_in_schema=False)
    def heartbeat() -> dict[str, str]:
        return {"status": "ok"}

    return app


class _DefaultAuthorProblemService:
    def __init__(self, *, create: CreateDraft, list_drafts: ListDrafts, get: GetDraft):
        self._create = create
        self._list = list_drafts
        self._get = get

    def create(self):
        return self._create()

    def list(self):
        return self._list()

    def get(self, problem_id):
        return self._get(problem_id)


class _RequestIdMiddleware:
    def __init__(self, app: ASGIApp, header_name: str) -> None:
        self.app = app
        self.header_name = header_name

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_request_id(message: Message) -> None:
            if message.get("type") == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((self.header_name.encode(), b"generated"))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_with_request_id)
