from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette import status


@dataclass(frozen=True)
class PublicError:
    code: str
    message: str


def public_error(code: str, message: str) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
        }
    }


def install_error_handlers(app: FastAPI, request_id_header: str) -> None:
    @app.exception_handler(Exception)
    async def _unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = request.headers.get(request_id_header)
        payload = public_error("internal_error", "An unexpected error occurred.")
        if request_id:
            payload["request_id"] = request_id
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=payload)
