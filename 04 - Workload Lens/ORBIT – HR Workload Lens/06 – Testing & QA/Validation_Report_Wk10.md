# ORBIT HR Workload Lens — Validation Report
## Week 10: March 1–7, 2026

**Generated:** 2026-03-10  
**Source Query:** `sql/validation_3week_hr_dataset.sql`  
**Data Window:** Sunday 2026-03-01 through Saturday 2026-03-07  
**Status:** Pre-deployment validation (views not yet deployed)

> This report documents the validation dataset exported from the standalone query. It mirrors the V_HWL_BASE → V_HWL_HR view pipeline and can be used to validate view output once deployed. Missed punch metrics are **excluded** pending data quality review of V_TIMECARD_EXCEPTION.

---

## 1. Dataset Overview

### Scope

| Parameter | Value |
|:---|:---|
| Date Range | 03/01/2026 – 03/07/2026 (Sun–Sat) |
| Business Units | FC (13 sites), Rx (13 sites), CVC (18 sites), CC (7 sites) |
| Actor Groups Included | Local HR, HRSS, Local Ops, WFM |
| Actor Groups Excluded | Team Member, Other, Automation |
| Self-Service Edits | Excluded |
| Unmapped Sites | Excluded |

### Filters Applied (mirrors V_HWL_HR)

1. `EDIT_TARGET != 'Self'` — removes self-service edits
2. `OBR_SITE_GROUP IS NOT NULL` — removes corporate/unmapped sites (BOS1, FLL7, SEA1, MSP2, etc.)
3. `OBR_ACTOR_GROUP NOT IN ('Team Member', 'Other', 'Automation')` — retains only HR-attributable work

---

## 2. Output Schema (20 Columns)

| # | Column | Type | Description |
|:--|:---|:---|:---|
| 1 | REPORT_WEEK | DATE | Sunday-based week start (computed from ENTITY_EVENT_DATE) |
| 2 | EMPLOYEE_ID | VARCHAR | UKG Person Number of the employee whose timecard was touched |
| 3 | BUILDING_LOCATION | VARCHAR | Site code extracted from PRIMARY_ORG_PATH_TXT (e.g., CLT1, SDF2) |
| 4 | OBR_SITE_GROUP | VARCHAR | Business unit classification: FC, Rx, CVC, or CC |
| 5 | OBR_ACTOR_GROUP | VARCHAR | Who performed the action: Local HR, HRSS, Local Ops, or WFM |
| 6 | EDIT_TARGET | VARCHAR | Always 'Other' (self-service filtered out) |
| 7 | ENTITY_EVENT_DATE | DATE | Calendar date of the timecard event |
| 8 | ENTITY_TYPE | VARCHAR | UKG audit type (Punch, Pay Code Edit, Historical Correction, etc.) |
| 9 | REVISION_TYPE | VARCHAR | Add, Edit, or Delete |
| 10 | PAYCODE_NAME | VARCHAR | Raw UKG paycode name (nullable for punch actions) |
| 11 | PAYCODE_CATEGORY | VARCHAR | Human-readable driver label (see Section 4) |
| 12 | HC_CATEGORY | VARCHAR | Historical Correction root cause bucket (see Section 5) |
| 13 | BUCKET_A | BOOLEAN | TRUE if the action is an Addition (non-rework) |
| 14 | BUCKET_B | BOOLEAN | TRUE if the action is a Correction / Rework (defect) |
| 15 | BUCKET_G | BOOLEAN | TRUE if the action is Governance (approval, review, comment) |
| 16 | FRICTION_SCORE | DECIMAL | Complexity weight: 5.0 (Hist. Corr.), 1.0 (Edit/Delete), 0.5 (other) |
| 17 | HIGH_RISK_REWORK | BOOLEAN | TRUE if the action requires mandatory documentation |
| 18 | HAS_COMMENT | INT | 1 if a comment or note is present, 0 otherwise |
| 19 | COMMENT | VARCHAR | Linked or raw audit comment text |
| 20 | NOTE_TEXT | VARCHAR | Linked or raw audit note text |

---

## 3. KPI Derivation Guide

The following KPIs can be computed directly from the exported CSV. All formulas match the Q1–Q7 thin query logic.

### Section 1: Network KPIs (Q1)

| KPI | Formula | Traffic Light |
|:---|:---|:---|
| **Total Actions** | `COUNT(*)` | — |
| **Defect Rate %** | `SUM(BUCKET_B) / COUNT(*) * 100` | 🟢 ≤25% · 🟡 26–40% · 🔴 >40% |
| **Unique TMs Touched** | `COUNT(DISTINCT EMPLOYEE_ID)` | — |
| **Total Friction Hrs** | `SUM(FRICTION_SCORE) / 60` | — |
| **Hist. Correction Count** | `COUNT(*) WHERE ENTITY_TYPE = 'Historical Correction'` | — |
| **Hist. Correction Rate %** | `Hist. Corr. Count / Total Actions * 100` | 🟢 ≤5% · 🟡 6–10% · 🔴 >10% |

### Section 2: Enterprise BU × Actor (Q2)

| KPI | Formula |
|:---|:---|
| **Touches by BU × Actor** | `GROUP BY OBR_SITE_GROUP, OBR_ACTOR_GROUP` → `COUNT(*)` |

### Section 2 (cont.): BU KPI Split (Q3)

| KPI | Formula |
|:---|:---|
| **BU-Level Defect Rate** | `SUM(BUCKET_B) / COUNT(*) * 100` grouped by `OBR_SITE_GROUP` |
| **BU-Level Friction Hrs** | `SUM(FRICTION_SCORE) / 60` grouped by `OBR_SITE_GROUP` |
| **BU-Level Unique TMs** | `COUNT(DISTINCT EMPLOYEE_ID)` grouped by `OBR_SITE_GROUP` |

### Section 2 (cont.): Top Paycode by BU (Q4)

| KPI | Formula |
|:---|:---|
| **Top 5 Rework Drivers** | Filter `BUCKET_B = TRUE`, then `GROUP BY OBR_SITE_GROUP, PAYCODE_CATEGORY` → `COUNT(*)` → `RANK() ≤ 5` per BU |

### Section 5: Historical Corrections (Q5)

| KPI | Formula |
|:---|:---|
| **HC by Root Cause** | Filter `ENTITY_TYPE = 'Historical Correction'`, then `GROUP BY HC_CATEGORY` → `COUNT(*)` |

### Section 6: Comment Compliance (Q7)

| KPI | Formula | Traffic Light |
|:---|:---|:---|
| **High-Risk Rework Actions** | `COUNT(*) WHERE HIGH_RISK_REWORK = TRUE` | — |
| **Comments Added** | `SUM(HAS_COMMENT) WHERE HIGH_RISK_REWORK = TRUE` | — |
| **Documentation Rate %** | `Comments Added / High-Risk Actions * 100` | 🟢 ≥85% · 🟡 70–84% · 🔴 <70% |

---

## 4. Paycode Category Reference

These human-readable labels are derived from the raw `PAYCODE_NAME` via pattern matching.

| PAYCODE_CATEGORY | Triggered By |
|:---|:---|
| Manual Punch Correction | NULL or blank paycode (punch adds/edits) |
| Time spent manually coding VTO | `%vto%` or `%voluntary%` |
| Time spent manually coding weather-related event | `%weather%` |
| Manual coding missed late arrival | `%late%` |
| Manual coding missed early departure | `%early%` |
| Manual coding No Call No Show | `%ncns%` |
| Manual coding Call Off | `%call off%` |
| Manual coding Sick Time | `%sick%` |
| Manual coding Leave of Absence | `%leave%` |
| Manual coding for early departure/long lunch to deduct UTO | `%pto paid dur%` or `%personal unpd dur%` |
| Manual coding of Paid Time Off | `%pto%` (after dur check) |
| Manual coding to prevent UTO (Meal Break) | `%meal break%` |
| Manual coding of Personal Time | `%personal%` |
| Orphaned Comment | Synthetic — comment row with no parent action |

> **Order matters.** The CASE expression evaluates top-to-bottom. For example, `%pto paid dur%` is checked before the generic `%pto%` pattern.

---

## 5. Historical Correction Root Cause Categories

| HC_CATEGORY | Triggered By | What It Means |
|:---|:---|:---|
| Attendance Enforcement | `%ncns%`, `%late%`, `%early%`, `%call off%` | Manager/HR failed to code attendance events before payroll close |
| Core Pay & Missing Time | `%regular%`, `%overtime%`, `%meal%`, `%pto paid%` | Retroactive payroll deposits for missed regular/premium/OT pay |
| Schedule & Unpaid True-Ups | `%personal%`, `%vto%`, `%weather%`, `%unpaid%` | Broad operational changes (VTO, weather) not processed in time |
| Leave & Compliance Lag | `%leave%`, `%fmla%`, `%loa%`, `%bereavement%` | Standard lag pending documentation (FMLA, accommodations) |
| Other | Everything else | Various other discrepancies |

---

## 6. Bucket Classification Logic

| Bucket | Name | What Counts |
|:---|:---|:---|
| **A** | Additions | Pay Code Edit (Add), Manager Justified Time (Add) — excluding attendance enforcement paycodes |
| **B** | Corrections / Rework | All Punches, Historical Corrections, Edit/Delete on Pay Code Edit or MJT, and MJT Adds for attendance paycodes (late, early, NCNS, call off, unpd) |
| **G** | Governance | Comments (Exception, Punch, Pay Code Edit, Historical Correction), Mark as Reviewed, Manager Approval |

> **Bucket B is the defect numerator.** Defect Rate = Bucket B / Total Actions × 100.

---

## 7. Actor Group Classification

| OBR_ACTOR_GROUP | Access Profiles Mapped |
|:---|:---|
| **HRSS** | Leave Support, Company Admin TMDM, Team Member Services, Super Access |
| **Local HR** | Company Admin Site Specific, Workers Compensation |
| **Local Ops** | Manager Basic, Manager Basic With Punch&Schedule Edits, Practice Manager, Facilities Manager |
| **WFM** | Workforce Reporting |
| **Automation** *(excluded)* | Super Access No Wages |
| **Team Member** *(excluded)* | Employee Basic, Employee Basic- Pharmacy, Training Basic, IT Admin, Training + Safety, Advanced Scheduler Lead, Advanced Scheduler Workforce Analyst, Facilities — plus name-match check |
| **Other** *(excluded)* | Everything else |

---

## 8. Site Classification (51 Sites)

| OBR_SITE_GROUP | Sites |
|:---|:---|
| **FC** (13) | AVP1, AVP2, BNA1, CFC1, CLT1, DAY1, DFW1, HOU1, MCI1, MCO1, MDT1, PHX1, RNO1 |
| **Rx** (13) | AVP4, AVP5, AVP6, DFW5, DFW8, MCO4, MCO5, PHX2, PHX5, SDF2, SDF4, SDF5, SDF6 |
| **CVC** (18) | ATLA, ATLB, ATLC, ATLD, AUSA, DENA, DENB, DEND, DFWA, DFWB, FLLA, FLLB, FLLC, FLLD, FLLF, IAHA, IAHD, PHXB |
| **CC** (7) | AV4V, DF4V, DFW4, FL3V, PH0V, PW0V, SD2V |

---

## 9. Friction Score Weights

| Scenario | Score | Approx. Time |
|:---|---:|:---|
| Historical Correction | 5.0 | ~5 min |
| Edit or Delete on Punch, Pay Code Edit, or MJT | 1.0 | ~1 min |
| All other actions | 0.5 | ~30 sec |

**FTE Hours** = `SUM(FRICTION_SCORE) / 60`

---

## 10. Validation Checklist

Use this checklist after views are deployed to confirm parity.

```sql
-- Step 1: Set session variables
SET WEEK_START = '2026-03-01';
SET WEEK_END   = '2026-03-07';

-- Step 2: Compare row counts
SELECT 'View' AS SOURCE, COUNT(*) AS ROW_COUNT FROM V_HWL_HR
UNION ALL
SELECT 'CSV',  <row_count_from_export>;

-- Step 3: Compare BU × Actor distribution
SELECT OBR_SITE_GROUP, OBR_ACTOR_GROUP, COUNT(*) AS TOUCHES
FROM V_HWL_HR
GROUP BY OBR_SITE_GROUP, OBR_ACTOR_GROUP
ORDER BY OBR_SITE_GROUP, TOUCHES DESC;

-- Step 4: Compare defect rate
SELECT
    COUNT(*) AS TOTAL_ACTIONS,
    SUM(CASE WHEN BUCKET_B THEN 1 ELSE 0 END) AS BUCKET_B_ACTIONS,
    ROUND(SUM(CASE WHEN BUCKET_B THEN 1 ELSE 0 END)/COUNT(*)*100,1) AS DEFECT_RATE_PCT
FROM V_HWL_HR;
```

- [ ] View row count matches CSV row count
- [ ] BU × Actor distribution matches
- [ ] Defect rate matches
- [ ] Thin Q1 output matches fat Q1 output
- [ ] Thin Q2–Q7 outputs match fat queries

---

## 11. Excluded Metrics

| Metric | Reason | Status |
|:---|:---|:---|
| DAILY_MISSED_PUNCHES | V_TIMECARD_EXCEPTION data quality under review | Excluded from report |
| WEEKLY_MISSED_PUNCHES | Depends on daily counts above | Excluded from report |
| MISSING_PUNCH_FLAG | Depends on daily/weekly counts | Excluded from report |
| MISSED_PUNCH_DATES | Depends on daily/weekly counts | Excluded from report |
| Q8 Missed Punch Engagement List | Depends on exception table | Excluded from report |

> These columns remain in the base CTE for structural parity with V_HWL_BASE but are not surfaced in the final output or this report. They will be reinstated after the V_TIMECARD_EXCEPTION data feed is validated.

---

## 12. How to Run

1. Open Snowflake and paste the full contents of `sql/validation_3week_hr_dataset.sql`
2. Execute the query — no session variables or view dependencies required
3. Export the result to CSV
4. Use the KPI formulas in Section 3 above to compute all OBR metrics from the flat file
5. After views are deployed, run the validation checklist in Section 10 to confirm parity

---

**Owner:** Kenny Wallace, ORBIT Program Lead  
**Version:** 1.0  
**Last Updated:** 2026-03-10
