from datetime import UTC, datetime

from fastapi.testclient import TestClient

from ioai.application.problems.assessment import SubmissionCommand
from ioai.application.problems.errors import PublishedProblemNotFoundError
from ioai.application.problems.feedback import SubmitFeedbackCommand
from ioai.application.problems.learner_records import (
    FeedbackCategory,
    LearnerAttempt,
    LearnerOutcome,
    ProblemFeedback,
)
from ioai.application.problems.public_queries import (
    PublicProblemProjection,
    PublicProblemProjectionPage,
    PublicProblemQuery,
)
from ioai.application.problems.recommendations import (
    LearningEvidenceContext,
    ProblemRecommendation,
    RecommendationContext,
)
from ioai.entrypoints.api.factory import create_app


class FakePublicProblemService:
    def __init__(self) -> None:
        self.query: PublicProblemQuery | None = None
        self.recommendation_context: RecommendationContext | None = None
        self.has_recommendation = True
        self.has_detail = True
        self.submission: SubmissionCommand | None = None
        self.feedback_command: SubmitFeedbackCommand | None = None

    def list(self, query: PublicProblemQuery) -> PublicProblemProjectionPage:
        self.query = query
        return PublicProblemProjectionPage(
            items=(
                PublicProblemProjection(
                    slug="metrics-basics",
                    content={
                        "title": {"en": "Metrics", "vi": "Độ đo"},
                        "objectives": [{"en": "Calculate metrics", "vi": "Tính độ đo"}],
                    },
                    metadata={
                        "stage": ["PATHWAY_STAGE", "AI_1_FOUNDATIONS"],
                        "difficulty": ["DIFFICULTY", "EASY"],
                        "primary_competency": ["COMPETENCY", "EVAL_METRICS"],
                        "topics": [
                            ["TOPIC", "CONFUSION_MATRIX"],
                            ["TOPIC", "ACCURACY"],
                            ["TOPIC", "PRECISION"],
                        ],
                        "task_type": ["TASK_TYPE", "QUIZ_SINGLE"],
                        "expected_minutes": 10,
                        "resources": {"compute_tier": ["COMPUTE_TIER", "NONE"]},
                    },
                    response_schema={},
                    published_at=datetime(2026, 8, 9, tzinfo=UTC),
                ),
            ),
            total=3,
            page=query.page,
            page_size=query.page_size,
        )

    def recommend(self, context: RecommendationContext) -> ProblemRecommendation | None:
        self.recommendation_context = context
        if not self.has_recommendation:
            return None
        return ProblemRecommendation(
            slug="next-problem",
            title={"en": "Next problem", "vi": "Bài tiếp theo"},
            stage_code=context.stage,
            difficulty_code="EASY",
            expected_minutes=15,
            compute_tier_code="NONE",
            label=(
                "Recommended next" if context.completed_slugs else "Recommended start"
            ),
            reason=(
                "Matches your stage and editorial path with available prerequisites."
            ),
        )

    def get(self, slug: str) -> PublicProblemProjection:
        if not self.has_detail:
            raise PublishedProblemNotFoundError("private or missing")
        item = self.list(PublicProblemQuery()).items[0]
        return PublicProblemProjection(
            slug=slug,
            content={
                **item.content,
                "summary": {"en": "Read a matrix.", "vi": "Đọc ma trận."},
                "blocks": [
                    {
                        "kind": "STATEMENT",
                        "content": {"en": "Find precision.", "vi": "Tìm precision."},
                        "order": 1,
                        "reveal_order": None,
                    },
                    {
                        "kind": "EXAMPLE",
                        "content": {"en": "", "vi": ""},
                        "order": 2,
                        "reveal_order": None,
                    },
                ],
            },
            metadata={
                **item.metadata,
                "secondary_competencies": [],
                "prerequisites": [
                    {
                        "relationship": "RECOMMENDED",
                        "target_type": "TOPIC",
                        "target_identity": ["TOPIC", "MATH_RATIOS"],
                        "target_id": None,
                        "minimum_evidence": "INTRODUCED",
                    }
                ],
                "modalities": [["DATA_MODALITY", "NONE"]],
                "resources": {
                    "compute_tier": ["COMPUTE_TIER", "NONE"],
                    "runtime_class": ["RUNTIME_CLASS", "NONE"],
                    "cpu_cores": 0,
                    "ram_mb": 0,
                    "gpu_count": 0,
                    "gpu_vram_mb": 0,
                    "storage_mb": 0,
                    "runtime_seconds": 0,
                    "network_policy": "DENIED",
                },
            },
            response_schema={
                "type": "QUIZ_SINGLE",
                "choices": [{"id": "a", "content": {"en": "0.5", "vi": "0,5"}}],
            },
            published_at=item.published_at,
        )

    def assess(self, command: SubmissionCommand) -> LearnerAttempt:
        self.submission = command
        return LearnerAttempt(
            attempt_id="attempt-public",
            snapshot_id="snapshot-private",
            submission_key=command.submission_key,
            request_digest="a" * 64,
            outcome=LearnerOutcome.ACCEPTED_RESULT,
            result={
                "score": "1.0",
                "passed": True,
                "components": [{"method": "EXACT_MATCH", "score": "1.0"}],
            },
            submitted_at=datetime(2026, 8, 9, tzinfo=UTC),
        )

    def feedback(self, command: SubmitFeedbackCommand) -> ProblemFeedback:
        self.feedback_command = command
        return ProblemFeedback(
            "feedback-public",
            "snapshot-private",
            command.feedback_key,
            "b" * 64,
            command.category,
            command.message,
            datetime(2026, 8, 9, tzinfo=UTC),
        )


def test_public_problem_list_returns_typed_safe_page() -> None:
    service = FakePublicProblemService()
    client = TestClient(create_app(public_problem_service=service))

    response = client.get(
        "/api/v1/problems",
        params={
            "stage": "AI_1_FOUNDATIONS",
            "topic": "EVAL_CONFUSION_MATRIX",
            "include_subtopics": "true",
            "sort": "TITLE",
            "page": 2,
            "page_size": 5,
        },
        headers={"X-Request-ID": "request-list-1"},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "request-list-1"
    assert response.json() == {
        "items": [
            {
                "slug": "metrics-basics",
                "public_short_id": "metrics-basics",
                "title": {"en": "Metrics", "vi": "Độ đo"},
                "objective": {"en": "Calculate metrics", "vi": "Tính độ đo"},
                "stage_code": "AI_1_FOUNDATIONS",
                "difficulty_code": "EASY",
                "primary_competency_code": "EVAL_METRICS",
                "topic_codes": ["CONFUSION_MATRIX", "ACCURACY"],
                "remaining_topic_count": 1,
                "task_type_code": "QUIZ_SINGLE",
                "expected_minutes": 10,
                "compute_tier_code": "NONE",
                "published_at": "2026-08-09T00:00:00Z",
            }
        ],
        "total": 3,
        "page": 2,
        "page_size": 5,
        "active_filters": {
            "stage": "AI_1_FOUNDATIONS",
            "topic": "EVAL_CONFUSION_MATRIX",
            "include_subtopics": True,
            "sort": "TITLE",
        },
    }
    assert service.query is not None and service.query.page == 2


def test_public_problem_list_falls_back_to_english_for_pending_vietnamese_text() -> (
    None
):
    service = FakePublicProblemService()
    original_list = service.list

    def list_with_pending_translation(
        query: PublicProblemQuery,
    ) -> PublicProblemProjectionPage:
        page = original_list(query)
        item = page.items[0]
        return PublicProblemProjectionPage(
            items=(
                PublicProblemProjection(
                    slug=item.slug,
                    content={
                        **item.content,
                        "title": {"en": "Metrics", "vi": ""},
                        "objectives": [{"en": "Calculate metrics", "vi": ""}],
                    },
                    metadata=item.metadata,
                    response_schema=item.response_schema,
                    published_at=item.published_at,
                ),
            ),
            total=page.total,
            page=page.page,
            page_size=page.page_size,
        )

    service.list = list_with_pending_translation  # type: ignore[method-assign]
    client = TestClient(create_app(public_problem_service=service))

    response = client.get("/api/v1/problems")

    assert response.status_code == 200
    assert response.json()["items"][0]["title"] == {
        "en": "Metrics",
        "vi": "Metrics",
    }
    assert response.json()["items"][0]["objective"] == {
        "en": "Calculate metrics",
        "vi": "Calculate metrics",
    }


def test_public_problem_detail_returns_explicit_safe_projection() -> None:
    client = TestClient(create_app(public_problem_service=FakePublicProblemService()))

    response = client.get("/api/v1/problems/metrics-basics")

    assert response.status_code == 200
    body = response.json()
    assert body["slug"] == "metrics-basics"
    assert body["permanent_url"] == "/problems/metrics-basics"
    assert body["title"] == {"en": "Metrics", "vi": "Độ đo"}
    assert body["objective"]["en"] == "Calculate metrics"
    assert body["blocks"][0]["kind"] == "STATEMENT"
    assert len(body["blocks"]) == 1
    assert body["prerequisites"] == [
        {
            "relationship": "RECOMMENDED",
            "target_type": "TOPIC",
            "target_code": "MATH_RATIOS",
            "target_id": None,
            "minimum_evidence": "INTRODUCED",
        }
    ]
    assert body["response_schema"]["type"] == "QUIZ_SINGLE"
    assert body["resources"]["network_policy"] == "DENIED"
    assert body["feedback_available"] is True
    assert body["recommendation_url"].endswith("/recommendation")
    serialized = response.text
    for forbidden in (
        "revision_id",
        "editorial_status",
        "correct_choice_id",
        "hidden_tests",
        "scoring",
        "object_key",
        "internal_notes",
    ):
        assert forbidden not in serialized


def test_public_problem_detail_uses_same_safe_not_found_for_non_public_content() -> (
    None
):
    service = FakePublicProblemService()
    service.has_detail = False
    client = TestClient(create_app(public_problem_service=service))

    response = client.get("/api/v1/problems/draft-or-missing")

    assert response.status_code == 404
    assert response.json()["detail"] == {
        "code": "PUBLIC_NOT_FOUND",
        "message": "Problem not found.",
    }


def test_public_submission_returns_safe_assessment_result_and_request_id() -> None:
    service = FakePublicProblemService()
    client = TestClient(create_app(public_problem_service=service))

    response = client.post(
        "/api/v1/problems/metrics-basics/submissions",
        json={
            "submission_key": "client-key-1",
            "receipt": "private-receipt-1234567890",
            "response": {"type": "QUIZ_SINGLE", "choice_id": "a"},
        },
        headers={"X-Request-ID": "submission-request-1"},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "submission-request-1"
    assert response.json() == {
        "attempt_id": "attempt-public",
        "receipt": "private-receipt-1234567890",
        "result_url": "/submissions/attempt-public",
        "submitted_at": "2026-08-09T00:00:00Z",
        "outcome": "ACCEPTED_RESULT",
        "score": "1.0",
        "passed": True,
        "components": [{"method": "EXACT_MATCH", "score": "1.0"}],
        "message": "Your answer was assessed.",
    }
    assert service.submission == SubmissionCommand(
        "metrics-basics",
        "client-key-1",
        {"type": "QUIZ_SINGLE", "choice_id": "a"},
        "private-receipt-1234567890",
    )


def test_pending_mixed_submission_returns_completed_automated_components() -> None:
    class MixedService(FakePublicProblemService):
        def assess(self, command: SubmissionCommand) -> LearnerAttempt:
            return LearnerAttempt(
                attempt_id="attempt-mixed",
                snapshot_id="snapshot-private",
                submission_key=command.submission_key,
                request_digest="a" * 64,
                outcome=LearnerOutcome.PENDING_ASSESSMENT,
                result={
                    "status": "PENDING_ASSESSMENT",
                    "automated_score": "0.4",
                    "components": [
                        {"method": "EXACT_MATCH", "score": "1.0", "weight": "0.4"}
                    ],
                },
                submitted_at=datetime(2026, 8, 9, tzinfo=UTC),
            )

    client = TestClient(create_app(public_problem_service=MixedService()))

    response = client.post(
        "/api/v1/problems/metrics-basics/submissions",
        json={
            "submission_key": "mixed-client-key",
            "receipt": "private-receipt-mixed-1234",
            "response": {"type": "QUIZ_SINGLE", "choice_id": "a"},
        },
    )

    assert response.status_code == 200
    assert response.json()["components"] == [
        {"method": "EXACT_MATCH", "score": "1.0", "weight": "0.4"}
    ]


def test_public_submission_rejects_malformed_discriminated_response() -> None:
    client = TestClient(create_app(public_problem_service=FakePublicProblemService()))
    response = client.post(
        "/api/v1/problems/metrics-basics/submissions",
        json={
            "submission_key": "client-key-1",
            "response": {"type": "QUIZ_SINGLE"},
        },
    )
    assert response.status_code == 422


def test_public_feedback_accepts_canonical_bounded_report_with_safe_receipt() -> None:
    service = FakePublicProblemService()
    client = TestClient(create_app(public_problem_service=service))
    response = client.post(
        "/api/v1/problems/metrics-basics/feedback",
        json={"feedback_key": "feedback-key", "category": "TYPO", "message": "A typo."},
    )
    assert response.status_code == 201
    assert response.json() == {
        "receipt_id": "feedback-public",
        "message": "Thank you. Your feedback was recorded.",
    }
    assert service.feedback_command is not None
    assert service.feedback_command.category is FeedbackCategory.TYPO
    assert len(service.feedback_command.abuse_token) == 64


def test_public_problem_list_rejects_unknown_and_unavailable_canonical_values() -> None:
    client = TestClient(create_app(public_problem_service=FakePublicProblemService()))

    unknown = client.get("/api/v1/problems?stage=NOT_A_STAGE")
    unavailable = client.get("/api/v1/problems?stage=AI_3_HIGHSCHOOL")
    leaked = client.get("/api/v1/problems?editorial_status=APPROVED")

    assert unknown.status_code == 422
    assert unknown.json()["detail"]["code"] == "UNKNOWN_VOCABULARY_VALUE"
    assert unavailable.status_code == 422
    assert unavailable.json()["detail"]["code"] == "POLICY_DISALLOWED"
    assert leaked.status_code == 422


def test_public_recommendation_accepts_bounded_local_context() -> None:
    service = FakePublicProblemService()
    client = TestClient(create_app(public_problem_service=service))

    response = client.get(
        "/api/v1/problems/current/recommendation",
        params=[
            ("stage", "AI_1_FOUNDATIONS"),
            ("completed", "current"),
            ("evidence", "TOPIC:EVAL_CONFUSION_MATRIX:PRACTICED"),
        ],
    )

    assert response.status_code == 200
    assert response.json() == {
        "slug": "next-problem",
        "permanent_url": "/problems/next-problem",
        "title": {"en": "Next problem", "vi": "Bài tiếp theo"},
        "stage_code": "AI_1_FOUNDATIONS",
        "difficulty_code": "EASY",
        "expected_minutes": 15,
        "compute_tier_code": "NONE",
        "label": "Recommended next",
        "reason": "Matches your stage and editorial path with available prerequisites.",
    }
    assert service.recommendation_context == RecommendationContext(
        stage="AI_1_FOUNDATIONS",
        current_slug="current",
        completed_slugs=("current",),
        evidence=(
            LearningEvidenceContext(
                vocabulary_type="TOPIC",
                code="EVAL_CONFUSION_MATRIX",
                level="PRACTICED",
            ),
        ),
    )


def test_public_recommendation_returns_no_content_when_no_candidate_exists() -> None:
    service = FakePublicProblemService()
    service.has_recommendation = False
    client = TestClient(create_app(public_problem_service=service))

    response = client.get(
        "/api/v1/problems/current/recommendation?stage=AI_1_FOUNDATIONS"
    )

    assert response.status_code == 204
