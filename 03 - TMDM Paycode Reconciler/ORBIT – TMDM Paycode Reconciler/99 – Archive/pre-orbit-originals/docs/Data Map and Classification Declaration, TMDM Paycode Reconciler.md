# Data Map and Classification Declaration, TMDM Paycode Reconciler

| Field | Value |
| --- | --- |
| **Product** | TMDM Paycode Reconciler |
| **Platform** | ORBIT Phoenix |
| **Product Owner** | Kenny Wallace |
| **Version** | 1.0 |
| **Last Updated** | 2026-03-03 |

---

## 1. Purpose

This document maps every data element used by the TMDM Paycode Reconciler from source system to agent output, classifies each element by sensitivity and PII status, and declares the data handling requirements for the product.

---

## 2. Data Lineage Overview

```text
SOURCE SYSTEMS                  SNOWFLAKE (EDLDB.UKG)              AGENT OUTPUT
──────────────                  ──────────────────────              ────────────

UKG Pro ──────────────────────► GOLD_V_PEOPLE ─────────┐
  • Employee master                                     │
  • Org hierarchy                                       ├──► Reconciliation
  • Schedule groups                                     │    Query (10 CTEs)
                                                        │         │
UKG Time & Attendance ────────► GOLD_V_SCHEDULE_TOTAL ──┤         │
  • Daily scheduled hours                               │         │
  • Paycode assignments                                 │         ▼
                                                        │    10-Column
UKG Time & Attendance ────────► GOLD_V_TIMECARD_TOTAL ──┘    Output Table
  • Actual punches                                           │
  • Paycode applications                                     ▼
                                                        Phoenix Agent
                                                        (tables, KPIs,
                                                         narratives,
                                                         exports)
```

---

## 3. Source-to-Output Field Map

### 3.1 From EDLDB.UKG.GOLD_V_PEOPLE

| Source Column | CTE | Output Column | Transformation | Data Classification |
| --- | --- | --- | --- | --- |
| `person_id` | `employees` | (join key only, not displayed) | None — used for joins | Internal Identifier |
| `person_number` | `employees` | **Employee ID** | Aliased to `employee_id` | **PII** — Employee Identifier |
| `full_name` | `employees` | **Employee Full Name** | Direct pass-through | **PII** — Employee Name |
| `job_transfer_set` | `employees` | **Location** (in employees CTE) | Aliased to `location`; also used in business-unit classification logic | Business Attribute |
| `supervisor_full_name` | `employees` | **Reports To** | Aliased to `reports_to` | **PII** — Employee Name (Supervisor) |
| `schedule_group` | `employees` | **Schedule Group Name** | Direct pass-through | Business Attribute |
| `primary_org_path_txt` | `employees` | **Business Unit** (derived / labeled in export) | Classification logic used to populate the business-unit field shown in the export | Business Attribute (derived) |
| `account_status` | `employees` | (filter only, not displayed) | `WHERE account_status <> 'Terminated'` | Internal Attribute |
| `deleted` | `employees` | (filter only, not displayed) | `WHERE NOT deleted` | Internal Flag |

### 3.2 From EDLDB.UKG.GOLD_V_SCHEDULE_TOTAL

| Source Column | CTE | Output Column | Transformation | Data Classification |
| --- | --- | --- | --- | --- |
| `person_id` | `schedule_totals` | (join key) | None | Internal Identifier |
| `partition_date` | `schedule_totals` | **Date** | Filtered by `date_range` CTE bounds | Business Attribute |
| `hours_amount` | `scheduled_eligible` | **Hours Scheduled** | `SUM(hours_amount)` grouped by person + date for eligible paycodes, then `ROUND(..., 2)` | Business Metric |
| `pay_code_id` | `schedule_totals` | (join key to `eligible_paycodes`) | Filtered to 17 eligible paycode IDs | Internal Identifier |
| `pay_code` | `schedule_totals` | (not directly displayed from schedules) | Used for paycode matching | Business Attribute |
| `combined_pay_code_swt` | `schedule_totals` | (filter only) | `WHERE combined_pay_code_swt = FALSE` | Internal Flag |
| `load_date_time` | `schedule_totals` | (dedup key) | `ROW_NUMBER() ... ORDER BY load_date_time DESC` to take latest | System Timestamp |

### 3.3 From EDLDB.UKG.GOLD_V_TIMECARD_TOTAL

| Source Column | CTE | Output Column | Transformation | Data Classification |
| --- | --- | --- | --- | --- |
| `person_id` | `timecard_totals` | (join key) | None | Internal Identifier |
| `partition_date` | `timecard_totals` | **Date** | Filtered by `date_range` CTE bounds | Business Attribute |
| `hours_amount` | `actual_worked`, `actual_timeoff`, `timeoff_detail` | **Hours Worked**, **Time-Off Applied**, **Paycodes (name: HH:MM)** | Aggregated by SUM; formatted via LISTAGG with HH:MM conversion | Business Metric |
| `pay_code_id` | `timecard_totals` | (join key to `paycode_types`) | Used to classify work vs. time-off and is_pto | Internal Identifier |
| `pay_code` | `timeoff_detail` | **Paycodes (name: HH:MM)** | Concatenated into LISTAGG string: pay_code + ': ' + HH:MM | Business Attribute |
| `COMBINED_PAY_CODE_SWT` | `timecard_totals` | (filter only) | `WHERE COMBINED_PAY_CODE_SWT = FALSE` | Internal Flag |
| `load_date_time` | `timecard_totals` | (dedup key) | `ROW_NUMBER() ... ORDER BY load_date_time DESC` | System Timestamp |

### 3.4 Computed / Derived Fields

| Field | CTE | Output Column | Derivation | Data Classification |
| --- | --- | --- | --- | --- |
| `scheduled_eligible_hours` | `scheduled_eligible` | **Hours Scheduled** | `SUM(schedule_totals.hours_amount)` for eligible paycodes | Business Metric |
| `worked_hours` | `actual_worked` | **Hours Worked** | `SUM(timecard_totals.hours_amount)` for work paycodes | Business Metric |
| `timeoff_applied_hours` | `actual_timeoff` | **Time-Off Applied** | `SUM(timecard_totals.hours_amount)` for time-off paycodes | Business Metric |
| `pto_hours_applied` | `actual_timeoff` | (intermediate — used for sort) | `SUM(CASE WHEN is_pto THEN hours_amount ELSE 0 END)` | Business Metric |
| `over_applied_hours` | `reconciliation` | **Over-Applied Hrs** | `GREATEST(0, timeoff_applied - GREATEST(0, scheduled_eligible - worked))` | Business Metric |
| `pto_over_applied_hours` | `reconciliation` | (sort key, not directly displayed) | `GREATEST(0, pto_hours_applied - GREATEST(0, scheduled_eligible - worked))` | Business Metric |
| `paycodes_detail` | `timeoff_detail` | **Paycodes (name: HH:MM)** | LISTAGG of pay_code + ': ' + HH:MM, ordered by is_pto then name | Business Attribute |
| `cohort` | `employees` | **Business Unit** | Classification field surfaced as business unit in the export | Business Attribute |
| Recommendation text | Final SELECT | **Recommendation** | CASE: high over-application and schedule exceptions mapped to user-facing action text | Business Recommendation |
| Root cause classification | Final SELECT | **Root Cause** | Derived defect-driver label based on schedule and paycode conditions | Business Attribute |
| Schedule anomaly flag | Final SELECT | **Schedule Anomaly** | Derived flag highlighting schedule-related exceptions when applicable | Business Attribute |

---

## 4. Data Classification Summary

### 4.1 Classification Levels

| Level | Definition | Examples in This Product |
| --- | --- | --- |
| **PII (Personally Identifiable Information)** | Data that can identify a specific individual | Employee ID, Employee Full Name, Supervisor Name |
| **Business Sensitive** | Operational data that is not PII but is internal/confidential | Paycode details, over-applied hours, recommendations, root cause labels, schedule groups |
| **Internal** | System identifiers and flags used in processing but not directly sensitive | person_id, pay_code_id, load_date_time, deleted flag, combined_pay_code_swt |

### 4.2 PII Inventory

| PII Element | Source Column | Output Column | PII Type | Justification for Inclusion |
| --- | --- | --- | --- | --- |
| **Employee ID** | `person_number` | Employee ID | Direct Identifier | Required for TMDM to locate the TM's timecard in UKG for correction |
| **Employee Full Name** | `full_name` | Employee Full Name | Direct Identifier | Required for TMDM workflow — reps identify TMs by name when navigating UKG |
| **Supervisor Full Name** | `supervisor_full_name` | Reports To | Direct Identifier | Required for filtering by team and for Field HR routing |

### 4.3 Sensitive Business Data

| Element | Output Column | Sensitivity | Reason |
| --- | --- | --- | --- |
| Over-applied hours | Over-Applied Hrs | Business Sensitive | Indicates potential payroll error — financial and compliance implications |
| Paycode details | Paycodes (name: HH:MM) | Business Sensitive | Reveals leave type usage (PTO, FMLA, unpaid) — health/leave privacy consideration |
| Schedule group | Schedule Group Name | Internal | Encodes shift pattern and location |
| Business-unit classification | Business Unit | Internal | Derived network / business-unit assignment |

---

## 5. Data Handling Requirements

### 5.1 Access Controls

| Requirement | Implementation |
| --- | --- |
| **Who can access** | Authorized TMDM reps, HRSS leadership, Payroll team, and designated Field HR partners |
| **Access mechanism** | Phoenix / ORBIT role-based access control + Snowflake RBAC grants |
| **Authentication** | SSO via corporate identity provider |
| **Authorization granularity** | Product-level access (all users see all networks); future: network-level RBAC if needed |

### 5.2 Data Retention

| Requirement | Policy |
| --- | --- |
| **Active data** | Rolling two-week window: previous week through current week, with weeks defined Sunday through Saturday |
| **Historical retention** | No persistent storage in Phoenix agent; query executes on-demand against Snowflake views |
| **Snowflake source retention** | Per enterprise data retention policy for `EDLDB.UKG` schema |
| **Agent session data** | Not cached beyond session; no persistent PII storage in the agent layer |

### 5.3 Data Transport

| Path | Method | Encryption |
| --- | --- | --- |
| UKG → Snowflake | Enterprise ETL pipeline (daily batch) | Encrypted in transit and at rest per enterprise policy |
| Snowflake → Phoenix Agent | Snowflake JDBC/ODBC query | TLS encrypted in transit; Snowflake encryption at rest |
| Phoenix Agent → End User | HTTPS via Phoenix web UI | TLS 1.2+ |
| Export (Excel/CSV) | Downloaded via browser | User's local device; subject to endpoint security policy |

### 5.4 Data Minimization

| Principle | Implementation |
| --- | --- |
| **Only necessary PII** | 3 PII fields included (Employee ID, Name, Supervisor); minimum viable for TMDM workflow |
| **No SSN, DOB, or compensation data** | Not queried, not available in output |
| **Paycode names only** | Hours per paycode type; no detailed leave reason or medical information |
| **Filtered output** | Only rows with `over_applied_hours > 0` are returned; clean timecards are excluded |

---

## 6. Data Flow Diagram

```text
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA FLOW                                    │
│                                                                     │
│  UKG Pro / T&A                                                      │
│       │                                                             │
│       ▼  (Daily ETL, encrypted)                                     │
│                                                                     │
│  Snowflake EDLDB.UKG                                                │
│  ┌──────────────────────┐                                           │
│  │ GOLD_V_PEOPLE         │──── PII: name, ID, supervisor            │
│  │ GOLD_V_SCHEDULE_TOTAL │──── Business: schedule hours, dates      │
│  │ GOLD_V_TIMECARD_TOTAL │──── Business: worked hours, paycodes     │
│  └──────────┬───────────┘                                           │
│             │  (On-demand query, TLS encrypted)                     │
│             ▼                                                       │
 │  Phoenix Agent                                                      │
 │  ┌──────────────────────┐                                           │
 │  │ Reconciliation Query  │──── Computes over-applied hours          │
 │  │ 10 CTEs → 14 columns │──── Applies risk classification          │
 │  │ Session-scoped only   │──── No persistent PII storage            │
 │  └──────────┬───────────┘                                           │
 │             │  (HTTPS, TLS 1.2+)                                    │
 │             ▼                                                       │
│  End User (TMDM Rep)                                                │
│  ┌──────────────────────┐                                           │
│  │ Browser / Phoenix UI  │──── Views tables, KPIs, narratives       │
│  │ Optional Excel export │──── Local file, endpoint security        │
│  └──────────────────────┘                                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 7. Compliance Considerations

| Area | Status | Notes |
| --- | --- | --- |
| **PII handling** | Compliant | Minimum viable PII; no SSN, DOB, medical, or compensation data |
| **FMLA/Leave privacy** | Review recommended | Paycode names (e.g., "Intermittent Leave") are visible; does not include leave reason or medical details. Confirm with Legal/Compliance that paycode name visibility is acceptable. |
| **Data access audit** | Supported | Snowflake and Phoenix both support query audit logging |
| **Right to access/delete** | Governed by enterprise HR data policies | Agent does not store persistent data; Snowflake retention per enterprise policy |
| **Cross-border data transfer** | N/A for current scope | All data resides in US-based Snowflake instance; users are US-based |

---

## 8. Data Quality Controls

| Control | Implementation |
| --- | --- |
| **Deduplication** | `ROW_NUMBER()` on `(person_id, partition_date, pay_code_id)` ordered by `load_date_time DESC` ensures only the latest record per person/date/paycode is used |
| **Null handling** | `COALESCE` in reconciliation CTE ensures no rows are lost from FULL OUTER JOIN; nulls default to 0 |
| **Combined paycode exclusion** | `combined_pay_code_swt = FALSE` filters out UKG-generated summary/combined paycode rows that would cause double-counting |
| **Terminated/deleted exclusion** | `account_status <> 'Terminated' AND NOT deleted` ensures only active employees are included |
| **Exempt exclusion** | `schedule_group <> 'Exempt' OR schedule_group IS NULL` scopes to non-exempt population |
| **Date range bounds** | `date_range` CTE enforces pay period boundaries; prevents out-of-period data leakage |

---

## 9. Change Control

| Change Type | Process | Owner |
| --- | --- | --- |
| **Add/remove paycode** | Update `paycode_types` VALUES list in SQL; update this Data Map | Product Owner + TMDM |
| **Change cohort classification** | Update CASE expression in `employees` CTE; update this Data Map | Product Owner |
| **Add new PII field** | Requires review against data classification policy; update PII Inventory (Section 4.2) | Product Owner + Data Governance |
| **Change source views** | Update source system references; regression test reconciliation output | Product Owner + Analytics Engineering |
| **Modify risk threshold** | Update CASE expression in final SELECT (currently >= 4 for HIGH PRIORITY) | Product Owner + TMDM |
