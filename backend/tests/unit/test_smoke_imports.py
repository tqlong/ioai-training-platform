from __future__ import annotations


def test_ioai_packages_import_without_side_effects() -> None:
    import ioai
    from ioai import adapters, application, domain, entrypoints, workers

    assert ioai.__name__ == "ioai"
    assert adapters.__name__ == "ioai.adapters"
    assert application.__name__ == "ioai.application"
    assert domain.__name__ == "ioai.domain"
    assert entrypoints.__name__ == "ioai.entrypoints"
    assert workers.__name__ == "ioai.workers"
