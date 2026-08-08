# ADR-0001: Foundation Scope and Deferrals

## Status

Accepted

## Context

Release 0 requires a runnable executable foundation with strict public/private boundaries and no speculative runtime services.

## Decision

- Expose only four local services in Compose: PostgreSQL, API, Learn, and Studio.
- Defer Redis, Celery, Docling, MinIO, and object storage until an explicit implementation phase requires it.
- Keep Studio bound to loopback by configuration intent in compose and scripts, while Learn remains on `3000`.
- Keep API startup/readiness tied to database readiness semantics.

## Consequences

- Reduced operational risk in early phases.
- Clear migration path to introduce async or storage-heavy services only when requirements explicitly open that path.
- Foundation remains aligned with no-auth pilot constraints and avoids accidental production-like assumptions.
