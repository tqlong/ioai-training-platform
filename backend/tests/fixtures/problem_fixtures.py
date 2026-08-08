from __future__ import annotations

from dataclasses import dataclass

from .ids import deterministic_id


@dataclass(frozen=True)
class ProblemFixture:
    id: str
    slug: str
    title: str
    published: bool


def published_problem() -> ProblemFixture:
    return ProblemFixture(
        id=deterministic_id("problem", "published-basics"),
        slug="published-basics",
        title="Published Problem",
        published=True,
    )


def draft_problem() -> ProblemFixture:
    return ProblemFixture(
        id=deterministic_id("problem", "draft-sample"),
        slug="draft-sample",
        title="Draft Problem",
        published=False,
    )
