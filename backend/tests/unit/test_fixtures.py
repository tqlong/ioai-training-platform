from __future__ import annotations

from tests.fixtures.clock import DeterministicClock
from tests.fixtures.problem_fixtures import draft_problem, published_problem


def test_draft_fixture_and_published_fixture_are_distinct() -> None:
    assert draft_problem().published is False
    assert published_problem().published is True


def test_deterministic_id_and_clock() -> None:
    assert str(draft_problem().id).startswith("problem:draft-sample:")

    clock = DeterministicClock()
    first = clock.now()
    second = clock.now()

    assert first != second
