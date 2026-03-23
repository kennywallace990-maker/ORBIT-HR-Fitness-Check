# Runbook, ECHO Intelligence

| Field | Value |
| --- | --- |
| **Product** | ECHO Intelligence |
| **Platform** | ORBIT Phoenix |
| **Product Owner** | Kenny Wallace |
| **Version** | 1.0 |
| **Last Updated** | 2026-03-17 |

---

## 1. Overview

This runbook documents the operational procedures for executing the ECHO Intelligence pipeline, generating the VOC Pulse Report, and handling common operational scenarios. The current pipeline is an **interim SQL-based workflow** pending an EPA automated pipeline.

---

## 2. Pipeline Execution (Interim)

### 2.1 Prerequisites

- Snowflake access to `EDLDB.PEOPLE_ANALYTICS_SANDBOX` with read permissions on all 5 source tables
- SQL client (Snowflake web UI, DBeaver, or equivalent)
- The production SQL file: `ECHO Intellegance V2 (1).sql`

### 2.2 Execution Steps

| Step | Action | Notes |
| --- | --- | --- |
| 1 | Open Snowflake and connect to `EDLDB` | Use SSO credentials |
| 2 | Open the production SQL file | Located in product documentation (04 – Pipelines & Architecture) |
| 3 | Review the date filter | Default: `ROW_DATE >= '2025-01-01'`; adjust if reporting period changes |
| 4 | Execute the query | Runtime: typically 30–90 seconds depending on data volume |
| 5 | Export results to CSV | Use Snowflake export or client export functionality |
| 6 | Verify row count | Expected: ~19,000+ for FC network (2025 full year) |
| 7 | Spot-check: verify all 13 FC sites present | `SITE_CODE` column should contain all 13 codes |
| 8 | Spot-check: verify mechanism normalization | No raw `GM/HRM Floor Walk`, `Gembas`, or `STANDUP MEETINGS` values |

### 2.3 Report Generation

| Step | Action | Notes |
| --- | --- | --- |
| 1 | Filter CSV to `BUSINESS_UNIT = 'FC'` | Primary report scope |
| 2 | Aggregate by `SITE_CODE` and `CATEGORY` | Produces site-level signal counts |
| 3 | Calculate network averages | Total per category / total FC signals × 100 |
| 4 | Copy the gold-standard HTML | Copy `05 – Application & UX/2025_VOC_Pulse_Report.html` and rename for new period (e.g., `2026_Q1_VOC_Pulse_Report.html`) |
| 5 | Update report sections | Follow the 18-step replication checklist in `05 – Application & UX/Report Skeleton and Narrative Templates, ECHO Intelligence.md`, Section 12 |
| 6 | Use HTML entities for special chars | `&ndash;` (en-dash), `&rarr;` (arrow), `&hellip;` (ellipsis), `&ne;` (not-equal), `&ge;` (greater-equal). **Do not paste from Word/Docs** — causes encoding corruption. |
| 7 | Update inline SVG Sankey diagram | Adjust node labels, flow path `stroke-width` values (proportional to signal counts), and value labels in Appendix B SVG |
| 8 | Run test cases | Execute test cases from `06 – Testing & QA/Test Plan` |
| 9 | Verify in browser | Open HTML locally — all visuals (charts, Sankey, heatmap) render with zero external dependencies |
| 10 | Distribute report | Via authorized channels to FC leadership |

---

## 3. Modifying the Pipeline

### 3.1 Adding a New Site

1. Determine the 4-character `SITE_CODE` and business unit (FC or Rx)
2. Add a new `WHEN '[SITE_CODE]' THEN '[BU]'` line to the `BUSINESS_UNIT` CASE expression in the final SELECT
3. Update the site list in the PRD (01), Data Dictionary (03), and Technical Design Doc (04)
4. Re-run pipeline and verify the new site appears in output

### 3.2 Adding a New Source Table

1. Create a new `UNION ALL` block in the `ALL_SOURCES` CTE
2. Map source columns to the 15-column unified schema
3. Apply appropriate filters (date, non-null feedback, filler exclusion)
4. Set the `VOICE_MECHANISM` label
5. Update the Data Dictionary (03), Technical Design Doc (04), and Data Map (02)
6. Re-run pipeline and verify new source rows appear

### 3.3 Adding a New Filler Value

1. Identify the filler value and which source table(s) it affects
2. Add the value to the `LOWER(TRIM(...)) NOT IN (...)` list in the relevant `UNION ALL` block
3. Update the Filler Value Exclusion Lists in the Data Dictionary (03)

### 3.4 Adding a New Excluded Mechanism

1. Identify the administrative mechanism name
2. Add to the `VOICE_MECHANISM NOT IN (...)` filter in the final WHERE clause
3. Update the Administrative Mechanism Exclusion table in the Technical Design Doc (04)

### 3.5 Modifying Escalation Regex

1. Coordinate with ER on the pattern change
2. Update the `REGEXP_LIKE` expression in the final SELECT
3. Test against known signals (see Test Plan, Section 3.7)
4. Update documentation in the Technical Design Doc (04) and Data Map (02)

---

## 4. Troubleshooting

### 4.1 Common Issues

| Issue | Likely Cause | Resolution |
| --- | --- | --- |
| Query returns 0 rows | Date filter too restrictive; schema change | Check `ROW_DATE` filter; verify source table exists |
| Missing site in output | Site code not in source data or filtered out | Check if site has data in source tables for the reporting period |
| Duplicate signals | VOC Board dedup not working | Verify `NOT EXISTS` subquery matches on site + date + text |
| Unexpected mechanism names | New mechanism added to CAT Tracker | Add normalization rule to CASE expression if needed |
| `Unknown` business unit | New site code not in CASE expression | Add site to business unit classification |
| High row count spike | New source data loaded; filler values not filtered | Check for new filler patterns in survey data |
| Query timeout | Large data volume | Run during off-peak hours; consider materializing as a view |

### 4.2 Escalation Path

| Severity | Scenario | Action |
| --- | --- | --- |
| **Low** | Filler values slipping through | Add to exclusion list; re-run |
| **Medium** | Source table schema change | Investigate column changes; update SQL mapping |
| **High** | Source table unavailable | Contact EPA data engineering; use last known good export |
| **Critical** | Level 1 escalation signal identified | Route to ER immediately per escalation protocol |

---

## 5. Operational Calendar

| Activity | Frequency | Owner | Notes |
| --- | --- | --- | --- |
| Pipeline execution | Per reporting cycle | Product Owner | Adjust date filter for new period |
| Report generation | Per reporting cycle | Product Owner | Follow generation steps in Section 2.3 |
| Filler value review | Quarterly | Product Owner | Review survey responses for new filler patterns |
| Mechanism name audit | Quarterly | Product Owner | Check for new/changed mechanism names in CAT Tracker |
| Escalation regex review | Semi-annually | Product Owner + ER | Review pattern effectiveness with ER |
| Site list review | As needed | Product Owner | When new FC/Rx sites open or close |

---

## 6. Contacts

| Role | Responsibility |
| --- | --- |
| **Product Owner (Kenny Wallace)** | Pipeline execution, report generation, documentation |
| **EPA Data Engineering** | Source table maintenance, future automated pipeline |
| **Employee Relations** | Escalation review for Level 1/2/3 flagged signals |
| **FC Site Leadership** | Report consumers; validate insights and act on recommendations |
