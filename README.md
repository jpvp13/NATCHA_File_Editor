# ACH Reversal Tool

Planning repository for an application that will help authorized users inspect ACH files, identify transactions, validate reversal eligibility, and produce reversal files according to approved banking specifications.

This repository contains the Phase 1 structural parser/validator foundation. No financial processing logic, bank-specific reversal transformation, direct submission, or production export has been implemented. All examples and test fixtures use synthetic data only.

## Project status

The project is in discovery and architecture planning. See:

- [Requirements](docs/REQUIREMENTS.md) — confirmed requirements, assumptions, open questions, and acceptance criteria to resolve.
- [Architecture](docs/ARCHITECTURE.md) — proposed system boundaries, components, data flow, and technology choices.
- [Development plan](docs/DEVELOPMENT_PLAN.md) — phased delivery plan and definition of done.
- [AGENTS.md](AGENTS.md) — engineering, security, data-handling, and change-control guidance for contributors and coding agents.
- [Field mapping](docs/field-mapping.md) — Phase 1 PPD layout mapping grounded in the supplied J.P. Morgan guide pages 20–25.
- [Architecture decisions](docs/decisions.md) — decisions and source limitations recorded before UI work.

## Phase 1 implementation

The `src/ach_reversal` package provides typed PPD models, fixed-width parsing, source SHA-256 fingerprinting, addenda association, structural/control validation, deterministic serialization, and a review-only selected-entry preview. Synthetic fixtures and tests are under `tests/`.

The user interface is intentionally deferred until the unresolved bank and reversal requirements are reviewed.

## Non-negotiable constraints

- Do not implement or enable financial processing logic until the specifications are reviewed and approved.
- Use synthetic or explicitly de-identified data only during development and testing.
- Do not commit or push changes without the repository owner’s approval.
