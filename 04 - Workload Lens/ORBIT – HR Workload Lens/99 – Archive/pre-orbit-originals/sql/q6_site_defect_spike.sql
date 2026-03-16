-- QUERY 6 — Site-Level Defect Stats with 1σ Spike Flags (Section 5)
-- Returns ~50 rows. Joins current-week data with 13-week baseline view.
-- v2.0 changes: Same shared CTE preamble as Q1.
-- v2.0 DPMO change: Multiplier updated from × 1000 to × 1000000 (PRD §5.1)

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
    WHERE PARTITION_DATE BETWEEN (SELECT WEEK_START FROM week_window) AND (SELECT WEEK_END FROM week_window)
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
    WHERE EVENT_DATE BETWEEN (SELECT WEEK_START FROM week_window) AND (SELECT WEEK_END FROM week_window)
    GROUP BY PERSON_ID
),
base AS (
    SELECT a.PERSON_NUMBER AS EMPLOYEE_ID, p.FIRST_NAME||' '||p.LAST_NAME AS EMPLOYEE_FULL_NAME,
        p.EMPLOYMENT_STATUS AS EMPLOYEE_STATUS, p.SUPERVISOR_FULL_NAME AS REPORTS_TO,
        REGEXP_SUBSTR(p.PRIMARY_ORG_PATH_TXT,'- ([A-Z0-9]{3,5})/',1,1,'e') AS BUILDING_LOCATION,
        a.AUDIT_REVISION_USER_PERSON_NUMBER AS REVISION_USER_ID,
        rev.ACCESS_PROFILE, rev.FIRST_NAME||' '||rev.LAST_NAME AS REVISION_USER_FULL_NAME,
        a.PARTITION_DATE AS ENTITY_EVENT_DATE, a.AUDIT_TYPE AS ENTITY_TYPE,
        a.AUDIT_REVISION_TYPE AS REVISION_TYPE, a.AUDIT_PAYCODE_NAME AS PAYCODE_NAME,
        COALESCE(cmt.LINKED_COMMENTS, a.AUDIT_COMMENT_TEXT) AS COMMENT, COALESCE(cmt.LINKED_NOTES, a.AUDIT_NOTE_TEXT) AS NOTE_TEXT,
        CASE WHEN a.PERSON_NUMBER = a.AUDIT_REVISION_USER_PERSON_NUMBER
             THEN 'Self' ELSE 'Other' END AS EDIT_TARGET,
        a.AUDIT_DATASOURCE AS DATASOURCE,
        CASE WHEN p.FIRST_NAME||' '||p.LAST_NAME = rev.FIRST_NAME||' '||rev.LAST_NAME THEN 'Team Member'
             WHEN rev.ACCESS_PROFILE = 'Super Access No Wages' THEN 'Automation'
             WHEN rev.ACCESS_PROFILE IN ('Leave Support','Company Admin TMDM','Team Member Services','Super Access') THEN 'HRSS'
             WHEN rev.ACCESS_PROFILE IN ('Employee Basic','Employee Basic- Pharmacy','Training Basic','IT Admin','Training + Safety','Advanced Scheduler Lead','Advanced Scheduler Workforce Analyst','Facilities') THEN 'Team Member'
             WHEN rev.ACCESS_PROFILE IN ('Company Admin Site Specific','Workers Compensation') THEN 'Local HR'
             WHEN rev.ACCESS_PROFILE IN ('Manager Basic','Manager Basic With Punch&Schedule Edits','Practice Manager','Facilities Manager') THEN 'Local Ops'
             WHEN rev.ACCESS_PROFILE='Workforce Reporting' THEN 'WFM'
             ELSE 'Other' END AS OBR_ACTOR_GROUP,
        CASE WHEN REGEXP_SUBSTR(p.PRIMARY_ORG_PATH_TXT,'- ([A-Z0-9]{3,5})/',1,1,'e') IN ('AVP1','AVP2','BNA1','CFC1','CLT1','DAY1','DFW1','HOU1','MCI1','MCO1','MDT1','PHX1','RNO1') THEN 'FC'
             WHEN REGEXP_SUBSTR(p.PRIMARY_ORG_PATH_TXT,'- ([A-Z0-9]{3,5})/',1,1,'e') IN ('AVP4','AVP5','AVP6','DFW5','DFW8','MCO4','MCO5','PHX2','PHX5','SDF2','SDF4','SDF5','SDF6') THEN 'Rx'
             WHEN REGEXP_SUBSTR(p.PRIMARY_ORG_PATH_TXT,'- ([A-Z0-9]{3,5})/',1,1,'e') IN ('ATLA','ATLB','ATLC','ATLD','AUSA','DENA','DENB','DEND','DFWA','DFWB','FLLA','FLLB','FLLC','FLLD','FLLF','IAHA','IAHD','PHXB') THEN 'CVC'
             WHEN REGEXP_SUBSTR(p.PRIMARY_ORG_PATH_TXT,'- ([A-Z0-9]{3,5})/',1,1,'e') IN ('AV4V','DF4V','DFW4','FL3V','PH0V','PW0V','SD2V') THEN 'CC'
             ELSE NULL END AS OBR_SITE_GROUP,
        CASE WHEN a.AUDIT_TYPE='Punch' THEN TRUE
             WHEN a.AUDIT_TYPE='Historical Correction' THEN TRUE
             WHEN a.AUDIT_REVISION_TYPE IN ('Edit','Delete') AND a.AUDIT_TYPE IN ('Pay Code Edit','Manager Justified Time') THEN TRUE
             WHEN a.AUDIT_TYPE='Manager Justified Time' AND a.AUDIT_REVISION_TYPE='Add' AND (LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%late%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%early%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%ncns%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%call off%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%unpd%') THEN TRUE
             ELSE FALSE END AS BUCKET_B,
        CASE WHEN a.AUDIT_TYPE='Pay Code Edit' AND a.AUDIT_REVISION_TYPE='Add' THEN TRUE
             WHEN a.AUDIT_TYPE='Manager Justified Time' AND a.AUDIT_REVISION_TYPE='Add' AND NOT (LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%late%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%early%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%ncns%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%call off%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%unpd%') THEN TRUE
             ELSE FALSE END AS BUCKET_A,
        CASE WHEN a.AUDIT_TYPE IN ('Exception Comment','Punch Comment','Pay Code Edit Comment','Historical Correction Comment') THEN TRUE
             WHEN a.AUDIT_TYPE IN ('Mark as reviewed','Manager Approval') THEN TRUE
             ELSE FALSE END AS BUCKET_G,
        CASE WHEN a.AUDIT_TYPE='Historical Correction' THEN 5.0 WHEN a.AUDIT_REVISION_TYPE IN ('Edit','Delete') AND a.AUDIT_TYPE IN ('Punch','Pay Code Edit','Manager Justified Time') THEN 1.0 ELSE 0.5 END AS FRICTION_SCORE,
        CASE WHEN a.AUDIT_TYPE='Historical Correction' THEN TRUE WHEN a.AUDIT_TYPE='Punch' AND a.AUDIT_REVISION_TYPE IN ('Add','Edit','Delete') THEN TRUE WHEN a.AUDIT_TYPE='Pay Code Edit' AND a.AUDIT_REVISION_TYPE IN ('Add','Edit') AND (LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%pto%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%sick%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%regular%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%overtime%') THEN TRUE ELSE FALSE END AS HIGH_RISK_REWORK,
        CASE WHEN (a.AUDIT_COMMENT_TEXT IS NOT NULL AND TRIM(a.AUDIT_COMMENT_TEXT)<>'') OR (a.AUDIT_NOTE_TEXT IS NOT NULL AND TRIM(a.AUDIT_NOTE_TEXT)<>'') THEN 1 ELSE 0 END AS HAS_COMMENT,
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
        CASE WHEN LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%ncns%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%late%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%early%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%call off%' THEN 'Attendance Enforcement'
             WHEN LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%regular%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%overtime%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%meal%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%pto paid%' THEN 'Core Pay & Missing Time'
             WHEN LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%personal%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%vto%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%weather%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%unpaid%' THEN 'Schedule & Unpaid True-Ups'
             WHEN LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%leave%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%fmla%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%loa%' OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%bereavement%' THEN 'Leave & Compliance Lag'
             ELSE 'Other' END AS HC_CATEGORY,
        COALESCE(mpc.DAILY_MISSED_PUNCHES, 0) AS DAILY_MISSED_PUNCHES,
        COALESCE(wmt.WEEKLY_MISSED_PUNCHES, 0) AS WEEKLY_MISSED_PUNCHES,
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
      AND a.AUDIT_TYPE NOT IN ('Exception Comment', 'Punch Comment', 'Pay Code Edit Comment', 'Historical Correction Comment')
),
hr AS (SELECT * FROM base WHERE EDIT_TARGET != 'Self' AND OBR_SITE_GROUP IS NOT NULL AND OBR_ACTOR_GROUP NOT IN ('Team Member', 'Other', 'Automation', 'WFM')),
mp_dedup AS (SELECT DISTINCT EMPLOYEE_ID, ENTITY_EVENT_DATE, BUILDING_LOCATION, DAILY_MISSED_PUNCHES FROM hr WHERE DAILY_MISSED_PUNCHES > 0),
site_mp AS (SELECT BUILDING_LOCATION, SUM(DAILY_MISSED_PUNCHES) AS MISSED_PUNCH_COUNT FROM mp_dedup GROUP BY BUILDING_LOCATION),
site_stats AS (
    SELECT h.BUILDING_LOCATION, h.OBR_SITE_GROUP,
        COUNT(*) AS TOTAL_ACTIONS,
        SUM(CASE WHEN h.BUCKET_B THEN 1 ELSE 0 END) AS BUCKET_B_COUNT,
        COUNT(DISTINCT h.EMPLOYEE_ID) AS UNIQUE_TMS
    FROM hr h
    GROUP BY h.BUILDING_LOCATION, h.OBR_SITE_GROUP
    HAVING COUNT(DISTINCT h.EMPLOYEE_ID)>5
),
current_week_metrics AS (
    SELECT s.BUILDING_LOCATION, s.OBR_SITE_GROUP, s.TOTAL_ACTIONS, s.BUCKET_B_COUNT, s.UNIQUE_TMS,
        COALESCE(m.MISSED_PUNCH_COUNT, 0) AS MISSED_PUNCH_COUNT,
        ROUND(COALESCE(m.MISSED_PUNCH_COUNT, 0)/NULLIF(s.UNIQUE_TMS,0)*100,1) AS MP_PER_100_TMS,
        -- v2.0: DPMO updated from ×1000 to ×1000000 (PRD §5.1)
        ROUND(s.BUCKET_B_COUNT/NULLIF(s.UNIQUE_TMS*20,0)*1000000,2) AS DPMO,
        (s.BUCKET_B_COUNT / NULLIF(s.TOTAL_ACTIONS, 0)) * 100 AS DEFECT_RATE_PCT
    FROM site_stats s
    LEFT JOIN site_mp m ON s.BUILDING_LOCATION = m.BUILDING_LOCATION
)
SELECT 
    c.*,
    v.MEAN_13WK_DEFECT_RATE,
    v.SD_13WK_DEFECT_RATE,
    (v.MEAN_13WK_DEFECT_RATE + v.SD_13WK_DEFECT_RATE) AS UCL_13WK_DEFECT_RATE,
    CASE WHEN c.DEFECT_RATE_PCT > (v.MEAN_13WK_DEFECT_RATE + v.SD_13WK_DEFECT_RATE) THEN TRUE ELSE FALSE END AS IS_RED_SPIKE
FROM current_week_metrics c
LEFT JOIN EDLDB.PEOPLE_ANALYTICS_SANDBOX.V_HWL_WEEKLY_SITE_METRICS v
       ON c.BUILDING_LOCATION = v.BUILDING_LOCATION 
      AND v.REPORT_WEEK = DATE_TRUNC('WEEK', (SELECT WEEK_START FROM week_window))
ORDER BY c.DPMO DESC;
