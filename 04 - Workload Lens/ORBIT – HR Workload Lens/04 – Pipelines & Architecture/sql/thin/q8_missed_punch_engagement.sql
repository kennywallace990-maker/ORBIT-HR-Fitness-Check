-- QUERY 8 (THIN) — Missed Punch Engagement Opportunities (Engagement List)
-- Standalone query — goes directly to V_TIMECARD_EXCEPTION, NOT through the audit pipeline.
-- Returns 0–500+ rows. 0 rows is valid (no flagged TMs). Never halt on 0 rows.
-- Caller must SET WEEK_START / WEEK_END session variables before executing.
--
-- PII WARNING: This query returns TM_NAME, TM_ID, and MANAGER columns.
-- These fields are PII and MUST only be surfaced in private/1:1 contexts.

WITH people_deduped AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY PERSON_NUMBER
            ORDER BY PERSON_ID DESC
        ) AS prn
    FROM EDLDB.UKG.V_PEOPLE
),
missed_punches_raw AS (
    SELECT
        e.PERSON_ID,
        DATE(e.EVENT_DATE) AS EVENT_DATE,
        COUNT(DISTINCT e.SHIFT_ID) AS DAILY_MISSED_PUNCHES
    FROM EDLDB.UKG.V_TIMECARD_EXCEPTION e
    WHERE e.EXCEPTION_TYPE_NAME IN ('Missed In Punch', 'Missed Out Punch')
      AND DATE(e.EVENT_DATE) BETWEEN $WEEK_START AND $WEEK_END
    GROUP BY e.PERSON_ID, DATE(e.EVENT_DATE)
),
weekly_totals AS (
    SELECT
        PERSON_ID,
        SUM(DAILY_MISSED_PUNCHES)  AS WEEKLY_MISSED_PUNCHES,
        MAX(DAILY_MISSED_PUNCHES)  AS MAX_DAILY_MISSED_PUNCHES,
        COUNT(DISTINCT EVENT_DATE) AS MISSED_DAYS,
        LISTAGG(TO_VARCHAR(EVENT_DATE, 'MM/DD'), ', ') 
            WITHIN GROUP (ORDER BY EVENT_DATE) AS MISSED_DATES
    FROM missed_punches_raw
    GROUP BY PERSON_ID
),
flagged AS (
    SELECT
        w.*,
        p.PERSON_NUMBER     AS EMPLOYEE_ID,
        p.FIRST_NAME || ' ' || p.LAST_NAME AS EMPLOYEE_FULL_NAME,
        p.EMPLOYMENT_STATUS AS EMPLOYEE_STATUS,
        COALESCE(p.SUPERVISOR_FULL_NAME, 'N/A') AS REPORTS_TO,
        REGEXP_SUBSTR(p.PRIMARY_ORG_PATH_TXT, '- ([A-Z0-9]{3,5})/', 1, 1, 'e') AS BUILDING_LOCATION,
        CASE
            WHEN REGEXP_SUBSTR(p.PRIMARY_ORG_PATH_TXT,'- ([A-Z0-9]{3,5})/',1,1,'e') IN ('AVP1','AVP2','BNA1','CFC1','CLT1','DAY1','DFW1','HOU1','MCI1','MCO1','MDT1','PHX1','RNO1') THEN 'FC'
            WHEN REGEXP_SUBSTR(p.PRIMARY_ORG_PATH_TXT,'- ([A-Z0-9]{3,5})/',1,1,'e') IN ('AVP4','AVP5','AVP6','DFW5','DFW8','MCO4','MCO5','PHX2','PHX5','SDF2','SDF4','SDF5','SDF6') THEN 'Rx'
            WHEN REGEXP_SUBSTR(p.PRIMARY_ORG_PATH_TXT,'- ([A-Z0-9]{3,5})/',1,1,'e') IN ('ATLA','ATLB','ATLC','ATLD','AUSA','DENA','DENB','DEND','DFWA','DFWB','FLLA','FLLB','FLLC','FLLD','FLLF','IAHA','IAHD','PHXB') THEN 'CVC'
            WHEN REGEXP_SUBSTR(p.PRIMARY_ORG_PATH_TXT,'- ([A-Z0-9]{3,5})/',1,1,'e') IN ('AV4V','DF4V','DFW4','FL3V','PH0V','PW0V','SD2V') THEN 'CC'
            ELSE 'Other'
        END AS OBR_SITE_GROUP
    FROM weekly_totals w
    JOIN people_deduped p ON w.PERSON_ID = p.PERSON_ID AND p.prn = 1
    WHERE p.EMPLOYMENT_STATUS = 'Active'
      AND (w.MAX_DAILY_MISSED_PUNCHES >= 2 OR w.WEEKLY_MISSED_PUNCHES >= 3)
)
SELECT
    OBR_SITE_GROUP  AS BU,
    BUILDING_LOCATION AS SITE,
    EMPLOYEE_FULL_NAME AS TM_NAME,
    EMPLOYEE_ID AS TM_ID,
    REPORTS_TO AS MANAGER,
    WEEKLY_MISSED_PUNCHES AS MISSED_COUNT,
    MISSED_DATES AS LOGS
FROM flagged
ORDER BY OBR_SITE_GROUP, BUILDING_LOCATION, WEEKLY_MISSED_PUNCHES DESC;
