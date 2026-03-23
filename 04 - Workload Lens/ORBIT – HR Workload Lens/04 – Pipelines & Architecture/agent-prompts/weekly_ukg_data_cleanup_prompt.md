# Weekly UKG Data Cleanup Prompt

Use this prompt when you want an agent to prepare a new weekly UKG timecard dataset for Workload Lens.

Before running, replace the placeholders in angle brackets.

## Required References

- `Workload_Lens_Data_Handling_Policy.md`
- `run-contracts/ukg_timecard_weekly_run_contract.json`
- `UKG_Timecard_Intake_Cleanup_and_Deidentification_Working_Artifact.md`

## Copy/Paste Prompt

```text
Prepare this week's Workload Lens UKG timecard dataset.

You must follow these references before doing any work:
- Workload_Lens_Data_Handling_Policy.md
- run-contracts/ukg_timecard_weekly_run_contract.json
- UKG_Timecard_Intake_Cleanup_and_Deidentification_Working_Artifact.md

Task inputs:
- Raw UKG file(s): <PATH_TO_UKG_RAW_FILE_OR_FOLDER>
- Run label: <RUN_LABEL>
- Reporting window: <START_DATE> to <END_DATE>
- Output root: <OUTPUT_ROOT>

Non-negotiable rules:
- Keep UKG separate from ticket data.
- Do not merge UKG rows with any ServiceNow or ticket dataset.
- Treat comments and notes as high-risk text.
- Remove, mask, or tokenize PII before any LLM-safe artifact is created.
- Use deterministic and auditable cleanup logic.
- Record assumptions, exclusions, and coverage warnings in the manifest and handoff.

Required outputs:
- ukg_run_manifest.json
- ukg_redaction_audit.json
- ukg_cleaned.csv
- ukg_cleaned_structured.json
- ukg_llm_compact.json
- ukg_chat_handoff.md

Execution expectations:
1. Land or reference the raw UKG source unchanged.
2. Validate schema, field presence, and date coverage for the requested window.
3. Normalize headers, timestamps, and controlled-value fields.
4. Detect and redact or mask PII.
5. Reduce noise in free-text fields while preserving business signal.
6. Produce a cleaned analytical file and a structured JSON output.
7. Build an LLM-safe compact JSON with minimized evidence only.
8. Write a handoff that states source, reporting window, row counts, redaction summary, limitations, and output paths.

At the end, return:
- whether the run passed
- key coverage or quality warnings
- the output file paths
- any unresolved blockers
```
