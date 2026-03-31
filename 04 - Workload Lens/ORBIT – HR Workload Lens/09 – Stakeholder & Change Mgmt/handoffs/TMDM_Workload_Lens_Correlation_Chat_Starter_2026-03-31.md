# TMDM Workload Lens Correlation Chat Starter

**Date:** 2026-03-31
**Purpose:** Start a focused Workload Lens discussion on how validated over-applied paycode defects relate to current HR tickets and timecard touches, how Daily People Pulse should reduce escalations by resolving defects faster, and how the new defect baseline can strengthen audit follow-up and upstream root-cause reduction.

## Executive Ask

I want to connect the validated TMDM Paycode Reconciler defect output to the Workload Lens workload story.

My working belief is that there is measurable correlation between:

- TMDM detected paycode defects
- Workload Lens Phase I UKG rework touches
- Workload Lens Phase I friction hours and historical corrections
- Workload Lens Phase II attendance and timecard ticket volume
- the gap between tickets and touches now described as dark work or Ticketed Rework Coverage %

This is the story I want to test and operationalize:

- today, the ORBIT paycode reconciler layered into Daily People Pulse for local HR and the standalone TMDM paycode reconciler for network-wide overages are giving us visibility into validated over-applied time-off defects
- those defects appear to be driving measurable downstream HR work, including timecard touches and some share of ticket demand
- when the ORBIT paycode reconciler is operating inside Daily People Pulse, I would expect fewer incidents to escalate into ticketed or higher-friction work, not because the defects stop happening, but because they are resolved faster at the site level
- once we have that operating motion in place, we can measure unresolved over-applied time by site and follow up with sites where the defect was visible in the paycode reconciler but the audit was not completed
- the biggest long-term value is still root-cause analysis so we can reduce the defect creation upstream

## Why This Matters Now

- The TMDM logic and edge cases have now been validated in Snowflake using data pulled from UKG.
- The latest validated TMDM sample output contains:
  - `1,480` defect rows
  - `1,176` unique employees
  - `1,077.4` total over-applied hours
- Latest root cause mix:
  - `Minor Over-Application`: `937`
  - `Meal Break (30 min) in Time-Off`: `525`
  - `Excess Time-Off Applied`: `16`
  - `AM/PM Miscoding (Likely)`: `1`
  - `AM/PM Miscoding (Possible)`: `1`
- Latest validation status mix:
  - `CLEAN`: `1,454` (`98.24%`)
  - `REVIEW`: `25` (`1.69%`)
  - `SUSPECT`: `1` (`0.07%`)
- The TMDM methodology document also records an `80/80` HITL validation sample and a `95.5%` exact lower confidence bound.

This gives us a credible baseline for unresolved over-applied time that can now be measured site by site instead of inferred indirectly from downstream workload.

## Early Overlap Signal

Workload Lens Phase II planning already identified ticket hotspots including `AVP2`, `AVP4`, `MCI1`, `AVP1`, `BNA1`, `RNO1`, `CLT1`, and `SDF4`.

Those same sites appear in the latest validated TMDM output with these defect counts:

| Site | TMDM Defect Rows |
| --- | ---: |
| `RNO1` | 127 |
| `AVP2` | 116 |
| `MCI1` | 96 |
| `CLT1` | 80 |
| `BNA1` | 80 |
| `AVP1` | 76 |
| `AVP4` | 30 |
| `SDF4` | 26 |

This is not proof by itself, but it is enough overlap to justify a formal site-week correlation study.

## Important Scope Note

- TMDM product docs currently describe `FC` and `Rx` as the initial production scope.
- The latest validated TMDM sample output currently contains rows classified to `FC`, `Rx`, `CC`, and `CVC`.
- Workload Lens already spans `FC`, `Rx`, `CC`, and `CVC`.

One of the first alignment questions for the new chat should be whether the correlation prototype should:

1. stay narrow and start with `FC` only
2. start with `FC` and `Rx`
3. use the broader validated sample exactly as-is

## Narrative To Test

1. The ORBIT paycode reconciler inside Daily People Pulse for local HR, together with the standalone TMDM paycode reconciler for network-wide overages, is identifying a validated defect population that is already contributing to measurable downstream HR rework and some portion of ticket demand.
2. After the ORBIT paycode reconciler is operationalized inside Daily People Pulse, escalated incidents related to over-applied time off should decline because sites are resolving the defects faster, not because the defects disappeared.
3. Site-level unresolved over-applied time should become a new audit management metric. If the defect was present in the paycode reconciler output and still remained unresolved, that creates a follow-up question for the site audit process.
4. Meal break defects will likely create a different workload pattern than PTO stacking or excess entries. Some may stay in dark work and never become tickets, while higher-severity defects may be more likely to convert into ticket or correction activity.
5. The highest-value outcome is not only detecting and clearing defects, but identifying repeat root causes so upstream process, RPA, or policy fixes can shrink the defect pool over time.

## Recommended V1 Analytical Grain

- `site x week`
- Shared join fields:
  - building or site code
  - business unit
  - locked Sunday through Saturday reporting week
- Start with site-week correlation before attempting employee-day or employee-ticket linkage

## Proposed V1 Merged Scorecard

Build one site-week table with these fields:

- `TMDM_DEFECT_ROWS`
- `TMDM_OVER_APPLIED_HRS`
- `TMDM_UNRESOLVED_OVER_APPLIED_HRS`
- `TMDM_UNIQUE_TMS`
- `TMDM_MINOR_ROWS`
- `TMDM_MEAL_BREAK_ROWS`
- `TMDM_EXCESS_ROWS`
- `PHASE1_TOTAL_TOUCHES`
- `PHASE1_REWORK_TOUCHES`
- `PHASE1_DEFECT_RATE_PCT`
- `PHASE1_FRICTION_HRS`
- `PHASE1_HIST_CORR_RATE_PCT`
- `PHASE2_ATTENDANCE_TIMECARD_TICKETS`
- `PHASE2_RESOLVED_RATE_PCT`
- `TICKETED_REWORK_COVERAGE_PCT`
- `AUDIT_COMPLETION_STATUS` or nearest available operational proxy
- `POST_DPP_ESCALATION_RATE` once Daily People Pulse deployment is live

Derived ratios to test:

- `TMDM defects per 100 TMs`
- `tickets per TMDM defect`
- `Phase I rework touches per TMDM defect`
- `TMDM over-applied hours per ticket`
- `unresolved over-applied hours per 100 TMs`
- `resolved before escalation %`

## Recommended First Analysis Cut

1. Build a locked site-week joined dataset for the overlapping time window.
2. Rank sites by TMDM defect rows, unresolved over-applied hours, Phase I rework touches, and Phase II ticket volume.
3. Run simple correlation checks at site-week grain.
4. Segment by root cause:
   - meal break
   - minor over-application
   - excess
   - AM/PM
5. Flag two special cases:
   - high TMDM defects with low tickets = likely dark work
   - high unresolved defect volume after visibility = likely audit follow-up issue
   - high tickets with low TMDM defects = likely non-paycode drivers
6. Once DPP is live, compare pre and post deployment behavior:
   - unresolved defect volume
   - escalated ticket volume
   - HR touch volume
   - time to resolution where available

## Questions To Answer In The New Chat

1. Should the first prototype be `FC` only because current ticket prep is strongest there, or should it include `Rx` and the broader sample?
2. Should TMDM live inside Workload Lens as a Section 4 cross-phase explanation, an audit follow-up metric, or both?
3. Should `Ticketed Rework Coverage %` be paired with a TMDM-oriented metric such as `Unresolved Over-Applied Time` or `Defects Resolved Before Escalation %`?
4. What is the cleanest first deliverable:
   - one exploratory merged dataset
   - one scorecard view
   - one one-off weekly analysis
   - or a durable metric added to the weekly answer pack

## Suggested Deliverables From The Team

- one merged site-week dataset
- one exploratory correlation summary
- one recommendation on where this belongs in the Workload Lens OBR narrative
- one recommendation on the best operating metrics for:
  - unresolved over-applied time
  - resolved before escalation
  - audit follow-up compliance
  - root-cause tracking

## Paste This Into A New Chat

I want to connect the ORBIT paycode reconciler and the TMDM Paycode Reconciler findings to the Workload Lens workload story. Workload Lens already looks at tickets and timecard touches. The ORBIT paycode reconciler is the local HR layer inside Daily People Pulse, and the standalone TMDM paycode reconciler captures network-wide defects in terms of overages.

The narrative I want to test is this: these validated over-applied time-off defects are driving measurable downstream work that we can already see in Workload Lens through HR touches and at least some share of ticket demand. When the ORBIT paycode reconciler is layered into Daily People Pulse, I would expect fewer incidents to escalate, not because the defects stop happening, but because they get resolved faster at the site level.

TMDM is now validated from Snowflake logic built on UKG-derived data. The latest validated output contains 1,480 defect rows, 1,176 unique employees, and 1,077.4 over-applied hours. The dominant root causes are Minor Over-Application (937) and Meal Break (30 min) in Time-Off (525). The methodology file also documents an 80/80 HITL validation sample and a 95.5% exact lower confidence bound.

This also gives us a new site-level audit baseline. I want to start measuring unresolved over-applied time by site and follow up when a defect was present in the paycode reconciler output but the audit was not completed. That improves our audit process because we now have a clear way to measure these defects directly instead of backing into them only from workload.

The bigger win is root-cause analysis so we can focus on upstream solutions that reduce the defect creation itself.

Please help design the cleanest site-week correlation prototype that joins TMDM defect counts and unresolved over-applied hours to Phase I rework touches, friction hours, historical corrections, and Phase II attendance/timecard ticket volume. I also want recommendations for the right operating metrics around unresolved defects, resolved before escalation behavior, audit follow-up, and root-cause tracking.

## Source Files To Reference

TMDM validation methodology:
`C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\ORBIT Products\03 - TMDM Paycode Reconciler\ORBIT – TMDM Paycode Reconciler\06 – Testing & QA\TMDM Validation & SPC Methodology.md`

TMDM validation artifact summary:
`C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\ORBIT Products\03 - TMDM Paycode Reconciler\ORBIT – TMDM Paycode Reconciler\06 – Testing & QA\Validation Artifacts, TMDM Paycode Reconciler.md`

TMDM validated sample output:
`C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\ORBIT Products\03 - TMDM Paycode Reconciler\ORBIT – TMDM Paycode Reconciler\06 – Testing & QA\test-data\final-training_data_reconciler_2026-03-31-1355.csv`

Workload Lens PRD:
`C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\ORBIT Products\04 - Workload Lens\ORBIT – HR Workload Lens\01 – Product Charter & PRD\PRD_Workload_Lens.md`

Workload Lens technical design:
`C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\ORBIT Products\04 - Workload Lens\ORBIT – HR Workload Lens\04 – Pipelines & Architecture\Technical_Design_Doc.md`

Phase II integration checklist:
`C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\ORBIT Products\04 - Workload Lens\ORBIT – HR Workload Lens\04 – Pipelines & Architecture\Phase_II_Integration_Checklist.md`

Ticket cleanup and classification standard:
`C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\ORBIT Products\04 - Workload Lens\ORBIT – HR Workload Lens\03 – Data Contract & Schema\Ticket_Cleanup_and_Classification_Standard.md`

Current HR OE review draft:
`C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\ORBIT Products\04 - Workload Lens\ORBIT – HR Workload Lens\08 – Metrics & WBR Artifacts\wbr-reports\hr_oe_exec_review_wk9.md`
