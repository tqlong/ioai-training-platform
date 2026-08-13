from __future__ import annotations

from alembic import command

from ioai.adapters.database.readiness import check_database_readiness
from ioai.adapters.database.session import check_connection
from ioai.entrypoints.api.factory import create_app

from .database_environment import require_test_database_url
from .test_vocabulary_migration import alembic_config


def test_readiness_probe_can_be_overridden() -> None:
    app = create_app(readiness_probe=lambda: True)

    assert app is not None


def test_check_connection_signature_is_defined() -> None:
    assert callable(check_connection)


def test_readiness_requires_connection_and_current_alembic_head() -> None:
    database_url = require_test_database_url()
    config = alembic_config()
    command.downgrade(config, "base")
    try:
        missing_schema = check_database_readiness(database_url)
        assert missing_schema.is_ready is False
        assert missing_schema.database == "ready"
        assert missing_schema.schema == "outdated"

        command.upgrade(config, "head")
        current = check_database_readiness(database_url)
        assert current.is_ready is True
        assert current.database == "ready"
        assert current.schema == "current"

        command.downgrade(config, "-1")
        outdated = check_database_readiness(database_url)
        assert outdated.is_ready is False
        assert outdated.database == "ready"
        assert outdated.schema == "outdated"
    finally:
        command.upgrade(config, "head")


def test_readiness_safely_reports_unavailable_database() -> None:
    result = check_database_readiness(
        "postgresql+psycopg://ioai:ioai@127.0.0.1:1/ioai",
        connect_timeout_seconds=1,
    )

    assert result.is_ready is False
    assert result.database == "unavailable"
    assert result.schema == "unknown"
