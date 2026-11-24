# Architecture

Status: proposed architecture with Phase 1 parser boundary implemented. This document describes boundaries and safeguards; it does not authorize financial processing behavior.

## Recommendation

Start with a modular monolith in Python behind an internal web interface. Keep parsing, domain rules, workflow, persistence, and file generation behind explicit interfaces so the application can be tested as a set of deterministic components and later split into services only if scale or isolation requires it.

This is appropriate for an early financial workflow because it limits operational complexity, keeps transactions and audit events close together, and makes approval gates visible. It should be deployed as a private service with managed identity, encrypted storage, and centralized logging.

## Logical components

```text
User / reviewer
      |
Internal web UI / API
      |
Workflow and authorization boundary
      |---- Upload and quarantine service
      |---- Parser / structural validator
      |---- Transaction search and selection
      |---- Eligibility rules engine (not implemented until approved)
      |---- Review and approval state machine
      |---- Generator / output validator (not implemented until approved)
      |
      |---- Relational metadata + audit store
      |---- Encrypted file/object storage
      |---- Observability and alerting
```

## Suggested technology baseline

These are recommendations, not locked dependencies:

- Python 3.12+ with a supported release policy.
- FastAPI for an internal API, with server-rendered or lightweight browser UI initially.
- Pydantic for typed request and domain models.
- `pyproject.toml` with a locked dependency workflow (uv, Poetry, or pip-tools to be selected).
- PostgreSQL for users, workflow state, file metadata, rule versions, approvals, and audit events.
- S3-compatible encrypted object storage for quarantined inputs and generated artifacts.
- SQLAlchemy plus Alembic if a relational persistence layer is approved.
- pytest, mypy or pyright, Ruff, and coverage reporting for quality gates.
- Structured JSON logs with redaction and correlation IDs; metrics and traces through the organization’s approved platform.

Do not add these dependencies until the technology choice and environment are approved. A first milestone can remain documentation-only.

## Phase 1 implementation boundary

The current implementation is intentionally headless and standard-library-only:

- `domain.models` contains immutable source-linked file, batch, entry, addenda, control, and issue models.
- `parser.ppd` parses 94-character file, batch, entry, addenda, control, and padding records while retaining raw record text and the source SHA-256 digest.
- `validation.ppd` checks PPD scope, record/header constraints, counts, entry hashes, debit/credit totals, addenda indicators, and 10-record block alignment.
- `writer` provides deterministic reserialization and a review-only selected-entry preview that recalculates structural controls without changing transaction semantics.
- `tests/` contains synthetic fixtures and direct pytest-compatible tests; no live or employee data is present.

The selected-entry preview is not a reversal file. It does not translate transaction codes, change dates or descriptions, issue trace numbers, or create bank-ready output.

## Key design principles

- Immutable source: uploaded files are content-addressed, quarantined, and never modified.
- Explicit versions: parser, ruleset, and generator versions are recorded with every artifact.
- Fail closed: unsupported or ambiguous records stop the workflow or enter manual review.
- Deterministic output: the same approved input, selection, ruleset, and configuration produce the same result.
- Human control: eligibility results are explainable and output release is gated by authorization/approval.
- Least privilege: users, services, and storage have only the access required for their role.
- Auditability: record who did what, when, against which file hash and ruleset, without exposing sensitive contents in ordinary logs.

## Proposed lifecycle

1. Upload: authenticate, authorize, record metadata and hash, quarantine the file.
2. Inspect: validate encoding/structure and display safe summaries using synthetic data in development.
3. Select: identify candidates using approved, explainable criteria.
4. Validate: run the versioned eligibility rules and show every result and reason.
5. Review: require the configured reviewer/approval controls.
6. Generate: create a new artifact only after approval; preserve provenance.
7. Validate output: re-parse the generated artifact and reconcile counts, hashes, totals, and required fields.
8. Export: provide a controlled download or later approved handoff; record the event.

## Security boundaries and failure handling

Files should pass through quarantine and malware/content checks before parsing. Size, record-count, encoding, and timeout limits should prevent resource exhaustion. Parsing errors, control-total mismatches, duplicate submissions, unavailable storage, database conflicts, and rule-engine uncertainty must produce a visible failure state and an audit event; they must not produce a partially trusted output.

The design must avoid raw-record logging, protect secrets through a managed secret store, encrypt data in transit and at rest, apply retention/deletion controls, and support security review before any real data is introduced.
