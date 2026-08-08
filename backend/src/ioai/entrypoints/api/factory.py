from __future__ import annotations

from collections.abc import Callable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .errors import install_error_handlers
from .routes.health import health_router
from .settings import ApiSettings
from ...adapters.database.session import check_connection
from ...adapters.database.settings import DatabaseSettings


ReadinessProbe = Callable[[], bool]


def create_app(
    *, settings: ApiSettings | None = None, readiness_probe: ReadinessProbe | None = None
) -> FastAPI:
    resolved_settings = settings or ApiSettings.from_env()
    resolved_probe = readiness_probe
    if readiness_probe is None:
        db_settings = DatabaseSettings.from_env()

        def default_probe() -> bool:
            try:
                return check_connection(db_settings.url)
            except Exception:
                return False

        resolved_probe = default_probe

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
    def __init__(self, app: FastAPI, header_name: str) -> None:
        self.app = app
        self.header_name = header_name

    async def __call__(self, scope, receive, send) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_request_id(message: dict) -> None:
            if message.get("type") == "http.response.start":
                headers = message.setdefault("headers", [])
                headers.append((self.header_name.encode(), b"generated"))
            await send(message)

        await self.app(scope, receive, send_with_request_id)
