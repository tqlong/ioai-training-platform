from __future__ import annotations

import os

from sqlalchemy.engine import make_url


def require_test_database_url() -> str:
    raw_url = os.getenv("IOAI_TEST_DATABASE_URL")
    if not raw_url:
        raise RuntimeError(
            "IOAI_TEST_DATABASE_URL is required for PostgreSQL integration tests. "
            "Run scripts/backend_test.sh to use the isolated test environment."
        )
    database = make_url(raw_url).database or ""
    if not database.endswith("_test"):
        raise RuntimeError(
            "Integration safety refuses to run destructive tests against "
            f"database {database!r}; use a dedicated database ending in '_test'."
        )
    return raw_url
