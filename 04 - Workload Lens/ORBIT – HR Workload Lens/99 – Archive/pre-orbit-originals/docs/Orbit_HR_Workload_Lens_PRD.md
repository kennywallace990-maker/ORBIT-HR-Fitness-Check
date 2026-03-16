# ORBIT HR Workload Lens — Product Requirements Document

**Status:** Draft  
**Version:** 1.0  
**Last Updated:** 2026-02-20  
**Owner:** HR Transformation / Enterprise AI  
**Delivery Platform:** Phoenix / ORBIT → Snowflake  

---

## Table of Contents

1. [Problem & Purpose](#1-problem--purpose)
2. [Product Vision](#2-product-vision)
3. [Audience](#3-audience)
4. [Phases & Data Sources](#4-phases--data-sources)
5. [Actor Groups & Ownership Model](#5-actor-groups--ownership-model)
6. [Work Classification Framework](#6-work-classification-framework)
7. [KPI Catalog](#7-kpi-catalog)
8. [Week-over-Week Measurement Framework](#8-week-over-week-measurement-framework)
9. [Report Structure & Experience](#9-report-structure--experience)
10. [Spotlight vs Standing Topics & Action Generation Rules](#10-spotlight-vs-standing-topics--action-generation-rules)
11. [Top Drivers Framework](#11-top-drivers-framework)
12. [Schedule Adjustment Tracking](#12-schedule-adjustment-tracking)
13. [Service Tier & Ownership Classification](#13-service-tier--ownership-classification)
14. [Site & Network Groupings](#14-site--network-groupings)
15. [Data & Technical Architecture](#15-data--technical-architecture)
16. [Feature Table](#16-feature-table)
17. [Success Metrics & Targets](#17-success-metrics--targets)
18. [Non-Goals](#18-non-goals)
19. [Open Questions & Decisions Needed](#19-open-questions--decisions-needed)
20. [Recommended Next Steps](#20-recommended-next-steps)
21. [Appendix: Glossary](#21-appendix-glossary)

---

## 1. Problem & Purpose

### The Problem

HR — both COE and Field/Local — is carrying a high and growing workload across Time & Attendance and other HR processes. Today we cannot answer three foundational questions with confidence:

1. **What is driving work to HR?** We see contact reasons but not root causes.
2. **Who is doing the work?** Attribution between Local HR, HRSS/COE, Managers, and Team Members is opaque.
3. **Where are we creating friction, rework, and waste?** We have counts; we don't have causality.

The result: we cannot systematically reduce HR workload, cannot set credible improvement targets, and cannot intelligently direct automation investment.

> From VP HR: *"We are still seeing Time and Attendance as the major case load for our teams and HRSS/TMDM. We need to own the reasons and common types of defects, the complexity of those defects, and where TMs/Managers vs HR are creating them. We should track these defects as deep as we can and create a separate WBR process to drive improvement. This is a pure operational problem, similar to quality issues in the field."*

### The Purpose

**Transform HR through scalability and intelligence.**

This product is the modernization engine for HR. It exists to:

- Use AI strategically, not reactively — reason through data, not apply static rules.
- Drive workflow automation and signal detection at scale.
- Reduce manual HR work by surfacing root causes of timecard touches, ticket volume, and rework.
- Give HR leadership a holistic, weekly, and actionable view of HR workload that drives real behavior change — not just awareness.

---

## 2. Product Vision

The **ORBIT HR Workload Lens** is a Phoenix/ORBIT-powered report agent, backed by Snowflake, that runs every Monday for the prior week (Sunday–Saturday). It produces a single, standardized, OBR-ready document — not an interactive dashboard — that tells the full story of HR operational quality for that week.

**Target state in one sentence:** Every Monday morning, HR leadership opens a report that tells them in plain language what happened last week, who drove it, where the hotspots are, what to do about it, and whether things are getting better or worse.

**The product lives in Phoenix as an ORBIT agent.** Each run is a fresh report generation: the agent reads the configured Snowflake views, applies the rules and KPIs defined in this PRD, and produces a formatted output document. No manual analyst work required after initial setup.

---

## 3. Audience

### Primary Consumers
| Role | What They Use It For |
|---|---|
| VP HR / HR Directors | Weekly headline view; approve top 3–5 focus areas; track network trend |
| COE Leadership (TMSC, TMDM, LOA) | Own their section; drive defect reduction within their team |
| Enterprise AI / Phoenix Engineering | Validate automation targets; track Automation → Correction conversion |
| HR Transformation Team | Baseline, target-setting, and weekly improvement tracking |

### Secondary Consumers
| Role | What They Use It For |
|---|---|
| FC + Rx HR Managers | Site-level view; manage engagement flags for their TMs |
| Enterprise People Analytics | Consume AI narratives and supplemental metrics for the HR OBR |
| HRSS/TMDM Ops | User-level baselines; identify training and process improvement opportunities |

---

## 4. Phases & Data Sources

### Phase I — Timecard Defects & Ownership (UKG Only)

**When:** Now. POC via Phoenix directly on Snowflake UKG views. *(Phase I reflects timecard work only).*

**What it measures:** Every timecard action in UKG — who touched it, what they did, whether the outcome was correct or required rework.

**Primary source:** UKG Timecard / Timesheet Audit (`All Timesheet Audit Information` report / Snowflake UKG feed)

Key fields used:
- `EMPLOYEE_ID`, `SITE_CODE` — who and where
- `REVISION_USER`, `REVISION_USER_FUNCTION_ACCESS_PROFILE` — which actor
- `ENTITY_TYPE` — Punch, Pay Code Edit, Historical Correction, Schedule Change, Exception Comment, Approval, etc.
- `EXCEPTION_TYPE_NAME`, `EXCEPTION_TYPE_DESC` — specific exception category (Missing Punch, MJT, etc.) and details.
- `REVISION_TYPE` — Add, Edit, Delete, Transfer
- `REVISION_DATE`, `ENTITY_EVENT_DATE` — when the action happened vs. when the event occurred (lag computation)
- `PAYCODE_NAME` — which paycode was touched
- `COMMENT` (mapped from `AUDIT_COMMENT_TEXT`) and `NOTE_TEXT` (mapped from `AUDIT_NOTE_TEXT`) — comment discipline tracking
- **Schedule-specific fields** — pattern, schedule assignment, shift changes (see Section 12)

**Supporting Snowflake objects:**
- `GOLD_V_PEOPLE` — site, department, supervisor, headcount (TM headcount denominator)
- HR role mapping table — maps `REVISION_USER_FUNCTION_ACCESS_PROFILE` to `ACTOR_GROUP`
- Service Tier mapping table — maps event patterns to `SERVICE_TIER` and `INTENDED_OWNER`
- Site reference table — maps sites to network groupings (1G, 2G, Rx, CVC, CC)

---

### Phase II — HR Workload & Intelligence (UKG + ServiceNow)

**When:** Once ServiceNow ticket data is available in Snowflake.

**What it adds:** Every HR ticket and case — what drove the contact, who worked it, whether it was routed correctly, and how it relates to timecard patterns at the same site and time window.

**Additional sources:**
- ServiceNow HR ticket tables (via Snowflake) — `HR_SERVICE`, `CATEGORY`, `SUBCATEGORY`, `ASSIGNMENT_GROUP`, open/close dates, SLA, requestor
- Integrated UKG + SNOW views — joined on employee, site, and time window

**Phase II unlocks:**
- Total HR workload (timecards + tickets) by site, actor group, and network
- DPMO – Tickets and DPMO – UKG Events (comparable defect density metrics)
- Root-cause clustering across both signals (e.g., same TM cohort generating both missed punches and leave inquiries)
- Non-timecard friction points: policy questions, access issues, escalations, and cases with no timecard footprint

---

## 5. Actor Groups & Ownership Model

Actor groups are mapped from `rev.ACCESS_PROFILE` (`REVISION_USER_FUNCTION_ACCESS_PROFILE`). There are **5 reporting groups**. The CASE logic below is the canonical SQL classification (see Section 15.5 for the full reference query).

| Actor Group | Sub-group | `ACCESS_PROFILE` values (exact) | Description |
|---|---|---|---|
| **Local HR** | — | `Company Admin Site Specific` | Site-level field HR. Corrections, documentation, first-line policy guidance. |
| **HRSS** | TMSC | `Team Member Services` | Centralized service center. Escalated transactions, complex adjustments. |
| **HRSS** | TMDM | `Company Admin TMDM` | UKG system config, pay rules, integrations, automations. |
| **HRSS** | Super Access | `Super Access` | Elevated admin access; treat as TMDM. |
| **Automation** | — | `Super Access No Wages` | Automated system traffic. Excluded from HR workload reporting. |
| **HRSS** | LOAA | `Leave Support` | Leave of absence administration. FMLA, disability, intermittent leave. |
| **Team Member** | — | `Employee Basic`, `Employee Basic- Pharmacy`, `Training Basic`, `IT Admin`, `Training + Safety`, `Advanced Scheduler Lead`, `Advanced Scheduler Workforce Analyst`, `Facilities` | Self-service. Applies when `EMPLOYEE_FULL_NAME = REVISION_USER_FULL_NAME`. |
| **Local Ops** | — | `Manager Basic`, `Manager Basic With Punch&Schedule Edits`, `Practice Manager`, `Facilities Manager` | Field operations managers. Approvals, attendance, daily execution. |
| **WFM** | — | `Workforce Reporting` | Scheduling, forecasting, intraday management. Retained in base data only; excluded from HR workload reporting. |

> [!NOTE]
> **Self-edit detection** uses `EMPLOYEE_FULL_NAME = REVISION_USER_FULL_NAME`. When a person's name matches the revision user's name, classify them as **Team Member** regardless of their access profile.

> HR KPI tables display only **3 reporting groups**: `Local HR`, `HRSS`, and `Local Ops`. `Team Member`, `Automation`, `Other`, and `WFM` remain classifiable in base data but are excluded from HR workload metrics.

> **TM self-service in UKG / timeclock currently includes:** clock in / clock out at a timeclock or via the app; view current timecard for the pay period; edit or submit a missed punch or forgot-to-punch request; submit timecard corrections or edits for manager approval; view punch history and punch detail, including location, device, and timestamps; confirm or acknowledge punches when prompted; view published schedule and future shifts; view time off balances and accruals; view status of submitted requests; receive notifications of approvals, denials, or required actions; complete simple approval tasks in-app when approver rights are enabled.

---

## 6. Work Classification Framework

Every UKG timecard audit row is classified into two dimensions: **Bucket** (nature of the work) and **Work Type** (category of the action). Together these drive all KPI calculations.

### 6.1 Bucket Classification

| Bucket | Label | Definition | Defect? |
|---|---|---|---|
| **A** | Governance | Expected, policy-compliant timecard management — approvals, comment discipline, scheduled audits, automation-driven population. No error or correction involved. | No |
| **B** | Correction / Rework | Action that changes a pay or attendance outcome on a record that was previously closed, approved, or accepted. Includes edits, deletes, historical corrections, and duplicate-reversal patterns. | **Yes — always counted as a defect** |
| **C** | Documentation | Required documentation on an existing record (comments, exception notes, justification text) that does not change a pay outcome but is required by policy or audit. | No |
| **D** | Schedule Touch | Any action on an employee's schedule template, shift assignment, or shift trade, whether or not it results in a paycode change. | Conditional (see Section 12) |

> [!NOTE]
> Bucket B events are the core defect signal. The share of Bucket B events in total actions, by actor group, work type, and site, is the primary quality metric.

### 6.2 Work Type Taxonomy

**Entity types confirmed in raw CSV data** (all 9 observed in the sample):

| Work Type | `ENTITY_TYPE` (exact string in data) | Notes |
|---|---|---|
| Punch | `Punch` | Core attendance signal. Punch rework = punch defect. |
| Pay Code Edit | `Pay Code Edit` | Time-off, leave, and pay adjustment coding. Sub-classify by PAYCODE_NAME. |
| Pay Code Edit Comment | `Pay Code Edit Comment` | Comment affixed to a Pay Code Edit. Governance / documentation. Bucket C. |
| Punch Comment | `Punch Comment` | Comment affixed to a punch record. Governance / documentation. Bucket C. |
| Exception Comment | `Exception Comment` | Comment on an active UKG exception. Governance / documentation. Bucket C. |
| Manager Justified Time | `Manager Justified Time` | Manager override of scheduled time to record actual time. Often indicates scheduling gap. |
| Historical Correction | `Historical Correction` | Retro changes to closed pay periods. See Section 6.3 for sub-categorization. |
| Mark as Reviewed | `Mark as reviewed` | Timecard review/signoff action. Governance. Bucket A. |
| Manager Approval | `Manager Approval` | Timecard finalization approval. Governance. Bucket A. |

> [!NOTE]
> `Pay Code Edit Comment` and `Punch Comment` are distinct entity types from `Exception Comment`. All three are Bucket C (Documentation) events. They should be tracked separately in the work type mix table since their volume signals comment discipline patterns.

### 6.3 Historical Correction Sub-Categorization
The `Historical Correction` work type aggregates changes made to a previously closed pay period. To isolate operational defects from natural compliance lag, Historical Corrections are divided into three sub-categories based on `PAYCODE_NAME`:

1. **Leave & Compliance Lag (Expected/Non-Defect):** Adjustments applied retroactively due to external approval timelines (e.g., Workers Comp, LOA, FMLA approval delays).
   * **Rule:** `PAYCODE_NAME` contains: `Workers Comp`, `FMLA`, `LOA`, `STD`, `Bereavement`, `Jury`.
2. **Incentive / Bonus True-Up (Expected/Non-Defect):** Batch administrative updates for performance or sign-on bonuses.
   * **Rule:** `PAYCODE_NAME` contains: `Bonus`, `Premium`, `Incentive`.
3. **Administrative Defect (Bucket B Rework):** Basic timekeeping errors that were missed during the active pay period and required retro-correction.
   * **Rule:** All other paycodes (e.g., `Regular`, `Overtime`, `PTO`, `Unpaid`).

Only **Administrative Defects** should be counted within the primary Defect Rate KPI.

### 6.4 Historical Correction Root Cause Generation
When analyzing Historical Corrections for the Executive Summary narrative, the ORBIT agent will cluster the exact `PAYCODE_NAME` into four insight categories to explain *why* the retro-action occurred:

1. **Leave & Compliance Lag:** (`LEAVE`, `Intermittent Leave-Unpaid`, `Bereavement`) → "Indicating standard operational lag while awaiting medical documentation or third-party approvals."
2. **Attendance Enforcement:** (`Personal UNPD NCNS`, `Early Departure`, `Late arrival`, `Call Off`) → "Indicating local managers or HR failed to code attendance infractions before the payroll window closed."
3. **Schedule & Unpaid True-Ups:** (`Personal UNPAID`, `Personal - HR`, `Voluntary Time Off`, `Weather`) → "Indicating site-wide events or schedule-deviation VTO were not properly processed prior to transmission."
4. **Core Pay & Missing Time:** (`Regular`, `Overtime`, `Meal Break`, `PTO PAID`) → "Indicating severe friction where employees were not paid correctly for worked or accrued time and required retroactive deposits."

---

## 7. KPI Catalog

All KPIs are computed at the **site × week** grain and rolled up to region and network. WoW delta is calculated vs. the prior week and vs. the 4-week rolling average (baseline).

### 7.1 Timecard Work Intensity

| KPI | Definition | Formula |
|---|---|---|
| **Total Actions per TM** | All UKG audit rows in the week, normalized by average TM headcount | `SUM(audit_rows) / AVG(tm_headcount)` by site-week |
| **Defect Actions per TM** | Bucket B rows only, normalized by TM headcount | `SUM(bucket_b_rows) / AVG(tm_headcount)` |
| **Rework Actions per TM** | Edit + Delete rows (all buckets), normalized by TM headcount | `SUM(edit_or_delete_rows) / AVG(tm_headcount)` |
| **Schedule Touch Actions per TM** | Bucket D rows, normalized by TM headcount | `SUM(bucket_d_rows) / AVG(tm_headcount)` |
| **HR-Originated Actions per TM** | Rows where ACTOR_GROUP in (LOCAL_HR, COE_TMSC, TMDM, LOCAL_OPS), normalized | `SUM(hr_actor_rows) / AVG(tm_headcount)` |

> **Direction:** All five metrics should trend **down** over time as defects are eliminated and self-service improves.

---

### 7.2 Defect & Rework Quality

| KPI | Definition | Formula |
|---|---|---|
| **Defect Rate** | % of all timecard actions that are Bucket B | [(SUM(bucket_b_rows) / SUM(all_rows)) × 100](file:///C:/Users/kenne/.gemini/antigravity/scratch/generate_wbr_stats.py#231-243) |
| **Rework Rate** | % of all timecard actions that are edit or delete | [(SUM(edit_delete_rows) / SUM(all_rows)) × 100](file:///C:/Users/kenne/.gemini/antigravity/scratch/generate_wbr_stats.py#231-243) |
| **Punch Defect Rate** | % of punch-type actions that are rework | [(SUM(punch_rework_rows) / SUM(punch_rows)) × 100](file:///C:/Users/kenne/.gemini/antigravity/scratch/generate_wbr_stats.py#231-243) |
| **Historical Correction Rate** | % of all actions that are Historical Correction | [(SUM(hist_corr_rows) / SUM(all_rows)) × 100](file:///C:/Users/kenne/.gemini/antigravity/scratch/generate_wbr_stats.py#231-243) |
| **MJT Rate** | % of all actions that are MJT | [(SUM(mjt_rows) / SUM(all_rows)) × 100](file:///C:/Users/kenne/.gemini/antigravity/scratch/generate_wbr_stats.py#231-243) |
| **Lag (days)** | Median days between ENTITY_EVENT_DATE and REVISION_DATE, for Bucket B rows | `MEDIAN(revision_date - entity_event_date)` where bucket = B |
| **Late Correction Rate** | % of Bucket B corrections made more than 7 days after the event date | [(SUM(bucket_b WHERE lag > 7) / SUM(bucket_b)) × 100](file:///C:/Users/kenne/.gemini/antigravity/scratch/generate_wbr_stats.py#231-243) |
| **DPMO - Defects per 1,000 expected punch opportunities** | Proxies expected workload to fairly compare sites of different sizes. Targets: Green < 20, Yellow 20-50, Red > 50 | [(SUM(bucket_b_rows) / (Distinct_Employee_Count * 20)) * 1000](file:///C:/Users/kenne/.gemini/antigravity/scratch/generate_wbr_stats.py#231-243) |

---

### 7.3 Schedule Quality

*(Full detail in Section 12)*

| KPI | Definition | Formula |
|---|---|---|
| **Schedule Touch Rate per TM** | Schedule audit rows ÷ TM headcount | `SUM(bucket_d_rows) / AVG(tm_headcount)` |
| **Schedule Defect Rate** | Schedule touches that resulted in a paycode change within 24h | `SUM(sched_touch → paycode_change_within_24h) / SUM(sched_touch_rows)` |
| **Unplanned Schedule Change Rate** | Schedule changes with lag < 24h from shift start | `SUM(sched_change WHERE revision_date < shift_start - 24h) / SUM(sched_change_rows)` |
| **Schedule Correction Rate** | Schedule edits or deletes to previously published schedules | `SUM(sched_edit_delete_rows) / SUM(sched_rows)` |

---

### 7.4 Ownership & Routing Quality

| KPI | Definition | Formula |
|---|---|---|
| **Ownership Split %** | Share of all actions by ACTOR_GROUP | `SUM(rows by actor_group) / SUM(all_rows) × 100` per group |
| **Tier 1 Correct Routing %** | Tier 1 events handled by intended owner | `SUM(tier1 WHERE actor = intended_owner) / SUM(tier1_rows) × 100` |
| **Tier 1 Misrouted to Local HR %** | Tier 1 events that should be HRSS but landed on Local HR | `SUM(tier1 WHERE intended_owner=HRSS AND actor=LOCAL_HR) / SUM(tier1_rows) × 100` |
| **Tier 2 Handled by Local HR %** | Specialist/COE-intended work performed by Local HR | `SUM(tier2 WHERE intended_owner=COE/TMDM AND actor=LOCAL_HR) / SUM(tier2_rows) × 100` |
| **HRSS Self-Resolution Rate** | HRSS-originated Tier 1 actions that closed without escalation | `SUM(tier1_hrss WHERE no escalation flag) / SUM(tier1_hrss_rows) × 100` |

---

### 7.5 Automation & Efficiency

| KPI | Definition | Formula |
|---|---|---|
| **Automation Share %** | % of all audit rows generated by SYSTEM actor | `SUM(system_rows) / SUM(all_rows) × 100` |
| **Automation → Correction Rate** | Employee-Day Cases where Bucket A (automation) was followed by Bucket B (correction) on the same employee-day | `SUM(cases WITH bucket_a AND bucket_b) / SUM(cases WITH bucket_a) × 100` |
| **Comment Compliance Rate** | See *Note on Targeted Comment Discipline* below. % of required high-risk rework actions that have a non-null, non-empty COMMENT text. | `SUM(HighRisk WITH Comment) / SUM(HighRisk Actions) × 100` |
| **Total Friction Hours Burned** | The time cost of HR timecard work calculated via proportional Friction Score Multiplier. Replaces flat counting. | `SUM(Friction Scores) / 60` |

#### Note on Targeted Comment Discipline
Not every HR action requires a comment. Forcing 100% comment compliance creates "junk data" (e.g., HR typing "ok" on hundreds of routine governance approvals). Comment Discipline is measured strictly against **High-Risk Rework (Targeted Bar):**
* **REQUIRED:** Historical Corrections (all types).
* **REQUIRED:** Manual Punch Edits/Adds by HR.
* **REQUIRED:** Pay Code Edits applying paid time (PTO, Sick, Overtime).
* **NOT REQUIRED:** Mark as Reviewed, Manager Approvals, Schedule generation, auto-deductions.
| **Estimated FTE Equivalent** | Converts Friction Hours to FTE equivalents for workforce planning. | `Friction Hours / 40` |

---

### 7.6 Missed Punch Intensity

| KPI | Definition | Formula |
|---|---|---|
| **Missed Punch Events per TM** | Missing punch exceptions fired per TM per week | `SUM(missed_punch_rows) / AVG(tm_headcount)` |
| **Repeat Missed Punch Rate** | % of TMs with ≥2 missed punch events in the week | `COUNT(tm WHERE missed_punch_count_week ≥ 2) / COUNT(tm) × 100` |
| **Chronic Missed Punch Rate** | % of TMs meeting any engagement threshold (see Section 10) | `COUNT(tm WHERE ANY engagement_flag = TRUE) / COUNT(tm) × 100` |

---

### 7.7 Phase II — Ticket & Combined Metrics *(future)*

| KPI | Definition | Formula |
|---|---|---|
| **DPMO – Tickets** | Defects per 1,000 expected ticket opportunities | [(SUM(defect_tickets) / SUM(all_tickets)) × 1,000](file:///C:/Users/kenne/.gemini/antigravity/scratch/generate_wbr_stats.py#231-243) — defect flags aligned with EPA HR OBR logic |
| **Total HR Workload per TM** | Combined timecard + ticket touches per TM | [(Employee_Day_Cases + ticket_count) / AVG(tm_headcount)](file:///C:/Users/kenne/.gemini/antigravity/scratch/generate_wbr_stats.py#231-243) |
| **Ticket–Timecard Overlap %** | % of SNOW tickets that have a same-employee, same-week UKG audit match | `SUM(tickets WITH ukg_match) / SUM(all_tickets) × 100` |
| **Non-Timecard HR Work %** | % of total HR workload represented by tickets with no UKG footprint | `SUM(tickets WHERE no ukg_match) / SUM(total_hr_workload) × 100` |
| **Misrouting Rate – Tickets** | Tickets where ASSIGNMENT_GROUP ≠ INTENDED_OWNER | `SUM(ticket WHERE assignment ≠ intended) / SUM(all_tickets) × 100` |

---

## 8. Week-over-Week Measurement Framework

Every KPI in Section 7 is displayed with four data points for each site-week:

| Column | Definition |
|---|---|
| **This Week** | Current reporting week (Sun–Sat) value |
| **Prior Week** | Prior Sun–Sat value |
| **WoW Δ** | `This Week − Prior Week` (absolute delta) |
| **WoW Δ%** | [(This Week − Prior Week) / Prior Week × 100](file:///C:/Users/kenne/.gemini/antigravity/scratch/generate_wbr_stats.py#231-243) (% change) |
| **4-Week Avg (Baseline)** | Rolling average of prior 4 weeks (not including current week) |
| **vs. Baseline** | `This Week − 4-Week Avg` (absolute delta vs. rolling baseline) |
| **13-Week Trend** | Sparkline showing the last 13 weeks (quarter view) |

### Traffic Light Rules (for WBR coloring)

| Color | Condition |
|---|---|
| 🟢 Green | Within ±5% of 4-week baseline, or improving vs. baseline |
| 🟡 Yellow | 6–15% worse than 4-week baseline |
| 🔴 Red | >15% worse than 4-week baseline, or triggered a threshold flag |

> Numeric targets (e.g., defect rate < X%) will be set with HR leadership after the first 4-week baseline is established. The framework above is threshold-agnostic until targets are agreed.

---

## 9. Report Structure & Experience

The ORBIT agent generates a single Markdown/formatted document every Monday. The structure is fixed and consistent — HR leaders should be able to navigate it from memory after the first two runs.

### Section 1 — AI-Generated Executive Summary

**Purpose:** Plain-language summary of the week. Written by the Phoenix LLM using the KPI data as input. No manual editing required.

**Contents:**
- **Headline sentence:** "Last week, the network generated X timecard actions per TM, [up/down] Y% from the prior week, driven primarily by [top driver]."
- **Ownership story:** Who did the work (% split by actor group), and whether that split improved or worsened vs. baseline.
- **Defect & rework story:** Overall defect rate, rework rate, punch defect rate, and whether they improved or degraded.
- **Schedule story:** Whether schedule touch rates increased or decreased, and the top schedule change driver.
- **Top 3 hotspot sites:** Red sites by defect rate or total actions per TM, with one-sentence reason each.
- **Top 3 improving sites:** Green sites with the largest WoW improvement, with one-sentence reason each.
- **Key signal of the week:** One notable pattern the AI identified that is not obvious from the headline numbers (e.g., "MJT rate at SDF2 spiked 40% — driven by a single supervisor accounting for 62% of site MJT actions").
- **Improvement Signal:** "3 metrics improving, 3 metrics deteriorating, Net improvement score."

**Tone:** Written for a VP-level reader. No jargon. No tables in this section. Direct and specific.

---

### Section 2 — WBR-Style Tables & Charts

**Purpose:** Granular breakdown of timecard actions, highlighting the split between governance and corrections, and isolating the specific drivers behind rework across the network.

**2.2 Business Unit Split (Prior Week Snapshot):**
Shows the total action volume split between Corrections (actual timecard changes) and Governance (approvals/reviews). Columns include Total Actions, Corrections, Defect %, Governance, Governance %, Missed Punch %, and Historical Correction %. 

**2.3 — 2.6 Top Timecard Drivers by Business Unit:**
Independent subsections for FC, Rx, CC, and CVC Networks. Each features a table showing the Top 5 rework signals (e.g., Late Arrival, Leave of Absence, Missing Punch). Columns break down *who* did the HR processing: `Local HR | HRSS | Local Ops | Total`. Each table is followed by an AI Insight translating the volume, FTE hour cost, and dominant HR actor group into a recommended action.

**2.7 HRSS Workload — By Business Unit:**
Unlike the BUs, HRSS is centralized. This table shows the Top 5 rework signals processed by HRSS overall, with columns showing *where* that effort occurred: `FC | Rx | CC | CVC | Total`. Followed by an AI Insight focused on centralization opportunities.

---

### Section 3 — Recommended Actions

**Purpose:** AI-generated, specific, prioritized action list. Not a summary of what happened — a list of what to do next week.

**Structure:** Numbered list, 5–10 items, ordered by estimated impact.

Each item contains:
- **Site or group:** e.g., "AVP2" or "LOCAL_HR network-wide"
- **Observation:** What the data shows
- **Action:** Who should do what, by when
- **Expected outcome:** What improvement to expect if the action is taken

**Example items:**
> 1. **AVP2 — Punch Defect Rate 34% (🔴, +12% WoW).** LOCAL_HR is correcting 89% of missed punches manually. **Action:** Site HR lead to audit top 5 offending TMs this week and initiate engagement conversations using the TM flag list below. Engineering to review whether punch suggestion automation is enabled for AVP2. **Expected:** 15–20% reduction in Punch Defect Rate within 2 weeks if engagement conversations occur.

> 2. **Network-wide — Automation → Correction Rate at 22%.** More than 1 in 5 automation-populated timecards is being manually corrected afterward. **Action:** TMDM to review pay-from-schedule rule configuration for the top 3 paycode/site combinations driving corrections. **Expected:** If rules are corrected, estimated 400 Bucket B events/week eliminated.

---

### Section 4 — Drill-Down Tables

**Purpose:** As the reader scrolls, the data gets more specific. Leaders should not need to pull a separate report.

**4a — Site-Level Deep Dives** (one table per site, red sites first)
- Ownership split (all actor groups)
- Work type mix
- Top 5 paycodes touched
- Rework and defect details
- Schedule touch breakdown

**4b — User-Level Baselines** (LOCAL_HR and HRSS/COE users only)
- Actions per user this week vs. 4-week baseline
- Estimated hours (actions × 2 min / 60)
- Top 3 work types per user
- % of site's total actions concentrated in top 3 users

**4c — Missed Punch Engagement Opportunities**
- Triggered TMs by site (see Section 10 for thresholds)
- Columns: Site, TM Name, TM ID, Manager, Missed Count, Logs

---

## 10. Spotlight vs Standing Topics & Action Generation Rules

The ORBIT agent automatically identifies operational friction points. To filter noise for the OBR, metrics are classified as either **Spotlight Topics** or **Standing Topics**.

### 10.0 Spotlight Auto-Detection Logic

If a site or metric meets **ANY** of the following thresholds, it is promoted to a **Spotlight Topic (House on Fire)**:
*   Defect Rate > 40% 🔴
*   DPMO > 120
*   Comment Compliance < 70%
*   WoW increase > 10%

**Treatment:**
*   **Spotlight Topics:** Receive full narrative + a "Path to Green" action plan.
*   **Standing Topics:** Receive Table only. No narrative unless triggered by the above logic.

### 10.1 Path to Green Structure

For every 🔴 Spotlight metric, the agent will generate a structured action block instead of generic coaching text:
*   **🔴 Issue:** [Metric & Value]
*   **Root Cause Hypothesis:** [AI-generated hypothesis based on sub-metrics]
*   **Owner:** [Responsible actor group]
*   **Path to Green:**
    *   [Specific action 1]
    *   [Specific action 2]
    *   [Tracking/weekly reduction target]

### 10.2 TM Missed Punch Engagement Flags

These flags generate a named TM entry in the Engagement Flag List for the site's HR team.

| Flag | Rule | Severity |
|---|---|---|
| **Single-Shift Spike** | TM has ≥ 2 distinct missed punch events within a single shift (same `ENTITY_EVENT_DATE`) | Medium |
| **Weekly Pattern**     | TM has ≥ 3 distinct missed punch events within the reporting week | High |
| **Chronic Flagger** | TM has triggered any engagement flag in 3 or more of the last 4 weeks | 🔴 High — escalate to HR Director |

**Output per flag:** TM identifier, site, flag type, event dates, count, and suggested conversation script generated by the Phoenix LLM.

> [!IMPORTANT]
> These flags are for **engagement and coaching conversations**, not disciplinary actions. The product does not initiate or recommend disciplinary outcomes.

### 10.2 Site-Level Automated Alerts

These rules generate entries in the Recommended Actions section automatically.

| Alert | Trigger | Recommended Action Type |
|---|---|---|
| **Defect Spike** | Site Defect Rate > 15% WoW increase | Site HR Lead coaching + TMDM audit |
| **MJT Surge** | Site MJT Rate > 20% WoW increase | WFM scheduling gap review |
| **Historical Correction Concentration** | ≥ 50% of site's Historical Corrections done by a single user | Manager conversation + training |
| **Comment Compliance Drop** | Site Comment Compliance Rate on high-risk actions drops below 85% | Automated coaching flag sent to specific HR users skipping comments. |
| **Automation Failure Signal** | Automation → Correction Rate > 30% at any site | TMDM pay rule configuration review |
| **Late Correction Spike** | Late Correction Rate (>7-day lag) increases >10pp WoW | Process gap investigation — why are corrections being made so late? |
| **Schedule Correction Surge** | Schedule Correction Rate > 25% WoW increase | WFM schedule build quality review |
| **LOAA Zero Signal** | COE-LOA = 0 actions for leave-coded paycodes at any site with active leave cases | Alert: leave coding may be misrouted to COE-TMSC or LOCAL_HR |

### 10.3 Network-Level Automated Insights

These generate entries in the Executive Summary "Key Signal" field.

- Any actor group whose share of total actions changes by >5pp WoW.
- Any work type whose share of total actions changes by >8pp WoW.
- Any site that moves from Green to Red or Red to Green.
- Any site where a single user accounts for >40% of that site's total actions.
- Any week where Automation Share % declines (automation running less than prior week).

---

## 11. Top Drivers Framework

The report surfaces top drivers at two levels: **what is being touched** and **why it's being touched (root cause inference)**.

### 11.1 What's Being Touched — Top Paycode & Work Type Drivers

Every section surfaces the top 5 paycodes and top 5 work types by:
- Volume (total actions)
- WoW delta (absolute and %)
- Actor group contribution (who is driving each paycode's volume)

Example output:
> "The top 5 paycodes this week accounted for 67% of all Bucket B events. Personal UNPD Late Arrival remains the #1 driver (11,102 events, +3% WoW), concentrated in LOCAL_HR across 1G sites. Weather Unpaid Dur dropped 89% WoW as the weather event from the prior week cleared."

### 11.2 Why It's Being Touched — Root Cause Inference

The Phoenix LLM applies pattern-matching across the data to infer probable root causes from the combination of signals. It considers:

| Signal | What It Suggests |
|---|---|
| High MJT + High Schedule Touch at same site | Upstream scheduling gap — schedules not matching operational reality |
| High Punch Defect Rate + Low Comment Discipline | Process discipline issue — TMs/managers not following punch correction SOP |
| High Historical Correction Rate + High Lag | Retro corrections being made weeks later — possibly payroll dispute or late LOA coding |
| High LOCAL_HR Volume + Low TM Volume | Self-service not being used; TMs relying on HR to initiate corrections |
| High Automation → Correction Rate at a site | Pay rule or pay-from-schedule misconfiguration specific to that site |
| LOAA = 0 with active leave paycodes | Leave admin work is landing in COE-TMSC or LOCAL_HR instead of COE-LOA |
| Single-user concentration | Training gap, access gap, or new user onboarding without SOP adherence |

Root cause inference is presented as a confidence-qualified statement:
> "Pattern suggests a scheduling-driven root cause with high confidence: MJT Rate at DFW1 is up 31% WoW while Schedule Correction Rate is also up 22%, indicating published schedules are not matching operational demand. Likely action: WFM to review DFW1 schedule build for the affected week."

---

## 12. Schedule Adjustment Tracking

Schedule adjustments are a distinct and important signal that were previously invisible in a paycode-only view. A timecard may look clean in paycode terms while having significant schedule churn underneath.

### 12.1 What We Track

| Event | UKG Entity Type | Tracked As |
|---|---|---|
| Schedule template change | SCHEDULE / PATTERN_CHANGE | Schedule Touch — Bucket D |
| Shift assignment edit | SHIFT_ASSIGN with REVISION_TYPE = Edit | Schedule Touch — Bucket D |
| Shift delete / removal | SHIFT_ASSIGN with REVISION_TYPE = Delete | Schedule Correction — Bucket D |
| Shift trade or swap | TRANSFER / SHIFT_TRADE | Schedule Touch — Bucket D |
| Unplanned shift add (< 24h before shift) | SHIFT_ASSIGN with lag < 24h | Unplanned Schedule Change |
| Schedule edit followed by Pay Code Edit within 24h | SHIFT_ASSIGN → PAY_CODE_EDIT (same employee, ≤ 24h) | Schedule → Paycode Defect Chain |

### 12.2 Schedule-Specific KPIs

| KPI | Formula | What It Tells You |
|---|---|---|
| Schedule Touch Rate per TM | `SUM(bucket_d) / AVG(tm_headcount)` | Overall schedule instability |
| Unplanned Change Rate | `SUM(sched WHERE lag < 24h) / SUM(sched_rows)` | Reactive scheduling; WFM planning quality signal |
| Schedule Correction Rate | `SUM(sched_edit_delete) / SUM(sched_rows)` | Rework in schedule build |
| Sched → Paycode Chain Rate | `SUM(sched_touch followed by PCE ≤ 24h) / SUM(sched_rows)` | % of schedule touches that cascade into a pay correction — indicates policy/coverage friction |
| Same-Day Schedule Changes | `SUM(sched WHERE revision_date = shift_date)` per site | Day-of instability (VTO, emergency adds, no-shows) |

### 12.3 WBR Schedule Table

Appears in Section 2 of the report after the main timecard table.

| Site | Sched Touch / TM | Unplanned % | Correction % | Sched→PCE Chain % | WoW Δ Touch Rate | vs. Baseline |
|---|---|---|---|---|---|---|
| (all sites) | | | | | | |

### 12.4 Root Cause Rules for Schedule Signals

| Pattern | Inferred Cause | Recommended Action |
|---|---|---|
| High Unplanned Change Rate + High MJT | Schedules not reflecting actual staffing needs | WFM build quality review; shrinkage assumptions audit |
| High Sched→PCE Chain Rate | Schedule changes driving pay consequences that require manual paycode correction | WFM + TMDM: review whether pay-from-schedule rules should auto-apply paycodes on schedule change |
| High Schedule Correction Rate + single user | Training gap on schedule build | User coaching; WFM manager review |
| Low Unplanned Rate + High Punch Defect | Schedules are stable but TMs are missing punches anyway | Engagement conversations; location/device check |

---

## 13. Service Tier & Ownership Classification

### 13.1 Tier Definitions

| Tier | Description | Examples |
|---|---|---|
| **Tier 1** | Standard, repeatable work defined in TMSC and TMDM Tier 1 service catalogs | Missing punch correction, standard PTO coding, password resets, VOE, basic timecard adjustments |
| **Tier 2 / Specialist** | Complex or compliance-sensitive work requiring specialist judgment | Complex LOA, retro pay corrections, comp adjustments, advanced system configuration |
| **Out of Scope** | Actions that are expected and require no HR intervention | Employee self-service punch (TM recording their own time), automated pay population |

### 13.2 Misrouting Classification

For every Tier 1 or Tier 2 event, compute INTENDED_OWNER from the service tier mapping table, then compare to ACTOR_GROUP:

| If intended owner is... | And actual actor is... | Classify as |
|---|---|---|
| HRSS_TMSC or HRSS_TMDM | HRSS (TMSC or TMDM) | ✅ Tier 1 – Correctly routed |
| HRSS_TMSC or HRSS_TMDM | LOCAL_HR | ⚠️ Tier 1 – Misrouted to Field/Local |
| HRSS_TMSC or HRSS_TMDM | MGR / LOCAL_OPS | ⚠️ Tier 1 – Handled by Manager |
| LOCAL_HR or MGR | HRSS | ⚠️ Tier 1 – Misrouted to HRSS |
| COE / TMDM (Tier 2) | LOCAL_HR | 🔴 Tier 2 – Misrouted to Local HR |
| COE / TMDM (Tier 2) | HRSS_TMSC | 🔴 Tier 2 – Misrouted to Tier 1 HRSS |

### 13.3 Example UKG Mapping Table (Illustrative)

The full mapping table lives in Snowflake as a co-owned configuration table between Enterprise People Analytics and the ORBIT product team. Changes require joint approval.

| EXCEPTION_TYPE_NAME | ENTITY_TYPE | PAYCODE_NAME pattern | SERVICE_TIER | INTENDED_OWNER |
|---|---|---|---|---|
| Missing In/Out Punch, Missed Punch | PUNCH | — | Tier 1 | HRSS_TMDM |
| Historical Correction | HISTORICAL_CORRECTION | `%REG%` or `%OT%` | Tier 2 | HRSS_TMDM |
| Historical Correction | HISTORICAL_CORRECTION | `%LOA%` or `%STD%` | Tier 2 | COE_LOA |
| — | PAY_CODE_EDIT | PTO, UTO, VTO, Sick, Bereavement, Jury Duty | Tier 1 | HRSS_TMDM |
| — | PAY_CODE_EDIT | `%Bonus%` or `%Incentive%` | Tier 2 | HRSS_TMDM |
| — | PUNCH (Add/Edit/Delete, no paycode) | — | Tier 1 | MGR / TM — defect if done by HRSS/LOCAL_HR |
| Manager Justified Time | MJT | — | Tier 1 | MGR — defect if done by HRSS/LOCAL_HR |
| — | SCHEDULE | — | Tier 1 | WFM — defect if done outside WFM |
| — | HISTORICAL_CORRECTION | `%Weather%` or `%Emergency%` | Tier 2 | COE_TMSC |

---

## 14. Site & Network Groupings

All KPIs are computed at site grain and rolled up to **4 WBR groups**. Corporate sites are excluded from all reporting.

### Confirmed Site List

| WBR Group | Sites | Count |
|---|---|---|
| **FC** | AVP1, AVP2, BNA1, CFC1, CLT1, DAY1, DFW1, HOU1, MCI1, MCO1, MDT1, PHX1, RNO1 | 13 |
| **Rx** | AVP4, AVP5, AVP6, DFW5, DFW8, MCO4, MCO5, PHX2, PHX5, SDF2, SDF4, SDF5, SDF6 | 13 |
| **CVC** | ATLA, ATLB, ATLC, ATLD, AUSA, DENA, DENB, DEND, DFWA, DFWB, FLLA, FLLB, FLLC, FLLD, FLLF, IAHA, IAHD, PHXB | 18 |
| **CC** | AV4V, DF4V, DFW4, FL3V, PH0V, PW0V, SD2V | 7 |
| **Total Network** | All 51 above | 51 |

### Excluded (Out of Scope)

| Site | Type | Reason |
|---|---|---|
| BOS1, FLL7, SEA1, MSP2 | Corp | Corporate offices — excluded from all HR Workload Lens KPIs and reporting |

> [!NOTE]
> The `BUILDING_LOCATION` field is derived in Snowflake via `REGEXP_SUBSTR(p.PRIMARY_ORG_PATH_TXT, '- ([A-Z0-9]{3,5})/', 1, 1, 'e')`. Confirm this regex correctly extracts all 49 site codes before the baseline run. Apply a `WHERE BUILDING_LOCATION NOT IN ('BOS1','FLL7','SEA1','MSP2')` filter in all `V_HWL_*` base views.

---

## 15. Data & Technical Architecture

### 15.0 Data-Layer Filtering & Deduplication Rules

These rules **must be applied in the Snowflake base views** before any KPI computation. They are derived from direct observation of the raw UKG audit data.

#### 15.0.1 Self-Service Exclusion Filter

Exclude rows where a TM is editing **their own record** — clocking themselves in/out with no HR involvement. These are normal operational events and should **not** count toward any HR workload or defect KPI.

**Rule:** If `EMPLOYEE_FULL_NAME = REVISION_USER_FULL_NAME`, the person who made the change is the same as the employee whose record was changed → classify as **TM self-service; exclude from HR KPIs.**

```sql
-- Exclude TM self-service rows from all HR workload KPIs
WHERE EMPLOYEE_FULL_NAME != REVISION_USER_FULL_NAME
```

> This rule is profile-agnostic and resolves the `Workforce Reporting` ambiguity: a WFM analyst clocking in under their own name is correctly treated as a self-service TM action, not a WFM action. It is more reliable than checking `ACTOR_GROUP` or `EDIT_TARGET` alone.

TM self-service in scope terms includes:

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

#### 15.0.2 Missed Punch Deduplication

The raw UKG audit feed contains **duplicate rows for the same missed punch event** — the same employee, same date, same missing punch type, and same flag appear N times (observed 4–10x per event in data). Counting raw rows inflates all missed-punch KPIs dramatically.

**Deduplication Key:** Apply `DISTINCT` on the following composite key before computing any missed punch KPI:

```sql
-- Base deduplication for missed punch KPI grain
SELECT DISTINCT
    EMPLOYEE_ID,
    ENTITY_EVENT_DATE,
    MISSING_PUNCH_FLAG,       -- 'Yes' / 'No'
    MISSING_PUNCH_TYPE        -- 'Missed In Punch' / 'Missed Out Punch'
FROM ukg_audit
WHERE MISSING_PUNCH_FLAG = 'Yes'
  AND EMPLOYEE_FULL_NAME != REVISION_USER_FULL_NAME  -- exclude self-service rows
```

> **Important:** Deduplication applies **only to missed punch KPI views** (`V_HWL_TM_MISSED_PUNCH_WEEK`). The full raw row count is still used for action-volume KPIs (Total Actions per TM, etc.) to capture the true footprint of rework activity in the system.

#### 15.0.3 Proxy Correction Pattern

Rows where **someone other than the employee** deletes the employee's own punch represent Local HR correcting a bad TM self-punch. These should be classified as **Bucket B (Rework)** with LOCAL_HR as the acting group.

```sql
-- Proxy correction: HR or manager deleting a TM's self-generated punch
EMPLOYEE_FULL_NAME != REVISION_USER_FULL_NAME  -- someone else made the change
AND ENTITY_TYPE = 'Punch'
AND REVISION_TYPE = 'Delete'
```

Classify these rows as: `ACTOR_GROUP` = value from `REVISION_USER_FUNCTION_ACCESS_PROFILE` mapping (likely `LOCAL_HR`), `BUCKET = 'B'`, `WORK_TYPE = 'Punch'`.

#### 15.0.4 WFM Datasource Note

WFM-group users (`ACTOR_GROUP = 'WFM'`) use both `Timecard Editor` and `Default` as their `DATASOURCE`. Keep this classification in the base layer for dependency analysis, but exclude WFM rows from HR KPI reporting because Workforce Management is not part of HR workload.

#### 15.0.5 VTO Exception Comment Pattern

`Exception Comment` rows where `NOTE_TEXT` matches the pattern `VTO per OM [name] [ticket#]` indicate a specific HR documentation workflow (VTO granted by Operations Manager, documented in UKG by HR). These should be parsed and tagged as:
- `WORK_TYPE = 'Exception Comment'`  
- `BUCKET = 'C'`  
- `NOTE_CATEGORY = 'VTO Authorization'`

This enables separate tracking of VTO documentation volume as a proxy for VTO activity.

#### 15.0.6 Group Edits Datasource

Some `Mark as reviewed` rows use `DATASOURCE = 'Group Edits'` instead of `'Timecard Editor'`. This indicates a bulk approval action (HR reviewed multiple timecards at once). Tag as `DATASOURCE_TYPE = 'Bulk'`. These are higher-efficiency actions and should be noted in user-level baselines.

---

### 15.1 Data Flow

```
UKG Timecard Audit Feed
        ↓
Snowflake UKG Raw / Stage Tables
        ↓
Snowflake Gold Views (GOLD_V_UKG_AUDIT, GOLD_V_PEOPLE, etc.)
        ↓
ORBIT HR Workload Lens Snowflake Views
  ├── V_HWL_ACTOR_GROUP_WEEK       ← Ownership split, WoW
  ├── V_HWL_WORK_TYPE_MIX_WEEK     ← Work type by actor, WoW
  ├── V_HWL_DEFECT_REWORK_WEEK     ← Bucket B / rework KPIs, WoW
  ├── V_HWL_SCHEDULE_TOUCH_WEEK    ← Section 12 schedule KPIs
  ├── V_HWL_USER_BASELINE_WEEK     ← Per-user actions, hours
  ├── V_HWL_TM_MISSED_PUNCH_WEEK   ← Engagement flag inputs
  ├── V_HWL_SITE_SUMMARY_WEEK      ← Site-grain all KPIs + WoW
  └── V_HWL_NETWORK_SUMMARY_WEEK   ← Network-grain rollup
        ↓
Phoenix / ORBIT Agent
  ├── Reads all V_HWL_* views for prior Sun–Sat window
  ├── Applies action generation rules (Section 10)
  ├── Calls LLM to write Executive Summary and Recommended Actions
  └── Assembles final report document
        ↓
Published Output (Confluence / email / shared location)
```

### 15.2 Run Schedule

| When | What |
|---|---|
| **Monday 06:00 ET** | ORBIT agent triggers on schedule; reads Sun–Sat prior week |
| **Monday 07:00 ET** | Report available to primary consumers |
| **Ad hoc** | Any authorized user can trigger a re-run for a custom date range |

### 15.3 POC vs. Production Path

| | POC (Now) | Production |
|---|---|---|
| **Platform** | Phoenix / ORBIT directly on Snowflake UKG views | Same ORBIT agent, hardened with monitoring and alerting |
| **Data** | Pilot FC + Rx sites (TBD with HR leadership) | Full FC + Rx + CVC + CC network |
| **Governance** | Manual review; rules iterated in config | Formal change management via EPA + ORBIT product team |
| **Phase II** | Not in scope | SNOW ticket tables in Snowflake; integrated views |

### 15.4 Data Quality Principles

- **Self-service filter:** Use `EMPLOYEE_FULL_NAME = REVISION_USER_FULL_NAME` to identify self-edits (see 15.0.1 and 15.5).
- **Missed punch deduplication:** Apply Section 15.0.2 dedup key in `V_HWL_TM_MISSED_PUNCH_WEEK` only.
- **Deleted-row logic:** Align with DPP/Bubble standards — do not count logically deleted rows unless explicitly computing delete rate.
- **Reporting week convention:** `REPORTING_WEEK_START` = Sunday 00:00:00 ET for all time windows.
- **TM headcount denominator:** Use `AVG(tm_headcount)` per week from `EDLDB.UKG.V_PEOPLE`, not a point-in-time snapshot.
- **Attribution:** Each audit row maps to exactly one `ACTOR_GROUP` via the CASE logic in Section 5. If `ACCESS_PROFILE` is null or unmapped, classify as `Other` and surface in a data quality alert.
- **Date key:** Use `PARTITION_DATE` (`ENTITY_EVENT_DATE`) for business week assignment; use `AUDIT_TIME_STAMP` (`REVISION_DATE`) for lag metrics.

### 15.5 Reference Query — Snowflake

This is the canonical SQL used to generate the base audit dataset. All ORBIT Snowflake views (`V_HWL_*`) are built on top of this query pattern.

**Source tables:**

| Alias | Table | Purpose |
|---|---|---|
| `a` | `EDLDB.PEOPLE_ANALYTICS_SANDBOX.UKG_V_TIMECARD_AUDIT` | Raw UKG timecard audit rows |
| `p` | `EDLDB.UKG.V_PEOPLE` | Employee profile (name, status, supervisor, org path) |
| `rev` | `EDLDB.UKG.V_PEOPLE` | Revision user profile (access profile, name) |
| `mp` | `EDLDB.UKG.V_TIMECARD_EXCEPTION` | Missed punch exceptions |

**Output columns:**

| Column | Description |
|---|---|
| `ACTOR_GROUP` | Granular label (COE, LOAA, TM, TM (Self-Punch), Local HR, Local Ops, WFM, HRSS) — for drill-downs |
| `WBR_ACTOR_GROUP` | Base actor rollup. HR KPI tables filter this down to Local HR, HRSS, and Local Ops only. |
| `WBR_SITE_GROUP` | FC / Rx / CVC / CC — Corp sites excluded via `WHERE IS NOT NULL` |
| `EDIT_TARGET` | Self / Other — self-service detection flag |
| `MISSING_PUNCH_FLAG` | Yes / No — dedupe on [(EMPLOYEE_ID, ENTITY_EVENT_DATE, MISSING_PUNCH_TYPE)](file:///C:/Users/kenne/.gemini/antigravity/scratch/generate_wbr_stats.py#231-243) before counting |

```sql
-- ============================================================================
-- DEDUPLICATION DOCUMENTATION
-- ============================================================================
-- ROOT CAUSE: UKG_V_TIMECARD_AUDIT is a table (not a view) that receives daily 
-- incremental loads. Each daily load appends new records WITHOUT deduplicating 
-- against existing data. This causes the same audit event to appear multiple 
-- times — once per daily load since the event occurred.
--
-- DEDUPLICATION APPROACH:
--   - Use ROW_NUMBER() partitioned by AUDIT_ID + AUDIT_REVISION_ID
--   - Keep only the earliest load (rn = 1) to get the original record
--   - V_PEOPLE has duplicate person records with changing data (status, supervisor)
--     so we dedupe using highest PERSON_ID to get LATEST employee info
-- ============================================================================

WITH audit_deduped AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY AUDIT_ID, AUDIT_REVISION_ID 
            ORDER BY LOAD_DTTM ASC
        ) AS rn
    FROM EDLDB.PEOPLE_ANALYTICS_SANDBOX.UKG_V_TIMECARD_AUDIT
    -- DYNAMIC 13-WEEK / YTD WINDOW
    WHERE PARTITION_DATE >= '2026-01-01'
      AND PARTITION_DATE < DATEADD('week', 0, DATE_TRUNC('week', CURRENT_DATE))
),

people_deduped AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY PERSON_NUMBER 
            ORDER BY PERSON_ID DESC
        ) AS prn
    FROM EDLDB.UKG.V_PEOPLE
),

base AS (
    SELECT
        -- Employee (whose timecard was edited)
        a.PERSON_NUMBER                                                          AS EMPLOYEE_ID,
        p.FIRST_NAME || ' ' || p.LAST_NAME                                      AS EMPLOYEE_FULL_NAME,
        p.EMPLOYMENT_STATUS                                                      AS EMPLOYEE_STATUS,
        p.SUPERVISOR_FULL_NAME                                                   AS REPORTS_TO,
        REGEXP_SUBSTR(p.PRIMARY_ORG_PATH_TXT, '- ([A-Z0-9]{3,5})/', 1, 1, 'e') AS BUILDING_LOCATION,

        -- Revision User (who made the change)
        a.AUDIT_REVISION_USER_PERSON_NUMBER                                      AS REVISION_USER_ID,
        rev.USER_NAME                                                            AS REVISION_USER,
        rev.FIRST_NAME || ' ' || rev.LAST_NAME                                  AS REVISION_USER_FULL_NAME,
        rev.ACCESS_PROFILE                                                       AS REVISION_USER_FUNCTION_ACCESS_PROFILE,

        -- Actor Group (granular — for drill-downs)
        CASE
            WHEN p.FIRST_NAME||' '||p.LAST_NAME = rev.FIRST_NAME||' '||rev.LAST_NAME THEN 'TM'
            WHEN rev.ACCESS_PROFILE = 'Super Access No Wages'                                                 THEN 'Automation'
            WHEN rev.ACCESS_PROFILE IN ('Leave Support', 'Company Admin TMDM', 'Team Member Services',
                                        'Super Access')                                                        THEN 'HRSS'
            WHEN rev.ACCESS_PROFILE IN ('Employee Basic', 'Employee Basic- Pharmacy', 'Training Basic',
                                        'IT Admin', 'Training + Safety', 'Advanced Scheduler Lead',
                                        'Advanced Scheduler Workforce Analyst', 'Facilities')                 THEN 'TM'
            WHEN rev.ACCESS_PROFILE IN ('Company Admin Site Specific', 'Workers Compensation')                THEN 'Local HR'
            WHEN rev.ACCESS_PROFILE IN ('Manager Basic', 'Manager Basic With Punch&Schedule Edits',
                                        'Practice Manager', 'Facilities Manager')                             THEN 'Local Ops'
            WHEN rev.ACCESS_PROFILE = 'Workforce Reporting'                                                   THEN 'WFM'
            ELSE 'Other'
        END AS ACTOR_GROUP,

        -- WBR Actor Group (base rollup before the HR scope filter removes Team Member, Automation, Other, and WFM)
        CASE
            WHEN p.FIRST_NAME||' '||p.LAST_NAME = rev.FIRST_NAME||' '||rev.LAST_NAME THEN 'Team Member'
            WHEN rev.ACCESS_PROFILE = 'Super Access No Wages'                                                 THEN 'Automation'
            WHEN rev.ACCESS_PROFILE IN ('Leave Support', 'Company Admin TMDM', 'Team Member Services',
                                        'Super Access')                                                        THEN 'HRSS'
            WHEN rev.ACCESS_PROFILE IN ('Employee Basic', 'Employee Basic- Pharmacy', 'Training Basic',
                                        'IT Admin', 'Training + Safety', 'Advanced Scheduler Lead',
                                        'Advanced Scheduler Workforce Analyst', 'Facilities')                 THEN 'Team Member'
            WHEN rev.ACCESS_PROFILE IN ('Company Admin Site Specific', 'Workers Compensation')                THEN 'Local HR'
            WHEN rev.ACCESS_PROFILE IN ('Manager Basic', 'Manager Basic With Punch&Schedule Edits',
                                        'Practice Manager', 'Facilities Manager')                             THEN 'Local Ops'
            WHEN rev.ACCESS_PROFILE = 'Workforce Reporting'                                                   THEN 'WFM'
            ELSE 'Other'
        END AS WBR_ACTOR_GROUP,

        -- Self vs Others flag
        CASE WHEN p.FIRST_NAME||' '||p.LAST_NAME = rev.FIRST_NAME||' '||rev.LAST_NAME
             THEN 'Self' ELSE 'Other' END                                        AS EDIT_TARGET,

        -- Audit Details
        a.AUDIT_TIME_STAMP       AS REVISION_DATE,
        a.PARTITION_DATE         AS ENTITY_EVENT_DATE,
        a.AUDIT_TYPE             AS ENTITY_TYPE,
        a.AUDIT_REVISION_TYPE    AS REVISION_TYPE,
        a.AUDIT_PAYCODE_NAME     AS PAYCODE_NAME,
        a.AUDIT_COMMENT_TEXT     AS COMMENT,
        a.AUDIT_NOTE_TEXT        AS NOTE_TEXT,
        a.AUDIT_DATASOURCE       AS DATASOURCE,
        a.AUDIT_AMOUNT_HOURS     AS AMOUNT_HOURS,

        -- Punch-specific fields
        a.TKAUDIT_PUNCH_TIME     AS PUNCH_TIME,
        a.TKAUDIT_PUNCH_OVERRIDE AS PUNCH_OVERRIDE_TYPE,
        a.TKAUDIT_PUNCH_DELETED  AS PUNCH_DELETED,

        -- Missing Punch Flag (deduplicated, excludes terminated employees)
        CASE WHEN mp.HAS_MISSING_PUNCH = 1 AND p.EMPLOYMENT_STATUS = 'Active' THEN 'Yes' ELSE 'No' END AS MISSING_PUNCH_FLAG

    FROM audit_deduped a
    JOIN      people_deduped p   ON  a.PERSON_NUMBER = p.PERSON_NUMBER AND p.prn = 1
    LEFT JOIN people_deduped rev ON  a.AUDIT_REVISION_USER_PERSON_NUMBER = rev.PERSON_NUMBER AND rev.prn = 1
    LEFT JOIN (
        SELECT PERSON_ID, DATE(EVENT_DATE) AS EVENT_DATE, 1 AS HAS_MISSING_PUNCH
        FROM EDLDB.UKG.V_TIMECARD_EXCEPTION
        WHERE EXCEPTION_TYPE_NAME IN ('Missed In Punch', 'Missed Out Punch')
        GROUP BY PERSON_ID, DATE(EVENT_DATE)
        HAVING COUNT(DISTINCT EXCEPTION_ID) >= 1
    ) mp ON mp.PERSON_ID = p.PERSON_ID AND mp.EVENT_DATE = a.PARTITION_DATE
    WHERE a.rn = 1
)

SELECT
    b.*,

    -- WBR Site Group (FC / Rx / CVC / CC — Corp excluded)
    CASE
        WHEN BUILDING_LOCATION IN ('AVP1','AVP2','BNA1','CFC1','CLT1','DAY1',
                                   'DFW1','HOU1','MCI1','MCO1','MDT1','PHX1','RNO1')          THEN 'FC'
        WHEN BUILDING_LOCATION IN ('AVP4','AVP5','AVP6','DFW5','DFW8',
                                   'MCO4','MCO5','PHX2','PHX5',
                                   'SDF2','SDF4','SDF5','SDF6')                               THEN 'Rx'
        WHEN BUILDING_LOCATION IN ('ATLA','ATLB','ATLC','ATLD','AUSA',
                                   'DENA','DENB','DEND','DFWA','DFWB',
                                   'FLLA','FLLB','FLLC','FLLD','FLLF',
                                   'IAHA','IAHD','PHXB')                                      THEN 'CVC'
        WHEN BUILDING_LOCATION IN ('AV4V','DF4V','DFW4','FL3V','PH0V','PW0V','SD2V')         THEN 'CC'
        ELSE NULL  -- Corp (BOS1, FLL7, SEA1, MSP2) and unknowns → excluded
    END AS WBR_SITE_GROUP

FROM base b
WHERE WBR_SITE_GROUP IS NOT NULL;
```

> [!NOTE]
> The ORBIT agent parameterizes `<WEEK_START>` and `<WEEK_END>` at runtime (see commented lines above). `WBR_ACTOR_GROUP` is the column to use in all KPI aggregations. `ACTOR_GROUP` retains sub-group granularity (COE vs LOAA vs TM) for drill-down views. Corp sites (BOS1, FLL7, SEA1, MSP2) are excluded via `WHERE WBR_SITE_GROUP IS NOT NULL`.

---

## 16. Feature Table

| Feature | Purpose | Logic | Source | Phase | Status |
|---|---|---|---|---|---|
| Ownership Split – Group Level | Baseline and track who is doing timecard work | Actor group classification from profile mapping; % by group per site-week | UKG Audit + role mapping table | I | Planned |
| Work Type Mix | Show how each group spends time across event types | Entity Type taxonomy per actor group × work type | UKG Audit + taxonomy table | I | Planned |
| Defect Rate (Bucket B) | Core quality signal | Bucket B classification; rate vs. total | UKG Audit + bucket mapping | I | Planned |
| Rework Rate (Edit/Delete) | Correction/rework trend | Edit + Delete rows ÷ total | UKG Audit | I | Planned |
| Punch Defect Rate | Punch-specific quality signal | Punch rework ÷ total punch | UKG Audit | I | Planned |
| Schedule Touch & Correction | Schedule stability signal | Bucket D rows; schedule-specific sub-KPIs | UKG Audit (schedule entity types) | I | Planned |
| Schedule → Paycode Chain | Cascading defect signal | Schedule touch followed by PCE ≤ 24h | UKG Audit (joined on employee+date) | I | Planned |
| Lag & Late Correction Rate | Process discipline | REVISION_DATE − ENTITY_EVENT_DATE; >7d threshold | UKG Audit | I | Planned |
| Individual HR User Baseline | Training and automation targeting | Per-user actions, estimated hours, top work types | UKG Audit + HR roster | I | Planned |
| TM Engagement Flag List | Missed punch pattern identification | Threshold rules (Section 10.1) with LLM-generated conversation context | UKG Audit | I | Planned |
| Comment Discipline Rate | AI-readiness and governance signal | Non-null, non-empty COMMENT % for Punch/PCE/Schedule | UKG Audit | I | Planned |
| Automation Share & Automation→Correction | Automation effectiveness | SYSTEM actor %; A→B conversion rate | UKG Audit | I | Planned |
| Service Tier Misrouting | Routing quality | Tier mapping + actor vs. intended owner comparison | UKG Audit + tier mapping table | I | Planned |
| DPMO – UKG Events | Normalized defect density for cross-site comparison | Bucket B / total × 1,000,000 | UKG Audit | I | Planned |
| WBR-Style Report (Phoenix) | Weekly deliverable | ORBIT agent report generation | All Phase I views | I | Planned |
| AI Executive Summary | Plain-language narrative | LLM reads KPI data; generates narrative per prompt | All Phase I views | I | Planned |
| Recommended Actions | Automated action list | Threshold rules (Section 10) + LLM | All Phase I views | I | Planned |
| DPMO – Tickets | Ticket defect density | Ticket defect flags ÷ total tickets × 1,000,000 | SNOW via Snowflake | II | Future |
| Total HR Workload (UKG + SNOW) | Combined workload view | Employee-Day Cases + ticket counts | UKG + SNOW Snowflake | II | Future |
| Ticket–Timecard Overlap | Cross-signal correlation | Join on employee + site + time window | UKG + SNOW Snowflake | II | Future |
| Non-Timecard HR Work % | Workload beyond timecards | Tickets with no UKG footprint | SNOW | II | Future |
| Misrouting Rate – Tickets | SNOW routing quality | Ticket assignment vs. intended owner | SNOW + tier mapping | II | Future |

---

## 17. Success Metrics & Targets

Baseline values to be set after the first 4-week network run. The table below defines the KPIs and the direction of improvement. Specific numeric targets to be agreed with HR leadership.

| # | KPI | Direction | Baseline (TBD) | Target (TBD) |
|---|---|---|---|---|
| 1 | Total Actions per TM (weekly) | ↓ | — | — |
| 2 | Defect Actions per TM (weekly) | ↓ | — | — |
| 3 | Rework Actions per TM (weekly) | ↓ | — | — |
| 4 | Defect Rate % | ↓ | — | — |
| 5 | Rework Rate % | ↓ | — | — |
| 6 | Punch Defect Rate % | ↓ | — | — |
| 7 | Schedule Touch Rate per TM | ↓ | — | — |
| 8 | Unplanned Schedule Change Rate % | ↓ | — | — |
| 9 | Automation → Correction Rate % | ↓ | — | — |
| 10 | Comment Discipline Rate % | ↑ | — | — |
| 11 | Tier 1 Correct Routing % | ↑ | — | — |
| 12 | Tier 1 Misrouted to Local HR % | ↓ | — | — |
| 13 | Estimated Hours Burned (weekly) | ↓ | — | — |
| 14 | Hours Saved vs. Baseline (cumulative) | ↑ | — | — |
| 15 | DPMO – UKG Events | ↓ | — | — |
| 16 | OBR Site Coverage % | ↑ | — | 100% |
| 17 | Chronic Missed Punch Rate % | ↓ | — | — |
| *(Phase II)* | DPMO – Tickets | ↓ | — | — |
| *(Phase II)* | Total HR Workload per TM | ↓ | — | — |

---

## 18. Non-Goals

The following are explicitly out of scope for Phase I and the initial production release:

- **Disciplinary workflows:** This lens does not initiate, recommend, or track disciplinary outcomes. Engagement flags are for coaching conversations only.
- **Replacing attendance policy tools:** This is a measurement and insight layer, not a policy enforcement system.
- **Real-time / intra-day dashboards:** The product is a weekly batch report. Intra-day use cases are future scope.
- **ServiceNow ticket integration (Phase I):** Fully scoped to Phase II.
- **Automated corrections:** Phoenix reads and reports; it does not write back to UKG.
- **Benefits, comp, or non-timekeeping HR processes (Phase I):** Phase I is Time & Attendance only.

---

## 19. Open Questions & Decisions Needed

| # | Question | Owner | Priority |
|---|---|---|---|
| 1 | **Final product name** — "ORBIT HR Workload Lens" or alternative? | HR Leadership | Low |
| 2 | **BNA1 grouping** — confirm 1G vs. 2G classification | HR Ops | High |
| 3 | **TM headcount denominator** — active employees only, or all on roster? Define "average" (daily average or week-end snapshot)? | EPA / HRIS | High |
| 4 | **Pilot site list** — which FC and Rx sites for the POC baseline? Target: 3–4 FC + 2 Rx groups | HR Leadership | High |
| 5 | **Defect category v1 taxonomy** — use Entity Type only, or add reason code / note text parsing? | ORBIT Product + EPA | Medium |
| 6 | **Missed punch threshold tuning** — are the thresholds in Section 10.1 correct, or should they be adjusted for site size or role type? | HR + Local HR leads | Medium |
| 7 | **ServiceNow readiness (Phase II)** — when will SNOW ticket tables be available in Snowflake with aligned site and employee keys? | Data Engineering | Medium |
| 8 | **Comment discipline required fields** — which event types require a comment per current policy? Define the denominator precisely. | HR Policy / TMDM | Medium |
| 9 | **LOAA data validation** — confirm whether COE-LOA team uses UKG or a separate leave platform for case tracking; if separate, how to reconcile. | COE-LOA + TMDM | High |
| 10 | **Numeric targets** — agree on specific target values for all KPIs in Section 17 after 4-week baseline is established | HR Leadership + EPA | Medium |
| 11 | **Update cadence** — Monday 06:00 ET confirmed? Any sites in non-ET time zones that affect the Sunday–Saturday window? | HR Ops / Engineering | Low |
| 12 | **Report publishing location** — Confluence, email distribution, SharePoint, or Phoenix portal? | HR Transformation | Low |
| 13 | **[KNOWN ISSUE] UKG Sandbox Data Gap (Jan 19 - Feb 15)** — The `UKG_V_TIMECARD_AUDIT` sandbox table is missing complete daily partitions for this 4-week period. A hybrid approach using the punch table was tested but fails because punch telemetry does not capture paycodes/schedules (Bucket B rework). An email request was submitted to the EDS team by Kenny Wallace on 2/21/2026 to execute a historical backfill to populate the missing data. | Data Engineering (EDS) | High |

---

## 20. Recommended Next Steps

### Immediate (Weeks 1–2)
1. **Confirm pilot site list** with HR leadership for the 4-week baseline run.
2. **Resolve LOAA data question** — understand what system COE-LOA uses and whether UKG reflects their work.
3. **Finalize actor group → ACTOR_GROUP mapping table** in Snowflake; validate against current UKG profile list.
4. **Agree on defect / work type taxonomy v1** (Section 6) with TMDM and EPA.

### Near-Term (Weeks 3–6)
5. **Run 4-week baseline** for pilot sites; generate baseline values for all KPIs in Section 17.
6. **Review baseline with HR leadership** to set numeric targets and traffic light thresholds.
7. **Design and test the ORBIT agent** report structure (Sections 1–4) against pilot site data.
8. **Validate missed punch engagement flag thresholds** (Section 10.1) with local HR leads; tune if needed.

### Medium-Term (Weeks 7–12)
9. **Roll out to full FC + Rx + CVC + CC network** — harden Snowflake views, governance, and monitoring.
10. **Integrate into HR WBR cadence** — agree on meeting format and how Recommended Actions are actioned and tracked.
11. **Identify top 3 AI automation candidates** from high-rework, high-volume defect patterns (e.g., punch suggestions, auto-coding for weather pay).
12. **Begin Phase II scoping** with Data Engineering for ServiceNow Snowflake availability.

### Long-Term (Months 4–6)
13. **Phase II delivery** — extend ORBIT agent to consume SNOW ticket data; add Phase II KPIs and report sections.
14. **DPMO alignment** — finalize DPMO – Tickets definition with EPA for full HR OBR consistency.
15. **Automation pilots** — launch first AI-assisted correction flow (e.g., punch suggestion); measure Automation → Correction Rate before and after.

---

## 21. Appendix: Glossary

| Term | Definition |
|---|---|
| **Governance Action** | Expected, compliant activity (approvals, reviews, exception documentation). No error or correction involved. Tracked separately from rework. |
| **Correction / Rework** | Action that changes a pay or attendance outcome on a previously closed record. Always a defect. |
| **Documentation** | Required comment/note that doesn't change a pay outcome (e.g. adding a reason code to a punch edit). |
| **Schedule Touch** | Action on an employee's schedule template or shift assignment. |
| **DPMO** | Defects Per Million Opportunities — normalizes defect density for volume comparison across sites. |
| **Employee-Day Case** | Distinct (site, employee_id, entity_event_date) tuple with ≥1 audit row. The core unit of HR timecard work. |
| **ENTITY_EVENT_DATE** | The business date on which the time event (punch, absence, etc.) occurred. |
| **Friction Time Cost** | An estimate of the raw labor hours consumed by timecard rework. Calculated by weighting each UKG action by complexity (e.g. Hist Correction = 5 mins, Standard Edit = 1 min). |
| **FTE Hours** | Full-Time Equivalent (FTE) Hours translates Friction Time Cost into real labor impact (e.g., 40 FTE Hours = the equivalent of one person working full-time for a week on manual data entry). |
| **Lag** | `REVISION_DATE − ENTITY_EVENT_DATE` — how many days after the event the action was taken. |
| **Late Correction** | A Bucket B action with lag > 7 calendar days. |
| **MJT** | Manager Justified Time — a manager override of an employee's scheduled time to record actual time worked. |
| **Missed Punch** | A UKG exception indicating an expected punch (In or Out) was not recorded. |
| **ORBIT** | Phoenix's agentic report/analysis framework. |
| **POC** | Proof of Concept — the initial Phoenix/ORBIT pilot validating rules and narratives before full production deployment. |
| **TM** | Team Member — front-line employee. As an ACTOR_GROUP, represents employee self-service actions in UKG. |
| **WBR** | Weekly Business Review — Chewy's standard operational review cadence. |
| **WoW** | Week-over-Week — the change in a metric from the prior week to the current week. |
