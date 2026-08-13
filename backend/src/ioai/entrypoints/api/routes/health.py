from __future__ import annotations

from typing import Callable

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from ioai.application.readiness import DependencyReadiness

ReadinessProbe = Callable[[], bool | DependencyReadiness]


class ReadinessResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    status: str
    database: str
    schema_state: str = Field(alias="schema")


def health_router(*, is_ready: ReadinessProbe | None = None) -> APIRouter:
    router = APIRouter(tags=["health"])
    probe = is_ready or (lambda: True)

    @router.get("/health/live", tags=["health"], summary="Liveness check")
    def live() -> dict[str, str]:
        return {
            "status": "ok",
            "scope": "platform",
        }

    @router.get(
        "/health/ready",
        tags=["health"],
        summary="Readiness check",
        response_model=ReadinessResponse,
        responses={503: {"model": ReadinessResponse}},
    )
    def ready() -> JSONResponse:
        try:
            result = probe()
        except Exception:
            result = DependencyReadiness.unavailable()
        state = (
            result
            if isinstance(result, DependencyReadiness)
            else DependencyReadiness.ready()
            if result
            else DependencyReadiness.unavailable()
        )
        return JSONResponse(
            status_code=200 if state.is_ready else 503,
            content={
                "status": "ready" if state.is_ready else "not_ready",
                "database": state.database,
                "schema": state.schema,
            },
        )

    return router
