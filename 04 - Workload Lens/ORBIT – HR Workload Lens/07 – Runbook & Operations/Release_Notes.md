# Workload Lens Agent Instructions — v2.0 Change Log

**Date:** 2026-03-03
**Author:** ORBIT Program (AI-assisted validation)
**Baseline:** `phoenix_agent_instructions (2).md` (v1.x, Downloads folder)
**Output:** `04 - Workload Lens/phoenix_agent_instructions_v2.md` + `sql/q1–q8`

---

## Purpose

This document tracks every discrepancy found between the original agent instructions and the authoritative PRD v2.0, Technical Design Doc v1.0, and Data Map v2.0. Each item lists the issue, the source of truth, and the resolution applied in v2.0.

---

## Critical Fixes (6)

### C1. Super Access No Wages Mapped to HRSS → Now Excluded as Automation

| | |
|:---|:---|
| **Found in** | Q1–Q7, OBR_ACTOR_GROUP CASE statement |
| **Old behavior** | `Super Access No Wages` grouped with HRSS — inflated HRSS counts |
| **Source of truth** | PRD §3.2, Data Map §5.2 |
| **Fix** | New CASE branch: `WHEN rev.ACCESS_PROFILE = 'Super Access No Wages' THEN 'Automation'` placed *before* the HRSS branch. `hr` CTE filter updated to `NOT IN ('Team Member', 'Other', 'Automation')` |

### C2. Workers Compensation Missing from Local HR

| | |
|:---|:---|
| **Found in** | Q1–Q7, OBR_ACTOR_GROUP CASE statement |
| **Old behavior** | `Workers Compensation` fell through to `Other` and was excluded |
| **Source of truth** | PRD §3.2 v2.0 update |
| **Fix** | `WHEN rev.ACCESS_PROFILE IN ('Company Admin Site Specific', 'Workers Compensation') THEN 'Local HR'` |

### C3. DPMO Uses ×1,000 — PRD Requires ×1,000,000

| | |
|:---|:---|
| **Found in** | Q6, `current_week_metrics` CTE |
| **Old behavior** | `ROUND(s.BUCKET_B_COUNT/NULLIF(s.UNIQUE_TMS*20,0)*1000,2) AS DPMO` |
| **Source of truth** | PRD §5.1, TDD §2.3 (known debt) |
| **Fix** | Changed multiplier to `*1000000` in Q6 |

### C4. DPMO Traffic Light Thresholds Stale at ×1K Scale

| | |
|:---|:---|
| **Found in** | Traffic Light Rules table |
| **Old behavior** | `Site DPMO: ≤20 / 21-50 / >50` (calibrated for ×1K) |
| **Source of truth** | PRD §5.1 — thresholds TBD pending recalibration |
| **Fix** | Set all DPMO thresholds to `TBD`. Added note explaining baseline collection period required. |

### C5. Weekly Missed Punch Threshold Inconsistency

| | |
|:---|:---|
| **Found in** | Q1–Q7 base CTE (MISSING_PUNCH_FLAG) vs Q8 (flagged CTE) |
| **Old behavior** | Q1–Q7 used `>= 4`, Q8 used `>= 3` |
| **Source of truth** | PRD §8 — Weekly Pattern = 3+ missed punch events |
| **Fix** | Aligned Q1–Q7 to `>= 3`, matching Q8 and PRD |

### C6. Historical Correction Comment Not Excluded from Base CTE

| | |
|:---|:---|
| **Found in** | Q1–Q7, base CTE WHERE clause |
| **Old behavior** | Excluded only 3 comment types: `Exception Comment`, `Punch Comment`, `Pay Code Edit Comment` |
| **Source of truth** | PRD §4.1 Bucket G + Data Map §5.1 — four comment types exist |
| **Fix** | Added `'Historical Correction Comment'` to the NOT IN list |

---

## Moderate Fixes (6)

### M7. Report Section Numbering Mismatch

| | |
|:---|:---|
| **Found in** | Guardrails §5 vs Phase 2 template ToC |
| **Old behavior** | Guardrails listed PRD order (4=HC, 5=Hotspots, 6=Comment) but template had 4=Hotspots, 5=HC, 6=Missed Punch |
| **Source of truth** | PRD §6.1 |
| **Fix** | Aligned template to PRD order: 4=Historical Corrections, 5=Hotspots, 6=Event Documentation |

### M8. Q6/Q7 Header Section References Wrong

| | |
|:---|:---|
| **Found in** | Query headers |
| **Old behavior** | Q6 said "Section 4", Q7 said "Section 5" |
| **Fix** | Q6 → "Section 5", Q7 → "Section 6" |

### M9. v2.0 Header Claims New Hires Filtered — They Aren't

| | |
|:---|:---|
| **Found in** | Line 4 of original file |
| **Old behavior** | Header stated "new hires filtered" |
| **Source of truth** | TDD §2.3 — hire date filter not implemented |
| **Fix** | Header now states: "First-week TM hire date filter is **not yet implemented** (pending HIRE_DATE field confirmation)" |

### M10. Section 5 Uses 2 SD for Missed Punch Outliers — PRD Uses 1 SD

| | |
|:---|:---|
| **Found in** | Phase 2 template, Section 5.1 prose |
| **Old behavior** | "Sites exceeding the Mean + 2 Standard Deviations threshold" |
| **Source of truth** | PRD §5.4 — 1 SD UCL for spike detection |
| **Fix** | Changed to "Mean + 1 Standard Deviation (UCL)" throughout Section 5. Reframed as defect rate spike (matches Q6 IS_RED_SPIKE logic) rather than missed punch outlier. |

### M11. Q2–Q7 Missing Two Paycode Category Patterns

| | |
|:---|:---|
| **Found in** | PAYCODE_CATEGORY CASE in Q2–Q7 |
| **Old behavior** | Missing `%pto paid dur%`/`%personal unpd dur%` → UTO deduction, and `%meal break%` → UTO prevention |
| **Source of truth** | PRD §4.3, Data Map §5.4 |
| **Fix** | Added both patterns *before* the generic `%pto%` and `%personal%` matchers in all queries |

### M12. week_window CTE Never Defined

| | |
|:---|:---|
| **Found in** | All queries reference `(SELECT WEEK_START FROM week_window)` |
| **Old behavior** | No documentation of how week_window is provided |
| **Fix** | Added explicit documentation in TRIGGER section: "provided by the `week_window` CTE, which is injected by the Phoenix platform at runtime. It supplies two columns: `WEEK_START` (DATE) and `WEEK_END` (DATE)." |

---

## Minor Fixes (4)

### m13. v2.0 Header Mentions Non-Existent Sections

| | |
|:---|:---|
| **Old behavior** | Referenced "Section 6 is now Defect Reduction Scorecard" and "Section 7 is FC Missed Punch Engagement List" |
| **Fix** | Removed. Header now accurately describes actual v2.0 changes. |

### m14. Guardrail #4 "Phase 2" Ambiguous

| | |
|:---|:---|
| **Old behavior** | "not defined in Phase 2" could be confused with Phase II (ServiceNow integration) |
| **Fix** | Changed to "not defined in this template" |

### m15. Section 5.2 Prose Says "per 1,000" for DPMO

| | |
|:---|:---|
| **Old behavior** | "Defects per 1,000 expected punch opportunities" |
| **Fix** | Changed to "Defects per Million expected punch opportunities" throughout |

### m16. Appendix A Has No Backing Query

| | |
|:---|:---|
| **Old behavior** | Appendix A (Governance by Actor Group) had no data source documented |
| **Fix** | Added data source note: "Derived from Q2 and Q4 results. Governance = Bucket G + Bucket A. Corrections = Bucket B. Hours = count × friction weight ÷ 60." |

---

## Structural Changes

| Change | Rationale |
|:---|:---|
| SQL extracted to individual `sql/*.sql` files | Readability, maintainability, easier diff review |
| `shared_cte_preamble.sql` reference doc added | Documents the repeated CTE logic and v2.0 changes in one place |
| Query-to-section mapping table added | Clear traceability for engineers |
| Engineer Note added for Phoenix configuration | Explicit instructions for embedding SQL into agent prompt |
| **V_HWL_BASE + V_HWL_HR views created** (`sql/views/`) | Centralizes ~140-line shared CTE preamble into 2 governed Snowflake views. Eliminates 7× CTE repetition (~980 lines / ~12K tokens) from agent prompt. |
| **Thin queries created** (`sql/thin/q1–q8*.sql`) | Replacement queries that SELECT from V_HWL_HR instead of embedding inline CTEs. Q2 went from 146 → 4 lines. Q4 from 148 → 6 lines. Q5 from 145 → 4 lines. Total inline SQL in agent prompt reduced from ~1,218 lines to ~238 lines. |
| **Date parameterization changed** | `week_window` CTE replaced with Snowflake session variables `$WEEK_START` / `$WEEK_END`. Phoenix must SET these before query execution. |
| **Fat queries retained** (`sql/q1–q8*.sql`) | Kept for POC regression testing. Not used in Phoenix agent prompt. |
| **Migration guide created** (`sql/views/MIGRATION_GUIDE.md`) | Deployment steps, validation checklist, and rollback instructions for data engineering team. |

---

## Open Items (Not Resolved — Require Engineering Decision)

| Item | Status | Owner |
|:---|:---|:---|
| First-week TM hire date exemption (Q8) | Blocked — needs HIRE_DATE field confirmation from V_PEOPLE | Data Engineering |
| DPMO traffic light thresholds at ×1M scale | TBD — needs 4 weeks of baseline data | ORBIT Program |
| ~~CTE repetition across Q1–Q7~~ | **RESOLVED** — V_HWL_BASE + V_HWL_HR views created, thin queries replace fat queries | Data Engineering |
| SD approximation for BU/Network rollups | Acceptable for POC per TDD §2.3 | Data Engineering |
| V_HWL_WEEKLY_SITE_METRICS WoW delta columns | Target state — not yet implemented | Data Engineering |
| Phoenix session variable support | Confirm Phoenix can execute `SET WEEK_START = ...` before queries | Platform Engineering |
| Q8 site classification duplication | Q8 still inlines the OBR_SITE_GROUP CASE statement (not in V_HWL_BASE because Q8 uses a different pipeline). Production should centralize site lists into a lookup table. | Data Engineering |
