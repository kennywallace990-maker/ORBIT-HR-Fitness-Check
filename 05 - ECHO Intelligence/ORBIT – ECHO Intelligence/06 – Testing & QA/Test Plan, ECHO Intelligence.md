# Test Plan, ECHO Intelligence

| Field | Value |
| --- | --- |
| **Product** | ECHO Intelligence |
| **Platform** | ORBIT Phoenix |
| **Product Owner** | Kenny Wallace |
| **Version** | 1.0 |
| **Last Updated** | 2026-03-17 |

---

## 1. Purpose

This document defines the test strategy, test cases, and acceptance criteria for the ECHO Intelligence pipeline and VOC Pulse Report. Testing ensures that the unified SQL query produces accurate, complete, and deduplicated output, and that the report correctly reflects the underlying data.

---

## 2. Test Strategy

| Layer | What Is Tested | Method |
| --- | --- | --- |
| **Pipeline SQL** | Query logic, joins, filters, dedup, normalization | SQL-level validation against source tables |
| **Data Completeness** | All expected sources and sites present in output | COUNT queries by source and site |
| **Data Accuracy** | Signal counts, category breakdowns, mechanism counts match source | Cross-reference unified output against individual source tables |
| **Deduplication** | VOC Board dedup against CAT Tracker working correctly | Targeted queries for known duplicate records |
| **Filler Filtering** | Non-substantive survey responses excluded | Spot-check filtered values against exclusion list |
| **Report Accuracy** | All figures in the VOC Pulse Report match unified dataset | Manual verification of hero stats, site totals, percentages, narratives |
| **Escalation Classification** | Regex patterns correctly flag/do not flag signals | Test corpus of known Level 1/2/3 and clean signals |

---

## 3. Pipeline SQL Test Cases

### 3.1 Source Completeness

| # | Test Case | Expected Result | SQL Validation |
| --- | --- | --- | --- |
| 1 | All 5 source tables contribute rows | Each source has > 0 rows in output | `SELECT VOICE_MECHANISM, COUNT(*) FROM output GROUP BY 1` — verify VOC Board, Standups, New Hire Survey, Week 3 Survey, and CAT Tracker mechanisms all present |
| 2 | All 13 FC sites present | 13 distinct FC site codes | `SELECT SITE_CODE, COUNT(*) FROM output WHERE BUSINESS_UNIT = 'FC' GROUP BY 1` |
| 3 | All Rx sites present | 7 distinct Rx site codes | `SELECT SITE_CODE, COUNT(*) FROM output WHERE BUSINESS_UNIT = 'Rx' GROUP BY 1` |
| 4 | Excluded sites absent | BOS4 and SDF1 not in output | `SELECT COUNT(*) FROM output WHERE SITE_CODE IN ('BOS4', 'SDF1')` → 0 |
| 5 | Date filter applied | No rows before 2025-01-01 | `SELECT COUNT(*) FROM output WHERE ROW_DATE < '2025-01-01'` → 0 |

### 3.2 Voice Mechanism Normalization

| # | Test Case | Expected Result |
| --- | --- | --- |
| 6 | No `GM/HRM Floor Walk`, `GM/HRM Walks`, or `Building Walk` in output | All mapped to `Site Leadership Walks` |
| 7 | No `Gembas` or `Gemba` (case-sensitive match) in output | All mapped to `Gemba Walks` |
| 8 | No `STANDUP MEETINGS` or `FULFILLMENT STANDUPS` in output | All mapped to `Standups` |
| 9 | NULL `VOICE_MECHANISM` from CAT Tracker defaults to `CAT Tracker` | No NULL mechanism values in output |

### 3.3 Administrative Mechanism Exclusion

| # | Test Case | Expected Result |
| --- | --- | --- |
| 10 | No `Monthly Engagement Calendar` rows | 0 rows |
| 11 | No `Chewtopian of the Month (Non-Exempt)` rows | 0 rows |
| 12 | No `Fishbowl Display` rows | 0 rows |
| 13 | No `All Manager Meeting Slides` rows | 0 rows |
| 14 | No `Leader of the Pack (Exempt)` rows | 0 rows |
| 15 | No `All Paws` rows | 0 rows |

### 3.4 VOC Board Deduplication

| # | Test Case | Expected Result |
| --- | --- | --- |
| 16 | VOC Board entries matching CAT Tracker on site + date + text are excluded | Identify a known duplicate; verify it appears once (from CAT Tracker), not twice |
| 17 | VOC Board entries with no CAT match are included | Identify a known unique VOC Board entry; verify it appears in output |
| 18 | Dedup is case-insensitive and trim-aware | Test with entries differing only by case or whitespace |

### 3.5 Survey Filler Filtering

| # | Test Case | Expected Result |
| --- | --- | --- |
| 19 | Standup responses of "n/a", "none", "yes" etc. are excluded | 0 rows with these exact `PRIMARY_TEXT` values from Standups |
| 20 | New Hire Survey responses of "nothing", "all good" etc. are excluded | 0 rows with filler values from New Hire Survey |
| 21 | Week 3 Survey responses of "nope", "not really" etc. are excluded | 0 rows with filler values from Week 3 Survey |
| 22 | Substantive survey responses are retained | Known substantive response present in output |

### 3.6 Business Unit Classification

| # | Test Case | Expected Result |
| --- | --- | --- |
| 23 | All 13 FC site codes classified as `FC` | `WHERE SITE_CODE IN ('AVP1','AVP2','BNA1','CFC1','CLT1','DAY1','DFW1','HOU1','MCI1','MCO1','MDT1','PHX1','RNO1') AND BUSINESS_UNIT = 'FC'` → all rows match |
| 24 | All 7 Rx site codes classified as `Rx` | Same pattern for Rx sites |
| 25 | Unrecognized site codes classified as `Unknown` | Any site code not in the CASE expression → `Unknown` |

### 3.7 Legacy Regex Escalation

| # | Test Case | Input Text | Expected Level |
| --- | --- | --- | --- |
| 26 | Level 1 — harassment | "My manager is harassing me daily" | Level 1 Priority |
| 27 | Level 1 — union | "We should organize a union" | Level 1 Priority |
| 28 | Level 2 — unsafe | "This area is unsafe to work in" | Level 2 Priority |
| 29 | Level 2 — favoritism | "There is clear favoritism in shift assignments" | Level 2 Priority |
| 30 | Level 3 — toxic | "The work environment is toxic" | Level 3 Priority |
| 31 | Clean signal | "We need more ladders on the mezzanine" | NULL |

---

## 4. Report Accuracy Test Cases

### 4.1 Hero Stats

| # | Test Case | Validation Method |
| --- | --- | --- |
| 32 | Total Signals matches `COUNT(*) WHERE BUSINESS_UNIT = 'FC'` | Compare report hero stat to SQL count |
| 33 | Active Sites matches `COUNT(DISTINCT SITE_CODE) WHERE BUSINESS_UNIT = 'FC'` | Compare to SQL count |
| 34 | Listening Channels count is accurate | Count distinct top-level channel types |
| 35 | Sub-Mechanisms matches `COUNT(DISTINCT VOICE_MECHANISM) WHERE BUSINESS_UNIT = 'FC'` | Compare to SQL count |

### 4.2 Site-Level Data

For each of the 13 FC sites:

| # | Test Case | Validation Method |
| --- | --- | --- |
| 36 | Site total signals matches `COUNT(*) WHERE SITE_CODE = '[X]' AND BUSINESS_UNIT = 'FC'` | Compare report value to SQL count |
| 37 | Unique mechanisms matches `COUNT(DISTINCT VOICE_MECHANISM) WHERE SITE_CODE = '[X]'` | Compare to SQL count |
| 38 | Category signal counts match `COUNT(*) WHERE SITE_CODE = '[X]' AND CATEGORY = '[Y]'` | Verify each category count cited in narrative |
| 39 | Category percentages = category count / site total × 100 | Recalculate and compare to report |
| 40 | Network average comparisons use correct baseline percentages | Verify against network benchmark table |

### 4.3 Monthly Volumes

| # | Test Case | Validation Method |
| --- | --- | --- |
| 41 | Monthly totals match `COUNT(*) WHERE BUSINESS_UNIT = 'FC' GROUP BY MONTH(ROW_DATE)` | Compare each month's total |
| 42 | Monthly category breakdowns match source | Verify per-category per-month counts |
| 43 | SVG chart data points match table values | Compare chart coordinates to table |

### 4.4 Appendix Data

| # | Test Case | Validation Method |
| --- | --- | --- |
| 44 | Appendix B site totals match site-level totals | Cross-reference Sankey data to site sections |
| 45 | Appendix C heatmap percentages match category_count / site_total | Recalculate each cell |
| 46 | Appendix E detailed breakdowns are consistent with narrative references | Spot-check signal mention counts |

---

## 5. Regression Testing

When the SQL pipeline is modified (new source, new site, new filter), run:

1. Full pipeline SQL test suite (Section 3)
2. Compare output row counts to previous known-good run
3. Verify no new NULL values in required columns (`SITE_CODE`, `VOICE_MECHANISM`, `ROW_DATE`, `PRIMARY_TEXT`)
4. Regenerate report and verify hero stats, site totals, and percentages

---

## 6. Acceptance Criteria

The pipeline and report pass testing when:

- All 46 test cases pass
- Zero old site totals, mechanism counts, or stale percentage references remain in the report
- Every percentage cited in the report can be derived from the underlying signal counts
- Every narrative reference to a signal count matches the data
- The report is structurally consistent with the 2025 reference implementation
