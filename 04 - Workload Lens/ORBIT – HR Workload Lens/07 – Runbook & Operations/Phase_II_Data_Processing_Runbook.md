# Phase II ServiceNow Data Processing Runbook

**Date:** 2026-03-23  
**Context:** This runbook defines the current weekly operating procedure for Workload Lens after production validation of the Outlook-driven BI intake, the manual Phase I UKG prerequisite, and calendar-week labeling in the final outputs.

---

## 1. Current Operating Model

The weekly operating truth is now:

1. Phase I UKG data is still a manual prerequisite. The analyst must download the weekly UKG raw CSV and refresh the Phase I compatibility file before the full cross-phase run.
2. Phase II ticket intake is automated from the configured OneDrive folder and from the default Outlook Inbox.
3. The governed ticket source is a rolling pair of weekly BI files:
   - `WBR Previous Week Open Cases`
   - `WBR Previous Week Resolved Cases`
4. The reporting window is always Sunday through Saturday.
5. The pipeline compares the two most recent completed weeks relative to the selected pull date.
6. Final outputs are labeled by the actual calendar week number.

Example:

- Week 10 = `2026-03-08` to `2026-03-14`
- Week 11 = `2026-03-15` to `2026-03-21`

Configured ticket drop folder for this workspace:

`C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Workload Lens Incoming ticket bi drop`

Configured Phase I compatibility CSV location:

`C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\ORBIT Products\04 - Workload Lens\Phase I\Phase I CSV\Snowflake UKG data.csv`

---

## 2. Weekly Owner Checklist

### Step 0: Refresh the manual Phase I UKG input

This step is intentionally manual and is not a Phase II automation failure if it has not been done yet.

Required action:

1. Download the prior-week UKG raw CSV.
2. Keep at least the last two completed weekly raw UKG files available so the trailing two-week comparison can be rebuilt.
3. Refresh the compatibility CSV used by the weekly pipeline.

Helper command:

```powershell
python "04 - Workload Lens\ORBIT – HR Workload Lens\04 – Pipelines & Architecture\phase2-weekly-hr-oe\build_manual_phase1_ukg_csv.py" `
  --input "C:\Users\kwallace12\Downloads\prior_week_1.csv" `
  --input "C:\Users\kwallace12\Downloads\prior_week_2.csv" `
  --output "C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\ORBIT Products\04 - Workload Lens\Phase I\Phase I CSV\Snowflake UKG data.csv"
```

Operational notes:

- The helper produces the de-identified compatibility CSV used by the Phase II weekly pipeline.
- This output is sufficient for the current cross-phase reporting flow.
- If Phase I has not been refreshed yet, the full HR/OE pipeline can still be run with `--allow-partial-phase1` or `-AllowPartialPhase1` for ticket-only validation, but that is a fallback path rather than the weekly target state.

### Step 1: Run the automated ticket intake

Use the configured launcher:

```powershell
powershell -ExecutionPolicy Bypass -File "04 - Workload Lens\ORBIT – HR Workload Lens\04 – Pipelines & Architecture\phase2-weekly-hr-oe\Run-Configured-Ticket-Folder-Drop.ps1"
```

What this launcher does:

1. Reads direct BI files already in the configured OneDrive drop folder.
2. Extracts `.csv`, `.xlsx`, and `.xlsm` attachments from any Outlook `.msg` files already dropped into that folder.
3. Scans the default Outlook Inbox for the weekly ServiceDesk report emails.
4. Extracts allowed BI attachments from Outlook into the configured OneDrive drop folder.
5. Prefixes generic attachment filenames with `open_cases_` or `resolved_cases_` when the email subject provides the classification cue.
6. Moves processed `.msg` files into `_processed_msg`.
7. Selects the trailing two completed weeks from the landing folder.
8. Reconstructs the tracked service-specific working CSVs.
9. Runs cleanup, exclusion, dedupe, classification, and self-service logic.
10. Writes the ticket prep artifacts and the folder-drop state file.

Observed Outlook pattern in production:

1. sender `ServiceDesk@chewy.com`
2. subject `WBR Previous Week Open Cases`
3. subject `WBR Previous Week Resolved Cases`

### Step 2: Verify ticket intake success

Check these artifacts first:

- `C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\ORBIT Products\04 - Workload Lens\Phase II\output\ticket_prep\ticket_folder_drop_state.json`
- `C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\ORBIT Products\04 - Workload Lens\Phase II\output\ticket_prep\<run_dir>\ticket_prep_chat_handoff.md`

Confirm:

1. the run selected the correct two weekly BI pairs
2. the covered dates match the intended Sunday-Saturday windows
3. the run status is successful or already processed
4. the cleaned service outputs exist

`already_processed` on a repeated run for the same successful week is expected behavior, not an error.

### Step 3: Run the full HR Operational Excellence pipeline

Use the configured launcher:

```powershell
powershell -ExecutionPolicy Bypass -File "04 - Workload Lens\ORBIT – HR Workload Lens\04 – Pipelines & Architecture\phase2-weekly-hr-oe\Run-Configured-HR-OE-BI.ps1"
```

Use the fallback only if the manual Phase I refresh has not happened yet:

```powershell
powershell -ExecutionPolicy Bypass -File "04 - Workload Lens\ORBIT – HR Workload Lens\04 – Pipelines & Architecture\phase2-weekly-hr-oe\Run-Configured-HR-OE-BI.ps1" -AllowPartialPhase1
```

What this launcher does:

1. Re-runs the same Outlook and folder extraction logic used by the ticket intake launcher.
2. Auto-discovers the Phase I compatibility CSV in `Phase I\Phase I CSV`.
3. Reconstructs Phase II BI inputs when needed.
4. Runs weekly analysis, math validation, and quality validation.
5. Writes the answer pack, metrics JSON, chat handoff, and pipeline run manifest.

### Step 4: Review and publish the weekly outputs

Primary deliverables:

- `C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\ORBIT Products\04 - Workload Lens\Phase II\output\hr_oe_answer_pack_<label>.md`
- `C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\ORBIT Products\04 - Workload Lens\Phase II\output\hr_oe_metrics_<label>.json`
- `C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\ORBIT Products\04 - Workload Lens\Phase II\output\hr_oe_chat_handoff_<label>.md`
- `C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\ORBIT Products\04 - Workload Lens\Phase II\output\hr_oe_pipeline_run_<label>.json`

Review expectations:

1. week labels should reflect the real calendar week, not a placeholder compare slot
2. Week 10 and Week 11 should map to the correct Sunday-Saturday dates
3. Phase I coverage should be fully locked unless partial mode was used intentionally
4. the answer pack should be the source of truth for the weekly business readout

---

## 3. Required Ticket Fields and Aliases

The ticket intake accepts `.csv`, `.xlsx`, and `.xlsm` BI sources.

Minimum required business fields:

1. service field:
   - `Hr Service`
   - `hr_service`
2. ticket identifier:
   - `Number`
   - `number`
3. ticket description:
   - `Description1`
   - `description`
   - `short_description`
4. opened timestamp:
   - `Opened At`
   - `opened_at`
5. resolved or closed timestamp:
   - `U Resolved`
   - `Resolved At`
   - `Closed At`
   - `resolved_at`
   - `closed_at`
6. assignment group:
   - `Assignment Group`
   - `assignment_group`

The resolved or closed file must contain a valid resolved or closed timestamp so the weekly selection and enrichment logic can lock the correct reporting window.

---

## 4. Expected Ticket Intake Outputs

The ticket prep run writes:

- `bi_weekly_ticket_intake_manifest.json`
- `ticket_prep_manifest.json`
- `ticket_prep_rollup_for_llm.json`
- `ticket_prep_chat_handoff.md`
- reconstructed service CSVs from the BI weekly files
- per-service cleaned CSVs
- per-service summary JSON
- per-service compact JSON
- `ticket_folder_drop_state.json`

The full HR/OE run writes:

- `hr_oe_answer_pack_<label>.md`
- `hr_oe_metrics_<label>.json`
- `hr_oe_math_validation_<label>.json`
- `hr_oe_quality_validation_<label>.json`
- `hr_oe_pipeline_run_<label>.json`
- `hr_oe_chat_handoff_<label>.md`

---

## 5. Weekly Control Checks

Every weekly run should confirm:

1. which opened and resolved BI files were selected for the two completed weeks
2. the exact date windows selected by the prep step
3. missing-opened-date rate
4. dedupe removal count
5. WFM exclusion count and excluded assignment groups
6. per-service ticket counts for both weeks
7. full Phase I required-range coverage for the same weeks
8. week-over-week category movement
9. self-service candidate count and percentage
10. that the published week labels match the actual calendar week numbers

---

## 6. Failure Triage

If ticket intake fails with `No BI weekly ticket files were discovered`:

1. confirm the weekly ServiceDesk emails actually landed in Outlook Inbox
2. confirm the configured OneDrive drop folder is reachable
3. confirm the attachments were saved as `.csv`, `.xlsx`, or `.xlsm`
4. confirm the filenames or email subjects still contain open or resolved cues

If the full run fails required-range validation for Phase I:

1. treat it as a missing manual UKG refresh, not a Phase II automation failure
2. rebuild `Snowflake UKG data.csv` from the latest two weekly raw UKG files
3. rerun the full launcher without partial mode

If a repeated scheduled run reports `already_processed`:

1. treat it as expected behavior if the same successful week was already locked
2. verify the existing outputs rather than forcing a duplicate rerun

---

## 7. Operational Caveats

1. Week boundaries are always Sunday through Saturday.
2. Phase I UKG remains a manual prerequisite until that feed is automated separately.
3. WFM-owned queues are excluded by `Assignment Group` proxy until BI provides a true resolver or owning-team field.
4. The ticket folder should retain at least the last two weekly BI pairs so the active comparison window can be rebuilt.
5. If BI changes column headers again, update the intake aliases before treating the run as production-safe.
