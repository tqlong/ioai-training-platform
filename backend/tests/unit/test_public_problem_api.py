from datetime import UTC, datetime

from fastapi.testclient import TestClient

from ioai.application.problems.public_queries import (
    PublicProblemProjection,
    PublicProblemProjectionPage,
    PublicProblemQuery,
)
from ioai.entrypoints.api.factory import create_app


class FakePublicProblemService:
    def __init__(self) -> None:
        self.query: PublicProblemQuery | None = None

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
