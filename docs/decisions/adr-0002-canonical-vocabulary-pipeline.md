# ADR-0002: Canonical vocabulary pipeline

Status: Accepted

## Context

Release 0 requires one canonical source, composite identity, explicit topic
parentage, bilingual search, future-value preservation, and deterministic
backend/frontend consumption without parallel enums.

## Decision

`vocab.md` is parsed by an adapter into framework-free domain records, validated
as a complete graph, and serialized to `backend/generated/vocabulary.json`.
PostgreSQL synchronization is idempotent by `(vocabulary_type, code)` and uses a
deferred self-referential parent constraint for one atomic whole-artifact write.
Release availability is a separate pure policy. OpenAPI-derived TypeScript and
the frontend vocabulary package are generated from backend-owned artifacts.
Missing-value proposals use a separate table and author API and cannot satisfy a
canonical reference.

## Consequences

- Canonical changes begin in `vocab.md` and require generation plus drift gates.
- Changing a vocabulary type or code creates a new identity; synchronization
  does not repurpose the old record.
- Future canonical values remain stored and visible to authors as unavailable.
- Phase 6/7 UI work consumes generated packages and APIs rather than defining
  local labels or enums.
