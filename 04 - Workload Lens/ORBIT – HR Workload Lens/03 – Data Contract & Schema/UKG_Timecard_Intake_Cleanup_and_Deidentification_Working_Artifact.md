# UKG Timecard Intake, Cleanup, and De-identification Working Artifact

**Status:** Working artifact  
**Last Updated:** 2026-03-18  
**Purpose:** Capture the initial data foundation, sequencing, and processing expectations for UKG timecard data before we implement scripts, schema objects, or downstream reporting.

## Why This Artifact Exists

Workload Lens depends on two source families:

1. UKG timecard data
2. HR ticket / ServiceNow data

These sources answer different parts of the workload question:

- UKG timecard data tells us who did the work, what HR business unit or actor group performed it, and what kind of timecard work occurred.
- Ticket data adds request context such as how the work came in, what service path it followed, and other operational detail that is not always visible in UKG.

The product needs both perspectives to explain what is driving HR work, where process gaps exist, where self-service may have been possible, and where there is opportunity to optimize or automate.

## Current Build Order

- Start with UKG timecard data first.
- Establish a formal intake, cleanup, de-identification, and quality-control process before building the script.
- Treat ticket data as a complementary source, not the sole system of record for workload volume.

## Source Reality and Constraints

- Ticket data usually contains richer request detail than UKG.
- Ticket data does not capture all of the real work being done by HR.
- UKG timecard data reflects actual work touches, even when no ticket exists.
- Reconciliation between UKG and ticket data is weak and often incomplete.
- Some UKG comments may reference a ticket number, but most rows do not provide a reliable direct link.
- The Workload Lens report must be explicit about whether an insight is based on UKG only, ticket data only, or blended directional evidence.
- The product should not imply one-to-one matching between UKG rows and tickets unless the linkage is directly evidenced.

## Phase 1 Objective

For UKG timecard data, the immediate objective is to define a repeatable process that:

- ingests raw extracts in a controlled way
- removes or masks PII and free-text noise
- preserves the fields required for workload analysis
- supports deterministic and auditable classification
- prepares clean weekly data for OBR analysis

## Recommended Logical Data Layers

| Layer | Purpose | Notes |
| --- | --- | --- |
| Raw | Immutable landing copy | Original extract remains unchanged and is not used directly by reporting or LLM workflows |
| Staged | Structural normalization | Header cleanup, datatype parsing, required field validation, file/date checks |
| Clean | De-identified analytical dataset | PII removed, masked, or tokenized; noise reduced; core business fields preserved |
| Classified | Business-rule output | Actor group, work type, workload driver, self-service candidate, and other derived fields |
| Reporting / LLM-safe | Weekly summarized output | Aggregated and minimized evidence artifacts only; no unnecessary direct identifiers |

## UKG Formal Process Draft

1. Land the raw UKG extract unchanged and capture load metadata.
2. Validate the expected columns, date coverage, and row counts.
3. Normalize headers, whitespace, timestamps, and controlled-value fields.
4. Separate direct identifiers and free-text fields from analytical fields.
5. Remove, hash, mask, or otherwise de-identify PII before downstream analysis.
6. Reduce noise from comments or free text while preserving business signal needed for classification.
7. Produce a cleaned analytical dataset for weekly workload analysis.
8. Apply deterministic business rules for actor group, work type, business unit, and future self-service opportunity flags.
9. Generate quality-control outputs that show what was redacted, dropped, retained, or left unresolved.
10. Publish only the cleaned and classified outputs to the reporting layer.

## PII and Noise Handling Principles

- Raw files may contain identifiers and comments that should not move downstream unchanged.
- Direct identifiers should be removed, masked, or replaced with stable surrogate keys when row continuity is still needed.
- Free-text comments should be treated as high-risk inputs and should only be retained in redacted or minimized form when they materially improve classification.
- No raw free-text field should be sent to LLM workflows by default.
- The cleanup process must favor auditability over convenience so we can explain exactly what was changed and why.

## What the Clean UKG Dataset Must Preserve

- reporting week or analyzed date range
- site, business unit, and organizational context
- revision actor and access profile needed to identify who did the work
- entity type, revision type, paycode, and other work descriptors
- enough linkage metadata to trace cleaned rows back to raw records in a controlled way
- quality-control metadata showing cleanup outcomes

## Planned Analytical Questions This Foundation Should Support

- What work is driving HR workload by week, site, business unit, and actor group?
- Who is doing the work: Local HR, HRSS, Local Ops, Team Members, or another group?
- What kinds of timecard actions are consuming the most effort?
- What work appears avoidable, rework-driven, or potentially self-service?
- What process gaps are most likely creating repeat HR effort?
- What source-backed answer can we provide in the weekly HR OBR for the prior week or selected time range?

## What This Artifact Does Not Do Yet

- define the final field-by-field schema
- define the exact redaction rules or regex library
- implement the cleanup script
- solve UKG-to-ticket reconciliation
- finalize self-service classification logic

## Decisions Captured Here

- UKG timecard data is the first source to operationalize.
- Ticket data remains important, but it is not complete enough to stand alone as the workload lens.
- Cleanup and de-identification must happen before downstream classification and before LLM usage.
- The Workload Lens narrative should clearly state which source and time window powered each conclusion.
