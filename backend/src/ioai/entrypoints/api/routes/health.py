from __future__ import annotations

from typing import Callable

from fastapi import APIRouter

ReadinessProbe = Callable[[], bool]


def health_router(*, is_ready: ReadinessProbe | None = None) -> APIRouter:
    router = APIRouter(tags=["health"])
    probe = is_ready or (lambda: True)

    @router.get("/health/live", tags=["health"], summary="Liveness check")
    def live() -> dict[str, str]:
        return {
            "status": "ok",
            "scope": "platform",
        }

    @router.get("/health/ready", tags=["health"], summary="Readiness check")
    def ready() -> dict[str, str | bool]:
        ready_state = bool(probe())
        return {
            "status": "ok" if ready_state else "degraded",
            "database": "ready" if ready_state else "not_ready",
        }

    return router
