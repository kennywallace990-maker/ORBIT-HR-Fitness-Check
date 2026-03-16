# Ticket Cleanup and Classification Standard

## Scope

This standard applies to the 4 EPA ticket files:

1. Attendance Inquiry
2. CS Time and Attendance
3. FC General Inquiry
4. Timesheet Inquiry

Raw files remain separated. No raw-row merge is allowed.
WFM-owned ticket work is out of HR scope and must be removed before metrics are calculated. Current EPA extracts do not include a dedicated resolver field, so the exclusion uses `Assignment Group` proxy rules.

## Week Lock

- Week 8: `2026-02-15` to `2026-02-21` (Sunday through Saturday)
- Week 9: `2026-02-22` to `2026-02-28` (Sunday through Saturday)
- Pull date is provided each run. Required trailing window is the two completed Sunday-Saturday weeks ending on the latest completed Saturday relative to pull date.

## Cleanup Steps

1. Read CSV as `utf-8-sig` to safely handle BOM headers.
2. Normalize headers to lowercase and compact whitespace.
3. Validate required fields:
   - `Hr Service`
   - `Number`
   - `Opened At`
   - `Assignment Group`
   - `Description1`
   - `U Resolved` (optional for open tickets)
4. Parse dates using deterministic format rules only.
5. Drop rows with missing/invalid `Opened At`.
6. Normalize description text:
   - trim edges
   - collapse repeated whitespace
7. Exclude WFM-owned queues using `Assignment Group` proxy rules:
   - any `Real Time Analyst*` queue
   - any queue with `WFM` / Workforce Management naming
8. Dedupe rows within the file using:
   - ticket number
   - opened timestamp
   - assignment group
   - normalized description
9. Extract site code from `Assignment Group` with fixed rules:
   - explicit handling for `SDF 1/4/6`
   - direct code extraction for patterns like `CLT1`, `AVP2`
   - centralized fallback for non-site queues
10. Compute `resolution_hours` when both timestamps exist and end >= start.
11. Assign `week_bucket`:
    - `week8`
    - `week9`
    - `outside`
12. Compute date coverage diagnostics:
    - min and max opened date in file
    - missing dates inside locked Week 8 and Week 9 windows
    - required trailing two-week range from pull date

## TM Self-Service Reference

Use the following list as the current definition of UKG and timeclock self-service that should be routed away from HR whenever the tool or process allows:

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

## Classification Steps

Classification is deterministic and auditable. No probabilistic inference.

1. Normalize description text to lowercase.
2. Apply first-match-wins keyword rules in fixed order.
3. Store both:
   - `category`
   - `rule_hit` (keyword or fallback marker)
4. Flag noise category rows with `is_noise = yes`.
5. Unmatched rows go to `Other / Unclassified`.

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

## LLM Token Control Strategy

The LLM does not ingest full raw CSV rows by default. It receives compact artifacts:

1. Per-service `llm_compact.json` with:
   - Week 8 and Week 9 KPIs
   - Top categories and site concentrations
   - Largest WoW category deltas
   - Limited evidence samples with truncated text
2. `ticket_prep_rollup_for_llm.json` with pointers to each service compact file.
3. Full cleaned CSV remains available for drill-down only when needed.

## Outputs Per Service

- `<service>_cleaned.csv`
- `<service>_summary.json`
- `<service>_llm_compact.json`

## Weekly Control Checks

1. Missing-opened-date rate
2. Dedupe removal count
3. Week 8 and Week 9 ticket counts
4. Top category drift WoW
5. Noise ratio
