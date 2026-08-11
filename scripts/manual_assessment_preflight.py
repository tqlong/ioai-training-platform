"""Reject rollout while legacy human rubrics or pending attempts remain."""

from __future__ import annotations

from sqlalchemy import text

from ioai.adapters.database.session import build_engine
from ioai.adapters.database.settings import DatabaseSettings


def main() -> int:
    engine = build_engine(DatabaseSettings.from_env())
    with engine.connect() as connection:
        legacy_snapshots = connection.scalar(
            text(
                "SELECT count(*) FROM published_snapshot ps "
                "JOIN problem p ON p.current_published_snapshot_id = ps.snapshot_id "
                "WHERE ps.slug NOT LIKE 'learner-e2e-%' "
                "AND ps.public_payload::text LIKE '%RUBRIC_HUMAN%' "
                "AND public_payload::text NOT LIKE '%criteria%'"
            )
        )
        legacy_attempts = connection.scalar(
            text(
                "SELECT count(*) FROM learner_attempt la "
                "JOIN published_snapshot ps ON ps.snapshot_id = la.snapshot_id "
                "WHERE ps.slug NOT LIKE 'learner-e2e-%' "
                "AND la.outcome = 'PENDING_ASSESSMENT' "
                "AND la.result::text NOT LIKE '%components%'"
            )
        )
        fixture_history = connection.scalar(
            text(
                "SELECT count(*) FROM published_snapshot ps "
                "WHERE ps.slug LIKE 'learner-e2e-%' "
                "AND ps.public_payload::text LIKE '%RUBRIC_HUMAN%' "
                "AND ps.public_payload::text NOT LIKE '%criteria%'"
            )
        )
    snapshots = int(legacy_snapshots or 0)
    attempts = int(legacy_attempts or 0)
    fixtures = int(fixture_history or 0)
    print(f"legacy human-scored published snapshots: {snapshots}")
    print(f"unresolved legacy human assessments: {attempts}")
    print(f"ignored reserved learner-e2e fixture snapshots: {fixtures}")
    if snapshots or attempts:
        print(
            "Manual-assessment rollout blocked: publish compliant successor "
            "revisions and resolve the legacy attempt policy without "
            "rewriting snapshots."
        )
        return 1
    print("Manual-assessment rollout preflight passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
