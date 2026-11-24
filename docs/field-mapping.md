# PPD field mapping

Status: Phase 1 structural mapping. Source: user-supplied J.P. Morgan Access NACHA File Specifications, dated August 23, 2021, pages 20–25 as cited in the project brief. This document records layout facts only; it does not authorize reversal transformations.

All physical records are 94 characters. Positions below are one-based and inclusive.

| Record | Positions | Field | Phase 1 behavior |
|---|---:|---|---|
| `1` | 1 | Record type | Require `1`. |
| `1` | 2–3 | Priority code | Preserve and expose. |
| `1` | 4–13 | Immediate destination | Preserve; mask in UI. |
| `1` | 14–23 | Immediate origin | Preserve; mask if displayed. |
| `1` | 24–29 | Creation date | Preserve and structurally expose. |
| `1` | 30–33 | Creation time | Preserve and structurally expose. |
| `1` | 34 | File ID modifier | Preserve. |
| `1` | 35–37 | Record size | Require `094`. |
| `1` | 38–39 | Blocking factor | Require `10`. |
| `1` | 40 | Format code | Require `1`. |
| `1` | 41–63 | Destination name | Preserve. |
| `1` | 64–86 | Origin name | Preserve. |
| `1` | 87–94 | Reference code | Preserve. |
| `5` | 1–3 | Service class code | Preserve; reversal reassignment is unresolved. |
| `5` | 4–20 | Company name | Preserve. |
| `5` | 21–40 | Company discretionary data | Preserve. |
| `5` | 41–50 | Company identification | Preserve. |
| `5` | 51–53 | SEC code | Recognize `PPD`; reject unsupported generation scope. |
| `5` | 54–63 | Company entry description | Preserve; reversal marker is unresolved. |
| `5` | 64–69 | Company descriptive date | Preserve. |
| `5` | 70–75 | Effective entry date | Preserve; timing rules are unresolved. |
| `5` | 76–78 | Settlement date | Preserve. |
| `5` | 79 | Originator status code | Preserve. |
| `5` | 80–87 | Originating DFI identification | Preserve. |
| `5` | 88–94 | Batch number | Preserve. |
| `6` | 1 | Record type | Require `6`. |
| `6` | 2–3 | Transaction code | Parse; no reversal mapping enabled. |
| `6` | 4–11 | Receiving DFI identification | Parse for hash; mask in UI. |
| `6` | 12 | Check digit | Preserve. |
| `6` | 13–29 | DFI account number | Preserve source; mask in UI. |
| `6` | 30–39 | Amount | Parse as integer cents; no arithmetic transformation enabled. |
| `6` | 40–54 | Individual identification number | Preserve; sensitive. |
| `6` | 55–76 | Individual name | Preserve; synthetic fixtures only. |
| `6` | 77–78 | Discretionary data | Preserve. |
| `6` | 79 | Addenda indicator | Associate `7` records; unsupported patterns block future generation. |
| `6` | 80–94 | Trace number | Preserve and use as source linkage. |
| `8` | 1 | Record type | Require `8`. |
| `8` | 2–4 | Service class code | Preserve and validate against parsed batch. |
| `8` | 5–10 | Entry/addenda count | Recalculate for validation. |
| `8` | 11–20 | Entry hash | Recalculate for validation. |
| `8` | 21–32 | Total debits | Recalculate for validation. |
| `8` | 33–44 | Total credits | Recalculate for validation. |
| `8` | 45–54 | Company identification | Preserve and compare to header. |
| `8` | 80–87 | Originating DFI identification | Preserve and compare to header. |
| `8` | 88–94 | Batch number | Preserve and compare to header. |
| `9` | 1 | Record type | Require `9`. |
| `9` | 2–7 | Batch count | Recalculate for validation. |
| `9` | 8–13 | Block count | Recalculate for validation. |
| `9` | 14–21 | Entry/addenda count | Recalculate for validation. |
| `9` | 22–31 | Entry hash | Recalculate for validation. |
| `9` | 32–43 | Total debits | Recalculate for validation. |
| `9` | 44–55 | Total credits | Recalculate for validation. |
| `9` | 56–94 | Reserved | Preserve. |

## Unresolved reversal semantics

Transaction-code translation, effective-date calculation, service-class changes, `REVERSAL` description behavior, trace-number generation, and bank acceptance of a one-entry file remain unverified. No code path in Phase 1 changes these fields or enables bank-ready export.
