from __future__ import annotations

from decimal import Decimal

from ioai.domain.problems.assessment import (
    Choice,
    QuizSingleResponse,
    ResponseType,
    ScoringComponent,
    ScoringMethod,
    ScoringScheme,
)
from ioai.domain.problems.content import (
    ContentBlock,
    ContentBlockKind,
    LearningObjective,
    LocalizedText,
    ProblemContent,
    TranslationState,
)
from ioai.domain.problems.identity import ProblemId, RevisionId, StableSlug
from ioai.domain.problems.metadata import (
    CurriculumMetadata,
    ExpectedMinutes,
    NetworkPolicy,
    ResourceLimits,
)
from ioai.domain.problems.revision import (
    ProblemRevision,
    ValidationSection,
    ValidationSeverity,
)
from ioai.domain.problems.workflow import EditorialStatus
from ioai.domain.vocabulary.availability import Release0AvailabilityPolicy
from ioai.domain.vocabulary.values import VocabularyIdentity, VocabularyType


def vid(vocabulary_type: str, code: str) -> VocabularyIdentity:
    return VocabularyIdentity(VocabularyType(vocabulary_type), code)


def content(*, pending_vi: bool = False) -> ProblemContent:
    vi = "" if pending_vi else "Độ đo"
    vi_state = TranslationState.PENDING if pending_vi else TranslationState.COMPLETE
    localized = LocalizedText(en="Metrics", vi=vi, vi_state=vi_state)
    return ProblemContent(
        title=localized,
        summary=localized,
        objectives=(
            LearningObjective(
                LocalizedText(
                    en="Calculate precision from a confusion matrix.",
                    vi="Tính precision từ ma trận nhầm lẫn.",
                )
            ),
        ),
        blocks=(ContentBlock(ContentBlockKind.STATEMENT, localized, order=1),),
    )


def metadata(
    *, stage: str = "AI_1_FOUNDATIONS", compute: str = "NONE"
) -> CurriculumMetadata:
    return CurriculumMetadata(
        stage=vid("PATHWAY_STAGE", stage),
        difficulty=vid("DIFFICULTY", "EASY"),
        primary_competency=vid("COMPETENCY", "EVAL_METRICS"),
        secondary_competencies=(),
        task_type=vid("TASK_TYPE", "QUIZ_SINGLE"),
        topics=(vid("TOPIC", "ML_CONFUSION_MATRIX"),),
        prerequisites=(),
        modalities=(vid("DATA_MODALITY", "NONE"),),
        expected_minutes=ExpectedMinutes(15),
        resources=ResourceLimits(
            compute_tier=vid("COMPUTE_TIER", compute),
            runtime_class=vid("RUNTIME_CLASS", "INSTANT"),
            cpu_cores=0,
            ram_mb=0,
            gpu_count=0,
            gpu_vram_mb=0,
            storage_mb=0,
            runtime_seconds=0,
            network_policy=NetworkPolicy.DENIED,
        ),
    )


def response() -> QuizSingleResponse:
    return QuizSingleResponse(
        choices=(
            Choice("A", LocalizedText(en="One", vi="Một")),
            Choice("B", LocalizedText(en="Two", vi="Hai")),
        ),
        correct_choice_id="A",
    )


def scoring() -> ScoringScheme:
    return ScoringScheme(
        ResponseType.QUIZ_SINGLE,
        (ScoringComponent(ScoringMethod.EXACT_MATCH, Decimal("1.0")),),
    )


def revision(**overrides: object) -> ProblemRevision:
    values: dict[str, object] = {
        "problem_id": ProblemId("problem-01"),
        "revision_id": RevisionId("revision-01"),
        "version": 1,
        "slug": StableSlug("metrics-basics"),
        "status": EditorialStatus.DRAFT,
        "content": content(),
        "metadata": metadata(),
        "response": response(),
        "scoring": scoring(),
    }
    values.update(overrides)
    return ProblemRevision(**values)  # type: ignore[arg-type]


def test_incomplete_draft_returns_field_addressable_blockers() -> None:
    report = revision(
        slug=None, content=None, metadata=None, response=None, scoring=None
    ).validate(Release0AvailabilityPolicy())

    assert report.revision_id == RevisionId("revision-01")
    assert report.revision_version == 1
    assert report.publication_eligible is False
    assert {(issue.section, issue.field_path) for issue in report.errors} == {
        (ValidationSection.CONTENT, "content"),
        (ValidationSection.CURRICULUM, "metadata"),
        (ValidationSection.ASSESSMENT, "response"),
        (ValidationSection.ASSESSMENT, "scoring"),
        (ValidationSection.PUBLICATION, "slug"),
    }
    assert all(issue.severity is ValidationSeverity.ERROR for issue in report.errors)


def test_valid_draft_is_publication_eligible_without_becoming_published() -> None:
    draft = revision()
    report = draft.validate(Release0AvailabilityPolicy())

    assert report.errors == ()
    assert report.publication_eligible is True
    assert draft.status is EditorialStatus.DRAFT


def test_pending_translation_is_a_warning_not_publication_blocker() -> None:
    report = revision(content=content(pending_vi=True)).validate(
        Release0AvailabilityPolicy()
    )

    assert report.publication_eligible is True
    assert {warning.code for warning in report.warnings} == {"TRANSLATION_PENDING"}
    assert report.warnings[0].field_path == "content.title.vi"


def test_policy_and_response_mismatch_are_grouped_actionable_errors() -> None:
    mismatched = ScoringScheme(
        ResponseType.NUMERIC_ANSWER,
        (ScoringComponent(ScoringMethod.EXACT_MATCH, Decimal("1.0")),),
    )
    report = revision(
        metadata=metadata(stage="AI_3_HIGHSCHOOL", compute="GPU_LIGHT"),
        scoring=mismatched,
    ).validate(Release0AvailabilityPolicy())

    assert report.publication_eligible is False
    assert {issue.field_path for issue in report.errors} == {
        "metadata.stage",
        "metadata.resources.compute_tier",
        "scoring.response_type",
    }
    assert all(issue.message for issue in report.errors)


def test_revision_version_must_be_positive() -> None:
    try:
        revision(version=0)
    except ValueError as error:
        assert "version" in str(error)
    else:
        raise AssertionError("zero version should be rejected")
