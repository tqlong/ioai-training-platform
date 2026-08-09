from __future__ import annotations

from collections.abc import Callable
from contextlib import contextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from ...adapters.database.session import (
    build_engine,
    build_session_factory,
    check_connection,
)
from ...adapters.database.settings import DatabaseSettings
from ...adapters.database.vocabulary_repository import SqlAlchemyVocabularyRepository
from .errors import install_error_handlers
from .routes.health import health_router
from .routes.vocabulary import VocabularyReaderFactory, vocabulary_router
from .settings import ApiSettings

ReadinessProbe = Callable[[], bool]


def create_app(
    *,
    settings: ApiSettings | None = None,
    readiness_probe: ReadinessProbe | None = None,
    vocabulary_reader_factory: VocabularyReaderFactory | None = None,
) -> FastAPI:
    resolved_settings = settings or ApiSettings.from_env()
    resolved_probe = readiness_probe
    resolved_reader_factory = vocabulary_reader_factory
    db_settings = DatabaseSettings.from_env()
    if readiness_probe is None:

        def default_probe() -> bool:
            try:
                return check_connection(db_settings.url)
            except Exception:
                return False

        resolved_probe = default_probe

    if resolved_reader_factory is None:
        engine = build_engine(db_settings)
        session_factory = build_session_factory(engine)

        @contextmanager
        def default_reader():
            with session_factory() as session:
                yield SqlAlchemyVocabularyRepository(session)

        resolved_reader_factory = default_reader

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
    install_error_handlers(app, request_id_header=resolved_settings.request_id_header)
    app.add_middleware(
        _RequestIdMiddleware,
        header_name=resolved_settings.request_id_header,
    )

    @app.get("/health", include_in_schema=False)
    def heartbeat() -> dict[str, str]:
        return {"status": "ok"}

    return app


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
