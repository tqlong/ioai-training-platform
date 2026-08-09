from __future__ import annotations

import json

from ioai.adapters.database.session import build_engine, build_session_factory
from ioai.adapters.database.settings import DatabaseSettings
from ioai.adapters.database.vocabulary_repository import (
    SqlAlchemyVocabularyUnitOfWork,
)
from ioai.adapters.vocabulary.runtime import load_generated_vocabulary
from ioai.application.vocabulary.synchronize import SynchronizeVocabulary


def main() -> None:
    engine = build_engine(DatabaseSettings.from_env())
    session_factory = build_session_factory(engine)
    synchronize = SynchronizeVocabulary(
        lambda: SqlAlchemyVocabularyUnitOfWork(session_factory)
    )
    try:
        result = synchronize(load_generated_vocabulary())
    finally:
        engine.dispose()
    print(
        json.dumps(
            {
                "added": result.added,
                "updated": result.updated,
                "unchanged": result.unchanged,
                "rejected": result.rejected,
                "policy_disabled": result.policy_disabled,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
