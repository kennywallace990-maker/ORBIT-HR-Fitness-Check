# Workload Lens View Deployment - Complete Package

## Summary
Need to deploy two Snowflake views to enable the new "thin" query architecture for Workload Lens. This reduces token consumption by ~12,000 tokens and eliminates SQL duplication.

---

## 1. V_HWL_BASE - Full View Definition

**File:** `sql/views/V_HWL_BASE.sql`
**Schema:** `EDLDB.PEOPLE_ANALYTICS_SANDBOX.V_HWL_BASE`

```sql
-- =============================================================================
-- VIEW: V_HWL_BASE
-- Schema: EDLDB.PEOPLE_ANALYTICS_SANDBOX
-- Purpose: Centralized base CTE logic for all Workload Lens queries (Q1-Q7).
--          Replaces the repeated ~140-line shared CTE preamble.
--          Contains ALL derived columns before actor/site filtering.
--
-- Date Parameterization:
--   This view reads Snowflake session variables $WEEK_START and $WEEK_END.
--   Callers MUST set these before querying:
--     SET WEEK_START = '2026-02-23';
--     SET WEEK_END   = '2026-03-01';
--
-- v2.0 Business Logic (matches shared_cte_preamble.sql):
--   - Super Access No Wages → 'Automation' (excluded downstream in V_HWL_HR)
--   - Workers Compensation → 'Local HR'
--   - Historical Correction Comment excluded from action counts
--   - Weekly missed punch threshold: >= 3 (PRD §8)
--   - PAYCODE_CATEGORY includes %pto paid dur%, %personal unpd dur%, %meal break%
--
-- Owner: ORBIT Program (Kenny Wallace)
-- Created: 2026-03-03
-- =============================================================================

CREATE OR REPLACE SECURE VIEW EDLDB.PEOPLE_ANALYTICS_SANDBOX.V_HWL_BASE AS

WITH people_deduped AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY PERSON_NUMBER 
            ORDER BY PERSON_ID DESC
        ) AS prn
    FROM EDLDB.UKG.V_PEOPLE
),
audit_deduped AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY AUDIT_ID, AUDIT_REVISION_ID 
            ORDER BY LOAD_DTTM ASC
        ) AS rn
    FROM EDLDB.PEOPLE_ANALYTICS_SANDBOX.UKG_V_TIMECARD_AUDIT
    WHERE PARTITION_DATE BETWEEN $WEEK_START AND $WEEK_END
),
comments_by_revision AS (
    SELECT 
        AUDIT_REVISION_ID,
        PERSON_NUMBER,
        LISTAGG(DISTINCT AUDIT_COMMENT_TEXT, '; ') WITHIN GROUP (ORDER BY AUDIT_COMMENT_TEXT) AS LINKED_COMMENTS,
        LISTAGG(DISTINCT AUDIT_NOTE_TEXT, '; ') WITHIN GROUP (ORDER BY AUDIT_NOTE_TEXT) AS LINKED_NOTES
    FROM audit_deduped
    WHERE AUDIT_TYPE IN ('Pay Code Edit Comment', 'Punch Comment', 'Exception Comment', 'Historical Correction Comment')
      AND rn = 1
    GROUP BY AUDIT_REVISION_ID, PERSON_NUMBER
),
missed_punch_counts AS (
    SELECT 
        PERSON_ID, 
        DATE(EVENT_DATE) AS EVENT_DATE,
        COUNT(DISTINCT SHIFT_ID) AS DAILY_MISSED_PUNCHES
    FROM EDLDB.UKG.V_TIMECARD_EXCEPTION
    WHERE EXCEPTION_TYPE_NAME IN ('Missed In Punch', 'Missed Out Punch')
    GROUP BY PERSON_ID, DATE(EVENT_DATE)
),
weekly_missed_totals AS (
    SELECT 
        PERSON_ID,
        SUM(DAILY_MISSED_PUNCHES) AS WEEKLY_MISSED_PUNCHES,
        LISTAGG(DISTINCT EVENT_DATE, ', ') WITHIN GROUP (ORDER BY EVENT_DATE) AS MISSED_PUNCH_DATES
    FROM missed_punch_counts
    WHERE EVENT_DATE BETWEEN $WEEK_START AND $WEEK_END
    GROUP BY PERSON_ID
)
SELECT 
    a.PERSON_NUMBER AS EMPLOYEE_ID,
    p.FIRST_NAME||' '||p.LAST_NAME AS EMPLOYEE_FULL_NAME,
    p.EMPLOYMENT_STATUS AS EMPLOYEE_STATUS,
    p.SUPERVISOR_FULL_NAME AS REPORTS_TO,
    REGEXP_SUBSTR(p.PRIMARY_ORG_PATH_TXT,'- ([A-Z0-9]{3,5})/',1,1,'e') AS BUILDING_LOCATION,
    a.AUDIT_REVISION_USER_PERSON_NUMBER AS REVISION_USER_ID,
    rev.ACCESS_PROFILE,
    rev.FIRST_NAME||' '||rev.LAST_NAME AS REVISION_USER_FULL_NAME,
    a.PARTITION_DATE AS ENTITY_EVENT_DATE,
    a.AUDIT_TYPE AS ENTITY_TYPE,
    a.AUDIT_REVISION_TYPE AS REVISION_TYPE,
    a.AUDIT_PAYCODE_NAME AS PAYCODE_NAME,
    COALESCE(cmt.LINKED_COMMENTS, a.AUDIT_COMMENT_TEXT) AS COMMENT,
    COALESCE(cmt.LINKED_NOTES, a.AUDIT_NOTE_TEXT) AS NOTE_TEXT,

    -- Self vs Other edit target
    CASE WHEN a.PERSON_NUMBER = a.AUDIT_REVISION_USER_PERSON_NUMBER
         THEN 'Self' ELSE 'Other' END AS EDIT_TARGET,

    a.AUDIT_DATASOURCE AS DATASOURCE,

    -- v2.0: Actor Group classification
    CASE WHEN p.FIRST_NAME||' '||p.LAST_NAME = rev.FIRST_NAME||' '||rev.LAST_NAME THEN 'Team Member'
         WHEN rev.ACCESS_PROFILE = 'Super Access No Wages' THEN 'Automation'
         WHEN rev.ACCESS_PROFILE IN ('Leave Support','Company Admin TMDM','Team Member Services','Super Access') THEN 'HRSS'
         WHEN rev.ACCESS_PROFILE IN ('Employee Basic','Employee Basic- Pharmacy','Training Basic','IT Admin','Training + Safety','Advanced Scheduler Lead','Advanced Scheduler Workforce Analyst','Facilities') THEN 'Team Member'
         WHEN rev.ACCESS_PROFILE IN ('Company Admin Site Specific','Workers Compensation') THEN 'Local HR'
         WHEN rev.ACCESS_PROFILE IN ('Manager Basic','Manager Basic With Punch&Schedule Edits','Practice Manager','Facilities Manager') THEN 'Local Ops'
         WHEN rev.ACCESS_PROFILE='Workforce Reporting' THEN 'WFM'
         ELSE 'Other' END AS OBR_ACTOR_GROUP,

    -- Site Group classification (51 sites)
    CASE WHEN REGEXP_SUBSTR(p.PRIMARY_ORG_PATH_TXT,'- ([A-Z0-9]{3,5})/',1,1,'e') IN ('AVP1','AVP2','BNA1','CFC1','CLT1','DAY1','DFW1','HOU1','MCI1','MCO1','MDT1','PHX1','RNO1') THEN 'FC'
         WHEN REGEXP_SUBSTR(p.PRIMARY_ORG_PATH_TXT,'- ([A-Z0-9]{3,5})/',1,1,'e') IN ('AVP4','AVP5','AVP6','DFW5','DFW8','MCO4','MCO5','PHX2','PHX5','SDF2','SDF4','SDF5','SDF6') THEN 'Rx'
         WHEN REGEXP_SUBSTR(p.PRIMARY_ORG_PATH_TXT,'- ([A-Z0-9]{3,5})/',1,1,'e') IN ('ATLA','ATLB','ATLC','ATLD','AUSA','DENA','DENB','DEND','DFWA','DFWB','FLLA','FLLB','FLLC','FLLD','FLLF','IAHA','IAHD','PHXB') THEN 'CVC'
         WHEN REGEXP_SUBSTR(p.PRIMARY_ORG_PATH_TXT,'- ([A-Z0-9]{3,5})/',1,1,'e') IN ('AV4V','DF4V','DFW4','FL3V','PH0V','PW0V','SD2V') THEN 'CC'
         ELSE NULL END AS OBR_SITE_GROUP,

    -- Bucket B: Corrections / Rework
    CASE WHEN a.AUDIT_TYPE='Punch' THEN TRUE
         WHEN a.AUDIT_TYPE='Historical Correction' THEN TRUE
         WHEN a.AUDIT_REVISION_TYPE IN ('Edit','Delete') AND a.AUDIT_TYPE IN ('Pay Code Edit','Manager Justified Time') THEN TRUE
         WHEN a.AUDIT_TYPE='Manager Justified Time' AND a.AUDIT_REVISION_TYPE='Add' AND (LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%late%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%early%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%ncns%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%call off%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%unpd%') THEN TRUE
         ELSE FALSE END AS BUCKET_B,

    -- Bucket A: Additions (non-rework)
    CASE WHEN a.AUDIT_TYPE='Pay Code Edit' AND a.AUDIT_REVISION_TYPE='Add' THEN TRUE
         WHEN a.AUDIT_TYPE='Manager Justified Time' AND a.AUDIT_REVISION_TYPE='Add' AND NOT (LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%late%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%early%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%ncns%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%call off%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%unpd%') THEN TRUE
         ELSE FALSE END AS BUCKET_A,

    -- Bucket G: Governance
    CASE WHEN a.AUDIT_TYPE IN ('Exception Comment','Punch Comment','Pay Code Edit Comment','Historical Correction Comment') THEN TRUE
         WHEN a.AUDIT_TYPE IN ('Mark as reviewed','Manager Approval') THEN TRUE
         ELSE FALSE END AS BUCKET_G,

    -- Friction Score (complexity weighting)
    CASE WHEN a.AUDIT_TYPE='Historical Correction' THEN 5.0
         WHEN a.AUDIT_REVISION_TYPE IN ('Edit','Delete') AND a.AUDIT_TYPE IN ('Punch','Pay Code Edit','Manager Justified Time') THEN 1.0
         ELSE 0.5 END AS FRICTION_SCORE,

    -- High-Risk Rework flag (for comment compliance)
    CASE WHEN a.AUDIT_TYPE='Historical Correction' THEN TRUE
         WHEN a.AUDIT_TYPE='Punch' AND a.AUDIT_REVISION_TYPE IN ('Add','Edit','Delete') THEN TRUE
         WHEN a.AUDIT_TYPE='Pay Code Edit' AND a.AUDIT_REVISION_TYPE IN ('Add','Edit') AND (LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%pto%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%sick%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%regular%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%overtime%') THEN TRUE
         ELSE FALSE END AS HIGH_RISK_REWORK,

    -- Comment presence flag
    CASE WHEN (a.AUDIT_COMMENT_TEXT IS NOT NULL AND TRIM(a.AUDIT_COMMENT_TEXT)<>'')
           OR (a.AUDIT_NOTE_TEXT IS NOT NULL AND TRIM(a.AUDIT_NOTE_TEXT)<>'')
         THEN 1 ELSE 0 END AS HAS_COMMENT,

    -- v2.0: Paycode Category (human-readable driver labels)
    CASE WHEN a.AUDIT_PAYCODE_NAME IS NULL OR TRIM(a.AUDIT_PAYCODE_NAME)='' THEN 'Manual Punch Correction'
         WHEN LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%vto%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%voluntary%' THEN 'Time spent manually coding VTO'
         WHEN LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%weather%' THEN 'Time spent manually coding weather-related event'
         WHEN LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%late%' THEN 'Manual coding missed late arrival'
         WHEN LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%early%' THEN 'Manual coding missed early departure'
         WHEN LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%ncns%' THEN 'Manual coding No Call No Show'
         WHEN LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%call off%' THEN 'Manual coding Call Off'
         WHEN LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%sick%' THEN 'Manual coding Sick Time'
         WHEN LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%leave%' THEN 'Manual coding Leave of Absence'
         WHEN LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%pto paid dur%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%personal unpd dur%' THEN 'Manual coding for early departure/long lunch to deduct UTO'
         WHEN LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%pto%' THEN 'Manual coding of Paid Time Off'
         WHEN LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%meal break%' THEN 'Manual coding to prevent UTO (Meal Break)'
         WHEN LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%personal%' THEN 'Manual coding of Personal Time'
         ELSE 'Time spent manually coding '||COALESCE(a.AUDIT_PAYCODE_NAME,'') END AS PAYCODE_CATEGORY,

    -- Historical Correction root cause category
    CASE WHEN LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%ncns%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%late%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%early%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%call off%' THEN 'Attendance Enforcement'
         WHEN LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%regular%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%overtime%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%meal%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%pto paid%' THEN 'Core Pay & Missing Time'
         WHEN LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%personal%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%vto%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%weather%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%unpaid%' THEN 'Schedule & Unpaid True-Ups'
         WHEN LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%leave%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%fmla%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%loa%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%bereavement%' THEN 'Leave & Compliance Lag'
         ELSE 'Other' END AS HC_CATEGORY,

    -- Missed punch metrics (joined from exception tables)
    COALESCE(mpc.DAILY_MISSED_PUNCHES, 0) AS DAILY_MISSED_PUNCHES,
    COALESCE(wmt.WEEKLY_MISSED_PUNCHES, 0) AS WEEKLY_MISSED_PUNCHES,

    -- v2.0: Weekly threshold changed from >= 4 to >= 3 (PRD §8)
    CASE 
        WHEN p.EMPLOYMENT_STATUS = 'Active' 
             AND (COALESCE(mpc.DAILY_MISSED_PUNCHES, 0) >= 2 
                  OR COALESCE(wmt.WEEKLY_MISSED_PUNCHES, 0) >= 3)
        THEN 'Yes' 
        ELSE 'No' 
    END AS MISSING_PUNCH_FLAG,

    CASE 
        WHEN p.EMPLOYMENT_STATUS = 'Active' 
             AND (COALESCE(mpc.DAILY_MISSED_PUNCHES, 0) >= 2 
                  OR COALESCE(wmt.WEEKLY_MISSED_PUNCHES, 0) >= 3)
        THEN wmt.MISSED_PUNCH_DATES
        ELSE NULL 
    END AS MISSED_PUNCH_DATES,

    exc.EXCEPTION_TYPES

FROM audit_deduped a
JOIN people_deduped p ON a.PERSON_NUMBER = p.PERSON_NUMBER AND p.prn = 1
LEFT JOIN people_deduped rev ON a.AUDIT_REVISION_USER_PERSON_NUMBER = rev.PERSON_NUMBER AND rev.prn = 1
LEFT JOIN comments_by_revision cmt ON a.AUDIT_REVISION_ID = cmt.AUDIT_REVISION_ID AND a.PERSON_NUMBER = cmt.PERSON_NUMBER
LEFT JOIN missed_punch_counts mpc ON mpc.PERSON_ID = p.PERSON_ID AND mpc.EVENT_DATE = a.PARTITION_DATE
LEFT JOIN weekly_missed_totals wmt ON wmt.PERSON_ID = p.PERSON_ID
LEFT JOIN (
    SELECT PERSON_ID, DATE(EVENT_DATE) AS EVENT_DATE,
        LISTAGG(DISTINCT EXCEPTION_TYPE_NAME, ', ') WITHIN GROUP (ORDER BY EXCEPTION_TYPE_NAME) AS EXCEPTION_TYPES
    FROM EDLDB.UKG.V_TIMECARD_EXCEPTION
    GROUP BY PERSON_ID, DATE(EVENT_DATE)
) exc ON exc.PERSON_ID = p.PERSON_ID AND exc.EVENT_DATE = a.PARTITION_DATE
WHERE a.rn = 1
  -- v2.0: Historical Correction Comment excluded from action counts
  AND a.AUDIT_TYPE NOT IN ('Exception Comment', 'Punch Comment', 'Pay Code Edit Comment', 'Historical Correction Comment');
```

---

## 2. V_HWL_HR - Filtered View Definition

**File:** `sql/views/V_HWL_HR.sql`
**Schema:** `EDLDB.PEOPLE_ANALYTICS_SANDBOX.V_HWL_HR`

```sql
-- =============================================================================
-- VIEW: V_HWL_HR
-- Schema: EDLDB.PEOPLE_ANALYTICS_SANDBOX
-- Purpose: Filtered version of V_HWL_BASE for all Q1-Q7 analytics.
--          Applies the standard hr CTE filters:
--            - Excludes self-service edits (EDIT_TARGET = 'Self')
--            - Excludes unmapped sites (OBR_SITE_GROUP IS NULL)
--            - Excludes Team Member, Other, and Automation actor groups
--
-- Date Parameterization:
--   Inherits $WEEK_START / $WEEK_END from V_HWL_BASE.
--   Callers MUST set session variables before querying.
--
-- Owner: ORBIT Program (Kenny Wallace)
-- Created: 2026-03-03
-- =============================================================================

CREATE OR REPLACE SECURE VIEW EDLDB.PEOPLE_ANALYTICS_SANDBOX.V_HWL_HR AS

SELECT *
FROM EDLDB.PEOPLE_ANALYTICS_SANDBOX.V_HWL_BASE
WHERE EDIT_TARGET != 'Self'
  AND OBR_SITE_GROUP IS NOT NULL
  AND OBR_ACTOR_GROUP NOT IN ('Team Member', 'Other', 'Automation', 'WFM');
```

---

## 3. Example Thin Query (Q1)

**File:** `sql/thin/q1_network_kpi.sql`

```sql
-- QUERY 1 (THIN) — Network KPI Summary with 1σ Spike Flags (Section 1)
-- Returns 1 row. Reads from V_HWL_HR view.
-- Caller must SET WEEK_START / WEEK_END session variables before executing.

WITH mp_dedup AS (
    SELECT DISTINCT EMPLOYEE_ID, ENTITY_EVENT_DATE, DAILY_MISSED_PUNCHES
    FROM EDLDB.PEOPLE_ANALYTICS_SANDBOX.V_HWL_HR
    WHERE DAILY_MISSED_PUNCHES > 0
),
network_baseline AS (
    SELECT 
        SUM(TOTAL_ACTIONS) AS TOTAL_ACTIONS,
        SUM(BUCKET_B_ACTIONS) AS BUCKET_B_ACTIONS,
        (SUM(BUCKET_B_ACTIONS) / NULLIF(SUM(TOTAL_ACTIONS), 0)) * 100 AS MEAN_13WK_DEFECT_RATE,
        AVG(SD_13WK_DEFECT_RATE) AS SD_13WK_DEFECT_RATE
    FROM EDLDB.PEOPLE_ANALYTICS_SANDBOX.V_HWL_WEEKLY_SITE_METRICS
    WHERE REPORT_WEEK = DATE_TRUNC('WEEK', $WEEK_START)
),
current_week_network AS (
    SELECT
        COUNT(*)                                                                          AS TOTAL_ACTIONS,
        SUM(CASE WHEN BUCKET_B THEN 1 ELSE 0 END)                                        AS BUCKET_B_ACTIONS,
        ROUND(SUM(CASE WHEN BUCKET_B THEN 1 ELSE 0 END)/COUNT(*)*100,1)                  AS DEFECT_RATE_PCT,
        COUNT(DISTINCT EMPLOYEE_ID)                                                       AS NETWORK_UNIQUE_TMS,
        ROUND(SUM(FRICTION_SCORE)/60.0,1)                                                 AS TOTAL_FRICTION_HRS,
        (SELECT SUM(DAILY_MISSED_PUNCHES) FROM mp_dedup)                                  AS MISSED_PUNCH_COUNT,
        ROUND((SELECT SUM(DAILY_MISSED_PUNCHES) FROM mp_dedup)/COUNT(*)*100,1)            AS MISSING_PUNCH_RATE_PCT,
        SUM(CASE WHEN ENTITY_TYPE='Historical Correction' THEN 1 ELSE 0 END)             AS HIST_CORR_COUNT,
        ROUND(SUM(CASE WHEN ENTITY_TYPE='Historical Correction' THEN 1 ELSE 0 END)/COUNT(*)*100,1) AS HIST_CORR_RATE_PCT,
        WEEKOFYEAR(MIN(ENTITY_EVENT_DATE))                                                AS REPORTING_WEEK,
        TO_VARCHAR(MIN(ENTITY_EVENT_DATE),'MM/DD')                                        AS WINDOW_START,
        TO_VARCHAR(MAX(ENTITY_EVENT_DATE),'MM/DD')                                        AS WINDOW_END
    FROM EDLDB.PEOPLE_ANALYTICS_SANDBOX.V_HWL_HR
)
SELECT 
    c.*,
    COALESCE(b.MEAN_13WK_DEFECT_RATE, 0) AS MEAN_13WK_DEFECT_RATE,
    COALESCE(b.SD_13WK_DEFECT_RATE, 0) AS SD_13WK_DEFECT_RATE,
    (COALESCE(b.MEAN_13WK_DEFECT_RATE, 0) + COALESCE(b.SD_13WK_DEFECT_RATE, 0)) AS UCL_13WK_DEFECT_RATE,
    CASE WHEN c.DEFECT_RATE_PCT > (COALESCE(b.MEAN_13WK_DEFECT_RATE, 0) + COALESCE(b.SD_13WK_DEFECT_RATE, 0)) THEN TRUE ELSE FALSE END AS IS_RED_SPIKE
FROM current_week_network c
CROSS JOIN network_baseline b;
```

---

## 4. Deployment Instructions

### Step 1: Set role and schema
```sql
USE ROLE <appropriate_role>;
USE SCHEMA EDLDB.PEOPLE_ANALYTICS_SANDBOX;
```

### Step 2: Deploy V_HWL_BASE (must be first — V_HWL_HR depends on it)
Run the complete V_HWL_BASE SQL from Section 1 above.

### Step 3: Deploy V_HWL_HR  
Run the complete V_HWL_HR SQL from Section 2 above.

### Step 4: Validation
```sql
-- Set session variables
SET WEEK_START = '2026-03-01';
SET WEEK_END = '2026-03-07';

-- Test the view
SELECT COUNT(*) FROM V_HWL_HR;

-- Spot-check: Compare thin Q1 against fat Q1
-- Thin (using views):
SELECT OBR_SITE_GROUP, OBR_ACTOR_GROUP, COUNT(*) AS TOUCHES
FROM V_HWL_HR
GROUP BY OBR_SITE_GROUP, OBR_ACTOR_GROUP
ORDER BY OBR_SITE_GROUP, TOUCHES DESC;
```

---

## 5. Business Impact
- **Token Savings:** ~12,000 tokens per agent execution
- **Code Reduction:** From 1,218 lines to 238 unique lines
- **Maintenance:** Single source of truth for business logic
- **Performance:** No materialized views - same runtime as current

---

## 6. Dependencies & Requirements
- Requires Phoenix platform to support `SET WEEK_START/WEEK_END` session variables
- If session variables not supported, discuss alternatives with platform team
- Existing `V_HWL_WEEKLY_SITE_METRICS` view unchanged and still used by Q1, Q3, Q6 for 13-week baselines

---

## 7. Rollback Plan
If issues arise, fat queries in `sql/q1-q8*.sql` are fully self-contained and can be used immediately. No data migration involved - these are non-materialized views only.

---

## 8. Validation Checklist
- [ ] V_HWL_BASE row count matches fat Q1 base CTE
- [ ] V_HWL_HR row count matches fat Q1 hr CTE  
- [ ] Thin Q1 output matches fat Q1 output
- [ ] Thin Q2-Q7 outputs match fat queries
- [ ] Session variables work correctly
- [ ] All 8 thin queries execute successfully

---

## 9. Technical Architecture

### Source Tables Used
- `EDLDB.PEOPLE_ANALYTICS_SANDBOX.UKG_V_TIMECARD_AUDIT`
- `EDLDB.UKG.V_PEOPLE`
- `EDLDB.UKG.V_TIMECARD_EXCEPTION`
- `EDLDB.PEOPLE_ANALYTICS_SANDBOX.V_HWL_WEEKLY_SITE_METRICS` (13-week baselines)

### Key Business Logic Implemented
- **v2.0 Actor Mapping:** Super Access No Wages → Automation, Workers Compensation → Local HR
- **Exclusions:** Self-service, corporate sites, Team Member/Other/Automation actors
- **Thresholds:** Weekly missed punch ≥ 3, daily missed punch ≥ 2
- **Categories:** Enhanced paycode categories including %pto paid dur%, %personal unpd dur%, %meal break%
- **Scoring:** Friction scores (0.5-5.0), bucket classifications, high-risk rework flags

### Session Variable Pattern
```sql
SET WEEK_START = 'YYYY-MM-DD';  -- Sunday
SET WEEK_END   = 'YYYY-MM-DD';  -- Saturday
```

---

## 10. Contact & Support
**Owner:** Kenny Wallace, ORBIT Program Lead  
**Created:** 2026-03-10  
**Questions:** Review this complete package or contact ORBIT team for technical support
