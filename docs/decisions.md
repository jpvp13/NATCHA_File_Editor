# Architecture decisions

## ADR-001: Modular Python package with headless parser boundary

Decision: Keep NACHA parsing, validation, writing, and future reversal rules as separate modules under `src/ach_reversal`.

Reason: Fixed-width parsing and control arithmetic need deterministic unit tests independent of a future UI. The UI must not manipulate raw NACHA strings.

Status: Accepted for Phase 1.

## ADR-002: Preserve source bytes and use immutable source-linked models

Decision: `SourceFile` stores the original bytes and SHA-256 digest; parsed records retain raw 94-character text and source record numbers.

Reason: Financial-file review needs provenance, leading-zero preservation, and evidence that the source was not edited in place.

Status: Accepted for Phase 1.

## ADR-003: Structural validation before reversal rules

Decision: Phase 1 validates lengths, record structure, PPD scope, addenda associations, counts, hashes, totals, and block alignment. It does not decide eligibility or transform transactions.

Reason: The project brief identifies current bank-specific reversal rules as unresolved and explicitly prohibits guessed transformations.

Status: Accepted for Phase 1.

## ADR-004: Synthetic fixtures only

Decision: Test fixtures use fictitious organizations, names, account identifiers, and amounts.

Reason: The project mandate and repository rules prohibit real employee or banking data during development.

Status: Accepted.

## Source limitation

The supplied PDF is retained as an external reference, not copied into the repository. The implementation mapping is based on the page 20–25 field layout transcribed in the supplied project brief. Exact PDF text extraction was unavailable in this environment; bank confirmation remains required before any production behavior.
