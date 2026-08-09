from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DatabaseSettings:
    url: str = "postgresql+psycopg://ioai:ioai@127.0.0.1:5432/ioai"
    pool_pre_ping: bool = True
    echo: bool = False

    @classmethod
    def from_env(cls) -> "DatabaseSettings":
        return cls(
            url=os.getenv("IOAI_DATABASE_URL", cls.url),
            pool_pre_ping=os.getenv(
                "IOAI_DATABASE_POOL_PRE_PING", str(cls.pool_pre_ping)
            ).lower()
            in {"1", "true", "yes"},
            echo=os.getenv("IOAI_DATABASE_ECHO", str(cls.echo)).lower()
            in {"1", "true", "yes"},
        )
