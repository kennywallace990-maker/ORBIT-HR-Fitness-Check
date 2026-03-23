# Technical Design Doc, ECHO Intelligence

| Field | Value |
| --- | --- |
| **Product** | ECHO Intelligence |
| **Platform** | ORBIT Phoenix |
| **Product Owner** | Kenny Wallace |
| **Version** | 1.0 |
| **Last Updated** | 2026-03-17 |
| **Pipeline Status** | Interim SQL; EPA automated pipeline pending |

---

## 1. Overview

This document describes the architecture, data flow, Snowflake schema, unification logic, production SQL, voice mechanism normalization, escalation classification, and operational considerations for the ECHO Intelligence ORBIT product.

---

## 2. Architecture

```text
┌──────────────────────────┐  ┌──────────────────────────┐  ┌──────────────────────────┐
│  CAT Tracker             │  │  VOC Board               │  │  Fulfillment Standups    │
│  (FULFILLMENT_CAT_       │  │  (VOC_BOARD)             │  │  (FULFILLMENT_STAND_UPS) │
│   TRACKER)               │  │                          │  │                          │
└────────────┬─────────────┘  └────────────┬─────────────┘  └────────────┬─────────────┘
             │                             │                             │
             │  ┌──────────────────────────┐  ┌──────────────────────────┐
             │  │  New Hire Surveys        │  │  Week 3 Surveys          │
             │  │  (FULFILLMENT_NEW_HIRE_  │  │  (FULFILLMENT_WEEK_      │
             │  │   SURVEYS)              │  │   THREE_SURVEY)          │
             │  └────────────┬─────────────┘  └────────────┬─────────────┘
             │               │                             │
             ▼               ▼                             ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                 SNOWFLAKE (EDLDB.PEOPLE_ANALYTICS_SANDBOX)                   │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │              UNIFIED SQL QUERY (ALL_SOURCES CTE)                       │  │
│  │                                                                        │  │
│  │  1. CAT Tracker ─── Voice mechanism normalization, site code extract   │  │
│  │  2. VOC Board ───── Dedup against CAT Tracker, site code extract      │  │
│  │  3. Standups ────── Filler filtering, site code extract               │  │
│  │  4. New Hire ────── Filler filtering, context concatenation           │  │
│  │  5. Week 3 ──────── Filler filtering, context concatenation           │  │
│  │                                                                        │  │
│  │  UNION ALL → 15-column unified schema                                  │  │
│  │  + Business unit classification (SITE_CODE → FC/Rx/Unknown)            │  │
│  │  + Legacy regex escalation (Level 1/2/3)                               │  │
│  │  + Administrative mechanism exclusion                                  │  │
│  │  + Site exclusion (BOS4, SDF1)                                         │  │
│  │  + Date filter (ROW_DATE >= 2025-01-01)                                │  │
│  └──────────────────────────────┬─────────────────────────────────────────┘  │
│                                  │                                           │
└──────────────────────────────────┼───────────────────────────────────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────┐
                    │     CSV Export            │
                    │     (Interim Pipeline)    │
                    └──────────────┬───────────┘
                                   │
                                   ▼
                    ┌──────────────────────────┐
                    │  Report Generation        │
                    │  (Manual / Assisted)      │
                    │                           │
                    │  • Aggregation by site    │
                    │  • Category analysis      │
                    │  • Network benchmarks     │
                    │  • Narrative generation    │
                    │  • HTML report output      │
                    └──────────────┬────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────┐
                    │  FC Leadership /          │
                    │  Network Leadership /     │
                    │  ER Partners              │
                    └──────────────────────────┘
```

---

## 3. Source Systems

### 3.1 EDLDB.PEOPLE_ANALYTICS_SANDBOX.FULFILLMENT_CAT_TRACKER

| Attribute | Detail |
| --- | --- |
| **Database.Schema.Table** | `EDLDB.PEOPLE_ANALYTICS_SANDBOX.FULFILLMENT_CAT_TRACKER` |
| **Purpose** | Primary feedback tracker; captures signals from multiple listening mechanisms per site |
| **Key columns used** | `MODIFIED`, `CREATED`, `PRIMARY_TEXT`, `RESOLUTION`, `ROW_DATE`, `VOICE_MECHANISM`, `CATEGORY`, `ACTION_COMPLETED`, `DATE_ARCHIVED`, `LOAD_DTTM`, `SHEET_NAME` |
| **Grain** | 1 row per feedback signal |
| **Site code derivation** | `LEFT(SHEET_NAME, 4)` |
| **Voice mechanism handling** | Normalized via CASE expressions (see Section 5) |

### 3.2 EDLDB.PEOPLE_ANALYTICS_SANDBOX.VOC_BOARD

| Attribute | Detail |
| --- | --- |
| **Database.Schema.Table** | `EDLDB.PEOPLE_ANALYTICS_SANDBOX.VOC_BOARD` |
| **Purpose** | VOC Board feedback — public whiteboard-style TM feedback |
| **Key columns used** | `CREATED_DATE`, `FEEDBACK`, `RESOLUTION`, `DATE_POSTED`, `CATEGORY`, `LOCATION` |
| **Grain** | 1 row per VOC Board entry |
| **Site code derivation** | `LEFT(LOCATION, 4)` |
| **Filters** | `DATE_POSTED >= '2025-01-01'`; excludes BOS4, SDF1; deduplicates against CAT Tracker via `NOT EXISTS` on matching site + date + text |

### 3.3 EDLDB.PEOPLE_ANALYTICS_SANDBOX.FULFILLMENT_STAND_UPS

| Attribute | Detail |
| --- | --- |
| **Database.Schema.Table** | `EDLDB.PEOPLE_ANALYTICS_SANDBOX.FULFILLMENT_STAND_UPS` |
| **Purpose** | Standup meeting TM feedback responses |
| **Key columns used** | `TIME_STAMP`, `TEAM_MEMBER_FEEDBACK`, `DATE`, `CONTENT_ASSESSMENT`, `FULFILLMENT_CENTER` |
| **Grain** | 1 row per TM feedback response during a standup |
| **Site code derivation** | `LEFT(FULFILLMENT_CENTER, 4)` |
| **Mapping** | `TEAM_MEMBER_FEEDBACK` → `PRIMARY_TEXT`; `CONTENT_ASSESSMENT` → `CATEGORY` |
| **Filters** | Non-null `TEAM_MEMBER_FEEDBACK`; excludes filler values (n/a, none, nothing to add, no feedback, yes, yes!) |

### 3.4 EDLDB.PEOPLE_ANALYTICS_SANDBOX.FULFILLMENT_NEW_HIRE_SURVEYS

| Attribute | Detail |
| --- | --- |
| **Database.Schema.Table** | `EDLDB.PEOPLE_ANALYTICS_SANDBOX.FULFILLMENT_NEW_HIRE_SURVEYS` |
| **Purpose** | New hire orientation improvement suggestions |
| **Key columns used** | `CREATED`, `NHO_IMPROVE`, `NHO_HAPPY`, `REC_MOST_IMPORTANT_FACTOR`, `LOCATION` |
| **Grain** | 1 row per new hire survey response |
| **Site code derivation** | `LEFT(LOCATION, 4)` |
| **Mapping** | `NHO_IMPROVE` → `PRIMARY_TEXT`; `NHO_HAPPY` + `REC_MOST_IMPORTANT_FACTOR` → `CATEGORY` (concatenated for context) |
| **Filters** | Non-null `NHO_IMPROVE`; excludes 17 filler values |

### 3.5 EDLDB.PEOPLE_ANALYTICS_SANDBOX.FULFILLMENT_WEEK_THREE_SURVEY

| Attribute | Detail |
| --- | --- |
| **Database.Schema.Table** | `EDLDB.PEOPLE_ANALYTICS_SANDBOX.FULFILLMENT_WEEK_THREE_SURVEY` |
| **Purpose** | Week 3 post-hire survey improvement suggestions |
| **Key columns used** | `CREATED`, `IMPROVE`, `HAPPY`, `PHYSICALITY`, `PREPARED`, `LOCATION` |
| **Grain** | 1 row per Week 3 survey response |
| **Site code derivation** | `LEFT(LOCATION, 4)` |
| **Mapping** | `IMPROVE` → `PRIMARY_TEXT`; `HAPPY` + `PHYSICALITY` + `PREPARED` → `CATEGORY` (concatenated for context) |
| **Filters** | Non-null `IMPROVE`; excludes 21 filler values |

---

## 4. Unified Output Schema (15 Columns)

All five source tables are normalized into this common schema via `UNION ALL`:

| # | Column | Data Type | Description |
| --- | --- | --- | --- |
| 1 | `MODIFIED` | TIMESTAMP | Last modification timestamp |
| 2 | `CREATED` | TIMESTAMP | Creation/submission timestamp |
| 3 | `PRIMARY_TEXT` | VARCHAR | The core TM feedback text — the signal payload |
| 4 | `RESOLUTION` | VARCHAR | Resolution or response text (if any) |
| 5 | `ROW_DATE` | DATE | Date the signal was recorded |
| 6 | `VOICE_MECHANISM` | VARCHAR | Normalized listening mechanism label |
| 7 | `CATEGORY` | VARCHAR | Signal category or contextual metadata |
| 8 | `ACTION_COMPLETED` | VARCHAR | Whether action was taken (Yes/No) |
| 9 | `DATE_ARCHIVED` | DATE | Archive date (if applicable) |
| 10 | `LOAD_DTTM` | TIMESTAMP | Data load timestamp |
| 11 | `SITE_CODE` | VARCHAR(4) | 4-character site identifier |
| 12 | `BUSINESS_UNIT` | VARCHAR | Derived: FC, Rx, or Unknown |
| 13 | `LEGACY_REGEX_ESCALATION` | VARCHAR | Derived: Level 1/2/3 Priority or NULL |

---

## 5. Voice Mechanism Normalization Rules

Applied in the `ALL_SOURCES` CTE for CAT Tracker records:

```sql
CASE 
    WHEN VOICE_MECHANISM IN ('GM/HRM Floor Walk', 'GM/HRM Walks', 'Building Walk')
        THEN 'Site Leadership Walks'
    WHEN VOICE_MECHANISM IN ('Gembas', 'Gemba')
        THEN 'Gemba Walks'
    WHEN UPPER(VOICE_MECHANISM) IN ('STANDUP MEETINGS', 'FULFILLMENT STANDUPS')
        THEN 'Standups'
    ELSE COALESCE(VOICE_MECHANISM, 'CAT Tracker')
END
```

Non-CAT sources receive fixed labels: `'VOC Board'`, `'Standups'`, `'New Hire Survey'`, `'Week 3 Survey'`.

---

## 6. Business Unit Classification

Derived from `SITE_CODE` in the final SELECT:

```sql
CASE SITE_CODE
    WHEN 'AVP1' THEN 'FC'
    WHEN 'AVP2' THEN 'FC'
    WHEN 'BNA1' THEN 'FC'
    WHEN 'CFC1' THEN 'FC'
    WHEN 'CLT1' THEN 'FC'
    WHEN 'DAY1' THEN 'FC'
    WHEN 'DFW1' THEN 'FC'
    WHEN 'HOU1' THEN 'FC'
    WHEN 'MCI1' THEN 'FC'
    WHEN 'MCO1' THEN 'FC'
    WHEN 'MDT1' THEN 'FC'
    WHEN 'PHX1' THEN 'FC'
    WHEN 'RNO1' THEN 'FC'
    WHEN 'MCO4' THEN 'Rx'
    WHEN 'PHX2' THEN 'Rx'
    WHEN 'AVP4' THEN 'Rx'
    WHEN 'DFW8' THEN 'Rx'
    WHEN 'SDF2' THEN 'Rx'
    WHEN 'SDF4' THEN 'Rx'
    WHEN 'SDF6' THEN 'Rx'
    ELSE 'Unknown'
END AS BUSINESS_UNIT
```

---

## 7. Legacy Regex Escalation Classification

Applied against `PRIMARY_TEXT` in the final SELECT for ER routing:

| Level | Key Patterns | Use Case |
| --- | --- | --- |
| **Level 1 Priority** | discriminat*, harass*, retaliat*, threat*, violen*, union*, attorney*, EEOC, OSHA, ADA, suicide*, CEO, Sumit, wrongful term* | Immediate ER/Legal escalation |
| **Level 2 Priority** | unfair*, bully*, unsaf*, danger*, assault*, drug*, alcohol*, wage*, safe*, under the influence | Elevated ER review |
| **Level 3 Priority** | dispute*, conflict*, disrespect*, theft*, toxic*, violat* | Standard ER review |

Full regex patterns are documented in the production SQL (Section 8).

---

## 8. Production SQL

```sql
-- ORBIT ECHO Intelligence
-- Step 1: Unified View (CAT + VOC)
-- This query creates a unified dataset for the Phoenix LLM by mapping VOC data into 
-- the standard FULFILLMENT_CAT_TRACKER 15-column schema.
-- Duplicate VOC comments (that already exist in the CAT tracker) are excluded.

WITH ALL_SOURCES AS (
    -- 1. CAT Tracker (Base Schema)
    SELECT
        MODIFIED,
        CREATED,
        PRIMARY_TEXT,
        RESOLUTION,
        ROW_DATE,
        CASE 
            WHEN VOICE_MECHANISM IN ('GM/HRM Floor Walk', 'GM/HRM Walks', 'Building Walk') THEN 'Site Leadership Walks'
            WHEN VOICE_MECHANISM IN ('Gembas', 'Gemba') THEN 'Gemba Walks'
            WHEN UPPER(VOICE_MECHANISM) IN ('STANDUP MEETINGS', 'FULFILLMENT STANDUPS') THEN 'Standups'
            ELSE COALESCE(VOICE_MECHANISM, 'CAT Tracker')
        END AS VOICE_MECHANISM,
        CATEGORY,
        ACTION_COMPLETED,
        DATE_ARCHIVED,
        LOAD_DTTM,
        LEFT(SHEET_NAME, 4) AS SITE_CODE
    FROM EDLDB.PEOPLE_ANALYTICS_SANDBOX.FULFILLMENT_CAT_TRACKER

    UNION ALL

    -- 2. VOC Board
    SELECT
        CURRENT_TIMESTAMP() AS MODIFIED,
        CREATED_DATE AS CREATED,
        FEEDBACK AS PRIMARY_TEXT,
        RESOLUTION AS RESOLUTION,
        DATE_POSTED AS ROW_DATE,
        'VOC Board' AS VOICE_MECHANISM,
        CATEGORY AS CATEGORY,
        CASE WHEN RESOLUTION IS NOT NULL AND TRIM(RESOLUTION) != '' THEN 'Yes' ELSE 'No' END AS ACTION_COMPLETED,
        NULL AS DATE_ARCHIVED,
        CURRENT_TIMESTAMP() AS LOAD_DTTM,
        LEFT(LOCATION, 4) AS SITE_CODE
    FROM EDLDB.PEOPLE_ANALYTICS_SANDBOX.VOC_BOARD VOC
    WHERE VOC.DATE_POSTED >= '2025-01-01'
      AND VOC.LOCATION NOT IN ('BOS4', 'SDF1')
      -- Exclude VOC comments that perfectly match an existing CAT comment
      AND NOT EXISTS (
          SELECT 1 
          FROM EDLDB.PEOPLE_ANALYTICS_SANDBOX.FULFILLMENT_CAT_TRACKER CAT
          WHERE LEFT(CAT.SHEET_NAME, 4) = VOC.LOCATION
            AND CAT.ROW_DATE = VOC.DATE_POSTED
            AND LOWER(TRIM(CAT.PRIMARY_TEXT)) = LOWER(TRIM(VOC.FEEDBACK))
      )

    UNION ALL

    -- 3. FULFILLMENT STAND UPS
    SELECT
        CURRENT_TIMESTAMP() AS MODIFIED,
        TIME_STAMP AS CREATED,
        TEAM_MEMBER_FEEDBACK AS PRIMARY_TEXT,
        NULL AS RESOLUTION,
        DATE AS ROW_DATE,
        'Standups' AS VOICE_MECHANISM,
        CONTENT_ASSESSMENT AS CATEGORY,
        NULL AS ACTION_COMPLETED,
        NULL AS DATE_ARCHIVED,
        CURRENT_TIMESTAMP() AS LOAD_DTTM,
        LEFT(FULFILLMENT_CENTER, 4) AS SITE_CODE
    FROM EDLDB.PEOPLE_ANALYTICS_SANDBOX.FULFILLMENT_STAND_UPS
    WHERE TEAM_MEMBER_FEEDBACK IS NOT NULL 
      AND TRIM(TEAM_MEMBER_FEEDBACK) != ''
      AND LOWER(TRIM(TEAM_MEMBER_FEEDBACK)) NOT IN ('n/a', 'none', 'nothing to add', 'no feedback', 'yes', 'yes!')

    UNION ALL

    -- 4. FULFILLMENT NEW HIRE SURVEYS
    SELECT
        CURRENT_TIMESTAMP() AS MODIFIED,
        CREATED AS CREATED,
        NHO_IMPROVE AS PRIMARY_TEXT,
        NULL AS RESOLUTION,
        TO_DATE(CREATED) AS ROW_DATE,
        'New Hire Survey' AS VOICE_MECHANISM,
        'Orientation Happiness: ' || COALESCE(NHO_HAPPY, 'N/A') || ' | Top Factor: ' || COALESCE(REC_MOST_IMPORTANT_FACTOR, 'N/A') AS CATEGORY,
        NULL AS ACTION_COMPLETED,
        NULL AS DATE_ARCHIVED,
        CURRENT_TIMESTAMP() AS LOAD_DTTM,
        LEFT(LOCATION, 4) AS SITE_CODE
    FROM EDLDB.PEOPLE_ANALYTICS_SANDBOX.FULFILLMENT_NEW_HIRE_SURVEYS
    WHERE NHO_IMPROVE IS NOT NULL
      AND TRIM(NHO_IMPROVE) != ''
      AND LOWER(TRIM(NHO_IMPROVE)) NOT IN (
          'n/a', 'na', 'none', 'nothing', 'no', 'yes', 'all good', 'it was great', 'good', 
          'it was good', 'everything was good', 'nothing at this time', 'nothing it was great', 
          'none.', '.', 'nothing.', 'n/a.', 'idk', 'na.', 'nothing to add', 'all fine'
      )

    UNION ALL

    -- 5. FULFILLMENT WEEK THREE SURVEYS
    SELECT
        CURRENT_TIMESTAMP() AS MODIFIED,
        CREATED AS CREATED,
        IMPROVE AS PRIMARY_TEXT,
        NULL AS RESOLUTION,
        TO_DATE(CREATED) AS ROW_DATE,
        'Week 3 Survey' AS VOICE_MECHANISM,
        'Happiness: ' || COALESCE(HAPPY, 'N/A') || ' | Physicality: ' || COALESCE(PHYSICALITY, 'N/A') || ' | Preparedness: ' || COALESCE(PREPARED, 'N/A') AS CATEGORY,
        NULL AS ACTION_COMPLETED,
        NULL AS DATE_ARCHIVED,
        CURRENT_TIMESTAMP() AS LOAD_DTTM,
        LEFT(LOCATION, 4) AS SITE_CODE
    FROM EDLDB.PEOPLE_ANALYTICS_SANDBOX.FULFILLMENT_WEEK_THREE_SURVEY
    WHERE IMPROVE IS NOT NULL
      AND TRIM(IMPROVE) != ''
      AND LOWER(TRIM(IMPROVE)) NOT IN (
          'n/a', 'na', 'none', 'nothing', 'no', 'yes', 'all good', 'it was great', 'good', 
          'it was good', 'everything was good', 'nothing at this time', 'nothing it was great', 
          'none.', '.', 'nothing.', 'n/a.', 'idk', 'na.', 'nothing to add', 'all fine',
          'not really', 'nope', 'none at this time', 'none at all', 'not at the moment'
      )
)

SELECT 
    MODIFIED,
    CREATED,
    PRIMARY_TEXT,
    RESOLUTION,
    ROW_DATE,
    VOICE_MECHANISM,
    CATEGORY,
    ACTION_COMPLETED,
    DATE_ARCHIVED,
    LOAD_DTTM,
    SITE_CODE,
    CASE SITE_CODE
        WHEN 'AVP1' THEN 'FC'
        WHEN 'AVP2' THEN 'FC'
        WHEN 'BNA1' THEN 'FC'
        WHEN 'CFC1' THEN 'FC'
        WHEN 'CLT1' THEN 'FC'
        WHEN 'DAY1' THEN 'FC'
        WHEN 'DFW1' THEN 'FC'
        WHEN 'HOU1' THEN 'FC'
        WHEN 'MCI1' THEN 'FC'
        WHEN 'MCO1' THEN 'FC'
        WHEN 'MDT1' THEN 'FC'
        WHEN 'PHX1' THEN 'FC'
        WHEN 'RNO1' THEN 'FC'
        WHEN 'MCO4' THEN 'Rx'
        WHEN 'PHX2' THEN 'Rx'
        WHEN 'AVP4' THEN 'Rx'
        WHEN 'DFW8' THEN 'Rx'
        WHEN 'SDF2' THEN 'Rx'
        WHEN 'SDF4' THEN 'Rx'
        WHEN 'SDF6' THEN 'Rx'
        ELSE 'Unknown'
    END AS BUSINESS_UNIT,
    -- Legacy Regex KPI Check
    CASE
        WHEN REGEXP_LIKE(PRIMARY_TEXT, '.*(discriminat\\w*|harass\\w*|retaliat\\w*|hostil\\w*|threat\\w*|racis\\w*|sex\\w*|union\\w*|organiz\\w*|strik\\w*|protest\\w*|picket\\w*|violen\\w*|attorney\\w*|counsel\\w*|illeg\\w*|suicide\\w*|touch\\w*|\\bEEOC\\b|\\bDOL\\b|\\bOSHA\\b|\\bADA\\b|\\bFLSA\\b|\\bFMLA\\b|law|\\bCEO\\b|\\bSumit\\b|\\bCTO\\b|\\bCHRO\\b|\\bCMO\\b|wrongful term\\w*).*', 'is') THEN 'Level 1 Priority'
        WHEN REGEXP_LIKE(PRIMARY_TEXT, '.*(Inconsistent\\w*|unfair\\w*|favorit\\w*|unjust\\w*|bully\\w*|abus\\w*|unsaf\\w*|risk\\w*|danger\\w*|inappropriate\\w*|intimidate\\w*|aggress\\w*|assault\\w*|drunk\\w*|drug\\w*|alcohol\\w*|marijuana\\w*|\\bpot\\b|falsif\\w*|\\bhot\\b|\\btemparature\\b|\\bheat\\b|freez\\w*|burn\\w*|wage\\w*|safe\\w*|under the influence).*', 'is') THEN 'Level 2 Priority'
        WHEN REGEXP_LIKE(PRIMARY_TEXT, '.*(dispute\\w*|conflict\\w*|berate\\w*|disrespect\\w*|demean\\w*|hate\\w*|violat\\w*|steal\\w*|theft\\w*|toxic\\w*|unrespons\\w*|disresp\\w*|teas\\w*).*', 'is') THEN 'Level 3 Priority'
        ELSE NULL
    END AS LEGACY_REGEX_ESCALATION
FROM ALL_SOURCES
WHERE SITE_CODE NOT IN ('BOS4', 'SDF1')
  AND ROW_DATE >= '2025-01-01'
  AND VOICE_MECHANISM NOT IN (
      'Monthly Engagement Calendar',
      'Chewtopian of the Month (Non-Exempt)',
      'Fishbowl Display',
      'All Manager Meeting Slides',
      'Leader of the Pack (Exempt)',
      'All Paws'
  )
ORDER BY SITE_CODE, ROW_DATE DESC, PRIMARY_TEXT, CREATED;
```

---

## 9. Deduplication Strategy

### 9.1 VOC Board → CAT Tracker Dedup

VOC Board entries are excluded if an exact match exists in the CAT Tracker on three dimensions:

```sql
NOT EXISTS (
    SELECT 1 
    FROM EDLDB.PEOPLE_ANALYTICS_SANDBOX.FULFILLMENT_CAT_TRACKER CAT
    WHERE LEFT(CAT.SHEET_NAME, 4) = VOC.LOCATION
      AND CAT.ROW_DATE = VOC.DATE_POSTED
      AND LOWER(TRIM(CAT.PRIMARY_TEXT)) = LOWER(TRIM(VOC.FEEDBACK))
)
```

This prevents double-counting when site leaders copy VOC Board comments into the CAT Tracker.

### 9.2 Survey Filler Filtering

Both New Hire and Week 3 surveys filter out non-substantive responses using an explicit exclusion list of common filler values (e.g., "n/a", "none", "nothing", "all good", "it was great"). The Week 3 survey has a slightly expanded list including "not really", "nope", "none at this time".

---

## 10. Administrative Mechanism Exclusion

Six mechanism types are excluded from the unified output because they represent administrative artifacts, not TM feedback:

| Excluded Mechanism | Reason |
| --- | --- |
| Monthly Engagement Calendar | Calendar event, not feedback |
| Chewtopian of the Month (Non-Exempt) | Recognition program entry |
| Fishbowl Display | Administrative display |
| All Manager Meeting Slides | Meeting material |
| Leader of the Pack (Exempt) | Recognition program entry |
| All Paws | Administrative |

---

## 11. Data Refresh and Timing

| Parameter | Current (Interim) | Target (EPA Pipeline) |
| --- | --- | --- |
| **Pipeline type** | Manual SQL execution + CSV export | Automated ETL/ELT |
| **Refresh frequency** | Per reporting cycle (manual) | TBD by EPA |
| **Source latency** | Source tables updated by EPA data loads | Same |
| **Date filter** | `ROW_DATE >= '2025-01-01'` (hardcoded) | Configurable per reporting period |
| **Report generation** | Manual HTML report creation using `05 – Application & UX/2025_VOC_Pulse_Report.html` as structural template. See Report Skeleton (Section 12) for 18-step replication checklist. | Target: automated via Phoenix agent |

---

## 12. Security and Access Control

| Concern | Approach |
| --- | --- |
| **Data access** | Unified dataset contains free-text TM feedback (potentially sensitive). Access restricted via Snowflake RBAC. |
| **PII considerations** | `PRIMARY_TEXT` may contain incidental PII (names, situations). Report output is aggregated — no individual signals are published in the VOC Pulse Report. |
| **Escalation data** | `LEGACY_REGEX_ESCALATION` flags are for ER routing only; flagged signals require human review before action. |
| **Report distribution** | VOC Pulse Report distributed to authorized FC and network leadership only. |

---

## 13. Future Enhancements

| Enhancement | Phase | Owner |
| --- | --- | --- |
| EPA automated pipeline replacing interim SQL | 2 | EPA + ORBIT |
| Materialized unified view in Snowflake | 2 | EPA |
| LLM-driven thematic classification (replacing manual CATEGORY) | 2+ | Phoenix / ORBIT |
| Automated report generation via Phoenix agent | 3 | Phoenix / ORBIT |
| Real-time signal alerting for Level 1 escalations | 3+ | ER + ORBIT |
| Rx network expansion with site-level analysis | 2+ | ORBIT |

---

## 14. Dependencies and Risks

| Dependency / Risk | Mitigation |
| --- | --- |
| EPA pipeline timeline | Interim SQL is production-ready and documented; can run indefinitely |
| Source table schema changes | Document all column mappings; alert on schema drift |
| New listening channels added | Extend `ALL_SOURCES` CTE with new `UNION ALL` block |
| New sites added | Add site code to `BUSINESS_UNIT` CASE expression |
| Filler value list incomplete | Review survey responses quarterly; add new filler values as discovered |
| Regex escalation false positives | Legacy regex is a screening tool only; all flags require human review |
| VOC Board dedup miss | Case-insensitive, trimmed text match; may miss paraphrased duplicates |
