-- QUERY 5 (THIN) — Historical Correction Root Cause Breakdown (Section 4)
-- Returns ~5 rows. Reads from V_HWL_HR view.
-- Caller must SET WEEK_START / WEEK_END session variables before executing.

SELECT HC_CATEGORY, COUNT(*) AS HC_COUNT
FROM EDLDB.PEOPLE_ANALYTICS_SANDBOX.V_HWL_HR
WHERE ENTITY_TYPE='Historical Correction'
GROUP BY HC_CATEGORY
ORDER BY HC_COUNT DESC;
