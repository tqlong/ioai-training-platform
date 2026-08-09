from __future__ import annotations

from ioai.adapters.database.problem_model import (
    EditorialTransitionModel,
    IdempotencyRecordModel,
    PrerequisiteReferenceModel,
    ProblemModel,
    ProblemRevisionModel,
    PublishedSnapshotModel,
    ResponseConfigurationModel,
    RevisionCompetencyModel,
    RevisionTopicModel,
    ScoringComponentModel,
)


def test_problem_tables_have_explicit_revision_owned_boundaries() -> None:
    assert ProblemModel.__tablename__ == "problem"
    assert ProblemRevisionModel.__tablename__ == "problem_revision"
    assert RevisionCompetencyModel.__tablename__ == "revision_competency"
    assert RevisionTopicModel.__tablename__ == "revision_topic"
    assert PrerequisiteReferenceModel.__tablename__ == "prerequisite_reference"
    assert ResponseConfigurationModel.__tablename__ == "response_configuration"
    assert ScoringComponentModel.__tablename__ == "scoring_component"
    assert EditorialTransitionModel.__tablename__ == "editorial_transition"
    assert PublishedSnapshotModel.__tablename__ == "published_snapshot"
    assert IdempotencyRecordModel.__tablename__ == "idempotency_record"


def test_problem_identity_and_revision_version_constraints_are_declared() -> None:
    problem_constraints = {item.name for item in ProblemModel.__table__.constraints}
    revision_constraints = {
        item.name for item in ProblemRevisionModel.__table__.constraints
    }

    assert "uq_problem_slug" in problem_constraints
    assert "uq_problem_revision_problem_number" in revision_constraints
    assert "ck_problem_revision_positive_versions" in revision_constraints


def test_publication_models_declare_uniqueness_and_audit_constraints() -> None:
    transition_constraints = {
        item.name for item in EditorialTransitionModel.__table__.constraints
    }
    snapshot_constraints = {
        item.name for item in PublishedSnapshotModel.__table__.constraints
    }
    idempotency_constraints = {
        item.name for item in IdempotencyRecordModel.__table__.constraints
    }

    assert "uq_editorial_transition_operation_id" in transition_constraints
    assert "uq_published_snapshot_revision_id" in snapshot_constraints
    assert "uq_idempotency_operation_target_key" in idempotency_constraints
    assert ProblemModel.current_published_snapshot_id.property.columns[0].nullable
