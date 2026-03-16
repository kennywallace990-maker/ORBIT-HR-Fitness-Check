-- =============================================================================
-- VIEW: V_HWL_HR
-- Schema: EDLDB.PEOPLE_ANALYTICS_SANDBOX
-- Purpose: Filtered version of V_HWL_BASE for all Q1-Q7 analytics.
--          Applies the standard hr CTE filters:
--            - Excludes self-service edits (EDIT_TARGET = 'Self')
--            - Excludes unmapped sites (OBR_SITE_GROUP IS NULL)
--            - Excludes Team Member, Other, Automation, and WFM actor groups
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
