# Weekly HR Operational Excellence Pipeline

## Ticket Prep and Classification (No Raw Data Merge)

Use this first when EPA provides the 4 ticket CSVs:

1. `Attendance Inquiry`
2. `CS Time and Attendance`
3. `FC General Inquiry`
4. `Timesheet Inquiry`

Run:

```powershell
python "Phase II\weekly_hr_oe\run_ticket_prep_pipeline.py" `
  --attendance-csv "Phase II\Attendance Inquiry Week 8-9.csv" `
  --cs-time-attendance-csv "Phase II\CS Time and Attendance Week 8-9.csv" `
  --fc-general-inquiry-csv "Phase II\FC General Inquiry Week 8-9.csv" `
  --timesheet-inquiry-csv "Phase II\Timesheet Inquiry Week 8-9.csv" `
  --pull-date 2026-03-02 `
  --week8-start 2026-02-15 --week8-end 2026-02-21 `
  --week9-start 2026-02-22 --week9-end 2026-02-28 `
  --out-dir "Phase II\output\ticket_prep" `
  --label "wk9_sun_sat_locked"
```

Optional auto-discovery mode if all 4 files are in one folder:

```powershell
python "Phase II\weekly_hr_oe\run_ticket_prep_pipeline.py" `
  --phase2-dir "Phase II" `
  --pull-date 2026-03-02 `
  --week8-start 2026-02-15 --week8-end 2026-02-21 `
  --week9-start 2026-02-22 --week9-end 2026-02-28 `
  --out-dir "Phase II\output\ticket_prep" `
  --label "wk9_sun_sat_locked"
```

What this does:

- Cleans each CSV independently.
- Excludes WFM-owned queues from HR reporting using `Assignment Group` proxy rules because the EPA extracts do not include a dedicated resolver field.
- Deduplicates rows inside each CSV.
- Classifies each row with deterministic keyword rules.
- Checks date coverage and flags missing dates in Week 8 and Week 9.
- Verifies required trailing two-week range coverage from pull date.
- Produces per-service `cleaned.csv`, `summary.json`, and `llm_compact.json`.
- Produces a non-merged manifest and compact rollup pointers for LLM orchestration.

Main outputs:

- `<run_dir>\ticket_prep_manifest.json`
- `<run_dir>\ticket_prep_rollup_for_llm.json`
- `<run_dir>\ticket_prep_chat_handoff.md`
- `<run_dir>\<service>\*_cleaned.csv`
- `<run_dir>\<service>\*_summary.json`
- `<run_dir>\<service>\*_llm_compact.json`

Important:

- Raw datasets are not combined.
- Week boundaries are locked to Sunday through Saturday.
- WFM-owned ticket work is excluded from HR metrics. Current proxy queues include `Real Time Analyst*` and `WFM*` assignment groups.
- Compact files are designed to reduce LLM token usage.

TM self-service reference:

- Clock in / clock out at a timeclock or via the app
- View current timecard for the pay period
- Edit or submit a missed punch or forgot-to-punch request
- Submit timecard corrections or edits for manager approval
- View punch history and punch detail, including location, device, and timestamps
- Confirm or acknowledge punches when the device or app prompts
- View published schedule and future shifts
- View time off balances and accruals
- View status of submitted requests, including timecard edits and PTO
- Get notifications of approvals, denials, or required actions
- Complete simple approval tasks in-app when approver rights are enabled

This pipeline builds a weekly answer pack focused on the Supplemental document's HR Operational Excellence questions.

It has three independent stages:

1. `hr_oe_weekly_analysis.py` builds the answer pack and metrics JSON.
2. `hr_oe_math_validator.py` recomputes key metrics from raw CSVs.
3. `hr_oe_quality_validator.py` checks section completeness and writing guardrails.

Use the orchestrator to run all three:

```powershell
python "Phase II\weekly_hr_oe\run_hr_oe_pipeline.py" `
  --phase1-dir "Phase I\Phase I CSV" `
  --phase2-dir "Phase II\Phase II CSVs" `
  --pull-date 2026-03-03 `
  --week8-start 2026-02-15 --week8-end 2026-02-21 `
  --week9-start 2026-02-22 --week9-end 2026-02-28 `
  --out-dir "Phase II\output" `
  --label "wk9_sun_sat_locked"
```

Notes:

- Phase I auto-discovery prefers a filename containing both `snowflake` and `ukg`.
- Phase II auto-discovery requires CSV filenames containing all service tokens:
  - `attendance` and `inquiry`
  - `cs`, `time`, and `attendance`
  - `fc`, `general`, and `inquiry`
  - `timesheet` and `inquiry`
- The runner fails early if the Phase I file does not cover the required trailing two completed weeks from `--pull-date`.

Outputs:

- `Phase II/output/hr_oe_answer_pack_<label>.md`
- `Phase II/output/hr_oe_metrics_<label>.json`
- `Phase II/output/hr_oe_math_validation_<label>.json`
- `Phase II/output/hr_oe_quality_validation_<label>.json`
- `Phase II/output/hr_oe_pipeline_run_<label>.json`
- `Phase II/output/hr_oe_chat_handoff_<label>.md`

Important notes:

- Week boundaries are explicit and should always be Sunday through Saturday.
- Cross phase coverage metrics are labeled as proxy values because ticket records and UKG touches are different units.
- Phase II metrics exclude WFM-owned queues by assignment group proxy until EPA provides a true `Resolved By` or owning-team field.
- SLA commitment accuracy cannot be fully answered unless SLA-specific fields are present in the ticket source data.
