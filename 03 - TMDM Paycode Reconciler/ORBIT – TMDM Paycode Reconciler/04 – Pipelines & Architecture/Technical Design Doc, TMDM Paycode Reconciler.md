# Technical Design Doc, TMDM Paycode Reconciler

| Field | Value |
| --- | --- |
| **Product** | TMDM Paycode Reconciler |
| **Platform** | ORBIT Phoenix |
| **Product Owner** | Kenny Wallace |
| **Version** | 1.0 |
| **Last Updated** | 2026-03-03 |

---

## 1. Overview

This document describes the architecture, data flow, Snowflake schema, reconciliation logic, production SQL, and operational considerations for the TMDM Paycode Reconciler ORBIT Phoenix agent.

---

## 2. Architecture

```text
┌──────────────────────┐     ┌──────────────────────┐
│   UKG Pro            │     │  UKG Time &           │
│   (People, Schedules)│     │  Attendance            │
│                      │     │  (Punches, Paycodes)   │
└──────────┬───────────┘     └──────────┬─────────────┘
           │                            │
           ▼                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    SNOWFLAKE  (EDLDB.UKG)                    │
│                                                              │
│  ┌─────────────────────┐  ┌──────────────────────────────┐  │
│  │ GOLD_V_PEOPLE        │  │ GOLD_V_SCHEDULE_TOTAL         │  │
│  │ (employee master,    │  │ (daily scheduled hours by     │  │
│  │  org path, supervisor│  │  person, paycode, date)       │  │
│  │  schedule group,     │  │                               │  │
│  │  account status)     │  │                               │  │
│  └─────────────────────┘  └──────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────┐                            │
│  │ GOLD_V_TIMECARD_TOTAL         │                            │
│  │ (actual hours by person,      │                            │
│  │  paycode, date — punches +    │                            │
│  │  paycode applications)        │                            │
│  └──────────────────────────────┘                            │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         RECONCILIATION QUERY (10 CTEs)                │   │
│  │  date_range → paycode_types → eligible_paycodes →     │   │
│  │  employees → schedule_totals → timecard_totals →      │   │
│  │  scheduled_eligible → actual_worked → actual_timeoff →│   │
│  │  reconciliation → final SELECT                        │   │
│  └──────────────────────────────┬───────────────────────┘   │
│                                 │                            │
└─────────────────────────────────┼────────────────────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │   PHOENIX / ORBIT         │
                    │   Agent Layer              │
                    │                            │
                    │   • System prompt          │
                    │   • SQL template router    │
                    │   • Intent classifier      │
                    │   • Response formatter     │
                    │   • Export handler          │
                    └──────────────┬─────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────┐
                    │   TMDM / HR / Payroll     │
                    │   End Users               │
                    └──────────────────────────┘
```

---

## 3. Source Systems

### 3.1 EDLDB.UKG.GOLD_V_PEOPLE

| Attribute | Detail |
| --- | --- |
| **Database.Schema.View** | `EDLDB.UKG.GOLD_V_PEOPLE` |
| **Purpose** | Employee master: demographics, org hierarchy, schedule group, supervisor, account status |
| **Key columns used** | `person_id`, `person_number` (employee_id), `full_name`, `job_transfer_set` (location), `supervisor_full_name`, `schedule_group`, `primary_org_path_txt`, `account_status`, `deleted` |
| **Grain** | 1 row per active employee |
| **Filters applied** | `schedule_group <> 'Exempt' OR schedule_group IS NULL`, `account_status <> 'Terminated'`, `NOT deleted` |

### 3.2 EDLDB.UKG.GOLD_V_SCHEDULE_TOTAL

| Attribute | Detail |
| --- | --- |
| **Database.Schema.View** | `EDLDB.UKG.GOLD_V_SCHEDULE_TOTAL` |
| **Purpose** | Daily scheduled hours per employee per paycode |
| **Key columns used** | `person_id`, `partition_date`, `hours_amount`, `pay_code`, `pay_code_id`, `combined_pay_code_swt`, `load_date_time` |
| **Grain** | 1 row per person per date per paycode (after dedup) |
| **Filters** | `combined_pay_code_swt = FALSE`; dedup via `ROW_NUMBER() OVER (PARTITION BY person_id, partition_date, pay_code_id ORDER BY load_date_time DESC) = 1` |

### 3.3 EDLDB.UKG.GOLD_V_TIMECARD_TOTAL

| Attribute | Detail |
| --- | --- |
| **Database.Schema.View** | `EDLDB.UKG.GOLD_V_TIMECARD_TOTAL` |
| **Purpose** | Actual timecard hours (worked + time-off applied) per employee per paycode per day |
| **Key columns used** | `person_id`, `partition_date`, `hours_amount`, `pay_code`, `pay_code_id`, `COMBINED_PAY_CODE_SWT`, `load_date_time` |
| **Grain** | 1 row per person per date per paycode (after aggregation + dedup) |
| **Filters** | `COMBINED_PAY_CODE_SWT = FALSE`; aggregated by `SUM(hours_amount)` then dedup via `ROW_NUMBER()` on `load_date_time DESC` |

---

## 4. Paycode Configuration

17 paycodes organized into two functional categories:

### 4.1 Work Paycodes (7)

Used to calculate actual worked hours. These reduce the "available time-off gap."

| Pay Code ID | Pay Code Name |
| --- | --- |
| 466 | Regular |
| 601 | Overtime |
| 2402 | Overtime $1.50 |
| 2503 | Overtime $2.00 |
| 2651 | Overtime $2.50 |
| 2153 | Overtime $3.00 |
| 2004 | Overtime $5.00 |

### 4.2 Time-Off Paycodes (10)

Checked for over-application. Subdivided by `is_pto` flag for PTO-specific prioritization.

| Pay Code ID | Pay Code Name | is_pto |
| --- | --- | --- |
| 479 | PTO PAID | TRUE |
| 480 | PTO PAID PTO Sick | TRUE |
| 481 | Vet Care - PTO PAID | TRUE |
| 1002 | Intermittent Leave PTO | TRUE |
| 503 | Customer Service PTO - VTO | TRUE |
| 473 | Personal UNPAID | FALSE |
| 474 | Personal UNPD Call Off | FALSE |
| 1001 | Intermittent Leave-Unpaid | FALSE |
| 3402 | TMDM Intermittent Leave | FALSE |
| 3251 | Customer Care Total VTO | FALSE |

---

## 5. Query Architecture (CTE Chain)

The production query uses 10 Common Table Expressions executed in sequence:

```text
1. date_range          → Defines report window (previous week through current week, with weeks defined Sunday through Saturday)
2. paycode_types       → Static lookup: 17 paycodes with category and is_pto flag
3. eligible_paycodes   → Filter: all 17 paycode IDs for schedule matching
4. employees           → Eligible population from GOLD_V_PEOPLE with cohort classification
5. schedule_totals     → Deduped scheduled hours from GOLD_V_SCHEDULE_TOTAL
6. timecard_totals     → Aggregated + deduped actual hours from GOLD_V_TIMECARD_TOTAL
7. scheduled_eligible  → SUM(scheduled hours) per person/date for eligible paycodes
8. actual_worked       → SUM(worked hours) per person/date for work paycodes only
9. actual_timeoff      → SUM(timeoff hours) + SUM(pto hours) per person/date
10. reconciliation     → FULL OUTER JOIN of scheduled vs worked vs timeoff
                          Computes over_applied_hours and pto_over_applied_hours
```

Final SELECT joins `employees`, `reconciliation`, and `timeoff_detail`, filters to `over_applied_hours > 0`, and applies risk classification.

---

## 6. Production SQL

```sql
WITH date_range AS (
    -- PREVIOUS WEEK + CURRENT WEEK: Previous Sunday through current week Saturday
    SELECT
        DATE_TRUNC('WEEK', CURRENT_DATE()) - 8 AS start_dt,
        DATE_TRUNC('WEEK', CURRENT_DATE()) + 5 AS end_dt
    -- LAST WEEK ONLY: Previous Sunday through Saturday (uncomment below, comment above)
    -- SELECT
    --     DATE_TRUNC('WEEK', CURRENT_DATE()) - 8 AS start_dt,
    --     DATE_TRUNC('WEEK', CURRENT_DATE()) - 2 AS end_dt
),

paycode_types AS (
    SELECT pay_code_id, pay_code, paycode_type, is_pto
    FROM (VALUES
        (466, 'Regular', 'work', FALSE),
        (601, 'Overtime', 'work', FALSE),
        (2402, 'Overtime $1.50', 'work', FALSE),
        (2503, 'Overtime $2.00', 'work', FALSE),
        (2651, 'Overtime $2.50', 'work', FALSE),
        (2153, 'Overtime $3.00', 'work', FALSE),
        (2004, 'Overtime $5.00', 'work', FALSE),
        (479, 'PTO PAID', 'timeoff', TRUE),
        (480, 'PTO PAID PTO Sick', 'timeoff', TRUE),
        (481, 'Vet Care - PTO PAID', 'timeoff', TRUE),
        (1002, 'Intermittent Leave PTO', 'timeoff', TRUE),
        (503, 'Customer Service PTO - VTO', 'timeoff', TRUE),
        (473, 'Personal UNPAID', 'timeoff', FALSE),
        (474, 'Personal UNPD Call Off', 'timeoff', FALSE),
        (1001, 'Intermittent Leave-Unpaid', 'timeoff', FALSE),
        (3402, 'TMDM Intermittent Leave', 'timeoff', FALSE),
        (3251, 'Customer Care Total VTO', 'timeoff', FALSE)
    ) AS t(pay_code_id, pay_code, paycode_type, is_pto)
),

eligible_paycodes AS (
    SELECT pay_code_id FROM paycode_types WHERE paycode_type IN ('work', 'timeoff')
),

employees AS (
    SELECT
        vp.person_id,
        vp.person_number AS employee_id,
        vp.full_name AS employee_full_name,
        vp.job_transfer_set AS location,
        vp.supervisor_full_name AS reports_to,
        vp.schedule_group,
        CASE
            WHEN UPPER(vp.primary_org_path_txt) LIKE '%FULFILLMENT%'
                 OR UPPER(vp.job_transfer_set) LIKE '%FC%' THEN 'FC'
            WHEN UPPER(vp.primary_org_path_txt) LIKE '%PHARMACY%'
                 OR UPPER(vp.primary_org_path_txt) LIKE '%VET CARE%'
                 OR UPPER(vp.primary_org_path_txt) LIKE '%HEALTHCARE%' THEN 'Rx'
            WHEN UPPER(vp.primary_org_path_txt) LIKE '%CUSTOMER CARE%'
                 OR UPPER(vp.primary_org_path_txt) LIKE '%CUSTOMER SERVICE%' THEN 'CC'
            ELSE 'Other'
        END AS cohort
    FROM EDLDB.UKG.GOLD_V_PEOPLE vp
    WHERE (vp.schedule_group <> 'Exempt' OR vp.schedule_group IS NULL)
        AND vp.account_status <> 'Terminated'
        AND NOT vp.deleted
),

schedule_totals AS (
    SELECT
        sc_st.person_id, sc_st.partition_date,
        sc_st.hours_amount, sc_st.pay_code, sc_st.pay_code_id
    FROM EDLDB.UKG.GOLD_V_SCHEDULE_TOTAL sc_st
    JOIN date_range dr ON sc_st.partition_date BETWEEN dr.start_dt AND dr.end_dt
    WHERE sc_st.combined_pay_code_swt = FALSE
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY sc_st.person_id, sc_st.partition_date, sc_st.pay_code_id
        ORDER BY sc_st.load_date_time DESC
    ) = 1
),

timecard_totals AS (
    SELECT
        tt.person_id, tt.partition_date,
        SUM(tt.hours_amount) AS hours_amount,
        tt.pay_code, tt.pay_code_id
    FROM EDLDB.UKG.GOLD_V_TIMECARD_TOTAL AS tt
    JOIN date_range dr ON tt.partition_date BETWEEN dr.start_dt AND dr.end_dt
    WHERE tt.COMBINED_PAY_CODE_SWT = FALSE
    GROUP BY tt.person_id, tt.partition_date, tt.pay_code, tt.pay_code_id, tt.load_date_time
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY tt.person_id, tt.partition_date, tt.pay_code_id
        ORDER BY tt.load_date_time DESC
    ) = 1
),

scheduled_eligible AS (
    SELECT
        s.person_id, s.partition_date,
        SUM(s.hours_amount) AS scheduled_eligible_hours
    FROM schedule_totals s
    JOIN eligible_paycodes ep ON s.pay_code_id = ep.pay_code_id
    GROUP BY s.person_id, s.partition_date
),

actual_worked AS (
    SELECT
        t.person_id, t.partition_date,
        SUM(t.hours_amount) AS worked_hours
    FROM timecard_totals t
    JOIN paycode_types pt ON t.pay_code_id = pt.pay_code_id AND pt.paycode_type = 'work'
    GROUP BY t.person_id, t.partition_date
),

actual_timeoff AS (
    SELECT
        t.person_id, t.partition_date,
        SUM(t.hours_amount) AS timeoff_applied_hours,
        SUM(CASE WHEN pt.is_pto THEN t.hours_amount ELSE 0 END) AS pto_hours_applied
    FROM timecard_totals t
    JOIN paycode_types pt ON t.pay_code_id = pt.pay_code_id AND pt.paycode_type = 'timeoff'
    GROUP BY t.person_id, t.partition_date
),

timeoff_detail AS (
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
),

reconciliation AS (
    SELECT
        COALESCE(se.person_id, aw.person_id, at.person_id) AS person_id,
        COALESCE(se.partition_date, aw.partition_date, at.partition_date) AS partition_date,
        COALESCE(se.scheduled_eligible_hours, 0) AS scheduled_eligible,
        COALESCE(aw.worked_hours, 0) AS worked,
        COALESCE(at.timeoff_applied_hours, 0) AS timeoff_applied,
        COALESCE(at.pto_hours_applied, 0) AS pto_hours_applied,
        GREATEST(0,
            COALESCE(at.timeoff_applied_hours, 0)
            - GREATEST(0, COALESCE(se.scheduled_eligible_hours, 0) - COALESCE(aw.worked_hours, 0))
        ) AS over_applied_hours,
        GREATEST(0,
            COALESCE(at.pto_hours_applied, 0)
            - GREATEST(0, COALESCE(se.scheduled_eligible_hours, 0) - COALESCE(aw.worked_hours, 0))
        ) AS pto_over_applied_hours
    FROM scheduled_eligible se
    FULL OUTER JOIN actual_worked aw
        ON se.person_id = aw.person_id AND se.partition_date = aw.partition_date
    FULL OUTER JOIN actual_timeoff at
        ON COALESCE(se.person_id, aw.person_id) = at.person_id
        AND COALESCE(se.partition_date, aw.partition_date) = at.partition_date
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
ORDER BY r.pto_over_applied_hours DESC, e.employee_full_name, r.partition_date;
```

---

## 7. Reconciliation Logic Detail

### 7.1 Core Formula

```text
available_gap = MAX(0, scheduled_eligible_hours - worked_hours)
over_applied_hours = MAX(0, timeoff_applied_hours - available_gap)
pto_over_applied_hours = MAX(0, pto_hours_applied - available_gap)
```

**Interpretation:** If a TM was scheduled for 10 hours and worked 6, there is a 4-hour gap available for time-off. If 5 hours of time-off were applied, 1 hour is over-applied.

### 7.2 Risk Classification

| Level | Condition | HR Action Text |
| --- | --- | --- |
| **High Priority** | `over_applied_hours >= 4` | "Reduce time-off by X hrs - HIGH PRIORITY" |
| **Standard** | `0 < over_applied_hours < 4` | "Review and reduce time-off by X hrs" |

### 7.3 Cohort (Network) Classification

| Cohort | Derivation Rule |
| --- | --- |
| **FC** | `primary_org_path_txt LIKE '%FULFILLMENT%'` OR `job_transfer_set LIKE '%FC%'` |
| **Rx** | `primary_org_path_txt LIKE '%PHARMACY%'` OR `'%VET CARE%'` OR `'%HEALTHCARE%'` |
| **CC** | `primary_org_path_txt LIKE '%CUSTOMER CARE%'` OR `'%CUSTOMER SERVICE%'` |
| **Other** | None of the above match |

### 7.4 Employee Eligibility

- `schedule_group <> 'Exempt'` OR `schedule_group IS NULL` (non-exempt only)
- `account_status <> 'Terminated'`
- `NOT deleted`

### 7.5 Deduplication Strategy

Both `schedule_totals` and `timecard_totals` use `ROW_NUMBER()` partitioned by `(person_id, partition_date, pay_code_id)` ordered by `load_date_time DESC` to take only the most recent record when multiple loads exist for the same entry.

### 7.6 Join Strategy

The `reconciliation` CTE uses a three-way `FULL OUTER JOIN` across `scheduled_eligible`, `actual_worked`, and `actual_timeoff` to ensure no records are lost when:

- A TM has a schedule but no timecard entries
- A TM has timecard entries but no schedule
- A TM has time-off applied but no worked hours

`COALESCE` ensures all three CTEs contribute to the final `person_id` and `partition_date`.

### 7.7 Paycodes Detail Formatting

The `timeoff_detail` CTE uses `LISTAGG` with custom formatting:

```text
PaycodeName: HH:MM
```

PTO paycodes sort first (via `CASE WHEN pt.is_pto THEN 0 ELSE 1 END`), then alphabetically by paycode name.

---

## 8. Date Range Configuration

| Mode | start_dt | end_dt | Use Case |
| --- | --- | --- | --- |
| **Previous week + current week** (default) | Previous week Sunday | Current week Saturday | Rolling two-week window: captures both the prior week and the current week, with each week defined Sunday through Saturday |

The `date_range` CTE is the single control point for period selection. The default mode covers the previous week through the current week, with weeks defined Sunday through Saturday, ensuring that both weekly windows are visible together.

---

## 9. Phoenix Agent Layer

### 9.1 Components

| Component | Description |
| --- | --- |
| **System Prompt** | Defines agent identity, capabilities, guardrails, and response templates |
| **SQL Template Router** | Maps 16 prompt types to SQL templates; injects filters via `{{FILTERS}}` tokens |
| **Intent Classifier** | Parses natural-language prompts for filter tokens (network, location, supervisor, employee ID, risk, pattern, date) |
| **Response Formatter** | Converts SQL results into formatted tables, KPI summaries, narratives, or root-cause breakdowns |
| **Export Handler** | Packages results for Excel/CSV download |

### 9.2 Default Behaviors

- If no network filter specified: include all cohorts (FC, Rx, CC, Other)
- If no date filter specified: use active pay period from `date_range` CTE
- Sort: `pto_over_applied_hours DESC`, `employee_full_name ASC`, `partition_date ASC`

---

## 10. Data Refresh and Timing

| Parameter | Current (Pilot) | Target (Production) |
| --- | --- | --- |
| **Refresh frequency** | Manual / on-demand | Daily, aligned to UKG ETL completion |
| **Source latency** | UKG → Snowflake ETL runs daily (overnight) | Same |
| **Data freshness** | T-1 | T-1 |
| **Availability target** | N/A | By 7:00 AM ET on business days |
| **Pay period scope** | Previous week + current week (Sunday–Saturday week definition) | Same |

---

## 11. Security and Access Control

| Concern | Approach |
| --- | --- |
| **Data access** | Reconciliation query contains PII (names, IDs). Access restricted via Snowflake RBAC + Phoenix access controls. |
| **Agent access** | Read-only to Snowflake views. No write access to source tables. |
| **Audit logging** | All agent queries logged for compliance. |
| **PII handling** | Employee data displayed only in audit workflow context. Agent does not cache PII outside session. |

---

## 12. Error Handling

| Scenario | Behavior |
| --- | --- |
| Query timeout | Display retry message with support contact |
| Empty result set | "No defects match your criteria for the active report window." |
| Unrecognized prompt | Display help response with prompt examples |
| Stale data | If latest `partition_date` > 1 day old, surface freshness warning |

---

## 13. Future Enhancements

| Enhancement | Phase |
| --- | --- |
| Materialize reconciliation as a Snowflake view or table for faster queries | 2 |
| Add `location` dimension join for richer site-level filtering | 2 |
| Integrate hire_date for tenure analysis without manual lookup | 2 |
| Join to Payroll ticket data for pre- vs. post-payroll capture rate KPI | 2+ |
| Automated defect routing to TMDM reps by location/network | 3 |
| Near-real-time refresh (intra-day) | 3+ |

---

## 14. Dependencies and Risks

| Dependency / Risk | Mitigation |
| --- | --- |
| UKG → Snowflake ETL reliability | Monitor ETL completion; alert on stale data |
| Paycode list changes in UKG | Maintain `paycode_types` CTE as config; review quarterly with TMDM |
| `combined_pay_code_swt` logic changes | Document filter rationale; test after UKG upgrades |
| `primary_org_path_txt` naming changes | Cohort classification may break if org path strings change; add monitoring |
| Snowflake compute costs | Monitor query credits; optimize with materialized view if needed |
