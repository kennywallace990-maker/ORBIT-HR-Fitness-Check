# PRD, TMDM Paycode Reconciler

| Field | Value |
| --- | --- |
| **Product** | TMDM Paycode Reconciler |
| **Platform** | ORBIT Phoenix |
| **Product Owner** | Kenny Wallace |
| **TMDM Sponsor** | Jen Hudson |
| **Validation Partners** | Ashley Bushwood, Ashley Greene |
| **Version** | 1.0 |
| **Last Updated** | 2026-03-03 |
| **Status** | Pilot validated; pending productionization decision |

---

## 1. Executive Summary

TMDM Paycode Reconciler is an ORBIT Phoenix agent that automates and prioritizes enterprise timecard audit workflows for non-exempt team members across FC, Rx, CC, and Other networks. It detects over-applied time-off paycodes (with emphasis on PTO) by comparing scheduled hours to applied time-off and actual worked hours across a rolling two-week window — the previous week through the current week, where weeks are defined Sunday through Saturday. The product converts a manual, reactive "scavenger hunt" in UKG into a proactive, prioritized review list that reduces audit effort and payroll defects before payroll close.

TMDM currently spends about **22 hours per week** manually auditing roughly **19,000 rows** of UKG data to identify situations where more time-off paycodes were applied than appropriate and time refunds are required prior to payroll closure. The TMDM Paycode Reconciler has been piloted in production-like conditions and has already surfaced defects that the legacy UKG report does not expose, while indicating a potential reduction in TMDM audit effort of approximately **60%**.

---

## 2. Audience

### Primary

- **HR Shared Services (HRSS) — Team Member Data Management (TMDM) COE** — primary users and business owners of the audit workflow.
- **Local HR partners / Field HR** — consumers of insights and downstream remediation stakeholders for paycode corrections in partnership with TMDM.
- **Payroll** — partner in preventing and resolving payroll defects related to over-applied time-off paycodes.

### Secondary

- **Enterprise People Analytics** — enablement partner for insights, metrics, and continuous improvement.
- **Phoenix / ORBIT product and engineering teams** — accountable for data pipeline, report logic, and user experience.

---

## 3. Purpose

Define the requirements, scope, experience, data flows, and success measures for the TMDM Paycode Reconciler ORBIT Phoenix product. This document aligns TMDM, HRSS, Payroll, Enterprise People Analytics, and Phoenix / ORBIT on what the product must deliver to reliably detect and prioritize over-applied time-off paycodes for enterprise timecards, enabling pre-payroll correction and reducing rework.

---

## 4. Partnership / Stakeholders

| Partner | Role |
| --- | --- |
| **TMDM COE** | Business owner, primary user, and sponsor. Defines business rules and validates output quality. |
| **HRSS and Field HR** | Downstream partners for implementing corrections in coordination with TMs and people leaders. |
| **Payroll** | Partner for understanding defect patterns, validating impact on rework and refunds, and supplying ticket / correction data for ROI measurement. |
| **Enterprise People Analytics** | Partner for Snowflake data models, paycode mapping, and metric design. |
| **Phoenix / ORBIT Product** | Owns the ORBIT report definition, experience design, prioritization logic, and enhancements. |

---

## 5. Background / Problem Statement

TMDM is accountable for ensuring that enterprise non-exempt timecards reflect accurate time worked and appropriate application of time-off paycodes prior to payroll close. For FC and Rx populations (with CC and Other as secondary), this requires auditing a large volume of timecard data each pay period.

### Current State

- TMDM spends approximately **22 hours per week** auditing around **19,000 rows** of UKG data to identify situations where time-off paycodes (PTO, Personal Unpaid, Intermittent Leave, etc.) have been over-applied and time refunds are required before payroll closure.
- The process begins by opening UKG Pro, running a report, and exporting to CSV. This report **does not show the type of time-off used**, preventing TMDM from meaningfully prioritizing cases.
- Because the report cannot distinguish between paycode-driven issues and benign situations (such as a TM clocking in early or staying late), TMDM spends significant time manually filtering, sorting, and reviewing individual timecards that may not need intervention.
- TMDM then manually reviews timecards one by one in UKG, creating a "scavenger hunt" workflow with high effort and risk of missed issues.

### Consequences

- Over-applied PTO and related paycodes lead to payroll defects when TMs are paid for time-off that should not have been applied, requiring time refunds or corrective actions after payroll close.
- Post-payroll rework involves field HR, the TM, TMDM, and Payroll, consuming time and introducing operational friction.
- The existing UKG-based report does not surface all relevant defects. In pilot testing, TMDM observed that some over-applied paycode issues identified by the Paycode Reconciler did not appear on the legacy UKG report at all.

### Problem Statement

> TMDM lacks an efficient, enterprise-scale, and paycode-aware mechanism to proactively detect and prioritize over-applied time-off paycodes on timecards prior to payroll close, leading to high audit effort, missed defects, and multi-team rework after payroll closure.

---

## 6. Phases and Data Sources

### Phase 1: Proof of Concept (Pilot) — Complete

- Rapidly validated that Phoenix can reliably identify over-applied time-off paycodes at scale using Snowflake-sourced UKG data.
- Designed a minimal, high-value ORBIT view tailored to TMDM workflows.
- Pilot report scanned the previous week through the current week, with weeks defined Sunday through Saturday, and surfaced defects the legacy UKG report missed.
- TMDM confirmed the report correctly prioritized cases with PTO-related risk.

### Phase 2: Productionization for FC and Rx — In Progress

- Hardened Phoenix / ORBIT agent with defined data refresh cadence aligned to payroll processing windows.
- Validated paycode mappings for all 17 in-scope paycodes (see Section 9).
- Configurable filters for FC, Rx, CC, and Other networks, plus location and supervisor segmentation.

### Phase 3: Expansion — Future

- Extend to additional paycode types or populations based on ROI validation.
- Integrate Payroll ticket data for pre- vs. post-payroll defect measurement.
- Evaluate automated routing of defects to specific TMDM reps or field HR.

---

## 7. Objectives

1. Reduce TMDM time spent on weekly enterprise timecard audits by automating detection and prioritization of over-applied time-off paycodes.
2. Identify and surface paycode-related payroll risks (especially PTO over-application) before payroll close, enabling proactive correction rather than reactive rework.
3. Improve coverage and accuracy of paycode reconciliation beyond what is possible with the current UKG report, ensuring that timecards with issues are not omitted from review lists.
4. Provide a structured, single-touch workflow that enables TMDM reps to open each TM's timecard once per pay period and complete all needed adjustments.

---

## 8. Data and Insight Lifecycle (EDA Loop)

### Observe

- Phoenix queries three Snowflake gold-layer UKG views (`GOLD_V_PEOPLE`, `GOLD_V_SCHEDULE_TOTAL`, `GOLD_V_TIMECARD_TOTAL`) for a rolling two-week window — the previous week through the current week, where weeks are defined Sunday through Saturday.
- The query computes relationships between scheduled hours, actual worked hours, and applied time-off paycode hours per team member per day.

### Diagnose

- The reconciliation logic flags team members where `time_off_applied > MAX(0, scheduled_hours - worked_hours)`, producing the `over_applied_hours` metric.
- PTO-specific over-application (`pto_over_applied_hours`) is calculated separately for prioritization.
- Risk classification: **High Priority** when over-applied hours >= 4; **Standard** otherwise.

### Act

- TMDM reps use the Phoenix / ORBIT agent as a work queue, sorted by PTO over-application (descending), then alphabetically by name, then by date.
- Each row provides the specific paycodes and recommended reduction amount so the TMDM rep can open UKG once per TM and make all corrections.

---

## 9. In-Scope Paycodes

The reconciliation query uses 17 paycodes organized into two categories:

### Work Paycodes (used to calculate actual worked hours)

| Pay Code ID | Pay Code Name | Description |
| --- | --- | --- |
| 466 | Regular | Standard regular hours |
| 601 | Overtime | Standard overtime |
| 2402 | Overtime $1.50 | Premium overtime tier |
| 2503 | Overtime $2.00 | Premium overtime tier |
| 2651 | Overtime $2.50 | Premium overtime tier |
| 2153 | Overtime $3.00 | Premium overtime tier |
| 2004 | Overtime $5.00 | Premium overtime tier |

### Time-Off Paycodes (checked for over-application)

| Pay Code ID | Pay Code Name | Is PTO | Risk Category |
| --- | --- | --- | --- |
| 479 | PTO PAID | Yes | High — direct overpayment risk |
| 480 | PTO PAID PTO Sick | Yes | High — direct overpayment risk |
| 481 | Vet Care - PTO PAID | Yes | High — direct overpayment risk |
| 1002 | Intermittent Leave PTO | Yes | High — leave + overpayment risk |
| 503 | Customer Service PTO - VTO | Yes | High — direct overpayment risk |
| 473 | Personal UNPAID | No | Medium — compliance concern |
| 474 | Personal UNPD Call Off | No | Medium-High — NCNS indicator |
| 1001 | Intermittent Leave-Unpaid | No | Medium — FMLA/leave related |
| 3402 | TMDM Intermittent Leave | No | Medium — TMDM-specific leave code |
| 3251 | Customer Care Total VTO | No | Low — VTO-specific |

---

## 10. Scope

### In Scope

- All non-exempt, non-terminated team members across FC, Rx, CC, and Other networks (exempt employees are excluded via `schedule_group <> 'Exempt'`).
- Detection of over-applied time-off paycodes for all 10 time-off paycodes listed above.
- Comparison of scheduled eligible hours versus actual worked hours versus applied time-off hours for the previous week through the current week, with weeks defined Sunday through Saturday.
- Phoenix / ORBIT agent experience for TMDM with natural-language prompts, filters, risk indicators, and prioritized review lists.

### Out of Scope

- Automation of corrections directly in UKG. TMDM and HR will continue to make updates in UKG manually.
- ServiceNow or other workload forecasting content not related to paycode reconciliation.
- Paycode types beyond the 17 defined above until business rules are validated.

---

## 11. High-Level Experience

The TMDM Paycode Reconciler is exposed as a conversational ORBIT Phoenix agent that functions as a prioritized work queue for TMDM reps. The experience is optimized for weekly audit cycles aligned to payroll deadlines.

### User Journey — TMDM Rep

1. Opens the Phoenix / ORBIT agent and types a natural-language prompt (e.g., "Show me defects that need attention").
2. Applies filters via follow-up prompts (network, location, supervisor, risk level, specific paycodes) to focus on the highest-risk population.
3. Views a table with business unit, date, scheduled hours, worked hours, applied time-off, paycodes detail, over-applied hours, recommendation, root cause, and schedule anomaly indicators.
4. Opens each flagged TM's timecard in UKG **once** per pay period and makes all needed corrections using the report data.
5. Monitors progress by re-querying; corrected timecards drop off after the next data refresh.

### User Journey — HR and Payroll Partners

- HR partners reference the report to identify coaching or process opportunities for specific locations or roles.
- Payroll aligns correction windows with report refresh timing.

---

## 12. Feature Table

| Feature | Description | Primary User Value |
| --- | --- | --- |
| **Paycode Over-Application Detection** | Detects cases where applied time-off paycodes exceed `MAX(0, scheduled - worked)` for non-exempt TMs using 17 defined paycodes. | Directly targets timecards with over-applied time-off instead of manual sifting. |
| **Rolling Two-Week Risk View** | Surfaces risk across the previous week and current week, where weeks are defined Sunday through Saturday, ensuring both weeks are visible in a single view. | Proactive correction before payroll close. |
| **PTO Risk Prioritization** | Calculates `pto_over_applied_hours` separately and sorts output by PTO risk descending. | Focuses TMDM on highest payroll impact first. |
| **Alphabetical Single-Touch Workflow** | Within risk tiers, lists TMs alphabetically with all defect dates grouped, enabling one UKG visit per TM. | Eliminates redundant timecard visits. |
| **Network / Location / Supervisor Filters** | Natural-language filters powered by cohort classification (FC, Rx, CC, Other), `job_transfer_set`, and `supervisor_full_name`. | Scopes work to relevant populations. |
| **Conversational Agent Interface** | 16-prompt library covering retrieval, filtering, KPIs, root cause, tenure, day-of-week, comparison, export, and help. | No SQL knowledge required; plain English. |

## 13. Reconciliation Logic

The core reconciliation formula (from the production SQL):

```text
over_applied_hours = MAX(0, timeoff_applied - MAX(0, scheduled_eligible - worked))
```

Where:
 
- `scheduled_eligible` = sum of hours from schedule_totals for all 17 eligible paycodes (work + time-off)
- `worked` = sum of hours from timecard_totals for the 7 work paycodes only
- `timeoff_applied` = sum of hours from timecard_totals for the 10 time-off paycodes only

PTO-specific over-application:

```text
pto_over_applied_hours = MAX(0, pto_hours_applied - MAX(0, scheduled_eligible - worked))
```

### Risk Classification

| Risk Level | Rule | Recommendation Format |
| --- | --- | --- |
| **High** | `over_applied_hours >= 4` | "Reduce time-off by X hrs - HIGH PRIORITY" |
| **Standard** | `over_applied_hours > 0 AND < 4` | "Review and reduce time-off by X hrs" |

### Network Classification

Derived from `GOLD_V_PEOPLE.primary_org_path_txt` and `job_transfer_set`:

| Cohort | Rule |
| --- | --- |
| **FC** | `primary_org_path_txt LIKE '%FULFILLMENT%'` OR `job_transfer_set LIKE '%FC%'` |
| **Rx** | `primary_org_path_txt LIKE '%PHARMACY%'` OR `'%VET CARE%'` OR `'%HEALTHCARE%'` |
| **CC** | `primary_org_path_txt LIKE '%CUSTOMER CARE%'` OR `'%CUSTOMER SERVICE%'` |
| **Other** | None of the above |

---

## 14. Output Schema

The current export returns 14 columns per defect row:

| # | Column | Source | Description |
| --- | --- | --- | --- |
| 1 | Business Unit | Business-unit / network field in final export | Business unit label shown in output (for example FC, Rx, CC, Other, and other source-driven values) |
| 2 | Employee ID | `person_number` | 6-digit UKG employee identifier |
| 3 | Employee Full Name | `full_name` | Last, First format |
| 4 | Schedule Group Name | `schedule_group` | UKG schedule group (nullable for non-FC) |
| 5 | Reports To | `supervisor_full_name` | Direct supervisor |
| 6 | Date | `partition_date` | Timecard date |
| 7 | Hours Scheduled | `scheduled_eligible` | Total scheduled eligible hours for the day |
| 8 | Hours Worked | `worked` | Total worked hours for the day across in-scope work paycodes |
| 9 | Time-Off Applied | `timeoff_applied` | Total time-off paycode hours applied |
| 10 | Paycodes (name: HH:MM) | Aggregated from `GOLD_V_TIMECARD_TOTAL` | Comma-separated paycode list with durations |
| 11 | Over-Applied Hrs | `over_applied_hours` | Computed over-application amount |
| 12 | Recommendation | Computed | User-facing action statement based on over-applied hours and schedule context |
| 13 | Root Cause | Computed | Derived defect-driver category |
| 14 | Schedule Anomaly | Computed | Derived schedule anomaly flag when applicable |

The sample export is severity-first, with the highest over-applied cases surfaced at the top of the list.

---

## 15. Prompt Library

| # | Prompt Type | Example | SQL Template |
| --- | --- | --- | --- |
| 1 | Basic retrieval | "Show me defects that need attention" | BASE QUERY |
| 2 | Executive summary | "Give me an executive summary" | BASE + KPI + ROOT CAUSE |
| 3 | Network filter | "Show me FC only" | BASE + `WHERE cohort = 'FC'` |
| 4 | Location filter | "Show me PHX1" | BASE + `WHERE location ILIKE '%PHX1%'` |
| 5 | Supervisor filter | "Show me John Smith's team" | BASE + `WHERE reports_to ILIKE '...'` |
| 6 | Employee lookup | "Look up employee 123456" | BASE + `WHERE employee_id = '123456'` |
| 7 | KPI request | "Show me the KPIs" | KPI TEMPLATE |
| 8 | Root cause | "What's driving the defects?" | ROOT CAUSE TEMPLATE |
| 9 | Day-of-week | "Are there patterns by day of week?" | DAY-OF-WEEK TEMPLATE |
| 10 | Tenure analysis | "Is this a new hire problem?" | TENURE TEMPLATE |
| 11 | Export | "Export to Excel" | BASE QUERY (platform export) |
| 12 | Risk filter | "Just show me high-risk defects" | BASE + `WHERE hr_action ILIKE '%HIGH PRIORITY%'` |
| 13 | Pattern filter | "Show me all NCNS defects" | BASE + `WHERE paycodes ILIKE '%Call Off%'` |
| 14 | Network compare | "How does FC compare to Rx?" | NETWORK COMPARE TEMPLATE |
| 15 | Repeat offenders | "Who has multiple defects?" | REPEAT OFFENDERS TEMPLATE |
| 16 | Help | "What can you help me with?" | Static response |

---

## 16. Success Metrics

| Metric | Definition | Baseline / Target |
| --- | --- | --- |
| **TMDM audit effort reduction** | Weekly hours spent on paycode-related audits, before vs. after. | Baseline: ~22 hrs/week. Target: ~60% reduction (~9 hrs). |
| **Pre- vs post-payroll defect capture** | Proportion of issues resolved before payroll close vs. discovered after. | Target: Increase pre-payroll share; reduce post-payroll discoveries. |
| **Rework reduction** | Decrease in Payroll/HR tickets, refunds, or adjustments for over-applied time-off. | Target: Meaningful % reduction in post-payroll tickets. |
| **Defect coverage improvement** | Defects found by ORBIT that are absent from the legacy UKG report. | Target: Net new defects per pay period > 0. |

---

## 17. KPIs

| KPI | Description | Calculation | Why It Matters |
| --- | --- | --- | --- |
| **Audit Time Reduction** | Hours saved vs. baseline | 22 - actual hours spent | Core productivity metric |
| **Pre-Payroll Capture Rate** | % defects resolved before close | Pre / (Pre + Post) * 100 | Measures proactive shift |
| **Total Over-Applied Hours** | Sum of all over-applied hours | SUM(over_applied_hours) | Financial risk exposure |
| **Defect Coverage Delta** | Net new vs. legacy report | ORBIT defects - UKG defects | Proves incremental value |
| **High-Risk Defect Rate** | % classified as High | High / Total * 100 | Prioritization effectiveness |
| **Defects per Location** | Count by location | COUNT(*) GROUP BY location | Enables Field HR routing |

---

## 18. Non-Goals

- Fully automated correction of timecards in UKG. Corrections remain human-in-the-loop.
- Replacing all UKG timekeeping reporting. This product is scoped to paycode reconciliation.
- Initial inclusion of paycode types beyond the 17 defined above.

---

## 19. Open Questions / Decisions Needed

1. **ROI quantification method:** Addressed — see **ROI Narrative, TMDM Paycode Reconciler.md** for the three-dimension ROI framework (audit efficiency, expanded coverage, faster cadence) and measurement plan. Financial impact translation pending Payroll ticket data integration.
2. **Report refresh cadence:** What is the optimal refresh frequency relative to payroll cut-offs? (Current: weekly on-demand; target: daily automated.)
3. **Production hosting and ownership:** Which Phoenix / ORBIT environment and team will own ongoing maintenance?
4. **Paycode list governance:** How often will the 17-paycode list be reviewed for additions or removals?

---

## 20. Recommended Next Steps

1. Finalize productionization decision based on pilot results.
2. Partner with Payroll and Enterprise People Analytics to source ticket/correction data for ROI quantification.
3. Confirm report refresh cadence, environment, and operational ownership.
4. Upon approval, promote to production for FC and Rx; plan subsequent expansion.

---

## 21. Roadmap Alignment

This PRD anchors to the **2026 HR Transformation pillars** — especially **Pillar 1: Leveraging Automation and Intelligence to Scale HR** — by proving an exception-driven, automation-first workflow on Phoenix for HRSS/TMDM. It reduces manual audit effort, standardizes insights, and creates a repeatable pattern for future HRSS/COE ORBIT products.
