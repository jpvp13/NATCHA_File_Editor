# AGENTS.md

## Purpose

This file provides working rules for contributors and coding agents developing the ACH Reversal Tool. The application is a high-risk financial-file workflow; correctness, traceability, and controlled change are more important than speed.

## Before changing code

1. Read [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
2. Identify whether the requested behavior is a confirmed requirement, an approved assumption, or an unresolved business rule.
3. Stop and request clarification when a change could affect transaction selection, reversal eligibility, amounts, dates, routing information, file control totals, or output formatting.
4. Keep changes small and explain the business rule or specification source behind them.

## Financial safety rules

- Do not process production or live banking files in development, tests, demos, or local tools.
- Use synthetic fixtures only. Never add account numbers, routing numbers, names, addresses, credentials, or other financial data to the repository.
- Do not implement reversal generation, eligibility decisions, or file mutation until the applicable NACHA/ODFI rules, bank-specific requirements, and approval workflow are documented and approved.
- Preserve source-file immutability. Any future output must be a separately named artifact with provenance and validation results.
- Prefer fail-closed behavior: an unknown, ambiguous, malformed, or unsupported transaction must be rejected or held for review rather than guessed.
- Do not log raw ACH records, sensitive fields, credentials, or complete generated files.

## Engineering expectations

- Keep parsing, domain validation, workflow/orchestration, and presentation concerns separate.
- Make validation deterministic, explainable, and auditable. Record rule identifiers and outcomes rather than only a pass/fail result.
- Add unit tests for every approved rule, including boundary dates, duplicate inputs, malformed records, control-total mismatches, and partial failures.
- Add property/invariant tests for record counts, hash totals, batch/file control totals, and output reproducibility when the specification defines them.
- Pin and review dependencies. Prefer a supported Python version, type hints, formatting, linting, and automated tests.
- Treat generated output as untrusted until it passes structural and business validation.

## Change control

- Do not commit, push, publish, or alter external systems without explicit owner approval.
- Before proposing a commit, show the changed files, tests run, known limitations, and any requirements that remain assumptions.
- Keep documentation current when a design decision or business rule changes.

## Repository note

The current workspace contains an empty nested `ACH-Reversal-Tool/.git` directory that is untracked by the root repository. Do not add, remove, merge, or commit that nested repository without explicit direction.
