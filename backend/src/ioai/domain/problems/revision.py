from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ioai.domain.vocabulary.availability import Release0AvailabilityPolicy

from .assessment import CodeFunctionResponse, ResponseConfiguration, ScoringScheme
from .content import ProblemContent
from .errors import InvalidProblemContentError
from .identity import ProblemId, RevisionId, StableSlug
from .metadata import CurriculumMetadata
from .workflow import EditorialStatus


class ValidationSection(StrEnum):
    CONTENT = "CONTENT"
    CURRICULUM = "CURRICULUM"
    ASSESSMENT = "ASSESSMENT"
    RESOURCES = "RESOURCES"
    PUBLICATION = "PUBLICATION"


class ValidationSeverity(StrEnum):
    ERROR = "ERROR"
    WARNING = "WARNING"


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    code: str
    section: ValidationSection
    field_path: str
    message: str
    severity: ValidationSeverity


@dataclass(frozen=True, slots=True)
class ValidationReport:
    revision_id: RevisionId
    revision_version: int
    errors: tuple[ValidationIssue, ...]
    warnings: tuple[ValidationIssue, ...]
    publication_eligible: bool


@dataclass(frozen=True, slots=True)
class ProblemRevision:
    problem_id: ProblemId
    revision_id: RevisionId
    version: int
    slug: StableSlug | None
    status: EditorialStatus
    content: ProblemContent | None
    metadata: CurriculumMetadata | None
    response: ResponseConfiguration | None
    scoring: ScoringScheme | None

    def __post_init__(self) -> None:
        if isinstance(self.version, bool) or self.version < 1:
            raise InvalidProblemContentError("revision version must be positive")

    def validate(self, policy: Release0AvailabilityPolicy) -> ValidationReport:
        errors: list[ValidationIssue] = []
        warnings: list[ValidationIssue] = []
        self._validate_required(errors)
        self._validate_content(errors, warnings)
        self._validate_metadata(policy, errors)
        self._validate_assessment(errors)
        return ValidationReport(
            revision_id=self.revision_id,
            revision_version=self.version,
            errors=tuple(errors),
            warnings=tuple(warnings),
            publication_eligible=not errors,
        )

    def _validate_required(self, errors: list[ValidationIssue]) -> None:
        required = (
            (self.content, ValidationSection.CONTENT, "content"),
            (self.metadata, ValidationSection.CURRICULUM, "metadata"),
            (self.response, ValidationSection.ASSESSMENT, "response"),
            (self.scoring, ValidationSection.ASSESSMENT, "scoring"),
            (self.slug, ValidationSection.PUBLICATION, "slug"),
        )
        for value, section, field in required:
            if value is None:
                errors.append(
                    ValidationIssue(
                        code="REQUIRED_FIELD_MISSING",
                        section=section,
                        field_path=field,
                        message=f"Complete {field} before submitting for review.",
                        severity=ValidationSeverity.ERROR,
                    )
                )

    def _validate_content(
        self, errors: list[ValidationIssue], warnings: list[ValidationIssue]
    ) -> None:
        if self.content is None:
            return
        required_english = [
            ("content.title.en", self.content.title.en),
            ("content.summary.en", self.content.summary.en),
        ]
        if not self.content.objectives:
            required_english.append(("content.objectives", ""))
        else:
            required_english.extend(
                (f"content.objectives.{index}.en", objective.content.en)
                for index, objective in enumerate(self.content.objectives)
            )
        for path, value in required_english:
            if not value:
                errors.append(
                    ValidationIssue(
                        code="REQUIRED_CONTENT_MISSING",
                        section=ValidationSection.CONTENT,
                        field_path=path,
                        message="Complete this required English learner content.",
                        severity=ValidationSeverity.ERROR,
                    )
                )
        for index, objective in enumerate(self.content.objectives):
            if not objective.is_observable:
                errors.append(
                    ValidationIssue(
                        code="OBJECTIVE_NOT_OBSERVABLE",
                        section=ValidationSection.CONTENT,
                        field_path=f"content.objectives.{index}.en",
                        message=(
                            "Begin the learning objective with an observable, "
                            "assessable verb."
                        ),
                        severity=ValidationSeverity.ERROR,
                    )
                )
        for path in self.content.pending_translation_paths:
            warnings.append(
                ValidationIssue(
                    code="TRANSLATION_PENDING",
                    section=ValidationSection.CONTENT,
                    field_path=f"content.{path}",
                    message="Translation is explicitly pending.",
                    severity=ValidationSeverity.WARNING,
                )
            )

    def _validate_metadata(
        self,
        policy: Release0AvailabilityPolicy,
        errors: list[ValidationIssue],
    ) -> None:
        if self.metadata is None:
            return
        for blocker in self.metadata.policy_blockers(policy):
            section = (
                ValidationSection.RESOURCES
                if blocker.field.startswith("resources")
                or blocker.field == "modalities"
                else ValidationSection.CURRICULUM
            )
            errors.append(
                ValidationIssue(
                    code=blocker.code,
                    section=section,
                    field_path=f"metadata.{blocker.field}",
                    message=blocker.message,
                    severity=ValidationSeverity.ERROR,
                )
            )

    def _validate_assessment(self, errors: list[ValidationIssue]) -> None:
        if self.response is None or self.scoring is None:
            return
        if self.response.response_type is not self.scoring.response_type:
            errors.append(
                ValidationIssue(
                    code="SCORING_RESPONSE_MISMATCH",
                    section=ValidationSection.ASSESSMENT,
                    field_path="scoring.response_type",
                    message="Scoring must target the configured response type.",
                    severity=ValidationSeverity.ERROR,
                )
            )
        if isinstance(self.response, CodeFunctionResponse):
            self._validate_code_function(errors, self.response)
        if (
            self.metadata is not None
            and self.metadata.task_type.code != self.response.response_type.value
        ):
            errors.append(
                ValidationIssue(
                    code="TASK_RESPONSE_MISMATCH",
                    section=ValidationSection.ASSESSMENT,
                    field_path="response.response_type",
                    message="Response type must match the canonical task type.",
                    severity=ValidationSeverity.ERROR,
                )
            )

    @staticmethod
    def _validate_code_function(
        errors: list[ValidationIssue], response: CodeFunctionResponse
    ) -> None:
        missing: list[tuple[str, str]] = []
        if not response.signature.strip():
            missing.append(("response.signature", "Enter the function signature."))
        if not response.starter_code.strip():
            missing.append(("response.starter_code", "Enter the starter code."))
        tests = response.public_tests + response.hidden_tests
        if not tests:
            missing.append(
                ("response.tests", "Add at least one public or hidden test.")
            )
        for collection, test_cases in (
            ("public_tests", response.public_tests),
            ("hidden_tests", response.hidden_tests),
        ):
            for index, test in enumerate(test_cases):
                if not test.invocation.strip():
                    missing.append(
                        (
                            f"response.{collection}.{index}.invocation",
                            "Enter the test invocation.",
                        )
                    )
                if not test.expected.strip():
                    missing.append(
                        (
                            f"response.{collection}.{index}.expected",
                            "Enter the expected test result.",
                        )
                    )
        errors.extend(
            ValidationIssue(
                code="INCOMPLETE_CODE_CONFIGURATION",
                section=ValidationSection.ASSESSMENT,
                field_path=field_path,
                message=message,
                severity=ValidationSeverity.ERROR,
            )
            for field_path, message in missing
        )
