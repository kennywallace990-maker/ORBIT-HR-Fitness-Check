# TMDM Paycode Reconciler — Data Dictionary

This document defines every field in the TMDM Paycode Reconciler output, including source columns from the three Snowflake gold-layer views and computed fields from the reconciliation CTE chain.

---

## 1. Source Views

| # | View | Database.Schema | Purpose |
| --- | --- | --- | --- |
| 1 | `GOLD_V_PEOPLE` | `EDLDB.UKG` | Employee master: demographics, org hierarchy, schedule group, supervisor, account status |
| 2 | `GOLD_V_SCHEDULE_TOTAL` | `EDLDB.UKG` | Daily scheduled hours per employee per paycode |
| 3 | `GOLD_V_TIMECARD_TOTAL` | `EDLDB.UKG` | Actual timecard hours (worked + time-off applied) per employee per paycode per day |

---

## 2. Output Columns

The current export returns 14 columns per defect row:

| # | Output Column | Data Type | Source | Source Column(s) | Nullable | Description | Example |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Business Unit | VARCHAR | Derived / labeled in export | `GOLD_V_PEOPLE.primary_org_path_txt`, `job_transfer_set` | No | Business unit / network value shown in the export | FC |
| 2 | Employee ID | VARCHAR | `GOLD_V_PEOPLE` | `person_number` | No | UKG employee identifier used to locate TM in UKG for corrections | 252212 |
| 3 | Employee Full Name | VARCHAR | `GOLD_V_PEOPLE` | `full_name` | No | Team member name | Magdits, Robert |
| 4 | Schedule Group Name | VARCHAR | `GOLD_V_PEOPLE` | `schedule_group` | Yes | UKG schedule group. Null for some non-FC populations. | Exempt, or specific shift code |
| 5 | Reports To | VARCHAR | `GOLD_V_PEOPLE` | `supervisor_full_name` | No | Direct supervisor name | Langston, Jacquez |
| 6 | Date | DATE | `GOLD_V_SCHEDULE_TOTAL` / `GOLD_V_TIMECARD_TOTAL` | `partition_date` | No | Timecard date for the flagged entry | 2026-03-02 |
| 7 | Hours Scheduled | FLOAT | Computed | `SUM(GOLD_V_SCHEDULE_TOTAL.hours_amount)` for eligible paycodes | No | Total scheduled eligible hours for the day, rounded to 2 decimals | 10.00 |
| 8 | Hours Worked | FLOAT | Computed | `SUM(GOLD_V_TIMECARD_TOTAL.hours_amount)` for in-scope work paycodes | No | Total worked hours for the day, rounded to 2 decimals | 8.50 |
| 9 | Time-Off Applied | FLOAT | Computed | `SUM(GOLD_V_TIMECARD_TOTAL.hours_amount)` for time-off paycodes | No | Total time-off paycode hours applied to the day, rounded to 2 decimals | 5.00 |
| 10 | Paycodes (name: HH:MM) | VARCHAR | Computed | `LISTAGG` of `GOLD_V_TIMECARD_TOTAL.pay_code` with formatted hours | No | Comma-separated paycode list with durations. PTO codes sort first. | PTO PAID: 05:00 |
| 11 | Over-Applied Hrs | FLOAT | Computed | `over_applied_hours` from reconciliation CTE | No | Total hours of time-off that exceed the available gap | 5.00 |
| 12 | Recommendation | VARCHAR | Computed | Derived from over-applied hours and schedule context | No | User-facing correction guidance | Reduce time-off by 5 hrs - HIGH PRIORITY |
| 13 | Root Cause | VARCHAR | Computed | Derived defect-driver label | Yes | Why the row was flagged | Excess Time-Off Applied |
| 14 | Schedule Anomaly | VARCHAR | Computed | Derived schedule exception flag | Yes | Schedule-related anomaly indicator when applicable | UNSCHEDULED_DAY_TIMEOFF |

---

## 3. Intermediate / Computed Fields

These fields are calculated within the CTE chain and used for output derivation or sorting but not all are directly displayed:

| # | Field | CTE | Data Type | Calculation | Displayed | Description |
| --- | --- | --- | --- | --- | --- | --- |
| 11 | `scheduled_eligible_hours` | `scheduled_eligible` | FLOAT | `SUM(schedule_totals.hours_amount)` for all 17 eligible paycodes | Yes (as "Hours Scheduled") | Total scheduled hours including both work and time-off eligible paycodes |
| 12 | `worked_hours` | `actual_worked` | FLOAT | `SUM(timecard_totals.hours_amount)` for 7 work paycodes | Yes (as "Hours Worked") | Actual hours worked based on Regular + Overtime paycodes |
| 13 | `timeoff_applied_hours` | `actual_timeoff` | FLOAT | `SUM(timecard_totals.hours_amount)` for 10 time-off paycodes | Yes (as "Time-Off Applied") | All time-off hours applied |
| 14 | `pto_hours_applied` | `actual_timeoff` | FLOAT | `SUM(CASE WHEN is_pto THEN hours_amount ELSE 0 END)` | No (used for sort) | PTO-specific hours applied (5 PTO paycodes only) |
| 15 | `over_applied_hours` | `reconciliation` | FLOAT | `GREATEST(0, timeoff_applied - GREATEST(0, scheduled_eligible - worked))` | Yes (as "Over-Applied Hrs") | Total hours of time-off that exceed the available gap |
| 16 | `pto_over_applied_hours` | `reconciliation` | FLOAT | `GREATEST(0, pto_hours_applied - GREATEST(0, scheduled_eligible - worked))` | No (used for sort order) | PTO-specific over-application for prioritization |
| 17 | `paycodes_detail` | `timeoff_detail` | VARCHAR | `LISTAGG` with HH:MM formatting, PTO codes first | Yes (as "Paycodes (name: HH:MM)") | Formatted paycode string |
| 18 | `cohort` | `employees` | VARCHAR | CASE on `primary_org_path_txt` and `job_transfer_set` | Yes (surfaced as "Business Unit" in the export) | Network / business-unit classification |

---

## 4. Paycode Reference

### 4.1 Work Paycodes (7) — used to calculate `worked_hours`

| Pay Code ID | Pay Code Name | Category |
| --- | --- | --- |
| 466 | Regular | Standard hours |
| 601 | Overtime | Standard OT |
| 2402 | Overtime $1.50 | Premium OT |
| 2503 | Overtime $2.00 | Premium OT |
| 2651 | Overtime $2.50 | Premium OT |
| 2153 | Overtime $3.00 | Premium OT |
| 2004 | Overtime $5.00 | Premium OT |

### 4.2 Time-Off Paycodes (10) — checked for over-application

| Pay Code ID | Pay Code Name | is_pto | Risk Category | Notes |
| --- | --- | --- | --- | --- |
| 479 | PTO PAID | TRUE | High | Most common; direct overpayment risk |
| 480 | PTO PAID PTO Sick | TRUE | High | Sick PTO bucket; same financial risk as PTO PAID |
| 481 | Vet Care - PTO PAID | TRUE | High | Vet Care specific PTO |
| 1002 | Intermittent Leave PTO | TRUE | High | Leave + overpayment risk |
| 503 | Customer Service PTO - VTO | TRUE | High | CS-specific VTO with PTO draw |
| 473 | Personal UNPAID | FALSE | Medium | No direct overpayment but compliance concern |
| 474 | Personal UNPD Call Off | FALSE | Medium-High | NCNS indicator; may be coding error |
| 1001 | Intermittent Leave-Unpaid | FALSE | Medium | FMLA/leave related; handle per leave policy |
| 3402 | TMDM Intermittent Leave | FALSE | Medium | TMDM-specific leave code |
| 3251 | Customer Care Total VTO | FALSE | Low | VTO-specific; CC population |

---

## 5. Network (Cohort) Classification

| Code | Full Name | Derivation Rule | In Primary Audit Scope |
| --- | --- | --- | --- |
| **FC** | Fulfillment Center | `UPPER(primary_org_path_txt) LIKE '%FULFILLMENT%'` OR `UPPER(job_transfer_set) LIKE '%FC%'` | Yes |
| **Rx** | Pharmacy | `UPPER(primary_org_path_txt) LIKE '%PHARMACY%'` OR `'%VET CARE%'` OR `'%HEALTHCARE%'` | Yes |
| **CC** | Customer Care | `UPPER(primary_org_path_txt) LIKE '%CUSTOMER CARE%'` OR `'%CUSTOMER SERVICE%'` | Secondary |
| **Other** | Corporate / Other | None of the above match | Secondary |

---

## 6. Risk Classification

| Level | Condition | Recommendation Format | Meaning |
| --- | --- | --- | --- |
| **High Priority** | `over_applied_hours >= 4` | "Reduce time-off by X hrs - HIGH PRIORITY" | Large mismatch; correct immediately |
| **Standard** | `0 < over_applied_hours < 4` | "Review and reduce time-off by X hrs" | Smaller mismatch; review before payroll close |

---

## 7. Employee Eligibility Filters

Applied in the `employees` CTE against `GOLD_V_PEOPLE`:

| Filter | Column | Condition | Rationale |
| --- | --- | --- | --- |
| Non-exempt only | `schedule_group` | `<> 'Exempt' OR IS NULL` | Exempt employees are out of scope |
| Active only | `account_status` | `<> 'Terminated'` | No terminated employees |
| Not deleted | `deleted` | `NOT deleted` | Exclude soft-deleted records |

---

## 8. Deduplication Logic

| Source View | Dedup Strategy |
| --- | --- |
| `GOLD_V_SCHEDULE_TOTAL` | `ROW_NUMBER() OVER (PARTITION BY person_id, partition_date, pay_code_id ORDER BY load_date_time DESC) = 1` — takes only the latest load per person/date/paycode |
| `GOLD_V_TIMECARD_TOTAL` | First aggregates `SUM(hours_amount)` by person/date/paycode/load_date_time, then applies `ROW_NUMBER()` on `load_date_time DESC` to take the latest |

Both views also filter `combined_pay_code_swt = FALSE` to exclude UKG-generated summary/combined paycode rows that would cause double-counting.

---

## 9. Date Range Configuration

| Mode | start_dt | end_dt | Use Case |
| --- | --- | --- | --- |
| **Previous week + current week** (default) | Previous week Sunday | Current week Saturday | Rolling two-week window: captures the prior week and the current week, with each week defined Sunday through Saturday |

---

## 10. Sort Order

Production output is sorted by:

1. `pto_over_applied_hours DESC` — highest PTO risk first
2. `employee_full_name ASC` — alphabetical within risk tier
3. `partition_date ASC` — chronological within employee

---

## 11. Data Quality Notes

| Issue | Impact | Mitigation |
| --- | --- | --- |
| Null `schedule_group` for some populations | Cannot determine shift pattern from this field alone | Use `job_transfer_set` or `primary_org_path_txt` for location/network |
| Multiple loads per person/date/paycode | Duplicate rows without dedup | `ROW_NUMBER()` on `load_date_time DESC` ensures latest record wins |
| `combined_pay_code_swt` rows | Double-counting of hours | Filtered out with `= FALSE` |
| Terminated or deleted employees | Should not appear in defect list | Excluded in `employees` CTE |
| Missing timecard data (no punches, no paycodes) | Person may appear with 0 worked and 0 timeoff | `FULL OUTER JOIN` + `COALESCE(0)` handles gracefully; filtered out if `over_applied_hours = 0` |
