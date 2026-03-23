# TMDM Paycode Reconciler — SQL Templates

All templates build on the production CTE chain that queries three Snowflake gold-layer views: `EDLDB.UKG.GOLD_V_PEOPLE`, `EDLDB.UKG.GOLD_V_SCHEDULE_TOTAL`, and `EDLDB.UKG.GOLD_V_TIMECARD_TOTAL`. The full production SQL is documented in the Technical Design Doc.

Templates are modular — the agent injects filters via `{{FILTERS}}` tokens and can compose multiple templates for compound requests (e.g., executive summary = BASE + KPI + ROOT CAUSE).

---

## Shared CTE Foundation

Every template begins with the same 10-CTE chain from the production query. The CTEs are:

1. `date_range` — report window bounds (previous week through current week, with weeks defined Sunday through Saturday)
2. `paycode_types` — 17 paycodes with category and is_pto flag
3. `eligible_paycodes` — all 17 paycode IDs for schedule matching
4. `employees` — eligible population with cohort classification
5. `schedule_totals` — deduped scheduled hours
6. `timecard_totals` — aggregated + deduped actual hours
7. `scheduled_eligible` — SUM(scheduled hours) per person/date
8. `actual_worked` — SUM(worked hours) per person/date
9. `actual_timeoff` — SUM(timeoff hours) + SUM(pto hours)
10. `reconciliation` — FULL OUTER JOIN computing over_applied_hours

The templates below show only the **final SELECT** that replaces the production query's final SELECT. The CTE chain above it remains identical.

---

## 1. BASE QUERY

Full detail view — the default output for defect retrieval or filtered requests.

```sql
-- After the shared CTE chain, add:
, timeoff_detail AS (
    SELECT
        t.person_id, t.partition_date,
        LISTAGG(
            t.pay_code || ': '
            || LPAD(FLOOR(t.hours_amount)::VARCHAR, 2, '0') || ':'
            || LPAD(ROUND((t.hours_amount - FLOOR(t.hours_amount)) * 60)::VARCHAR, 2, '0'),
            ', '
        ) WITHIN GROUP (
            ORDER BY CASE WHEN pt.is_pto THEN 0 ELSE 1 END, t.pay_code
        ) AS paycodes_detail
    FROM timecard_totals t
    JOIN paycode_types pt ON t.pay_code_id = pt.pay_code_id AND pt.paycode_type = 'timeoff'
    GROUP BY t.person_id, t.partition_date
)
SELECT
    e.cohort                                    AS "Cohort",
    e.employee_id                               AS "Employee ID",
    e.employee_full_name                        AS "Employee Full Name",
    e.schedule_group                            AS "Schedule Group Name",
    e.reports_to                                AS "Reports To",
    r.partition_date                            AS "Date",
    ROUND(r.scheduled_eligible, 2)              AS "Hours Scheduled",
    ROUND(r.timeoff_applied, 2)                 AS "Total Hours Code Applied",
    td.paycodes_detail                          AS "Paycodes (name: HH:MM)",
    CASE
        WHEN r.over_applied_hours >= 4
            THEN 'Reduce time-off by ' || ROUND(r.over_applied_hours, 2) || ' hrs - HIGH PRIORITY'
        WHEN r.over_applied_hours > 0
            THEN 'Review and reduce time-off by ' || ROUND(r.over_applied_hours, 2) || ' hrs'
        ELSE NULL
    END                                         AS "HR Action"
FROM employees e
INNER JOIN reconciliation r ON r.person_id = e.person_id
LEFT JOIN timeoff_detail td ON r.person_id = td.person_id AND r.partition_date = td.partition_date
WHERE r.over_applied_hours > 0
  {{FILTERS}}
ORDER BY r.pto_over_applied_hours DESC, e.employee_full_name, r.partition_date;
```

### Filter Injection Patterns

Append to `{{FILTERS}}`:

| Filter | SQL Fragment |
| --- | --- |
| Network | `AND e.cohort = '{{network}}'` |
| Location | `AND e.location ILIKE '%{{location}}%'` |
| Supervisor | `AND e.reports_to ILIKE '%{{supervisor}}%'` |
| Employee ID | `AND e.employee_id = '{{employee_id}}'` |
| Risk level (High) | `AND r.over_applied_hours >= 4` |
| Risk level (Standard) | `AND r.over_applied_hours > 0 AND r.over_applied_hours < 4` |
| Defect pattern (NCNS) | `AND td.paycodes_detail ILIKE '%Call Off%'` |
| Defect pattern (PTO) | `AND td.paycodes_detail ILIKE '%PTO%'` |
| Date | `AND r.partition_date = '{{date}}'` |

---

## 2. KPI TEMPLATE

Returns key metrics for the previous week through current week.

```sql
-- After the shared CTE chain (no timeoff_detail needed):
SELECT 'Total Defect Rows'              AS kpi,
       COUNT(*)::VARCHAR                 AS value
FROM reconciliation r
JOIN employees e ON r.person_id = e.person_id
WHERE r.over_applied_hours > 0 {{FILTERS}}

UNION ALL
SELECT 'Unique Team Members',
       COUNT(DISTINCT e.employee_id)::VARCHAR
FROM reconciliation r
JOIN employees e ON r.person_id = e.person_id
WHERE r.over_applied_hours > 0 {{FILTERS}}

UNION ALL
SELECT 'Total Over-Applied Hours',
       ROUND(SUM(r.over_applied_hours), 2)::VARCHAR
FROM reconciliation r
JOIN employees e ON r.person_id = e.person_id
WHERE r.over_applied_hours > 0 {{FILTERS}}

UNION ALL
SELECT 'Total PTO Over-Applied Hours',
       ROUND(SUM(r.pto_over_applied_hours), 2)::VARCHAR
FROM reconciliation r
JOIN employees e ON r.person_id = e.person_id
WHERE r.over_applied_hours > 0 {{FILTERS}}

UNION ALL
SELECT 'High-Risk Defects (>= 4 hrs)',
       COUNT(*)::VARCHAR
FROM reconciliation r
JOIN employees e ON r.person_id = e.person_id
WHERE r.over_applied_hours >= 4 {{FILTERS}}

UNION ALL
SELECT 'High-Risk Rate (%)',
       ROUND(
           COUNT(*) FILTER (WHERE r.over_applied_hours >= 4) * 100.0
           / NULLIF(COUNT(*), 0), 1
       )::VARCHAR
FROM reconciliation r
JOIN employees e ON r.person_id = e.person_id
WHERE r.over_applied_hours > 0 {{FILTERS}}

UNION ALL
SELECT 'FC Defects',
       COUNT(*)::VARCHAR
FROM reconciliation r
JOIN employees e ON r.person_id = e.person_id
WHERE r.over_applied_hours > 0 AND e.cohort = 'FC' {{FILTERS}}

UNION ALL
SELECT 'Rx Defects',
       COUNT(*)::VARCHAR
FROM reconciliation r
JOIN employees e ON r.person_id = e.person_id
WHERE r.over_applied_hours > 0 AND e.cohort = 'Rx' {{FILTERS}};
```

---

## 3. ROOT CAUSE TEMPLATE

Breaks down defects by paycode pattern.

```sql
-- After the shared CTE chain, add timeoff_detail, then:
SELECT
    CASE
        WHEN td.paycodes_detail ILIKE '%Personal UNPD Call Off%'     THEN 'NCNS'
        WHEN td.paycodes_detail ILIKE '%Intermittent Leave%'         THEN 'Intermittent Leave'
        WHEN td.paycodes_detail ILIKE '%Personal UNPAID%'
             AND td.paycodes_detail NOT ILIKE '%PTO%'                THEN 'Personal Unpaid'
        WHEN td.paycodes_detail ILIKE '%PTO%'
             AND td.paycodes_detail ILIKE '%Personal%'               THEN 'Mixed (PTO + Personal)'
        WHEN td.paycodes_detail ILIKE '%PTO%'                        THEN 'PTO Over-Application'
        ELSE 'Other'
    END                                         AS defect_pattern,
    COUNT(*)                                    AS defect_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_total,
    ROUND(SUM(r.over_applied_hours), 2)         AS total_over_applied_hrs,
    ROUND(AVG(r.over_applied_hours), 2)         AS avg_over_applied_hrs,
    COUNT(DISTINCT e.employee_id)               AS unique_tms
FROM employees e
INNER JOIN reconciliation r ON r.person_id = e.person_id
LEFT JOIN timeoff_detail td ON r.person_id = td.person_id AND r.partition_date = td.partition_date
WHERE r.over_applied_hours > 0
  {{FILTERS}}
GROUP BY defect_pattern
ORDER BY defect_count DESC;
```

---

## 4. DAY-OF-WEEK TEMPLATE

7-row distribution of defects by day of week.

```sql
-- After the shared CTE chain:
SELECT
    DAYNAME(r.partition_date)                   AS day_of_week,
    DAYOFWEEK(r.partition_date)                 AS day_number,
    COUNT(*)                                    AS defect_count,
    ROUND(SUM(r.over_applied_hours), 2)         AS total_over_applied_hrs,
    COUNT(DISTINCT e.employee_id)               AS unique_tms
FROM employees e
INNER JOIN reconciliation r ON r.person_id = e.person_id
WHERE r.over_applied_hours > 0
  {{FILTERS}}
GROUP BY DAYNAME(r.partition_date), DAYOFWEEK(r.partition_date)
ORDER BY day_number;
```

---

## 5. TENURE TEMPLATE

Buckets defects by employee tenure. Requires hire_date from an employee dimension (future enhancement).

```sql
-- After the shared CTE chain:
-- NOTE: This template requires a hire_date field not currently in GOLD_V_PEOPLE.
-- When available, join to employee_dim or equivalent:
SELECT
    CASE
        WHEN DATEDIFF('month', e_dim.hire_date, CURRENT_DATE()) < 3   THEN '0-3 months (New Hire)'
        WHEN DATEDIFF('month', e_dim.hire_date, CURRENT_DATE()) < 12  THEN '3-12 months'
        WHEN DATEDIFF('month', e_dim.hire_date, CURRENT_DATE()) < 24  THEN '1-2 years'
        WHEN DATEDIFF('month', e_dim.hire_date, CURRENT_DATE()) < 60  THEN '2-5 years'
        ELSE '5+ years (Veteran)'
    END                                         AS tenure_bucket,
    COUNT(*)                                    AS defect_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_total,
    ROUND(SUM(r.over_applied_hours), 2)         AS total_over_applied_hrs,
    COUNT(DISTINCT e.employee_id)               AS unique_tms
FROM employees e
INNER JOIN reconciliation r ON r.person_id = e.person_id
LEFT JOIN employee_dim e_dim ON e.employee_id = e_dim.employee_id
WHERE r.over_applied_hours > 0
  {{FILTERS}}
GROUP BY tenure_bucket
ORDER BY
    CASE tenure_bucket
        WHEN '0-3 months (New Hire)' THEN 1
        WHEN '3-12 months'           THEN 2
        WHEN '1-2 years'             THEN 3
        WHEN '2-5 years'             THEN 4
        ELSE 5
    END;
```

> **Note:** The `employee_dim` table and `hire_date` column must be confirmed with Enterprise People Analytics. Defer this template until data is provisioned.

---

## 6. NETWORK COMPARE TEMPLATE

Side-by-side metrics for two networks (default: FC vs Rx).

```sql
-- After the shared CTE chain:
SELECT
    e.cohort                                    AS network,
    COUNT(*)                                    AS defect_count,
    COUNT(DISTINCT e.employee_id)               AS unique_tms,
    ROUND(SUM(r.over_applied_hours), 2)         AS total_over_applied_hrs,
    ROUND(AVG(r.over_applied_hours), 2)         AS avg_over_applied_hrs,
    ROUND(SUM(r.pto_over_applied_hours), 2)     AS total_pto_over_applied_hrs,
    COUNT(*) FILTER (WHERE r.over_applied_hours >= 4) AS high_risk_count,
    ROUND(
        COUNT(*) FILTER (WHERE r.over_applied_hours >= 4)
        * 100.0 / NULLIF(COUNT(*), 0), 1
    )                                           AS high_risk_pct
FROM employees e
INNER JOIN reconciliation r ON r.person_id = e.person_id
WHERE r.over_applied_hours > 0
  AND e.cohort IN ('{{network_1}}', '{{network_2}}')
  {{FILTERS}}
GROUP BY e.cohort
ORDER BY e.cohort;
```

---

## 7. REPEAT OFFENDERS TEMPLATE

Employees appearing 2+ times in the current report window (previous week through current week).

```sql
-- After the shared CTE chain:
SELECT
    e.cohort                                    AS network,
    e.employee_id,
    e.employee_full_name,
    e.reports_to                                AS supervisor,
    COUNT(*)                                    AS defect_count,
    ROUND(SUM(r.over_applied_hours), 2)         AS total_over_applied_hrs,
    ROUND(SUM(r.pto_over_applied_hours), 2)     AS total_pto_over_applied_hrs,
    LISTAGG(DISTINCT r.partition_date::VARCHAR, ', ')
        WITHIN GROUP (ORDER BY r.partition_date) AS defect_dates
FROM employees e
INNER JOIN reconciliation r ON r.person_id = e.person_id
WHERE r.over_applied_hours > 0
  {{FILTERS}}
GROUP BY e.cohort, e.employee_id, e.employee_full_name, e.reports_to
HAVING COUNT(*) >= 2
ORDER BY total_pto_over_applied_hrs DESC, e.employee_full_name;
```

---

## Template Usage Notes

- All templates share the same 10-CTE foundation. The agent should prepend the full CTE chain before each template's final SELECT.
- `{{FILTERS}}` tokens are injected consistently across all templates.
- The default filter `AND e.cohort IN ('FC', 'Rx')` should be applied unless the user explicitly requests CC or Other.
- Sort order defaults to `pto_over_applied_hours DESC, employee_full_name, partition_date` to match the production query's prioritization.
- The `timeoff_detail` CTE is only needed for BASE QUERY and ROOT CAUSE templates; other templates can omit it for performance.
- The `date_range` CTE is the single control point for switching between current week and prior week modes.
