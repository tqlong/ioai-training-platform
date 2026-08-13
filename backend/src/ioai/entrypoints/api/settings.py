from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_ALLOWED_ORIGINS = (
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://127.0.0.1:3001",
    "http://localhost:3001",
)


@dataclass(frozen=True)
class ApiSettings:
    """Runtime settings for HTTP layer wiring."""

    project_name: str = "IOAI Training Platform"
    api_prefix: str = "/api/v1"
    debug: bool = False
    request_id_header: str = "x-request-id"
    allowed_origins: tuple[str, ...] = DEFAULT_ALLOWED_ORIGINS

    def __post_init__(self) -> None:
        if not self.allowed_origins:
            raise ValueError("allowed origins require at least one local origin")
        if any(
            origin == "*" or not origin.startswith(("http://", "https://"))
            for origin in self.allowed_origins
        ):
            raise ValueError("allowed origins must use explicit http or https origins")

    @classmethod
    def from_env(cls) -> "ApiSettings":
        debug = os.getenv("IOAI_DEBUG", "false").lower() in {"1", "true", "yes"}
        configured_origins = os.getenv("IOAI_ALLOWED_ORIGINS")
        allowed_origins = (
            tuple(
                origin.strip().rstrip("/")
                for origin in configured_origins.split(",")
                if origin.strip()
            )
            if configured_origins is not None
            else DEFAULT_ALLOWED_ORIGINS
        )
        return cls(
            project_name=os.getenv("IOAI_PROJECT_NAME", cls.project_name),
            api_prefix=os.getenv("IOAI_API_PREFIX", cls.api_prefix),
            debug=debug,
            request_id_header=os.getenv(
                "IOAI_REQUEST_ID_HEADER", cls.request_id_header
            ),
            allowed_origins=allowed_origins,
        )
