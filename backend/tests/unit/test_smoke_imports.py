from __future__ import annotations


def test_ioai_packages_import_without_side_effects() -> None:
    import ioai

    from ioai import adapters, application, domain, entrypoints, workers

    assert hasattr(ioai, "adapters")
    assert hasattr(ioai, "application")
    assert hasattr(ioai, "domain")
    assert hasattr(ioai, "entrypoints")
    assert hasattr(ioai, "workers")
