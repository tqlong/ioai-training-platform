from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class ApiSettings:
    """Runtime settings for HTTP layer wiring."""

    project_name: str = "IOAI Training Platform"
    api_prefix: str = "/api/v1"
    debug: bool = False
    request_id_header: str = "x-request-id"

    @classmethod
    def from_env(cls) -> "ApiSettings":
        debug = os.getenv("IOAI_DEBUG", "false").lower() in {"1", "true", "yes"}
        return cls(
            project_name=os.getenv("IOAI_PROJECT_NAME", cls.project_name),
            api_prefix=os.getenv("IOAI_API_PREFIX", cls.api_prefix),
            debug=debug,
            request_id_header=os.getenv("IOAI_REQUEST_ID_HEADER", cls.request_id_header),
        )
