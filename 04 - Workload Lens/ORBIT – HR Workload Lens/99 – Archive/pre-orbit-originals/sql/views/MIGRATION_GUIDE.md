# V_HWL View Migration Guide

**Product:** Workload Lens (Phase I)
**Owner:** Kenny Wallace, ORBIT Program Lead
**Created:** 2026-03-03
**Target:** EDLDB.PEOPLE_ANALYTICS_SANDBOX

---

## Purpose

This migration centralizes the ~140-line shared CTE preamble (repeated 7× across Q1–Q7) into two governed Snowflake views. This eliminates ~980 lines of SQL duplication from the Phoenix agent prompt, reducing token consumption by ~12,000 tokens.

## Views to Deploy

### 1. V_HWL_BASE

- **DDL:** `sql/views/V_HWL_BASE.sql`
- **Schema:** `EDLDB.PEOPLE_ANALYTICS_SANDBOX.V_HWL_BASE`
- **Type:** Secure View (non-materialized)
- **Source Tables:**
  - `EDLDB.PEOPLE_ANALYTICS_SANDBOX.UKG_V_TIMECARD_AUDIT`
  - `EDLDB.UKG.V_PEOPLE`
  - `EDLDB.UKG.V_TIMECARD_EXCEPTION`
- **Date Parameterization:** Reads `$WEEK_START` and `$WEEK_END` session variables
- **What it does:** Full base CTE — deduplication, actor group classification, site group classification, bucket assignment, friction scoring, paycode categorization, missed punch joins, comment linkage

### 2. V_HWL_HR

- **DDL:** `sql/views/V_HWL_HR.sql`
- **Schema:** `EDLDB.PEOPLE_ANALYTICS_SANDBOX.V_HWL_HR`
- **Type:** Secure View on top of V_HWL_BASE
- **Filters applied:**
  - `EDIT_TARGET != 'Self'` (excludes self-service)
  - `OBR_SITE_GROUP IS NOT NULL` (excludes corporate/unmapped sites)
  - `OBR_ACTOR_GROUP NOT IN ('Team Member', 'Other', 'Automation', 'WFM')` (HR actors only)

## Deployment Steps

```sql
-- Step 1: Set role and schema
USE ROLE <appropriate_role>;
USE SCHEMA EDLDB.PEOPLE_ANALYTICS_SANDBOX;

-- Step 2: Deploy V_HWL_BASE (must be first — V_HWL_HR depends on it)
-- Run the contents of sql/views/V_HWL_BASE.sql

-- Step 3: Deploy V_HWL_HR
-- Run the contents of sql/views/V_HWL_HR.sql

-- Step 4: Validate — set a known reporting week and compare row counts
SET WEEK_START = '2026-02-23';
SET WEEK_END   = '2026-03-01';

-- Should return a positive row count matching the fat Q2 query output
SELECT COUNT(*) FROM V_HWL_HR;

-- Spot-check: Compare thin Q2 against fat Q2
-- Thin:
SELECT OBR_SITE_GROUP, OBR_ACTOR_GROUP, COUNT(*) AS TOUCHES
FROM V_HWL_HR
GROUP BY OBR_SITE_GROUP, OBR_ACTOR_GROUP
ORDER BY OBR_SITE_GROUP, TOUCHES DESC;
```

## Validation Checklist

| Check | How |
|:---|:---|
| V_HWL_BASE row count matches fat Q1 base CTE | Compare `SELECT COUNT(*) FROM V_HWL_BASE` vs inline base CTE |
| V_HWL_HR row count matches fat Q1 hr CTE | Compare `SELECT COUNT(*) FROM V_HWL_HR` vs inline hr CTE |
| Thin Q1 output matches fat Q1 output | Run both, diff all columns |
| Thin Q2 output matches fat Q2 output | Run both, diff all columns |
| Thin Q6 DPMO values match fat Q6 | Spot-check top 5 sites |
| Thin Q8 output matches fat Q8 output | Run both, diff row counts and top TMs |

## Session Variable Usage

Phoenix must execute two SET statements before any query:

```sql
SET WEEK_START = '<sunday_date>';
SET WEEK_END   = '<saturday_date>';
```

This replaces the former `week_window` CTE that was injected by Phoenix. The session variables are read by `V_HWL_BASE` (and transitively by `V_HWL_HR`) and by the thin Q8 query directly.

**Phoenix Platform Engineering Note:** If Phoenix cannot execute Snowflake SET statements, an alternative is to wrap the views in table functions or use a `week_window` temp table created at session start. Discuss with platform team.

## Rollback

If issues are found, the fat queries in `sql/q1–q8*.sql` are fully self-contained and can be used without any views. No data migration is involved — these are non-materialized views only.

## Dependencies

- No new tables created
- No data migration required
- Existing `V_HWL_WEEKLY_SITE_METRICS` view is unchanged and still used by Q1, Q3, Q6 for 13-week baselines
- Fat queries retained in `sql/` for regression testing
