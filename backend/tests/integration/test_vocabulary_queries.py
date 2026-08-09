from __future__ import annotations

import os

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker

from ioai.adapters.database.vocabulary_model import VocabularyRecordModel
from ioai.adapters.database.vocabulary_repository import (
    SqlAlchemyVocabularyRepository,
    SqlAlchemyVocabularyUnitOfWork,
)
from ioai.adapters.vocabulary.runtime import load_generated_vocabulary
from ioai.application.vocabulary.queries import VocabularyQuery
from ioai.application.vocabulary.synchronize import SynchronizeVocabulary
from ioai.domain.vocabulary.values import VocabularyIdentity, VocabularyType

DATABASE_URL = os.getenv(
    "IOAI_TEST_DATABASE_URL",
    "postgresql+psycopg://ioai:ioai@127.0.0.1:5432/ioai",
)


@pytest.fixture
def populated_session_factory():
    engine = create_engine(DATABASE_URL)
    try:
        with engine.connect():
            pass
    except Exception as error:
        pytest.skip(f"PostgreSQL is unavailable: {error}")
    config = Config("backend/alembic.ini")
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    SynchronizeVocabulary(lambda: SqlAlchemyVocabularyUnitOfWork(factory))(
        load_generated_vocabulary()
    )
    yield factory
    command.downgrade(config, "base")
    engine.dispose()


def test_identity_lookup_is_scoped_by_vocabulary_type(
    populated_session_factory,
) -> None:
    with populated_session_factory() as session:
        repository = SqlAlchemyVocabularyRepository(session)
        competency = repository.get(
            VocabularyIdentity(VocabularyType("COMPETENCY"), "DL_TRANSFORMERS")
        )
        topic = repository.get(
            VocabularyIdentity(VocabularyType("TOPIC"), "DL_TRANSFORMERS")
        )

    assert competency is not None and topic is not None
    assert competency.identity != topic.identity


def test_query_searches_english_vietnamese_and_approved_aliases(
    populated_session_factory,
) -> None:
    with populated_session_factory() as session:
        session.execute(
            update(VocabularyRecordModel)
            .where(
                VocabularyRecordModel.vocabulary_type == "TOPIC",
                VocabularyRecordModel.code == "ML_LOGISTIC_REGRESSION",
            )
            .values(aliases=["logit"])
        )
        session.commit()

    with populated_session_factory() as session:
        repository = SqlAlchemyVocabularyRepository(session)
        english = repository.query(
            VocabularyQuery("PATHWAY_STAGE", search="foundations")
        )
        vietnamese = repository.query(
            VocabularyQuery("PATHWAY_STAGE", search="nền tảng")
        )
        alias = repository.query(VocabularyQuery("TOPIC", search="LOGIT"))

    assert {record.identity.code for record in english} >= {"AI_1_FOUNDATIONS"}
    assert {record.identity.code for record in vietnamese} >= {"AI_1_FOUNDATIONS"}
    assert [record.identity.code for record in alias] == ["ML_LOGISTIC_REGRESSION"]


def test_descendants_require_explicit_option_and_use_stable_hierarchy_order(
    populated_session_factory,
) -> None:
    root = "TOPIC_MATHEMATICS"
    with populated_session_factory() as session:
        repository = SqlAlchemyVocabularyRepository(session)
        exact = repository.query(VocabularyQuery("TOPIC", root_code=root))
        expanded = repository.query(
            VocabularyQuery("TOPIC", root_code=root, include_descendants=True)
        )

    assert [record.identity.code for record in exact] == [root]
    assert expanded[0].identity.code == root
    assert "MATH_LINEAR_ALGEBRA_TOPICS" in {record.identity.code for record in expanded}
    assert "MATH_VECTORS_MATRICES" in {record.identity.code for record in expanded}


def test_breadcrumbs_are_root_to_leaf_and_preserve_composite_identity(
    populated_session_factory,
) -> None:
    identity = VocabularyIdentity(VocabularyType("TOPIC"), "MATH_VECTORS_MATRICES")
    with populated_session_factory() as session:
        repository = SqlAlchemyVocabularyRepository(session)
        breadcrumbs = repository.breadcrumbs(identity)

    assert [record.identity.code for record in breadcrumbs] == [
        "TOPIC_MATHEMATICS",
        "MATH_LINEAR_ALGEBRA_TOPICS",
        "MATH_VECTORS_MATRICES",
    ]
