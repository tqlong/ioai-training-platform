from __future__ import annotations

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from ioai.application.readiness import DependencyReadiness

BACKEND_ROOT = Path(__file__).resolve().parents[4]


def expected_migration_heads() -> frozenset[str]:
    config = Config(str(BACKEND_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_ROOT / "alembic"))
    return frozenset(ScriptDirectory.from_config(config).get_heads())


def check_database_readiness(
    url: str,
    *,
    connect_timeout_seconds: int = 2,
) -> DependencyReadiness:
    """Check connection and exact Alembic heads without exposing error details."""

    engine = create_engine(
        url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": connect_timeout_seconds},
    )
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            rows = connection.execute(text("SELECT version_num FROM alembic_version"))
            current_heads = frozenset(str(row.version_num) for row in rows)
        schema = (
            "current" if current_heads == expected_migration_heads() else "outdated"
        )
        return DependencyReadiness(database="ready", schema=schema)
    except SQLAlchemyError:
        return DependencyReadiness.unavailable()
    finally:
        engine.dispose()
