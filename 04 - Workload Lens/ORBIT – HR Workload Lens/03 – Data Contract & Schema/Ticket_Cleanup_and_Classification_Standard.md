# Ticket Cleanup and Classification Standard

**Status:** Governed working standard  
**Version:** 2.0  
**Last Updated:** 2026-03-18  
**Purpose:** Define the repeatable, deterministic standard for landing, reconstructing, cleaning, scoping, classifying, and packaging weekly HR ticket extracts for Workload Lens now that BI delivers a weekly `opened last week` report and a weekly `closed last week` report instead of four service-specific files.

## Governing Position

This standard is the source-specific rulebook for HR ticket / ServiceNow preparation under Workload Lens.

It should be read together with:

- `Workload_Lens_Data_Handling_Policy.md`
- `run-contracts/ticket_weekly_run_contract.json`
- `weekly_ticket_data_cleanup_prompt.md`
- `build_ticket_bi_service_inputs.py`
- `run_ticket_prep_pipeline.py`
- `ticket_dataset_prepare.py`

If an ad hoc request conflicts with this standard, this standard wins unless an authorized product owner changes the governed rule.

## Scope

This standard applies to the weekly BI ticket source pair:

1. `cases opened last week`
2. `cases closed last week`

Those two source files are the governed landing artifacts. The official analytical scope inside those reports remains the same four tracked HR services:

1. Attendance Inquiry
2. CS Time and Attendance
3. FC General Inquiry
4. Timesheet Inquiry

Required scope rules:

- Raw weekly BI files must be landed unchanged as received.
- The prep flow must reconstruct service-specific working files from the raw weekly opened / closed reports before classification begins.
- No raw-row merge is allowed across ticket services in official prepared outputs.
- Controlled consolidation between the weekly `opened` and `closed` reports is allowed only to reconstruct one canonical record per ticket within the same tracked service.
- No raw-row merge is allowed with UKG data.
- WFM-owned ticket work is out of HR scope and must be removed before metrics are calculated.
- Current EPA / BI extracts still do not include a dedicated resolver or owning-team field, so WFM exclusion uses `Assignment Group` proxy rules.

## Non-Negotiable Rules

1. Weekly ticket prep must be deterministic and auditable.
2. Official categories must come from fixed rules, not probabilistic inference.
3. Free-text cleanup and PII suppression must happen before any LLM-safe artifact is produced.
4. `rule_hit` and `self_service_rule_hit` must preserve the audit trail for why a row was labeled.
5. Official outputs must preserve service separation even when a downstream rollup JSON is produced.
6. Official outputs must declare week boundaries and coverage warnings.
7. The BI intake layer must record which weekly opened / closed files were selected for the active run.

## BI Intake Model

The governed source model is now folder-based and cumulative.

Production expectation:

- Each Sunday, BI delivers one weekly `opened last week` file and one weekly `closed last week` file.
- Current Outlook delivery pattern is sender `ServiceDesk@chewy.com` with subjects `WBR Previous Week Open Cases` and `WBR Previous Week Resolved Cases`.
- Those files cover the prior completed Sunday-Saturday window.
- The raw intake folder should retain recent weekly files so the pipeline can reconstruct the required trailing two-week window.

For example:

- A delivery that arrives on Sunday `2026-03-22` should represent Sunday `2026-03-15` through Saturday `2026-03-21`.

The governed prep flow must therefore:

1. land the weekly opened / closed files unchanged
2. select the required Week 8 and Week 9 opened / closed files from the retained folder
3. rebuild service-specific working CSVs from those BI reports
4. run the deterministic cleanup and classification flow on those reconstructed service files

## Week Lock

Current baseline lock used in the active Phase II example set:

- Week 8: `2026-02-15` to `2026-02-21` (Sunday through Saturday)
- Week 9: `2026-02-22` to `2026-02-28` (Sunday through Saturday)

Production rule:

- `pull_date` is provided each run.
- The required trailing window is the two completed Sunday-Saturday weeks ending on the latest completed Saturday relative to `pull_date`.
- `week_bucket` must be assigned as `week8`, `week9`, or `outside`.

## Source File Expectations

The weekly source files may arrive as `.csv`, `.xlsx`, or `.xlsm`.

The filenames should identify report type clearly:

- `opened`
- `closed`
- `open cases`
- `resolved cases`

The prep layer may use filename hints to distinguish report types, but the governed date logic must come from the row data itself:

- `Opened At` style fields determine whether a file matches an `opened last week` window
- `Closed At` / `Resolved At` style fields determine whether a file matches a `closed last week` window

## Source Field Expectations

The extract may vary slightly by header name, but the standard expects the following canonical inputs:

| Canonical Field | Accepted Source Headers | Required |
|---|---|---|
| `Hr Service` | `Hr Service`, `Service`, `Ticket Type` | Yes |
| `Number` | `Number`, `Ticket Number`, `Case Number` | Yes, but a synthetic row id may be used if missing |
| `Opened At` | `Opened At`, `Opened`, `Created At` | Yes |
| `Assignment Group` | `Assignment Group`, `AssignmentGroup` | Yes |
| `Description1` | `Description1`, `Description`, `Short Description` | Yes |
| `U Resolved` | `U Resolved`, `Resolved At`, `Closed At`, `Closed` | Required for the `closed last week` file, optional for the `opened last week` file |

## Reconstruction Standard

Before classification begins, the BI intake layer must create service-specific working files from the weekly opened / closed source pair.

Required reconstruction rules:

1. Land each weekly BI report unchanged.
2. Select the required Week 8 and Week 9 opened / closed reports from the raw folder using row-level dates, not just filenames.
3. Read CSV as `utf-8-sig` and Excel files through a deterministic sheet reader.
4. Normalize headers to lowercase and compact internal whitespace.
5. Keep only the four tracked services.
6. Rebuild one canonical ticket row per ticket number within the same service.
7. When the same ticket appears in both the opened and closed reports:
   - keep one canonical row
   - preserve the earliest valid `Opened At`
   - preserve the latest valid `U Resolved` / `Closed At`
   - prefer richer non-empty text for `Assignment Group` and description fields
8. Emit one reconstructed working CSV per tracked service before classification.
9. Preserve intake provenance in the BI intake manifest.

## Cleanup Standard

After service-specific working files are reconstructed, the cleanup flow must run in this order:

1. Parse dates using deterministic format rules only.
2. Drop rows with missing or invalid `Opened At`.
3. Normalize description text by trimming edges and collapsing repeated whitespace.
4. Remove or suppress obvious noise before LLM packaging when present:
   - HTML
   - signatures
   - confidentiality footers
   - out-of-office text
   - automated system noise
5. Exclude WFM-owned queues using governed `Assignment Group` proxy rules.
6. Deduplicate within each service file using:
   - ticket number
   - opened timestamp
   - assignment group
   - normalized description
7. Extract `site` from `Assignment Group` using the fixed site rules below.
8. Compute `resolution_hours` when both timestamps exist and `resolved_at >= opened_at`.
9. Assign `week_bucket`.
10. Compute date coverage diagnostics:
   - minimum and maximum opened date in file
   - missing dates inside locked Week 8 and Week 9 windows
   - required trailing two-week range from `pull_date`

Deterministic date parsing is limited to the approved formats already used by the implementation:

- `MM/DD/YYYY`
- `MM/DD/YYYY HH:MM:SS`
- `MM/DD/YYYY HH:MM`
- `YYYY-MM-DD`
- `YYYY-MM-DD HH:MM:SS`

## WFM Scope Exclusion Rules

Until BI provides a true resolver or owning-team field, the following `Assignment Group` markers are treated as out of HR scope:

- `Real Time Analyst`
- `WFM`
- `Workforce Management`
- `NICE Operations`
- `Scheduling Team`

Rows matching these markers must be removed from HR reporting outputs and counted in data-quality diagnostics.

## Site Extraction Rules

`site` must be derived from `Assignment Group` using fixed rules in this order:

1. Empty value -> `UNKNOWN`
2. Contains `SDF 1/4/6` -> `SDF-CAMPUS`
3. Contains `TEAM MEMBER SERVICE CENTER` -> `TMSC`
4. Contains `LOA/ADA` -> `LOA-ADA`
5. Contains `PAYROLL` -> `PAYROLL`
6. Regex match `\b([A-Z]{3,4}\d{1,2}[A-Z]?)\b` -> matched site code such as `CLT1` or `AVP2`
7. Otherwise -> `CENTRALIZED`

## TM Self-Service Reference

Use the following list as the current approved definition of UKG and timeclock self-service that should be routed away from HR whenever the tool or process allows:

- Clock in / clock out at a timeclock or via the app
- View current timecard for the pay period
- Edit or submit a missed punch or forgot-to-punch request
- Submit timecard corrections or edits for manager approval
- View punch history and punch detail (location, device, timestamps)
- Confirm or acknowledge punches when the device/app prompts
- View published schedule and future shifts
- View time off balances and accruals
- View status of submitted requests (timecard edits, PTO, etc)
- Get notifications of approvals, denials, or required actions

## Self-Service Candidate Attribution

After cleanup, each row must be evaluated for whether the request could have been handled through existing UKG self-service.

This attribution is deterministic and conservative:

1. Use normalized description text only.
2. Apply fixed self-service rules in first-match-wins order.
3. Do not mark a row as self-service when the resolved category is outside the approved self-service scope.
4. Only mark `ukg_self_service_eligible = yes` when the ticket text clearly maps to an approved option from the list above.
5. Store:
   - `ukg_self_service_eligible`
   - `could_have_been_self_service`
   - `self_service_option`
   - `self_service_rule_hit`
6. `could_have_been_self_service` is a backward-compatible alias of `ukg_self_service_eligible`.
7. If no deterministic rule matches, store:
   - `ukg_self_service_eligible = no`
   - `could_have_been_self_service = no`
   - empty `self_service_option`
   - `self_service_rule_hit = not_self_service_candidate`

The following categories are excluded from self-service eligibility by default:

- I-9 / Onboarding / Compliance Docs
- Pay Discrepancy / Missing Pay
- Leave of Absence / FMLA / LOA
- Suspension / Termination / Discipline / TM Relations
- Transfer / Job Change / Position
- Benefits / Enrollment / Payroll
- VTO / VET / Voluntary Time
- Badge / Access / IT / Workday
- Personal Info / Verification / Records
- Noise / Spam / Auto-Generated Junk
- Other / Unclassified
- Empty / No Description

## Classification Standard

Classification is deterministic and auditable. No probabilistic inference is allowed in the official weekly metrics flow.

Required sequence:

1. Normalize description text to lowercase.
2. If the normalized description is empty, assign `Empty / No Description`.
3. Apply first-match-wins keyword rules in fixed order.
4. Store both:
   - `category`
   - `rule_hit`
5. Apply deterministic self-service candidate rules after category assignment.
6. Flag noise rows with `is_noise = yes` only when the category is `Noise / Spam / Auto-Generated Junk`.
7. Unmatched non-empty rows go to `Other / Unclassified` with `rule_hit = fallback`.

## Category Set

- I-9 / Onboarding / Compliance Docs
- Pay Discrepancy / Missing Pay
- PTO / Time-Off Balance
- Leave of Absence / FMLA / LOA
- Attendance / Call-Off / NCNS
- Timecard / Punch / Schedule
- Suspension / Termination / Discipline / TM Relations
- Transfer / Job Change / Position
- Benefits / Enrollment / Payroll
- VTO / VET / Voluntary Time
- Badge / Access / IT / Workday
- Personal Info / Verification / Records
- Noise / Spam / Auto-Generated Junk
- Other / Unclassified
- Empty / No Description

## Cleaned Output Contract

Per-service cleaned ticket outputs must include these fields:

| Field | Meaning |
|---|---|
| `service_name` | Logical ticket service name |
| `ticket_number` | Canonical ticket id or deterministic synthetic fallback |
| `opened_at` | Parsed opened timestamp |
| `resolved_at` | Parsed resolved timestamp when available |
| `opened_date` | ISO date derived from `opened_at` |
| `week_bucket` | `week8`, `week9`, or `outside` |
| `assignment_group` | Queue value used for scope and site logic |
| `site` | Derived site or centralized bucket |
| `category` | Deterministic classification category |
| `rule_hit` | Keyword or fallback marker that triggered the category |
| `ukg_self_service_eligible` | `yes` or `no` |
| `could_have_been_self_service` | Alias of `ukg_self_service_eligible` |
| `self_service_option` | Approved self-service capability when matched |
| `self_service_rule_hit` | Rule evidence for the self-service assignment |
| `is_noise` | `yes` or `no` |
| `resolution_hours` | Hours from opened to resolved when valid |
| `description_clean` | Normalized analytical description text |

At minimum, downstream consumers must be able to rely on these derived fields:

- `category`
- `rule_hit`
- `ukg_self_service_eligible`
- `could_have_been_self_service`
- `self_service_option`
- `self_service_rule_hit`
- `is_noise`

## Summary and Compact Output Requirements

Each service must emit:

- `<service>_cleaned.csv`
- `<service>_summary.json`
- `<service>_llm_compact.json`

The summary output should include:

- `data_quality`
- `date_coverage`
- Week 8 and Week 9 ticket counts
- resolution metrics
- category counts
- self-service counts and percentages
- WoW category deltas
- top Week 9 sites

The compact LLM-safe output should remain token-efficient and include only minimized evidence:

- Week 8 and Week 9 KPIs
- top Week 9 categories
- top self-service options
- top sites
- largest WoW category deltas
- truncated evidence samples
- date coverage summary
- explicit limitations

## LLM Token Control Strategy

The LLM does not ingest full raw CSV rows by default. It receives compact artifacts:

1. Per-service `llm_compact.json` with minimized KPIs and limited evidence samples.
2. `ticket_prep_rollup_for_llm.json` with pointers to each service compact file.
3. `ticket_prep_chat_handoff.md` for human-readable run context.
4. Full cleaned CSV only for drill-down or validator use when needed.

The following are not allowed as default LLM inputs:

- raw source BI files
- raw CSV files
- unredacted free text
- merged raw ticket rows
- blended ticket and UKG rows

## Weekly Control Checks

Every run should report, at minimum:

1. Selected raw opened / closed BI report paths for Week 8 and Week 9
2. Missing-opened-date rate
3. Dedupe removal count
4. WFM exclusion count and excluded assignment groups
5. Week 8 and Week 9 ticket counts
6. Locked-window and required-window coverage
7. Top category drift WoW
8. Noise ratio
9. Self-service candidate count and percentage

## Outcome Standard

A valid weekly ticket prep run leaves behind:

- the original raw weekly opened / closed files unchanged
- an intake manifest that shows which weekly BI files were selected
- reconstructed service-specific working CSVs for the tracked services
- a cleaned analytical dataset for each service
- deterministic category and self-service fields with audit markers
- structured JSON outputs for downstream reasoning
- explicit coverage and data-quality diagnostics

That is the minimum bar for Workload Lens ticket preparation.
