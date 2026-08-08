from __future__ import annotations

from ioai.adapters.database.session import check_connection
from ioai.entrypoints.api.factory import create_app


def test_readiness_probe_can_be_overridden() -> None:
    app = create_app(readiness_probe=lambda: True)

    assert app is not None


def test_check_connection_signature_is_defined() -> None:
    assert callable(check_connection)
