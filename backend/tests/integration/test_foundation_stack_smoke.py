from __future__ import annotations

from pathlib import Path

from tests.fixtures.problem_fixtures import draft_problem, published_problem

from ioai.entrypoints.api.factory import create_app


def test_compose_declares_runtime_and_isolated_test_services() -> None:
    compose_text = Path("docker-compose.yml").read_text()

    assert "postgres:" in compose_text
    assert "api:" in compose_text
    assert "learn:" in compose_text
    assert "studio:" in compose_text
    assert "postgres-test:" in compose_text
    assert "postgres-test-data:" in compose_text
    assert "'127.0.0.1:5432:5432'" in compose_text
    assert "'127.0.0.1:5433:5432'" in compose_text
    assert "'127.0.0.1:8000:8000'" in compose_text
    assert "depends_on:" in compose_text
    assert "postgres" in compose_text.split("api:")[1]


def test_studio_binding_remains_loopback_in_compose() -> None:
    compose_text = Path("docker-compose.yml").read_text()

    assert "'127.0.0.1:3001:3001'" in compose_text
    assert Path("frontend/apps/studio/app/author/problems/page.tsx").is_file()


def test_compose_configures_explicit_local_cors_origins() -> None:
    compose_text = Path("docker-compose.yml").read_text()
    api_service = compose_text.split("\n  api:\n", maxsplit=1)[1].split(
        "\n  learn:\n", maxsplit=1
    )[0]

    assert "IOAI_ALLOWED_ORIGINS:" in api_service
    assert "http://127.0.0.1:3000" in api_service
    assert "http://127.0.0.1:3001" in api_service
    assert "IOAI_ALLOWED_ORIGINS: '*'" not in api_service


def test_compose_dependencies_wait_for_api_readiness() -> None:
    compose_text = Path("docker-compose.yml").read_text()
    api_service = compose_text.split("\n  api:\n", maxsplit=1)[1].split(
        "\n  learn:\n", maxsplit=1
    )[0]
    learn_service = compose_text.split("\n  learn:\n", maxsplit=1)[1].split(
        "\n  studio:\n", maxsplit=1
    )[0]
    studio_service = compose_text.split("\n  studio:\n", maxsplit=1)[1].split(
        "\nvolumes:", maxsplit=1
    )[0]

    assert "/health/ready" in api_service
    assert "condition: service_healthy" in learn_service
    assert "condition: service_healthy" in studio_service
    assert Path("scripts/health_dependency_check.sh").is_file()


def test_compose_runtime_and_migration_commands_use_the_committed_uv_lock() -> None:
    compose_text = Path("docker-compose.yml").read_text()
    migrate_text = Path("scripts/dev_migrate.sh").read_text()

    assert "uv sync --frozen --only-group backend" in compose_text
    assert "uv run --frozen --no-sync uvicorn" in compose_text
    assert 'user: "${LOCAL_UID:-1000}:${LOCAL_GID:-1000}"' in compose_text
    assert "UV_CACHE_DIR: /tmp/ioai-uv-cache" in compose_text
    assert "uv run --with" not in compose_text
    assert "uv sync --frozen --only-group backend" in migrate_text
    assert "uv run --frozen --no-sync alembic" in migrate_text
    assert "uv run --with" not in migrate_text


def test_clean_compose_lifecycle_has_an_isolated_documented_entrypoint() -> None:
    override_text = Path("docker-compose.system.yml").read_text()
    script_text = Path("scripts/compose_lifecycle_check.sh").read_text()
    package_text = Path("package.json").read_text()

    assert "127.0.0.1:58000:8000" in override_text
    assert "127.0.0.1:55432:5432" in override_text
    assert "127.0.0.1:53001:3001" in override_text
    assert "project=${IOAI_SYSTEM_COMPOSE_PROJECT:-ioai-r0-system}" in script_text
    assert '[[ "$project" != ioai-r0-system ]]' in script_text
    assert "git archive" in script_text
    assert "down --volumes --remove-orphans" in script_text
    assert "uv sync --frozen --all-groups" in script_text
    assert "pnpm install --frozen-lockfile" in script_text
    assert '"test:compose-system"' in package_text


def test_restore_and_reset_refuse_unconfirmed_active_targets() -> None:
    script_text = Path("scripts/db_backup_restore.sh").read_text()

    assert "Refusing non-disposable restore target" in script_text
    assert "explicit volume confirmation" in script_text
    assert "ioai_restore_" in script_text
    assert "--confirm-database=" in script_text
    assert "--confirm-volume=" in script_text
    assert "docker compose down -v" not in script_text


def test_backup_restore_has_a_disposable_rehearsal_entrypoint() -> None:
    assert Path("scripts/backup_restore_rehearsal.sh").is_file()
    assert '"test:recovery-system"' in Path("package.json").read_text()


def test_studio_uses_compose_api_service_for_server_side_requests() -> None:
    compose_text = Path("docker-compose.yml").read_text()
    studio_service = compose_text.split("\n  studio:\n", maxsplit=1)[1].split(
        "\nvolumes:", maxsplit=1
    )[0]

    assert "API_INTERNAL_BASE: http://api:8000" in studio_service
    assert Path("frontend/apps/studio/next.config.mjs").is_file()


def test_public_vocabulary_schema_does_not_expose_author_fields() -> None:
    app = create_app()
    openapi = app.openapi()

    public_schema = openapi["components"]["schemas"]["PublicVocabularyRecord"]
    assert "availability" in public_schema["properties"]
    assert "status" not in public_schema["properties"]


def test_public_list_foundation_rejects_draft_fixture() -> None:
    assert published_problem().published is True
    assert draft_problem().published is False
