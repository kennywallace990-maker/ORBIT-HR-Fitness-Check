# Weekly HR Operational Excellence Pipeline

## Current Source Model

The governed Phase II ticket intake now starts from a rolling BI folder that contains two weekly files:

1. `cases opened last week`
2. `cases closed last week`

Those files cover the prior completed Sunday-Saturday week. The pipeline reconstructs the four tracked service inputs from that rolling folder before cleanup and reporting:

- `Attendance Inquiry`
- `CS Time and Attendance`
- `FC General Inquiry`
- `Timesheet Inquiry`

Legacy four-service CSV mode still works, but it is no longer the primary intake model.

## Recommended Folder-Drop Workflow

Point the pipeline at a OneDrive-synced folder that retains the recent weekly BI drops. The folder should contain filenames that clearly include:

- `opened`
- `closed`

If you drag the Outlook emails themselves into the folder, save or drop them as `.msg`. The configured PowerShell launchers will extract any attached `.csv`, `.xlsx`, or `.xlsm` BI files before running the pipeline.

The configured PowerShell launchers also scan the default Outlook Inbox for the observed weekly ServiceDesk report emails and extract their BI attachments into the same OneDrive folder.

## Preferred Weekly Entry Point

If you are running the full weekly operating flow, the preferred entry point is:

```powershell
powershell -ExecutionPolicy Bypass -File "04 - Workload Lens\ORBIT – HR Workload Lens\04 – Pipelines & Architecture\phase2-weekly-hr-oe\Run-Configured-Weekly-HR-OE.ps1"
```

Use this after the manual Phase I UKG refresh is complete. The wrapper runs the configured ticket intake first, then the full HR/OE pipeline, and writes a small orchestration summary JSON into `Phase II\output`.

Current Outlook pattern observed in production:

- sender: `ServiceDesk@chewy.com`
- subject: `WBR Previous Week Open Cases`
- subject: `WBR Previous Week Resolved Cases`

Example:

```text
OneDrive Ticket Drop/
  cases_opened_2026-03-08_to_2026-03-14.xlsx
  cases_closed_2026-03-08_to_2026-03-14.xlsx
  cases_opened_2026-03-15_to_2026-03-21.xlsx
  cases_closed_2026-03-15_to_2026-03-21.xlsx
```

The pipeline uses the row-level dates to select the required Week 8 and Week 9 files relative to `--pull-date`.

Configured folder for this workspace:

`C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Workload Lens Incoming ticket bi drop`

Configured launcher behavior:

- reads direct BI files already in the folder
- also scans for Outlook `.msg` emails in the same folder
- also scans the default Outlook Inbox for the weekly ServiceDesk report emails
- extracts allowed BI attachments into the folder
- prefixes extracted attachments from the observed Outlook subjects with `open_cases_` or `resolved_cases_` when needed
- moves processed `.msg` files into `_processed_msg`
- re-runs safely because the Inbox extractor skips files that already exist in the drop folder

## Ticket Prep and Classification

Use this first when you want the deterministic cleanup and classification outputs.

```powershell
python "Phase II\weekly_hr_oe\run_ticket_prep_pipeline.py" `
  --bi-weekly-dir "OneDrive Ticket Drop" `
  --pull-date 2026-03-22 `
  --week8-start 2026-03-08 --week8-end 2026-03-14 `
  --week9-start 2026-03-15 --week9-end 2026-03-21 `
  --out-dir "Phase II\output\ticket_prep" `
  --label "wk11_sun_sat_bi_locked"
```

What this does:

- Selects the required weekly opened / closed BI reports from the rolling folder
- Reconstructs service-specific working CSVs from the BI source pair
- Cleans each service independently
- Excludes WFM-owned queues from HR reporting using `Assignment Group` proxy rules
- Deduplicates rows inside each service file
- Classifies each row with deterministic keyword rules
- Adds deterministic self-service candidate fields based on the approved UKG self-service capability list
- Checks date coverage and flags missing dates in Week 8 and Week 9
- Verifies required trailing two-week range coverage from pull date
- Produces per-service `cleaned.csv`, `summary.json`, and `llm_compact.json`
- Produces a non-merged manifest and compact rollup pointers for LLM orchestration

Main outputs:

- `<run_dir>\_bi_service_inputs\bi_weekly_ticket_intake_manifest.json`
- `<run_dir>\ticket_prep_manifest.json`
- `<run_dir>\ticket_prep_rollup_for_llm.json`
- `<run_dir>\ticket_prep_chat_handoff.md`
- `<run_dir>\_bi_service_inputs\*_from_bi_weekly_reports.csv`
- `<run_dir>\<service>\*_cleaned.csv`
- `<run_dir>\<service>\*_summary.json`
- `<run_dir>\<service>\*_llm_compact.json`

Important:

- Raw BI files are not modified.
- Official outputs stay separated by service.
- Week boundaries are locked to Sunday through Saturday.
- WFM-owned ticket work is excluded from HR metrics. Current proxy queues include `Real Time Analyst*` and `WFM*` assignment groups.
- Compact files are designed to reduce LLM token usage.

## Folder-Drop Runner

If you want a simple script to schedule against the OneDrive-synced folder, use:

```powershell
python "Phase II\weekly_hr_oe\run_ticket_folder_drop.py" `
  --bi-weekly-dir "OneDrive Ticket Drop" `
  --pull-date 2026-03-22 `
  --out-dir "Phase II\output\ticket_prep"
```

Or use the configured launcher in this repo:

```powershell
powershell -ExecutionPolicy Bypass -File "04 - Workload Lens\ORBIT – HR Workload Lens\04 – Pipelines & Architecture\phase2-weekly-hr-oe\Run-Configured-Ticket-Folder-Drop.ps1"
```

What it adds:

- Computes the default trailing two-week lock from `--pull-date`
- Runs `run_ticket_prep_pipeline.py` in BI folder mode
- Writes a small state file so a repeated scheduled run can no-op after a successful run for the same week

This is the easiest entrypoint to pair with Task Scheduler or a Power Automate file-drop flow.

If you are dropping Outlook emails instead of attachments, use the configured PowerShell launcher rather than calling the Python runner directly so the Outlook extraction step runs first.

## Full HR OE Pipeline

This pipeline builds the weekly answer pack focused on the Supplemental document's HR Operational Excellence questions.

It has three independent stages:

1. `hr_oe_weekly_analysis.py` builds the answer pack and metrics JSON.
2. `hr_oe_math_validator.py` recomputes key metrics from the source CSVs.
3. `hr_oe_quality_validator.py` checks section completeness and writing guardrails.

Use the orchestrator to run all three from the BI folder:

```powershell
python "Phase II\weekly_hr_oe\run_hr_oe_pipeline.py" `
  --phase1-dir "Phase I\Phase I CSV" `
  --phase2-bi-dir "OneDrive Ticket Drop" `
  --pull-date 2026-03-22 `
  --week8-start 2026-03-08 --week8-end 2026-03-14 `
  --week9-start 2026-03-15 --week9-end 2026-03-21 `
  --out-dir "Phase II\output" `
  --label "wk11_sun_sat_bi_locked"
```

Or use the configured launcher in this repo:

```powershell
powershell -ExecutionPolicy Bypass -File "04 - Workload Lens\ORBIT – HR Workload Lens\04 – Pipelines & Architecture\phase2-weekly-hr-oe\Run-Configured-HR-OE-BI.ps1"
```

That configured launcher also extracts BI attachments from any Outlook `.msg` emails found in the configured folder before it runs the full pipeline, then scans the default Outlook Inbox for the weekly ServiceDesk report emails.

Outputs:

- `Phase II/output/hr_oe_answer_pack_<label>.md`
- `Phase II/output/hr_oe_metrics_<label>.json`
- `Phase II/output/hr_oe_math_validation_<label>.json`
- `Phase II/output/hr_oe_quality_validation_<label>.json`
- `Phase II/output/hr_oe_pipeline_run_<label>.json`
- `Phase II/output/hr_oe_chat_handoff_<label>.md`

Important notes:

- Phase I auto-discovery prefers a filename containing both `snowflake` and `ukg`.
- Phase II BI mode reconstructs the service-specific CSVs automatically before analysis and validation.
- Cross phase coverage metrics are labeled as proxy values because ticket records and UKG touches are different units.
- Phase II metrics exclude WFM-owned queues by assignment group proxy until BI provides a true resolver or owning-team field.
- SLA commitment accuracy cannot be fully answered unless SLA-specific fields are present in the ticket source data.

## Legacy Four-File Mode

If BI or EPA ever sends service-specific files again, the old modes still work:

- `--attendance-csv`
- `--cs-time-attendance-csv`
- `--fc-general-inquiry-csv`
- `--timesheet-inquiry-csv`
- `--phase2-dir`

Those modes are preserved for backward compatibility, but the governed source model is now the weekly BI opened / closed folder.
