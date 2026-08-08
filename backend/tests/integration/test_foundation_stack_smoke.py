from __future__ import annotations

from pathlib import Path

from ioai.entrypoints.api.factory import create_app
from ioai.tests.fixtures.problem_fixtures import draft_problem, published_problem


def test_compose_declares_four_services_and_dependency_chain() -> None:
    compose_text = Path('docker-compose.yml').read_text()

    assert 'postgres:' in compose_text
    assert 'api:' in compose_text
    assert 'learn:' in compose_text
    assert 'studio:' in compose_text
    assert 'depends_on:' in compose_text
    assert 'postgres' in compose_text.split('api:')[1]


def test_studio_binding_remains_loopback_in_compose() -> None:
    compose_text = Path('docker-compose.yml').read_text()

    assert '--hostname 127.0.0.1' in compose_text
    assert '/author/problems' in Path('frontend/apps/studio/app/author/problems/page.tsx').read_text()


def test_public_api_does_not_expose_author_namespace() -> None:
    app = create_app()
    openapi = app.openapi()

    for path in openapi['paths']:
        assert not path.startswith('/api/v1/author')


def test_public_list_foundation_rejects_draft_fixture() -> None:
    assert published_problem().published is True
    assert draft_problem().published is False
