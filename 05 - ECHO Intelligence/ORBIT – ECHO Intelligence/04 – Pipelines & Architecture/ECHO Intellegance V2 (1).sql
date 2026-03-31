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
