# ACH Reversal Tool

Planning repository for an application that will help authorized users inspect ACH files, identify transactions, validate reversal eligibility, and produce reversal files according to approved banking specifications.

This repository is intentionally documentation-first. No financial processing logic has been implemented. Until the requirements and banking rules are reviewed and approved, all examples and test fixtures must use synthetic data only.

## Project status

The project is in discovery and architecture planning. See:

- [Requirements](docs/REQUIREMENTS.md) — confirmed requirements, assumptions, open questions, and acceptance criteria to resolve.
- [Architecture](docs/ARCHITECTURE.md) — proposed system boundaries, components, data flow, and technology choices.
- [Development plan](docs/DEVELOPMENT_PLAN.md) — phased delivery plan and definition of done.
- [AGENTS.md](AGENTS.md) — engineering, security, data-handling, and change-control guidance for contributors and coding agents.

## Non-negotiable constraints

- Do not implement or enable financial processing logic until the specifications are reviewed and approved.
- Use synthetic or explicitly de-identified data only during development and testing.
- Do not commit or push changes without the repository owner’s approval.
