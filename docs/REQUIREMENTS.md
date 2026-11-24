# Requirements

Status: discovery draft — not approved for financial processing.

## Scope

The proposed ACH Reversal Tool will eventually support authorized users who need to inspect ACH files, identify candidate transactions, determine whether candidates are eligible for reversal, and generate a reversal file that conforms to approved banking specifications.

## Confirmed requirements

These are the requirements explicitly stated at project start:

1. The application is Python-based.
2. Authorized users are the intended users.
3. The future workflow includes ACH file processing, transaction identification, reversal eligibility validation, and reversal-file generation.
4. Output must follow applicable banking specifications.
5. Requirements and specifications must be reviewed before financial processing logic is implemented.
6. Development and testing must use synthetic data only.
7. Changes must not be committed or pushed without owner approval.

## Working assumptions — require confirmation

The following are planning assumptions, not approved requirements:

- The initial interface will be a local or internal web application rather than a public service.
- Users will upload NACHA files and download a separately generated result; the source file will never be edited in place.
- A human reviewer will approve the candidate set and generated output before release.
- The system will initially support a defined subset of NACHA formats and transaction types rather than every possible entry class.
- A relational database will store workflow metadata and audit events, while raw files will use controlled object/file storage.
- Authentication and authorization will be delegated to an organization-managed identity provider in a deployed environment.
- The first release will not transmit files to a bank or call a banking API.

## Business questions to resolve

### Rules and scope

- Which NACHA rulebook version, ODFI/RDFI rules, and bank-specific implementation guide govern the output?
- Which SEC codes, entry types, addenda records, batches, and file types are in scope?
- Which reversal reasons are allowed, and how are they mapped to codes and descriptions?
- What are the time limits and effective-entry-date rules for each reversal scenario?
- Which original transactions are eligible, and what makes a transaction ineligible?
- How should returned, rejected, already-reversed, duplicate, prenote, zero-dollar, same-day, and future-dated entries be handled?
- How are amounts, sign conventions, trace numbers, effective dates, company identifiers, and descriptive fields derived?

### User workflow and controls

- What roles exist (operator, reviewer, administrator, auditor), and which actions require separation of duties?
- Is dual approval required before a file can be downloaded or released?
- Can a user override a validation result? If yes, which roles may do so and what justification is mandatory?
- What search and filtering fields are needed to identify transactions?
- Are bulk selections allowed, and what maximum file/transaction sizes must be supported?
- What status lifecycle and expiration rules apply to uploaded files and draft reversals?

### File handling and integration

- Which encodings, line endings, blocking factors, padding, and fixed-width constraints are required?
- Must the tool preserve original ordering, or may it group/reorder transactions?
- What control totals and hash calculations must be validated before and after generation?
- Where will files be stored, for how long, and how will they be securely deleted?
- Will import/export eventually integrate with SFTP, a bank portal, or another system? What is the approved transport and handoff control?

### Operations and compliance

- What retention, legal hold, audit, and incident-response requirements apply?
- What availability, recovery point objective, recovery time objective, and support model are required?
- Which environments are needed, and how will synthetic fixtures be prevented from being confused with production data?
- What accessibility, browser, localization, and time-zone requirements apply?

## Acceptance criteria for the specification phase

Financial processing work may begin only after the owner and appropriate banking/compliance reviewers approve:

- the supported input/output scope and governing specifications;
- the complete eligibility and reversal-rule catalog, including precedence and exception handling;
- roles, approval controls, audit requirements, retention, and data boundaries;
- file-format examples using synthetic data;
- error-handling, reconciliation, and operational requirements; and
- test vectors and expected results for valid, invalid, boundary, and adversarial cases.
