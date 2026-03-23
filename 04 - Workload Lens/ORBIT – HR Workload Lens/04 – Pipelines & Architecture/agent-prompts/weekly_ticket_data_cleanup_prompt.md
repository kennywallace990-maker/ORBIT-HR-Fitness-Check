# Weekly Ticket Data Cleanup Prompt

Use this prompt when you want an agent to prepare a new weekly ticket dataset for Workload Lens from the current BI delivery model.

Before running, replace the placeholders in angle brackets.

## Required References

- `Workload_Lens_Data_Handling_Policy.md`
- `run-contracts/ticket_weekly_run_contract.json`
- `Ticket_Cleanup_and_Classification_Standard.md`
- `..\phase2-weekly-hr-oe\build_ticket_bi_service_inputs.py`
- `..\phase2-weekly-hr-oe\run_ticket_prep_pipeline.py`

## Copy/Paste Prompt

```text
Prepare this week's Workload Lens ticket dataset.

You must follow these references before doing any work:
- Workload_Lens_Data_Handling_Policy.md
- run-contracts/ticket_weekly_run_contract.json
- Ticket_Cleanup_and_Classification_Standard.md

Prefer using the existing local pipeline if it is available:
- phase2-weekly-hr-oe/build_ticket_bi_service_inputs.py
- phase2-weekly-hr-oe/run_ticket_prep_pipeline.py

Task inputs:
- Rolling BI ticket folder: <PATH_TO_BI_OPENED_CLOSED_FOLDER>
- Pull date: <PULL_DATE_YYYY-MM-DD>
- Week 8 start: <WEEK8_START>
- Week 8 end: <WEEK8_END>
- Week 9 start: <WEEK9_START>
- Week 9 end: <WEEK9_END>
- Run label: <RUN_LABEL>
- Output root: <OUTPUT_ROOT>

Non-negotiable rules:
- Keep ticket data separate from UKG data.
- Land raw BI opened / closed files unchanged.
- Keep official prepared outputs separated by service.
- Do not merge raw rows across services.
- Controlled consolidation between the BI opened and closed reports is allowed only to reconstruct one canonical row per ticket within the same service.
- Exclude WFM-owned work using the current approved proxy rules unless a better governed field is supplied.
- Remove or suppress PII and noisy free text before any LLM-safe output is produced.
- Use deterministic classification and keep an audit trail.

Required outputs:
- bi_weekly_ticket_intake_manifest.json
- ticket_prep_manifest.json
- ticket_prep_rollup_for_llm.json
- ticket_prep_chat_handoff.md
- reconstructed per-service working CSVs
- per-service cleaned.csv
- per-service summary.json
- per-service llm_compact.json

Required cleaned columns:
- category
- rule_hit
- ukg_self_service_eligible
- could_have_been_self_service
- self_service_option
- self_service_rule_hit

Execution expectations:
1. Validate that the rolling BI folder contains the required weekly opened / closed files for Week 8 and Week 9.
2. Reconstruct service-specific working files from the selected BI reports.
3. Run the existing ticket prep pipeline when possible; otherwise apply equivalent deterministic processing manually.
4. Normalize headers and dates.
5. Remove HTML, signatures, out-of-office text, and obvious system noise when present.
6. Mask or remove PII before building LLM-safe artifacts.
7. Add deterministic self-service candidate fields using the approved UKG self-service capability list.
8. Keep outputs separated by service and create only a pointer-based rollup.
9. Report coverage warnings, row drops, selected raw BI files, service mismatches, and self-service candidate counts in the manifest and handoff.

At the end, return:
- whether the run passed
- which raw BI files were selected
- coverage warnings
- per-service output paths
- any unresolved blockers or data-quality risks
```
