# Technical Design Document: ORBIT HR Workload Lens

**Product:** Workload Lens (Phase I — Time & Attendance / UKG)
**Program:** ORBIT · Pillar 2 (Design & POC)
**Status:** Draft
**Version:** 1.0
**Last Updated:** 2026-03-03
**Owner:** Kenny Wallace, ORBIT Program Lead
**Engineering Handoff To:** TBD
**Platform:** Phoenix (LLM Agent) → Snowflake (Data Layer)

---

## 1. Architecture Overview

Workload Lens is a Phoenix-hosted LLM agent that generates a weekly Operational Business Review (OBR) from UKG timecard audit data stored in Snowflake. The architecture separates data computation (Snowflake SQL) from narrative generation (Phoenix LLM), with a strict contract between the two layers.

### 1.1 System Components

**Snowflake (Data Layer):** Stores all raw source data, deduplication logic, classification rules, and KPI computation. The agent executes 8 immutable SQL queries in sequence. One pre-materialized view (`V_HWL_WEEKLY_SITE_METRICS`) provides 13-week baseline statistics. Target state replaces all inline CTEs with 8 governed `V_HWL_*` views.

**Phoenix Agent (Presentation & Reasoning Layer):** Receives SQL result sets, applies traffic light thresholds and Top 5 filtering, writes narrative interpretations, and assembles the final OBR markdown report. The agent does not perform arithmetic. All rates, percentages, DPMO, and spike flags are pre-calculated by Snowflake.

**Delivery Layer:** OBR published to Confluence and/or email. PII-sensitive engagement list (Q8) delivered separately through restricted channels.

### 1.2 Design Principles

**SQL is immutable.** The agent executes queries verbatim and never modifies, optimizes, or rewrites them. If a query needs improvement, the change goes through the data engineering review process, not the agent prompt.

**Snowflake computes, the agent reasons.** Every number in the OBR is a Snowflake output. The agent's job is to interpret, narrate, and surface patterns, not to calculate.

**Governed views replace inline CTEs.** The current POC runs everything as inline CTEs for rapid iteration. Production will migrate these to materialized Snowflake views with version control, testing, and SLA monitoring.

**WoW deltas belong in the view layer.** Week-over-week comparisons, 4-week rolling averages, and baseline deviations should be pre-computed in production views so the agent reads them as columns rather than deriving them from raw data.

---

## 2. Current State: POC Architecture

### 2.1 Query Pipeline

The agent executes 8 queries in strict sequence (Q1 → Q8). Each query is self-contained with its own deduplication CTEs, classification logic, and aggregation.

```
Q1: Network KPI Summary (1 row)                    → Section 1
Q2: Enterprise View by BU × Actor Group (~20 rows)  → Section 2.1
Q3: BU KPI Split with Spike Flags (~6 rows)         → Section 2.2
Q4: Top Paycode Categories by BU (~80 rows)          → Sections 2.3-2.7
Q5: Historical Correction Root Cause (~5 rows)       → Section 4
Q6: Site-Level Defect Stats with Spikes (~50 rows)   → Section 5
Q7: Comment Compliance by BU (~5 rows)               → Section 6
Q8: Missed Punch Engagement (0-500+ rows)            → Separate PII deliverable
```

### 2.2 Shared CTE Pattern

Every query (Q1 through Q7) repeats the same CTE preamble:

1. `people_deduped` — ROW_NUMBER on PERSON_NUMBER, keep latest PERSON_ID
2. `audit_deduped` — ROW_NUMBER on (AUDIT_ID, AUDIT_REVISION_ID), keep earliest LOAD_DTTM
3. `comments_by_revision` — LISTAGG comments grouped by AUDIT_REVISION_ID + PERSON_NUMBER
4. `missed_punch_counts` — Daily COUNT(DISTINCT SHIFT_ID) from V_TIMECARD_EXCEPTION
5. `weekly_missed_totals` — SUM of daily counts filtered to reporting week
6. `base` — Full derived field computation (all Buckets, Actor Groups, Site Groups, Friction, DPMO inputs)
7. `hr` — Filtered base: self-service excluded, automation excluded, WFM excluded, corporate excluded, Team Member/Other excluded

Q8 is standalone and queries V_TIMECARD_EXCEPTION directly.

### 2.3 Known Technical Debt

**CTE repetition.** The same deduplication and classification logic is repeated verbatim in 7 queries. Any classification rule change requires updating all 7 queries simultaneously. Production views will centralize this.

**Standard deviation approximation.** For BU and network rollups, the agent approximates the combined standard deviation by averaging site-level SDs from `V_HWL_WEEKLY_SITE_METRICS`. This is a statistical simplification. The correct approach would compute the pooled standard deviation from the raw site-week observations, but this is acceptable for POC given the small number of sites per BU.

**DPMO scale mismatch.** The current agent SQL computes DPMO as `× 1000` (per thousand). PRD v2.0 standardizes to `× 1,000,000` (per million). The agent SQL and DPMO traffic light thresholds must be updated before production.

**Missing hire date filter.** The v2 agent instructions header claims "new hires filtered" for Q8, but the actual SQL does not implement a hire date exclusion. A `HIRE_DATE` column from `V_PEOPLE` is needed to filter first-week TMs.

**Q8 weekly threshold.** The agent SQL uses `WEEKLY_MISSED_PUNCHES >= 3` (confirmed from the source). Documentation should consistently reference this threshold.

**Phase II resolver proxy.** The weekly ticket CSV extracts do not include a dedicated `Resolved By` field. Current pipeline logic therefore excludes WFM-owned ticket work using `Assignment Group` proxy rules (`Real Time Analyst*`, `WFM*`, and equivalent queue names). This is acceptable for current EPA extracts but should be replaced by a true resolver or owning-team field when available.

### 2.4 Scope Boundary Notes

The HR reporting layer excludes `Team Member`, `Other`, `Automation`, and `WFM`. WFM remains classified in base data for dependency analysis and schedule-root-cause research, but WFM touches are not counted as HR workload.

TM self-service for scope purposes includes:

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

---

## 3. Target State: Production Architecture

### 3.1 V_HWL_* View Migration Plan

Each inline CTE pattern will be migrated to a governed Snowflake view. The views centralize classification logic, eliminate CTE repetition, and pre-compute WoW deltas.

| View | Source Tables | Refresh | Key Columns |
|:---|:---|:---|:---|
| `V_HWL_ACTOR_GROUP_WEEK` | UKG_V_TIMECARD_AUDIT + V_PEOPLE | Weekly (Sunday night) | OBR_ACTOR_GROUP, OBR_SITE_GROUP, TOUCHES, TOUCHES_PRIOR_WEEK, WOW_DELTA, WOW_DELTA_PCT |
| `V_HWL_WORK_TYPE_MIX_WEEK` | UKG_V_TIMECARD_AUDIT + V_PEOPLE | Weekly | ENTITY_TYPE, PAYCODE_CATEGORY, OBR_ACTOR_GROUP, ACTION_COUNT, ESTIMATED_HRS |
| `V_HWL_DEFECT_REWORK_WEEK` | UKG_V_TIMECARD_AUDIT + V_PEOPLE | Weekly | BUILDING_LOCATION, TOTAL_ACTIONS, BUCKET_B_COUNT, DEFECT_RATE_PCT, PRIOR_WEEK_DEFECT_RATE, WOW_DELTA, ROLLING_4WK_AVG |
| `V_HWL_SCHEDULE_TOUCH_WEEK` | TBD (Phase I: not implemented) | Weekly | Schedule-specific KPIs |
| `V_HWL_USER_BASELINE_WEEK` | UKG_V_TIMECARD_AUDIT + V_PEOPLE | Weekly | REVISION_USER_ID, TOTAL_ACTIONS, TOP_WORK_TYPES, FRICTION_HRS |
| `V_HWL_TM_MISSED_PUNCH_WEEK` | V_TIMECARD_EXCEPTION + V_PEOPLE | Weekly | PERSON_ID, BUILDING_LOCATION, WEEKLY_MISSED_PUNCHES, ENGAGEMENT_FLAG, HIRE_DATE |
| `V_HWL_SITE_SUMMARY_WEEK` | UKG_V_TIMECARD_AUDIT + V_PEOPLE | Weekly | All site-level KPIs with WoW deltas, DPMO (×1M), UCL, IS_RED_SPIKE |
| `V_HWL_NETWORK_SUMMARY_WEEK` | V_HWL_SITE_SUMMARY_WEEK | Weekly | Network rollup with WoW deltas |

### 3.2 View Refresh Strategy

Views refresh weekly on Sunday night after the UKG daily load completes. The agent runs Monday at 06:00 ET and reads the refreshed views. If the Sunday load fails, the agent will detect 0 rows on Q1 and halt per guardrail #3.

### 3.3 WoW Delta Columns (Target State)

Each `V_HWL_*` view that feeds a report section should include:

| Column | Type | Description |
|:---|:---|:---|
| `*_THIS_WEEK` | DECIMAL | Current week value |
| `*_PRIOR_WEEK` | DECIMAL | Prior week value |
| `*_WOW_DELTA` | DECIMAL | This week minus prior week |
| `*_WOW_DELTA_PCT` | DECIMAL | (This week / Prior week) × 100 - 100 |
| `*_ROLLING_4WK_AVG` | DECIMAL | Average of the last 4 completed weeks |
| `*_VS_13WK_BASELINE` | DECIMAL | This week value minus 13-week mean |

The agent reads these columns and narrates improvement/deterioration signals without performing the arithmetic.

---

## 4. Agent Configuration

### 4.1 Phoenix Agent Settings

| Setting | Value |
|:---|:---|
| Trigger | Monday 06:00 ET |
| Reporting Window | Prior Sunday through Saturday |
| Model | Phoenix platform default |
| SQL Execution | Snowflake connector, read-only |
| Max Query Runtime | 120 seconds per query |
| Halt on Error | Yes (all queries except Q8 on 0 rows) |

### 4.2 Agent Guardrails

1. SQL is immutable. Execute verbatim, never modify.
2. Halt on Snowflake error. Report exact error message.
3. Row count sanity check. Halt if Q1 through Q7 return 0 rows.
4. No improvisation. Only use numbers from query results.
5. Hard stop after Section 6. No closing commentary.
6. Sequence is mandatory. Q1 → Q8 in order.

### 4.3 Prompt Architecture

The agent instructions are structured in three phases:

**Phase 1 (Data Queries):** 8 SQL queries with execution rules and expected row counts.
**Phase 2 (Report Format):** Markdown template with placeholders, section-by-section writing guidelines, traffic light rules, and AI Insight trigger conditions.
**Phase 3 (Interactive Drill-Down):** 5-level progressive disclosure rules for follow-up questions after the OBR is published.

---

## 5. Data Contract

### 5.1 Agent SQL → Phoenix Contract

The agent SQL returns structured result sets that the Phoenix agent consumes. Each query has a defined schema that the agent must not modify.

| Query | Expected Columns | Row Count |
|:---|:---|:---|
| Q1 | TOTAL_ACTIONS, DEFECT_RATE_PCT, TOTAL_FRICTION_HRS, MISSING_PUNCH_RATE_PCT, HIST_CORR_RATE_PCT, MEAN_13WK_DEFECT_RATE, SD_13WK_DEFECT_RATE, UCL_13WK_DEFECT_RATE, IS_RED_SPIKE | 1 |
| Q2 | OBR_SITE_GROUP, OBR_ACTOR_GROUP, TOUCHES | ~20 |
| Q3 | GROUP_NAME, ACTION_VOLUME, BUCKET_B_COUNT, DEFECT_PCT, MISSED_PUNCH_COUNT, MISSED_PUNCH_PCT, HIST_CORR_COUNT, HIST_CORR_PCT, UCL_13WK_DEFECT_RATE, IS_RED_SPIKE | ~6 |
| Q4 | BU_OR_GROUP, PAYCODE_CATEGORY, ENTITY_TYPE, ACTION_COUNT, ESTIMATED_HRS | ~80 |
| Q5 | HC_CATEGORY, HC_COUNT | ~5 |
| Q6 | BUILDING_LOCATION, OBR_SITE_GROUP, TOTAL_ACTIONS, BUCKET_B_COUNT, UNIQUE_TMS, DPMO, DEFECT_RATE_PCT, MEAN_13WK_DEFECT_RATE, UCL_13WK_DEFECT_RATE, IS_RED_SPIKE | ~50 |
| Q7 | OBR_SITE_GROUP, HIGH_RISK_ACTIONS, COMMENTS_ADDED, DOCUMENTATION_RATE_PCT | ~5 |
| Q8 | BU, SITE, TM_NAME, TM_ID, MANAGER, MISSED_COUNT, LOGS | 0 to 500+ |

### 5.2 Column Naming Standards

All Snowflake column names use `UPPER_SNAKE_CASE`. Derived metrics include the unit or scale in the name where appropriate (e.g., `DEFECT_RATE_PCT` for percentage, `TOTAL_FRICTION_HRS` for hours, `DPMO` for per-million).

---

## 6. Testing Strategy

### 6.1 POC Testing (Current — Windsurf + CSV)

During Pillar 2, SQL logic is tested against CSV exports pulled from Snowflake. Testing in Windsurf validates:

- Classification rule correctness (Bucket assignment, Actor Group mapping, Paycode Category matching)
- Deduplication behavior (row counts before and after dedup)
- KPI computation accuracy (spot-check against manual calculation)
- Agent prompt quality (narrative tone, traffic light application, Top 5 filtering)

### 6.2 Production Testing (Target — Snowflake + Views)

Before moving to Pillar 3, each `V_HWL_*` view must pass:

- Schema validation (all expected columns present with correct types)
- Row count sanity (non-zero for all active reporting weeks)
- KPI equivalence (view output matches inline CTE output for the same reporting week)
- WoW delta accuracy (manual verification of delta and rolling average calculations)
- Backfill validation (historical data correctly populated for 13-week baseline)

---

## 7. Security and PII

### 7.1 Data Classification

| Data Element | Classification | Handling |
|:---|:---|:---|
| TM Names (Q8 engagement list) | PII | Restricted to private/1:1 delivery channels |
| TM IDs (PERSON_NUMBER) | PII | Same as above |
| Manager Names | PII | Same as above |
| Site-level KPIs | Internal/Confidential | OBR distribution list |
| Network-level KPIs | Internal/Confidential | OBR distribution list |

### 7.2 Agent Guardrails for PII

The agent must never expose TM names in shared channels. The engagement list (Q8 output) is delivered separately from the main OBR and restricted to authorized recipients.

---

## 8. Migration Path: POC → Production

### 8.1 Pillar 2 Gate Requirements

Before exiting Pillar 2 (Design & POC), the following must be complete:

| Deliverable | Status |
|:---|:---|
| PRD v2.0 | Complete |
| Data Map and Classification Declaration v2.0 | Complete |
| Technical Design Doc v1.0 | This document |
| Value Scorecard baseline | In progress |
| POC Agent Instructions (updated with v2.0 changes) | In progress |
| CSV-based testing of all 8 queries | In progress |
| Agent prompt quality validation | In progress |

### 8.2 Pillar 3 (Build) Entry Requirements

| Requirement | Description |
|:---|:---|
| V_HWL_* view DDL | All 8 views defined with schema, refresh schedule, and ownership |
| DPMO formula updated | × 1,000,000 in all views and queries |
| Actor Group SQL updated | Workers Comp → Local HR, Super Access No Wages exclusion, WFM exclusion from HR reporting layer |
| DPMO threshold calibration | 4 weeks of baseline data collected at ×1M scale |
| Hire date field confirmed | V_PEOPLE HIRE_DATE column availability verified with data engineering |
| WoW delta columns | Production views include pre-computed deltas |
| Backfill request | Jan 19 to Feb 15 data gap resolved in UKG_V_TIMECARD_AUDIT |

### 8.3 Pillar 4 (Launch & Measure) Entry Requirements

| Requirement | Description |
|:---|:---|
| Agent deployed to production Phoenix | Monday 06:00 ET automated trigger configured |
| OBR delivery pipeline | Confluence and/or email automation |
| Monitoring | View refresh SLA alerts, agent error halting notifications |
| Stakeholder onboarding | Site HR leads trained on OBR interpretation |

---

## 9. Open Engineering Questions

| # | Question | Owner | Target Date |
|:---|:---|:---|:---|
| 1 | Does `V_PEOPLE` include a `HIRE_DATE` column? If not, what is the source table for hire date? | Data Engineering | TBD |
| 2 | What is the refresh SLA for `V_HWL_WEEKLY_SITE_METRICS`? Can we guarantee Sunday night completion? | Data Engineering | TBD |
| 3 | Is the Jan 19 to Feb 15 UKG_V_TIMECARD_AUDIT backfill on the EDS roadmap? | EDS | Submitted 2/21/2026 |
| 4 | Can Phoenix support scheduled triggers (Monday 06:00 ET) natively, or does this require an external orchestrator? | Platform Engineering | TBD |
| 5 | What is the max query runtime allowed by the Phoenix-Snowflake connector? | Platform Engineering | TBD |

---

## 10. Version History

| Version | Date | Author | Changes |
|:---|:---|:---|:---|
| 1.0 | 2026-03-03 | Kenny Wallace / ORBIT | Initial Technical Design Doc. Captures current POC architecture, target state view migration plan, data contract, testing strategy, and production migration path. |
