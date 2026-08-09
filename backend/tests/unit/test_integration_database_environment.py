from __future__ import annotations

import pytest

from backend.tests.integration.database_environment import require_test_database_url


def test_integration_database_requires_explicit_environment(monkeypatch) -> None:
    monkeypatch.delenv("IOAI_TEST_DATABASE_URL", raising=False)

    with pytest.raises(RuntimeError, match="IOAI_TEST_DATABASE_URL is required"):
        require_test_database_url()


@pytest.mark.parametrize(
    "url",
    [
        "postgresql+psycopg://ioai:ioai@127.0.0.1:5432/ioai",
        "postgresql+psycopg://ioai:ioai@postgres:5432/ioai",
        "postgresql+psycopg://ioai:ioai@127.0.0.1:5433/postgres",
    ],
)
def test_integration_database_refuses_development_or_system_databases(
    monkeypatch, url: str
) -> None:
    monkeypatch.setenv("IOAI_TEST_DATABASE_URL", url)

    with pytest.raises(RuntimeError, match="refuses to run destructive tests"):
        require_test_database_url()


def test_integration_database_accepts_dedicated_test_environment(monkeypatch) -> None:
    url = "postgresql+psycopg://ioai_test:ioai_test@127.0.0.1:5433/ioai_test"
    monkeypatch.setenv("IOAI_TEST_DATABASE_URL", url)

    assert require_test_database_url() == url
