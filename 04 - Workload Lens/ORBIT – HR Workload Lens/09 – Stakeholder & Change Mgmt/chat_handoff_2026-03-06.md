# Workload Lens Chat Handoff - 2026-03-06

## Current State

- Phase I source folder is `Phase I\Phase I CSV`
- Current discovered Phase I file is `Snowflake UKG data.csv`
- Phase II source folder is `Phase II\Phase II CSVs`
- Expected Phase II services:
  - `Attendance Inquiry`
  - `CS Time and Attendance`
  - `FC General Inquiry`
  - `Timesheet Inquiry`

## Hard Blockers

- Phase I date coverage is incomplete for the required two-week window tied to pull date `2026-03-03`
- Missing Phase I dates:
  - `2026-02-16`
  - `2026-02-17`
  - `2026-02-18`
  - `2026-02-19`
  - `2026-02-20`
  - `2026-02-21`
- `Attendance Inquiry` in `Phase II\Phase II CSVs` is currently `.xlsx`, not `.csv`

## Available Automation

- Ticket prep pipeline:
  - `Phase II\weekly_hr_oe\run_ticket_prep_pipeline.py`
- HR Operational Excellence answer-pack pipeline:
  - `Phase II\weekly_hr_oe\run_hr_oe_pipeline.py`
- Both pipelines generate chat handoff files after runs

## Fastest Path To Generate Tonight's Report

1. Replace the Phase I export with a CSV covering both completed weeks with no missing dates.
2. Replace `Attendance Inquiry.xlsx` with `Attendance Inquiry.csv`.
3. Keep the other three Phase II CSVs in `Phase II\Phase II CSVs`.
4. Run the full pipeline:

```powershell
python "Phase II\weekly_hr_oe\run_hr_oe_pipeline.py" `
  --phase1-dir "Phase I\Phase I CSV" `
  --phase2-dir "Phase II\Phase II CSVs" `
  --pull-date 2026-03-03 `
  --week8-start 2026-02-15 --week8-end 2026-02-21 `
  --week9-start 2026-02-22 --week9-end 2026-02-28 `
  --out-dir "Phase II\output" `
  --label "wk9_locked"
```

## If EPA Cannot Refresh Tonight

- Strict path:
  - Do not publish WoW conclusions
  - Wait for corrected Phase I and CSV version of Attendance Inquiry
- Provisional path:
  - Publish a Week 9 only answer section
  - Explicitly mark Week 8 comparison as incomplete due to source coverage gap

## Key Output Files

- Report markdown:
  - `Phase II\output\hr_oe_answer_pack_<label>.md`
- Metrics JSON:
  - `Phase II\output\hr_oe_metrics_<label>.json`
- Run summary:
  - `Phase II\output\hr_oe_pipeline_run_<label>.json`
- Chat handoff:
  - `Phase II\output\hr_oe_chat_handoff_<label>.md`
