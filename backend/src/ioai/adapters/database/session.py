from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from .settings import DatabaseSettings


def build_engine(settings: DatabaseSettings | None = None) -> Engine:
    resolved = settings or DatabaseSettings.from_env()
    return create_engine(
        resolved.url,
        echo=resolved.echo,
        pool_pre_ping=resolved.pool_pre_ping,
        poolclass=QueuePool,
    )


def build_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def unit_of_work(
    settings: DatabaseSettings | None = None,
) -> Generator[Session, None, None]:
    engine = build_engine(settings=settings)
    factory = build_session_factory(engine)
    with factory() as session:
        try:
            yield session
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise


def check_connection(url: str) -> bool:
    engine = create_engine(url)
    with engine.connect() as connection:
        return bool(connection.execute(text("SELECT 1")))
