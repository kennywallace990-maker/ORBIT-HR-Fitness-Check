# Workload Lens Data Handling Policy

**Status:** Governed working standard  
**Version:** 1.0  
**Last Updated:** 2026-03-18  
**Purpose:** Define the formal, repeatable, agent-readable policy for how Workload Lens data is ingested, cleaned, de-identified, structured, and prepared for weekly analysis.

## Why This Policy Exists

Workload Lens uses two different source families:

1. UKG timecard data
2. HR ticket / ServiceNow data

They answer different questions and must remain operationally separate.

- UKG tells us who did the work and what timecard work occurred.
- Ticket data tells us more about how the request entered HR and what request context surrounded the work.
- Neither source should be treated as a perfect substitute for the other.
- The product must be able to explain which source and which time window were used for every insight.

This policy is the top-level handling standard that any agent must follow before preparing weekly Workload Lens outputs.

## Governing References

This policy sits above the source-specific standards and run contracts:

- `Ticket_Cleanup_and_Classification_Standard.md`
- `UKG_Timecard_Intake_Cleanup_and_Deidentification_Working_Artifact.md`
- `Data_Map_and_Classification_Declaration.md` in the Governance & Risk folder
- `run-contracts/ticket_weekly_run_contract.json`
- `run-contracts/ukg_timecard_weekly_run_contract.json`
- `weekly_ticket_data_cleanup_prompt.md` in the Pipelines & Architecture `agent-prompts/` folder
- `weekly_ukg_data_cleanup_prompt.md` in the Pipelines & Architecture `agent-prompts/` folder

If this policy conflicts with an ad hoc request, this policy wins unless an authorized product owner explicitly changes the standard.

## Non-Negotiable Rules

1. UKG and ticket data must be prepared separately.
2. Ticket raw files must remain separated by service. No raw-row merge is allowed across ticket files.
3. Raw data is immutable once landed for a run.
4. PII cleanup happens before any LLM summarization or prompt packaging.
5. Weekly production outputs must be deterministic and auditable.
6. Official metrics cannot depend on probabilistic clustering or synthetic data generation.
7. Every run must produce a machine-readable manifest and a human-readable handoff.
8. Every insight must declare its source family, time window, and known limitations.
9. When the source supports it, the cleaned analytical output must include deterministic self-service candidate fields.

## Source Separation Policy

| Source Family | Primary Value | Allowed Relationship to Other Source |
|---|---|---|
| UKG Timecard | Work actually touched in UKG, actor group, work type, audit trail | Can be compared to ticket data only at an aggregate or explicitly evidenced level |
| HR Ticket / ServiceNow | Intake path, contact context, assignment routing, case detail | Can be compared to UKG only at an aggregate or explicitly evidenced level |

The following are not allowed in the weekly operational prep flow:

- blended raw-row datasets combining UKG and ticket rows
- assumed one-to-one ticket-to-UKG matching
- LLM-generated linkage between ticket records and UKG records presented as fact

## Required Data Layers

| Layer | Required | Purpose |
|---|---|---|
| Raw | Yes | Immutable landing copy of the source file(s) exactly as received |
| Staged | Yes | Structural normalization, schema checks, date parsing, required-field validation |
| Clean | Yes | De-identified analytical dataset with noise reduced and high-risk text controlled |
| Classified | Yes | Deterministic business rules applied for category, actor, scope, and flags |
| LLM-safe | Yes | Compact, minimized, redacted JSON prepared for weekly reasoning and narrative work |

JSON is the canonical structured handoff format for agent-to-agent work. CSV may be emitted as a flat analytical companion where useful.

## PII Handling Policy

The weekly run must minimize sensitive content before any downstream LLM use.

| Data Element | Handling Rule |
|---|---|
| Team member names | Remove, mask, or replace with stable surrogate keys in shared analytical outputs |
| Employee IDs / person numbers | Replace with stable surrogate keys unless the output is explicitly PII-restricted |
| Manager names | Remove, mask, or restrict to private outputs only |
| Email addresses | Redact before LLM-safe outputs |
| Phone numbers | Redact before LLM-safe outputs |
| Comments / notes / descriptions with free text | Treat as high-risk; retain only cleaned and minimized excerpts when materially required |
| Ticket numbers | May be retained in cleaned operational files if needed for traceability; do not assume they are safe for broad sharing |

## Noise Handling Policy

Noise removal is required when the content does not improve classification or workload insight.

Examples of noise to remove or suppress:

- HTML tags
- email signatures
- confidentiality footers
- out-of-office replies
- automated system alerts
- repeated boilerplate
- empty descriptions
- obvious spam or junk text

If a noisy text block still contains a business signal, keep the signal and drop the rest.

## Weekly Production Method Standard

The official weekly run is deterministic-first.

### Required in production

- schema validation
- required-field checks
- date coverage checks
- de-duplication
- PII scrubbing or masking
- structured metadata retention
- deterministic classification rules
- redaction audit reporting

### Allowed with guardrails

- regex-based anonymization
- NER-assisted PII detection if the redaction output is still reviewable and auditable
- ticket thread flattening when the source contains multi-message chains
- exploratory embedding clustering as a sidecar research aid only
- manually curated golden set for QA and rule validation

### Not allowed in the official weekly metrics pipeline

- synthetic augmentation of production input data
- probabilistic labels presented as official categories
- raw text prompts that include unredacted PII
- LLM-only classification without a deterministic audit trail

## Disposition of Suggested Ticket-LLM Practices

The following guidance is adopted with Workload Lens guardrails:

| Practice | Policy Position | Workload Lens Rule |
|---|---|---|
| Anonymization | Approved | Required before LLM-safe packaging |
| Noise removal | Approved | Required |
| Thread flattening | Conditionally approved | Ticket-only and chronology must be preserved when available |
| Metadata integration | Approved | Required in structured outputs |
| De-duplication | Approved | Required within each source and within each ticket service |
| Embedding clustering | Research only | Cannot drive official weekly KPI outputs by itself |
| Golden set | Approved | Recommended QA artifact |
| Synthetic augmentation | Not approved for weekly production | Keep out of official weekly run artifacts |

## Weekly Run Folder Policy

The folder path can vary by environment, but every weekly run must keep source families separate and must include a run label.

Recommended pattern:

```text
<run_root>/
  ukg/<run_label>/...
  ticket/<run_label>/...
```

Ticket service files should remain separated beneath the ticket run folder.

## Required Weekly Outputs

### UKG run

- `ukg_run_manifest.json`
- `ukg_redaction_audit.json`
- `ukg_cleaned.csv`
- `ukg_cleaned_structured.json`
- `ukg_llm_compact.json`
- `ukg_chat_handoff.md`

### Ticket run

- `ticket_prep_manifest.json`
- `ticket_prep_rollup_for_llm.json`
- `ticket_prep_chat_handoff.md`
- per-service `*_cleaned.csv`
- per-service `*_summary.json`
- per-service `*_llm_compact.json`
- per-service `*_redaction_audit.json` when free-text redaction is performed outside the existing deterministic script

## Weekly Agent Operating Procedure

1. Read this policy and the source-specific run contract before touching the data.
2. Create or identify the source-specific run folder.
3. Land the raw source file(s) unchanged.
4. Validate file presence, schema expectations, and date coverage.
5. Normalize headers, values, and timestamps.
6. Remove or mask PII and suppress obvious noise.
7. Produce the cleaned analytical output.
8. Apply deterministic classifications and scope rules.
9. Add deterministic self-service candidate fields when the source text clearly maps to an approved self-service capability.
10. Produce structured JSON artifacts for downstream LLM and operational handoff.
11. Document what was excluded, redacted, dropped, or left unresolved.

## Required Handoff Content

Every weekly handoff must state:

- source family
- run label
- pull date or extract date
- reporting window used
- input row count
- clean row count
- dropped row count
- redaction summary
- coverage warnings
- classification limitations
- output file paths

## Source-Specific Notes

### UKG

- UKG is the primary evidence set for real work touches.
- Free-text comments and note fields are high-risk and should not flow to LLM-safe artifacts unchanged.
- Preserve the fields needed to understand actor group, entity type, revision type, paycode, week, site, and business unit.

### Ticket

- Ticket detail is richer but not complete enough to stand alone as the workload lens.
- Keep ticket services separate at the raw-row level.
- Ticket prep may emit a rollup JSON that points to separate service artifacts, but that rollup is not a merged raw dataset.

## Policy Outcome

The weekly Workload Lens prep flow must always leave behind:

- a traceable raw source record
- a cleaned analytical dataset
- a structured JSON handoff for agents
- a documented explanation of what the data can and cannot support

That is the minimum bar for a valid weekly run.
