from __future__ import annotations

import re
from collections.abc import Callable
from contextlib import contextmanager
from datetime import UTC, datetime
from time import monotonic
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from ...adapters.database.problem_repository import (
    SqlAlchemyAssessmentUnitOfWork,
    SqlAlchemyDraftUnitOfWork,
    SqlAlchemyManualAssessmentUnitOfWork,
    SqlAlchemyPublishedProblemReader,
)
from ...adapters.database.proposal_repository import SqlAlchemyProposalUnitOfWork
from ...adapters.database.readiness import check_database_readiness
from ...adapters.database.session import (
    build_engine,
    build_session_factory,
)
from ...adapters.database.settings import DatabaseSettings
from ...adapters.database.vocabulary_repository import SqlAlchemyVocabularyRepository
from ...adapters.observability.json_event_sink import JsonEventSink
from ...adapters.vocabulary.runtime import load_generated_vocabulary
from ...application.observability import (
    EventSink,
    ObservabilityEvent,
    bind_request_id,
    observe_operation,
)
from ...application.problems.assessment import AssessSubmission, SubmissionCommand
from ...application.problems.authoring import (
    CreateDraft,
    GetDraft,
    GetRevisionDraft,
    ListDrafts,
    PreviewDraft,
    SaveDraft,
    ValidateDraft,
)
from ...application.problems.editorial import (
    ApproveRevision,
    ListEditorialHistory,
    RequestChanges,
    StartSuccessorDraft,
    SubmitForReview,
)
from ...application.problems.feedback import (
    FixedWindowFeedbackThrottle,
    RecordProblemFeedback,
    SubmitFeedbackCommand,
)
from ...application.problems.manual_assessment import (
    AssessmentSelection,
    GetLearnerSubmission,
    GetManualAssessment,
    ListManualAssessments,
    ResolveManualAssessment,
)
from ...application.problems.payload import decode_revision_payload
from ...application.problems.public_queries import (
    GetPublishedProblem,
    ListPublishedProblems,
    PublicProblemQuery,
)
from ...application.problems.publication import ArchiveProblem, PublishRevision
from ...application.problems.recommendations import (
    RecommendationContext,
    RecommendNextProblem,
)
from ...application.readiness import DependencyReadiness
from ...application.vocabulary.proposals import RecordVocabularyProposal
from ...domain.problems.identity import ProblemId, RevisionId, StableSlug
from ...domain.problems.revision import ProblemRevision
from ...domain.problems.workflow import ActorContext, EditorialStatus
from ...domain.vocabulary.availability import Release0AvailabilityPolicy
from .contracts.problems import (
    ArchiveProblemRequest,
    AssessmentDecisionRequest,
    EditorialCommandRequest,
    PreviewDraftRequest,
    PublishRevisionRequest,
    SaveDraftRequest,
    StartRevisionRequest,
)
from .errors import install_error_handlers
from .routes.health import health_router
from .routes.manual_assessments import (
    ManualAssessmentService,
    author_assessment_router,
    public_submission_router,
)
from .routes.problems import (
    AuthorProblemService,
    author_problem_router,
    author_revision_router,
)
from .routes.proposals import ProposalService, proposal_router
from .routes.public_problems import PublicProblemService, public_problem_router
from .routes.vocabulary import VocabularyReaderFactory, vocabulary_router
from .settings import ApiSettings

ReadinessProbe = Callable[[], bool | DependencyReadiness]


def create_app(
    *,
    settings: ApiSettings | None = None,
    readiness_probe: ReadinessProbe | None = None,
    vocabulary_reader_factory: VocabularyReaderFactory | None = None,
    proposal_service: ProposalService | None = None,
    author_problem_service: AuthorProblemService | None = None,
    public_problem_service: PublicProblemService | None = None,
    manual_assessment_service: ManualAssessmentService | None = None,
    event_sink: EventSink | None = None,
) -> FastAPI:
    resolved_settings = settings or ApiSettings.from_env()
    resolved_probe = readiness_probe
    resolved_reader_factory = vocabulary_reader_factory
    resolved_proposal_service = proposal_service
    resolved_author_problem_service = author_problem_service
    resolved_public_problem_service = public_problem_service
    resolved_manual_assessment_service = manual_assessment_service
    resolved_event_sink = event_sink or JsonEventSink()
    db_settings = DatabaseSettings.from_env()
    engine = build_engine(db_settings)
    session_factory = build_session_factory(engine)
    if readiness_probe is None:

        def default_probe() -> DependencyReadiness:
            return check_database_readiness(db_settings.url)

        resolved_probe = default_probe

    if resolved_reader_factory is None:

        @contextmanager
        def default_reader():
            with session_factory() as session:
                yield SqlAlchemyVocabularyRepository(session)

        resolved_reader_factory = default_reader

    if resolved_proposal_service is None:
        resolved_proposal_service = RecordVocabularyProposal(
            unit_of_work_factory=lambda: SqlAlchemyProposalUnitOfWork(session_factory),
            id_generator=lambda: str(uuid4()),
            clock=lambda: datetime.now(UTC),
        )

    if resolved_author_problem_service is None:

        def draft_uow() -> SqlAlchemyDraftUnitOfWork:
            return SqlAlchemyDraftUnitOfWork(session_factory)

        resolved_author_problem_service = _DefaultAuthorProblemService(
            create=CreateDraft(
                unit_of_work_factory=draft_uow,
                id_generator=lambda: str(uuid4()),
                clock=lambda: datetime.now(UTC),
            ),
            list_drafts=ListDrafts(draft_uow),
            get=GetDraft(draft_uow),
            get_revision=GetRevisionDraft(draft_uow),
            save=SaveDraft(draft_uow, lambda: datetime.now(UTC)),
            validate=ValidateDraft(draft_uow, Release0AvailabilityPolicy()),
            preview=PreviewDraft(draft_uow, Release0AvailabilityPolicy()),
            submit=SubmitForReview(
                unit_of_work_factory=draft_uow,
                policy=Release0AvailabilityPolicy(),
                id_generator=lambda: str(uuid4()),
                clock=lambda: datetime.now(UTC),
            ),
            request_changes=RequestChanges(
                unit_of_work_factory=draft_uow,
                policy=Release0AvailabilityPolicy(),
                id_generator=lambda: str(uuid4()),
                clock=lambda: datetime.now(UTC),
            ),
            approve=ApproveRevision(
                unit_of_work_factory=draft_uow,
                policy=Release0AvailabilityPolicy(),
                id_generator=lambda: str(uuid4()),
                clock=lambda: datetime.now(UTC),
            ),
            history=ListEditorialHistory(draft_uow),
            publish=PublishRevision(
                unit_of_work_factory=draft_uow,
                policy=Release0AvailabilityPolicy(),
                id_generator=lambda: str(uuid4()),
                clock=lambda: datetime.now(UTC),
            ),
            start_revision=StartSuccessorDraft(
                unit_of_work_factory=draft_uow,
                id_generator=lambda: str(uuid4()),
                clock=lambda: datetime.now(UTC),
            ),
            archive=ArchiveProblem(
                unit_of_work_factory=draft_uow,
                id_generator=lambda: str(uuid4()),
                clock=lambda: datetime.now(UTC),
            ),
            event_sink=resolved_event_sink,
            environment=resolved_settings.environment,
        )

    if resolved_public_problem_service is None:
        resolved_public_problem_service = _DefaultPublicProblemService(
            session_factory,
            event_sink=resolved_event_sink,
            environment=resolved_settings.environment,
        )
    if resolved_manual_assessment_service is None:
        resolved_manual_assessment_service = _DefaultManualAssessmentService(
            session_factory,
            event_sink=resolved_event_sink,
            environment=resolved_settings.environment,
        )

    app = FastAPI(
        title=resolved_settings.project_name,
        debug=resolved_settings.debug,
        openapi_url=f"{resolved_settings.api_prefix}/openapi.json",
        redoc_url=None,
        docs_url="/api/docs",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(resolved_settings.allowed_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "OPTIONS"],
        allow_headers=[
            "content-type",
            resolved_settings.request_id_header,
            "x-submission-receipt",
        ],
        expose_headers=[resolved_settings.request_id_header],
    )

    app.include_router(health_router(is_ready=resolved_probe), prefix="")
    app.include_router(
        vocabulary_router(resolved_reader_factory), prefix=resolved_settings.api_prefix
    )
    app.include_router(
        proposal_router(resolved_proposal_service), prefix=resolved_settings.api_prefix
    )
    app.include_router(
        author_problem_router(resolved_author_problem_service),
        prefix=resolved_settings.api_prefix,
    )
    app.include_router(
        author_revision_router(resolved_author_problem_service),
        prefix=resolved_settings.api_prefix,
    )
    app.include_router(
        public_problem_router(
            resolved_public_problem_service, load_generated_vocabulary()
        ),
        prefix=resolved_settings.api_prefix,
    )
    app.include_router(
        public_submission_router(resolved_manual_assessment_service),
        prefix=resolved_settings.api_prefix,
    )
    app.include_router(
        author_assessment_router(resolved_manual_assessment_service),
        prefix=resolved_settings.api_prefix,
    )
    install_error_handlers(app, request_id_header=resolved_settings.request_id_header)
    app.add_middleware(
        _RequestIdMiddleware,
        header_name=resolved_settings.request_id_header,
        event_sink=resolved_event_sink,
        environment=resolved_settings.environment,
    )

    @app.get("/health", include_in_schema=False)
    def heartbeat() -> dict[str, str]:
        return {"status": "ok"}

    return app


class _DefaultPublicProblemService:
    def __init__(
        self,
        session_factory,
        *,
        event_sink: EventSink,
        environment: str,
    ) -> None:
        self._session_factory = session_factory
        self._feedback_throttle = FixedWindowFeedbackThrottle(lambda: datetime.now(UTC))
        self._event_sink = event_sink
        self._environment = environment

    def list(self, query: PublicProblemQuery):
        with self._session_factory() as session:
            use_case = ListPublishedProblems(SqlAlchemyPublishedProblemReader(session))
            return use_case(query)

    def get(self, slug: str):
        with self._session_factory() as session:
            return GetPublishedProblem(SqlAlchemyPublishedProblemReader(session))(slug)

    def assess(self, command: SubmissionCommand):
        return observe_operation(
            sink=self._event_sink,
            event_name="learner.submission",
            environment=self._environment,
            raw_operation_id=command.submission_key,
            reference=command.slug,
            action=lambda: AssessSubmission(
                lambda: SqlAlchemyAssessmentUnitOfWork(self._session_factory),
                lambda: str(uuid4()),
                lambda: datetime.now(UTC),
            )(command),
            clock=monotonic,
        )

    def feedback(self, command: SubmitFeedbackCommand):
        return observe_operation(
            sink=self._event_sink,
            event_name="learner.feedback",
            environment=self._environment,
            raw_operation_id=command.feedback_key,
            reference=command.slug,
            action=lambda: RecordProblemFeedback(
                lambda: SqlAlchemyAssessmentUnitOfWork(self._session_factory),
                lambda: str(uuid4()),
                lambda: datetime.now(UTC),
                self._feedback_throttle,
            )(command),
            clock=monotonic,
        )

    def recommend(self, context: RecommendationContext):
        with self._session_factory() as session:
            reader = SqlAlchemyPublishedProblemReader(session)
            GetPublishedProblem(reader)(context.current_slug or "")
            return RecommendNextProblem(reader)(context)


class _DefaultManualAssessmentService:
    def __init__(
        self,
        session_factory,
        *,
        event_sink: EventSink,
        environment: str,
    ) -> None:
        def factory():
            return SqlAlchemyManualAssessmentUnitOfWork(session_factory)

        self._list = ListManualAssessments(factory)
        self._get = GetManualAssessment(factory)
        self._get_submission = GetLearnerSubmission(factory)
        self._resolve = ResolveManualAssessment(
            factory, lambda: str(uuid4()), lambda: datetime.now(UTC)
        )
        self._event_sink = event_sink
        self._environment = environment

    def list_assessments(self, *, status, problem, limit, offset):
        return self._list(status=status, problem=problem, limit=limit, offset=offset)

    def get_assessment(self, attempt_id):
        return self._get(attempt_id)

    def get_submission(self, attempt_id, receipt):
        return self._get_submission(attempt_id, receipt)

    def decide(self, attempt_id: str, request: AssessmentDecisionRequest):
        record = self._get(attempt_id)
        return observe_operation(
            sink=self._event_sink,
            event_name="author.assessment",
            environment=self._environment,
            raw_operation_id=request.expected_decision_id or attempt_id,
            reference=record.slug,
            action=lambda: self._resolve(
                attempt_id,
                tuple(
                    AssessmentSelection(
                        item.component_index,
                        item.criterion_id,
                        item.level_id,
                        item.feedback,
                    )
                    for item in request.selections
                ),
                expected_decision_id=request.expected_decision_id,
                overall_feedback=request.overall_feedback,
                correction_reason=request.correction_reason,
            ),
            clock=monotonic,
        )


class _DefaultAuthorProblemService:
    def __init__(
        self,
        *,
        create: CreateDraft,
        list_drafts: ListDrafts,
        get: GetDraft,
        get_revision: GetRevisionDraft,
        save: SaveDraft,
        validate: ValidateDraft,
        preview: PreviewDraft,
        submit: SubmitForReview,
        request_changes: RequestChanges,
        approve: ApproveRevision,
        history: ListEditorialHistory,
        publish: PublishRevision,
        start_revision: StartSuccessorDraft,
        archive: ArchiveProblem,
        event_sink: EventSink,
        environment: str,
    ):
        self._create = create
        self._list = list_drafts
        self._get = get
        self._get_revision = get_revision
        self._save = save
        self._validate = validate
        self._preview = preview
        self._transitions = {
            EditorialStatus.IN_REVIEW: submit,
            EditorialStatus.CHANGES_REQUESTED: request_changes,
            EditorialStatus.APPROVED: approve,
        }
        self._history = history
        self._publish = publish
        self._start_revision = start_revision
        self._archive = archive
        self._event_sink = event_sink
        self._environment = environment

    def create(self):
        return self._create()

    def list(self, *, search=None, status=None):
        return self._list(search=search, status=status)

    def get(self, problem_id):
        return self._get(problem_id)

    def get_revision(self, revision_id: RevisionId):
        return self._get_revision(revision_id)

    def save(self, revision_id: RevisionId, request: SaveDraftRequest):
        current = self._get_revision(revision_id)
        content, metadata, response, scoring = decode_revision_payload(
            {
                "content": request.content,
                "metadata": request.metadata,
                "response": request.response,
                "scoring": request.scoring,
            }
        )
        revision = ProblemRevision(
            problem_id=ProblemId(request.problem_id),
            revision_id=revision_id,
            version=request.expected_version,
            slug=StableSlug(request.slug) if request.slug else None,
            status=current.status,
            content=content,
            metadata=metadata,
            response=response,
            scoring=scoring,
        )
        return self._save(revision, expected_version=request.expected_version)

    def validate(self, revision_id: RevisionId, expected_version: int):
        return self._validate(revision_id, expected_version=expected_version)

    def preview(self, revision_id: RevisionId, request: PreviewDraftRequest):
        current = self._get_revision(revision_id)
        unsaved = None
        if request.unsaved_state is not None:
            state = request.unsaved_state
            content, metadata, response, scoring = decode_revision_payload(
                {
                    "content": state.content,
                    "metadata": state.metadata,
                    "response": state.response,
                    "scoring": state.scoring,
                }
            )
            unsaved = ProblemRevision(
                problem_id=ProblemId(state.problem_id),
                revision_id=revision_id,
                version=request.expected_version,
                slug=StableSlug(state.slug) if state.slug else None,
                status=current.status,
                content=content,
                metadata=metadata,
                response=response,
                scoring=scoring,
            )
        return self._preview(
            revision_id,
            expected_version=request.expected_version,
            unsaved=unsaved,
        )

    def transition(
        self,
        revision_id: RevisionId,
        request: EditorialCommandRequest,
        target: EditorialStatus,
    ):
        command = self._transitions[target]
        return command(
            revision_id,
            expected_version=request.expected_version,
            note=request.note,
            actor=ActorContext(request.actor_context),
            operation_id=request.operation_id,
        )

    def list_history(self, revision_id: RevisionId):
        return self._history(revision_id)

    def publish(self, revision_id: RevisionId, request: PublishRevisionRequest):
        current = self._get_revision(revision_id)
        reference = current.slug.value if current.slug else "unassigned"
        return observe_operation(
            sink=self._event_sink,
            event_name="author.publication",
            environment=self._environment,
            raw_operation_id=request.idempotency_key,
            reference=reference,
            action=lambda: self._publish(
                revision_id,
                expected_version=request.expected_version,
                note=request.note,
                actor=ActorContext(request.actor_context),
                idempotency_key=request.idempotency_key,
            ),
            clock=monotonic,
        )

    def start_revision(self, problem_id: ProblemId, request: StartRevisionRequest):
        source = self._get_revision(RevisionId(request.source_revision_id))
        if source.problem_id != problem_id:
            from ...application.problems.errors import DraftNotFoundError

            raise DraftNotFoundError(source.revision_id)
        return self._start_revision(
            source.revision_id,
            expected_version=request.expected_version,
            operation_id=request.operation_id,
        )

    def archive(self, problem_id: ProblemId, request: ArchiveProblemRequest):
        return self._archive(
            problem_id,
            expected_version=request.expected_version,
            note=request.note,
            actor=ActorContext(request.actor_context),
            operation_id=request.operation_id,
        )


class _RequestIdMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        header_name: str,
        event_sink: EventSink,
        environment: str,
    ) -> None:
        self.app = app
        self.header_name = header_name
        self.event_sink = event_sink
        self.environment = environment

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return
        header_name = self.header_name.lower().encode()
        request_headers = dict(scope.get("headers", []))
        request_id = _safe_request_id(request_headers.get(header_name))
        status_code = 500
        started = monotonic()

        async def send_with_request_id(message: Message) -> None:
            nonlocal status_code
            if message.get("type") == "http.response.start":
                status_code = int(message.get("status", 500))
                headers = list(message.get("headers", []))
                headers.append((header_name, request_id.encode()))
                message["headers"] = headers
            await send(message)

        try:
            with bind_request_id(request_id):
                await self.app(scope, receive, send_with_request_id)
        finally:
            route = scope.get("route")
            route_template = getattr(route, "path", "unmatched")
            self.event_sink.emit(
                ObservabilityEvent(
                    event="http.request.completed",
                    outcome=_http_outcome(status_code),
                    environment=self.environment,
                    request_id=request_id,
                    duration_ms=max(0, round((monotonic() - started) * 1000)),
                    method=str(scope.get("method", "UNKNOWN")),
                    route=route_template,
                    status_code=status_code,
                )
            )


def _safe_request_id(raw_value: bytes | None) -> str:
    if raw_value is not None:
        value = raw_value.decode("ascii", errors="ignore")
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", value):
            return value
    return str(uuid4())


def _http_outcome(status_code: int):
    if status_code < 400:
        return "success"
    if status_code < 500:
        return "client_error"
    return "failure"
