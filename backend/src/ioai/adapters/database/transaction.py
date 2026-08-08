from __future__ import annotations

from contextlib import contextmanager
from collections.abc import Generator

from sqlalchemy.orm import Session


@contextmanager
def session_transaction(session: Session) -> Generator[None, None, None]:
    """Guarantee explicit transactional behavior with rollback on exception."""

    try:
        yield
        session.commit()
    except Exception:
        session.rollback()
        raise
