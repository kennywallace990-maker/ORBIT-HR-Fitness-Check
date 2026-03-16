# ORBIT HR Workload Lens — Data Map & Classification Declaration

**Product:** Workload Lens (Phase I — Time & Attendance / UKG)
**Program:** ORBIT · Pillar 2 (Design & POC)
**Status:** Draft
**Version:** 2.0
**Last Updated:** 2026-03-03
**Owner:** Kenny Wallace, ORBIT Program Lead
**Delivery Platform:** Phoenix / ORBIT → Snowflake

---

## Purpose

This document serves two functions for the Workload Lens product:

**Part 1 — Data Map** traces every data source, table, column, join, and derived field from Snowflake through the agent's SQL to the final OBR report output. It answers: where does the data come from, how does it flow, and what does each field mean?

**Part 2 — Classification Declaration** codifies how each UKG audit row is classified into Buckets, Work Types, Actor Groups, Paycode Categories, and flags. It answers: what are the rules, and how is every row scored?

Both parts are documented at two layers:

- **Current State** — what the Phoenix agent actually queries and computes today (inline CTEs against raw Snowflake tables plus one pre-materialized view).
- **Target State** — the full `V_HWL_*` Snowflake view architecture that will serve as the durable data layer once production-hardened.

This document gates the Technical Design Doc, the Value Scorecard, and production handoff. If a rule is not declared here, it does not exist in the product.

---

## Document Conventions

- "OBR" refers to the Operational Business Review (the weekly report). All legacy references to "WBR" should be read as OBR.
- Column names use the exact Snowflake aliases returned by the agent's SQL (e.g., `ENTITY_TYPE`, `BUCKET_B`, `OBR_ACTOR_GROUP`).
- "Agent SQL" refers to the 8 immutable queries defined in the Phoenix Agent Instructions v2.
- "PRD" refers to the ORBIT HR Workload Lens Product Requirements Document v2.0.

---

# PART 1: DATA MAP

---

## 1.1 Source Systems

| Source System | System of Record For | Snowflake Landing | Phase |
|:---|:---|:---|:---|
| UKG Kronos (Time & Attendance) | Timecard audit trail | `EDLDB.PEOPLE_ANALYTICS_SANDBOX.UKG_V_TIMECARD_AUDIT` | I |
| UKG Kronos (People) | Employee profile | `EDLDB.UKG.V_PEOPLE` | I |
| UKG Kronos (Exceptions) | Missed punch exceptions | `EDLDB.UKG.V_TIMECARD_EXCEPTION` | I |
| ServiceNow (HR Tickets) | HR case/ticket data | Snowflake TBD | II |

---

## 1.2 Primary Source Tables (Phase I)

### 1.2.1 `EDLDB.PEOPLE_ANALYTICS_SANDBOX.UKG_V_TIMECARD_AUDIT`

Core audit table receiving daily incremental loads. Each daily load appends new records without deduplicating against existing data, meaning the same audit event can appear multiple times.

**Alias in agent SQL:** `a`

| Column | Type | Description | Used In |
|:---|:---|:---|:---|
| `AUDIT_ID` | VARCHAR | Unique identifier for the audit event | Deduplication key (with `AUDIT_REVISION_ID`) |
| `AUDIT_REVISION_ID` | VARCHAR | Revision identifier within the audit event | Deduplication key (with `AUDIT_ID`) |
| `PERSON_NUMBER` | VARCHAR | Employee ID (whose timecard was edited) | Join to `V_PEOPLE`; mapped to `EMPLOYEE_ID` |
| `AUDIT_REVISION_USER_PERSON_NUMBER` | VARCHAR | Person number of the user who made the change | Join to `V_PEOPLE` for revision user profile; mapped to `REVISION_USER_ID` |
| `PARTITION_DATE` | DATE | Business date of the time event | Mapped to `ENTITY_EVENT_DATE`; reporting week assignment |
| `AUDIT_TIME_STAMP` | TIMESTAMP | When the audit action was recorded | Mapped to `REVISION_DATE` |
| `AUDIT_TYPE` | VARCHAR | Entity type of the action | Mapped to `ENTITY_TYPE`; drives Work Type and Bucket classification |
| `AUDIT_REVISION_TYPE` | VARCHAR | Operation performed (Add, Edit, Delete, Transfer) | Mapped to `REVISION_TYPE`; drives Bucket B classification |
| `AUDIT_PAYCODE_NAME` | VARCHAR | Which paycode was touched | Mapped to `PAYCODE_NAME`; drives Paycode Category and HC Category |
| `AUDIT_COMMENT_TEXT` | VARCHAR | Comment attached to the action | Mapped to `COMMENT`; used for comment compliance |
| `AUDIT_NOTE_TEXT` | VARCHAR | Note text attached to the action | Mapped to `NOTE_TEXT`; used for comment compliance |
| `AUDIT_DATASOURCE` | VARCHAR | Source system or interface | Mapped to `DATASOURCE` |
| `AUDIT_AMOUNT_HOURS` | DECIMAL | Hours affected by the action | Mapped to `AMOUNT_HOURS` |
| `TKAUDIT_PUNCH_TIME` | TIMESTAMP | Actual punch time (punch events only) | Mapped to `PUNCH_TIME` |
| `TKAUDIT_PUNCH_OVERRIDE` | VARCHAR | Punch override type | Mapped to `PUNCH_OVERRIDE_TYPE` |
| `TKAUDIT_PUNCH_DELETED` | VARCHAR | Whether the punch was deleted | Mapped to `PUNCH_DELETED` |
| `LOAD_DTTM` | TIMESTAMP | When the row was loaded into Snowflake | Deduplication (earliest load wins) |

### 1.2.2 `EDLDB.UKG.V_PEOPLE`

Employee and revision user profile data. Contains duplicate person records with changing data, so deduplication is required.

**Alias in agent SQL:** `p` (employee), `rev` (revision user)

| Column | Type | Description | Used In |
|:---|:---|:---|:---|
| `PERSON_NUMBER` | VARCHAR | Employee identifier | Join key to audit table |
| `PERSON_ID` | INT | Internal ID; higher = more recent record | Deduplication |
| `FIRST_NAME` | VARCHAR | Employee first name | Self-edit detection; name display |
| `LAST_NAME` | VARCHAR | Employee last name | Self-edit detection; name display |
| `EMPLOYMENT_STATUS` | VARCHAR | Active, Terminated, etc. | Missed punch flags require Active status |
| `SUPERVISOR_FULL_NAME` | VARCHAR | Direct supervisor name | Mapped to `REPORTS_TO` |
| `PRIMARY_ORG_PATH_TXT` | VARCHAR | Full organizational path | `BUILDING_LOCATION` extracted via regex |
| `ACCESS_PROFILE` | VARCHAR | UKG access profile (on revision user record) | Drives `OBR_ACTOR_GROUP` classification |
| `HIRE_DATE` | DATE | Employee hire date | **Needed for first-week TM exemption (unresolved — field availability TBD)** |

### 1.2.3 `EDLDB.UKG.V_TIMECARD_EXCEPTION`

Missed punch exception events fired by UKG. Used for engagement flag computation.

| Column | Type | Description | Used In |
|:---|:---|:---|:---|
| `PERSON_ID` | INT | Employee internal ID | Join to `V_PEOPLE` |
| `EVENT_DATE` | TIMESTAMP | Date the exception was fired | Grouped by `DATE(EVENT_DATE)` for daily counts |
| `SHIFT_ID` | VARCHAR | Shift identifier | `COUNT(DISTINCT SHIFT_ID)` for daily count |
| `EXCEPTION_TYPE_NAME` | VARCHAR | Exception type | Filter: `IN ('Missed In Punch', 'Missed Out Punch')` |

### 1.2.4 `EDLDB.PEOPLE_ANALYTICS_SANDBOX.V_HWL_WEEKLY_SITE_METRICS`

Pre-materialized view containing 13-week rolling baseline statistics at the site-week grain. This is the only `V_HWL_*` view that currently exists in production.

| Column | Type | Description | Used In |
|:---|:---|:---|:---|
| `BUILDING_LOCATION` | VARCHAR | Site code | Join key to current-week site stats |
| `OBR_SITE_GROUP` | VARCHAR | Business unit (FC, Rx, CVC, CC) | BU-level rollup |
| `REPORT_WEEK` | DATE | Week start date (Sunday) | Filter for current reporting week |
| `TOTAL_ACTIONS` | INT | Total HR audit actions for that site-week | Baseline numerator |
| `BUCKET_B_ACTIONS` | INT | Bucket B (defect) actions for that site-week | Baseline numerator |
| `MEAN_13WK_DEFECT_RATE` | DECIMAL | 13-week rolling mean defect rate | UCL computation |
| `SD_13WK_DEFECT_RATE` | DECIMAL | 13-week rolling standard deviation | UCL computation |

---

## 1.3 Deduplication Rules (Current State)

### 1.3.1 Audit Row Deduplication

**Problem:** Daily incremental loads create duplicate audit events.
**Key:** `(AUDIT_ID, AUDIT_REVISION_ID)`
**Rule:** Keep earliest load (`ORDER BY LOAD_DTTM ASC`, keep `rn = 1`).

```sql
audit_deduped AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY AUDIT_ID, AUDIT_REVISION_ID
            ORDER BY LOAD_DTTM ASC
        ) AS rn
    FROM EDLDB.PEOPLE_ANALYTICS_SANDBOX.UKG_V_TIMECARD_AUDIT
    WHERE PARTITION_DATE BETWEEN <WEEK_START> AND <WEEK_END>
)
```

### 1.3.2 People Record Deduplication

**Problem:** `V_PEOPLE` contains multiple records per person.
**Key:** `PERSON_NUMBER`
**Rule:** Keep highest `PERSON_ID` (most recent record).

```sql
people_deduped AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY PERSON_NUMBER
            ORDER BY PERSON_ID DESC
        ) AS prn
    FROM EDLDB.UKG.V_PEOPLE
)
```

### 1.3.3 Missed Punch Deduplication

Within the audit pipeline (Q1 through Q7), daily counts use `COUNT(DISTINCT SHIFT_ID)` per `(PERSON_ID, DATE(EVENT_DATE))`. Q8 runs standalone against `V_TIMECARD_EXCEPTION` with the same grain.

---

## 1.4 Join Relationships (Current State)

| Join | Left (Alias) | Right (Alias) | Join Key | Type | Notes |
|:---|:---|:---|:---|:---|:---|
| Employee Profile | `audit_deduped (a)` | `people_deduped (p)` | `a.PERSON_NUMBER = p.PERSON_NUMBER AND p.prn = 1` | INNER | Every audit row must have an employee record |
| Revision User Profile | `audit_deduped (a)` | `people_deduped (rev)` | `a.AUDIT_REVISION_USER_PERSON_NUMBER = rev.PERSON_NUMBER AND rev.prn = 1` | LEFT | Some system-generated rows lack a mapped revision user |
| Linked Comments | `audit_deduped (a)` | `comments_by_revision (cmt)` | `a.AUDIT_REVISION_ID = cmt.AUDIT_REVISION_ID AND a.PERSON_NUMBER = cmt.PERSON_NUMBER` | LEFT | Pulls comment text from related comment-type rows |
| Daily Missed Punches | `people_deduped (p)` | `missed_punch_counts (mpc)` | `mpc.PERSON_ID = p.PERSON_ID AND mpc.EVENT_DATE = a.PARTITION_DATE` | LEFT | Day-grain missed punch count |
| Weekly Missed Totals | `people_deduped (p)` | `weekly_missed_totals (wmt)` | `wmt.PERSON_ID = p.PERSON_ID` | LEFT | Week-grain missed punch aggregate |
| Exception Types | `people_deduped (p)` | `exc` subquery | `exc.PERSON_ID = p.PERSON_ID AND exc.EVENT_DATE = a.PARTITION_DATE` | LEFT | Concatenated exception type names |
| 13-Week Baseline (site) | `current_week_metrics` | `V_HWL_WEEKLY_SITE_METRICS (v)` | `c.BUILDING_LOCATION = v.BUILDING_LOCATION` | LEFT | Q6: site-level spike flags |
| 13-Week Baseline (network/BU) | `current_week_bu` | `weekly_baseline_agg` | `GROUP_NAME` match | LEFT | Q1, Q3: network and BU spike flags |

---

## 1.5 Derived Fields

These fields are computed inline in the agent's `base` CTE and used downstream in all KPI aggregations.

### 1.5.1 `BUILDING_LOCATION`
```sql
REGEXP_SUBSTR(p.PRIMARY_ORG_PATH_TXT, '- ([A-Z0-9]{3,5})/', 1, 1, 'e')
```

### 1.5.2 `EDIT_TARGET`
```sql
CASE WHEN a.PERSON_NUMBER = a.AUDIT_REVISION_USER_PERSON_NUMBER THEN 'Self' ELSE 'Other' END
```

### 1.5.3 `OBR_ACTOR_GROUP`
The primary actor classification used in all KPI tables. See Part 2, Section 2.2 for the full mapping including the v2.0 changes (Workers Comp → Local HR, Super Access No Wages → excluded, Other → excluded from customer output).

### 1.5.4 `OBR_SITE_GROUP`
Maps `BUILDING_LOCATION` to FC, Rx, CVC, or CC. NULL for corporate/excluded sites. See Part 2, Section 2.6.

### 1.5.5 `BUCKET_B`
Core defect flag. See Part 2, Section 2.1.

### 1.5.6 `BUCKET_A`
Governance population flag. See Part 2, Section 2.1.

### 1.5.7 `BUCKET_G`
Governance/documentation flag. See Part 2, Section 2.1.

### 1.5.8 `FRICTION_SCORE`
```sql
CASE
    WHEN a.AUDIT_TYPE = 'Historical Correction' THEN 5.0
    WHEN a.AUDIT_REVISION_TYPE IN ('Edit','Delete')
         AND a.AUDIT_TYPE IN ('Punch','Pay Code Edit','Manager Justified Time') THEN 1.0
    ELSE 0.5
END
```

### 1.5.9 `HIGH_RISK_REWORK`
TRUE for Historical Corrections, Punch Add/Edit/Delete, and Pay Code Edits for PTO/Sick/Regular/Overtime.

### 1.5.10 `HAS_COMMENT`
Binary 1/0 flag for non-null, non-empty comment or note text.

### 1.5.11 `PAYCODE_CATEGORY`
Human-readable label from `PAYCODE_NAME` pattern matching. See Part 2, Section 2.4.

### 1.5.12 `HC_CATEGORY`
Historical Correction root cause category. See Part 2, Section 2.5.

### 1.5.13 `MISSING_PUNCH_FLAG`
'Yes' when employee is Active AND has 2+ daily missed punches OR 3+ weekly missed punches.

### 1.5.14 `DPMO`
```sql
ROUND(s.BUCKET_B_COUNT / NULLIF(s.UNIQUE_TMS * 20, 0) * 1000000, 2)
```
Note: The current agent SQL uses `× 1000`. This must be updated to `× 1000000` per the PRD v2.0 standardization to Six Sigma DPMO (per million).

---

## 1.6 Exclusion Filters

Applied in the `hr` CTE to produce the HR-only working dataset.

| Filter | SQL | Rationale |
|:---|:---|:---|
| Self-service exclusion | `WHERE EDIT_TARGET != 'Self'` | TM self-service is not HR workload |
| Corporate site exclusion | `AND OBR_SITE_GROUP IS NOT NULL` | Corp sites not in scope |
| Non-HR actor exclusion | `AND OBR_ACTOR_GROUP NOT IN ('Team Member', 'Other', 'Automation', 'WFM')` | Team Member self-service, unmapped profiles, automation traffic, and Workforce Management work are excluded from HR KPIs. |
| Comment-type entity exclusion | Applied in `base` CTE: `AND a.AUDIT_TYPE NOT IN ('Exception Comment', 'Punch Comment', 'Pay Code Edit Comment')` | Documentation rows excluded from counts; text linked back via CTE |

**Self-edit detection note:** The agent uses two complementary checks. `EDIT_TARGET` compares `PERSON_NUMBER` values. `OBR_ACTOR_GROUP` uses a name-match override (`p.FIRST_NAME||' '||p.LAST_NAME = rev.FIRST_NAME||' '||rev.LAST_NAME`). The name match takes precedence in the CASE statement, so a Manager editing their own timecard is classified as Team Member and subsequently filtered.

---

## 1.7 Query to Report Section Mapping (Current State)

| Query | Returns | Feeds Report Section | Key Output Columns |
|:---|:---|:---|:---|
| Q1 | 1 row: network KPI summary | Section 1 (Executive Summary) | `TOTAL_ACTIONS`, `DEFECT_RATE_PCT`, `TOTAL_FRICTION_HRS`, `MISSING_PUNCH_RATE_PCT`, `HIST_CORR_RATE_PCT`, `IS_RED_SPIKE` |
| Q2 | ~20 rows: BU × Actor Group | Section 2.1 (Enterprise View) | `OBR_SITE_GROUP`, `OBR_ACTOR_GROUP`, `TOUCHES` |
| Q3 | ~6 rows: BU split with spike flags | Section 2.2 (BU Split) | `GROUP_NAME`, `ACTION_VOLUME`, `DEFECT_PCT`, `UCL_13WK_DEFECT_RATE`, `IS_RED_SPIKE` |
| Q4 | ~80 rows: paycode categories by BU | Sections 2.3 through 2.7 (Top Drivers) | `BU_OR_GROUP`, `PAYCODE_CATEGORY`, `ACTION_COUNT`, `ESTIMATED_HRS` |
| Q5 | ~5 rows: HC root cause breakdown | Section 4 (Historical Corrections) | `HC_CATEGORY`, `HC_COUNT` |
| Q6 | ~50 rows: site-level stats with spike flags | Section 5 (Hotspots) | `BUILDING_LOCATION`, `DPMO`, `DEFECT_RATE_PCT`, `IS_RED_SPIKE` |
| Q7 | ~5 rows: comment compliance by BU | Section 6 (Event Documentation) | `OBR_SITE_GROUP`, `HIGH_RISK_ACTIONS`, `DOCUMENTATION_RATE_PCT` |
| Q8 | 0 to 500+ rows: missed punch engagement | Separate PII-restricted deliverable | `SITE`, `TM_NAME`, `TM_ID`, `MANAGER`, `MISSED_COUNT`, `LOGS` |

---

## 1.8 Data Flow Diagram (Current State)

```
UKG Kronos
  ├── Timecard Audit Feed ──→ UKG_V_TIMECARD_AUDIT
  ├── People Feed ──────────→ V_PEOPLE
  └── Exception Feed ───────→ V_TIMECARD_EXCEPTION

                                         ↓
                              ┌──────────────────────┐
                              │  Agent SQL (Q1 - Q8)  │
                              │  Inline CTEs:          │
                              │  ├ audit_deduped       │
                              │  ├ people_deduped      │
                              │  ├ comments_by_revision│
                              │  ├ missed_punch_counts │
                              │  ├ weekly_missed_totals│
                              │  ├ base (all fields)   │
                              │  └ hr (filtered)       │
                              └──────────┬─────────────┘
                                         │
                    ┌────────────────────┤
                    │                    │
    ┌───────────────▼──────┐  ┌─────────▼──────────────────────┐
    │ V_HWL_WEEKLY_SITE_   │  │  Phoenix / ORBIT Agent          │
    │ METRICS              │  │  ├ Reads Q1-Q8 results          │
    │ (13-week baseline)   │  │  ├ Applies traffic light rules  │
    │                      │  │  ├ Applies Top 5 filter         │
    │  Joined in Q1,Q3,Q6  │  │  ├ Writes narrative (LLM)       │
    └──────────────────────┘  │  └ Assembles report document   │
                              └─────────────┬──────────────────┘
                                            │
                                            ▼
                               Published OBR Report
```

---

## 1.9 Target State: V_HWL_* View Architecture

| View | Grain | Purpose | Current Equivalent |
|:---|:---|:---|:---|
| `V_HWL_ACTOR_GROUP_WEEK` | Actor Group × Site × Week | Ownership split with WoW deltas | Q2 inline aggregation |
| `V_HWL_WORK_TYPE_MIX_WEEK` | Work Type × Actor Group × Site × Week | Work type distribution by actor | Q4 inline aggregation |
| `V_HWL_DEFECT_REWORK_WEEK` | Site × Week | Bucket B / rework KPIs with WoW | Q1/Q3/Q6 inline aggregation |
| `V_HWL_SCHEDULE_TOUCH_WEEK` | Site × Week | Schedule-specific KPIs (Bucket D) | Not yet implemented |
| `V_HWL_USER_BASELINE_WEEK` | User × Site × Week | Per-user actions, hours, top work types | Not yet implemented |
| `V_HWL_TM_MISSED_PUNCH_WEEK` | Employee × Site × Week | Engagement flag inputs | Q8 inline aggregation |
| `V_HWL_SITE_SUMMARY_WEEK` | Site × Week | All KPIs at site grain with WoW | Q6 inline aggregation |
| `V_HWL_NETWORK_SUMMARY_WEEK` | Network × Week | Network-level rollup | Q1 inline aggregation |

**Design principle:** Push as much computation as possible into production views so the agent reads pre-calculated values (including WoW deltas, 4-week rolling averages, and baseline comparisons) and focuses on reasoning and narrative rather than arithmetic.

**Currently materialized:** Only `V_HWL_WEEKLY_SITE_METRICS`.

---

# PART 2: CLASSIFICATION DECLARATION

---

## 2.1 Bucket Classification

### Bucket B — Correction / Rework (Defect = Yes, always)

```sql
CASE
    WHEN a.AUDIT_TYPE = 'Punch' THEN TRUE
    WHEN a.AUDIT_TYPE = 'Historical Correction' THEN TRUE
    WHEN a.AUDIT_REVISION_TYPE IN ('Edit','Delete')
         AND a.AUDIT_TYPE IN ('Pay Code Edit','Manager Justified Time') THEN TRUE
    WHEN a.AUDIT_TYPE = 'Manager Justified Time'
         AND a.AUDIT_REVISION_TYPE = 'Add'
         AND (LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%late%'
              OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%early%'
              OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%ncns%'
              OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%call off%'
              OR LOWER(a.AUDIT_PAYCODE_NAME) LIKE '%unpd%') THEN TRUE
    ELSE FALSE
END AS BUCKET_B
```

### Bucket A — Governance Population (Defect = No)

```sql
CASE
    WHEN a.AUDIT_TYPE = 'Pay Code Edit'
         AND a.AUDIT_REVISION_TYPE = 'Add' THEN TRUE
    WHEN a.AUDIT_TYPE = 'Manager Justified Time'
         AND a.AUDIT_REVISION_TYPE = 'Add'
         AND NOT (...attendance patterns...) THEN TRUE
    ELSE FALSE
END AS BUCKET_A
```

### Bucket G — Governance / Documentation (Defect = No)

Comment-type entities and approval/review actions.

### Bucket D — Schedule Touch (Not Yet Implemented)

Deferred to production. See PRD Section 4.1.

---

## 2.2 OBR Actor Group Classification

### Self-Edit Override (Highest Priority)
```sql
WHEN p.FIRST_NAME||' '||p.LAST_NAME = rev.FIRST_NAME||' '||rev.LAST_NAME THEN 'Team Member'
```

### OBR Actor Group Mapping (v2.0)

| OBR Actor Group | ACCESS_PROFILE Values | Description |
|:---|:---|:---|
| **Local HR** | `Company Admin Site Specific`, `Workers Compensation` | Site-level field HR including workers comp case management |
| **HRSS** | `Leave Support`, `Company Admin TMDM`, `Team Member Services`, `Super Access` | Centralized HR shared services |
| **Team Member** | `Employee Basic`, `Employee Basic- Pharmacy`, `Training Basic`, `IT Admin`, `Training + Safety`, `Advanced Scheduler Lead`, `Advanced Scheduler Workforce Analyst`, `Facilities` | Employee self-service and self-edit overrides |
| **Local Ops** | `Manager Basic`, `Manager Basic With Punch&Schedule Edits`, `Practice Manager`, `Facilities Manager` | Field operations managers |
| **WFM** | `Workforce Reporting` | Workforce Management. Classified in base data for dependency analysis but excluded from the HR KPI layer. |
| **Other** | Any unmapped or NULL access profile | Retained in Snowflake for research. **Excluded from customer-facing OBR output.** |

**HR reporting boundary:** customer-facing HR KPI tables use the filtered `hr` dataset, which retains only `Local HR`, `HRSS`, and `Local Ops`.

### TM Self-Service Capability Catalog

The following UKG and timeclock actions are treated as Team Member self-service when initiated by the TM and are outside HR workload:

- Clock in / clock out at a timeclock or via the app
- View current timecard for the pay period
- Edit or submit a missed punch or forgot-to-punch request
- Submit timecard corrections or edits for manager approval
- View punch history and punch detail, including location, device, and timestamps
- Confirm or acknowledge punches when the device or app prompts
- View published schedule and future shifts
- View time off balances and accruals
- View status of submitted requests, including timecard edits and PTO
- Get notifications of approvals, denials, or required actions
- Complete simple approval tasks in-app when approver rights are enabled

### Automation Exclusion
```sql
-- Super Access No Wages = automated system processes
-- Excluded at the hr CTE level: OBR_ACTOR_GROUP NOT IN ('Team Member', 'Other', 'Automation', 'WFM')
-- OR explicitly filtered: rev.ACCESS_PROFILE != 'Super Access No Wages'
```

`Super Access No Wages` was previously grouped under HRSS. As of v2.0, these rows are excluded from all reporting pipelines because they represent automated processes that skew volume and defect metrics. The recommended implementation either maps them to a dedicated 'Automation' label and filters, or adds an explicit ACCESS_PROFILE exclusion in the base CTE before OBR_ACTOR_GROUP assignment.

### v2.0 Changes from v1

| Change | What Moved | Rationale |
|:---|:---|:---|
| Workers Compensation → Local HR | New ACCESS_PROFILE added to Local HR mapping | Workers comp case work is site-level HR activity |
| Super Access No Wages → Excluded | Removed from HRSS, filtered as automation | Not human-initiated; inflates HRSS volume |
| WFM → Excluded from HR KPI layer | Retained in base only | Workforce Management touches are not HR workload |
| Other → Snowflake only | Not shown in customer OBR | Supports research without polluting metrics |
| COE subgroup → Eliminated | No longer used in any document | HRSS is the single reporting label for all centralized HR |

---

## 2.3 Work Type Taxonomy

| Work Type | ENTITY_TYPE | Bucket | Notes |
|:---|:---|:---|:---|
| Punch | `Punch` | B (always, in HR context) | Core attendance signal |
| Pay Code Edit | `Pay Code Edit` | A (if Add) or B (if Edit/Delete) | Sub-classified by PAYCODE_NAME |
| Pay Code Edit Comment | `Pay Code Edit Comment` | G | Excluded from counts; text linked via CTE |
| Punch Comment | `Punch Comment` | G | Excluded from counts; text linked via CTE |
| Exception Comment | `Exception Comment` | G | Excluded from counts; text linked via CTE |
| Manager Justified Time | `Manager Justified Time` | A or B | Attendance-related paycodes = B |
| Historical Correction | `Historical Correction` | B (always) | Highest friction score (5.0) |
| Mark as Reviewed | `Mark as reviewed` | G | Timecard signoff |
| Manager Approval | `Manager Approval` | G | Timecard finalization |

---

## 2.4 Paycode Category Mapping

Pattern matching uses `LOWER()` and `LIKE`. First match wins.

| Paycode Category | Pattern on PAYCODE_NAME |
|:---|:---|
| Manual Punch Correction | NULL or empty |
| Time spent manually coding VTO | `%vto%` or `%voluntary%` |
| Time spent manually coding weather-related event | `%weather%` |
| Manual coding missed late arrival | `%late%` |
| Manual coding missed early departure | `%early%` |
| Manual coding No Call No Show | `%ncns%` |
| Manual coding Call Off | `%call off%` |
| Manual coding Sick Time | `%sick%` |
| Manual coding Leave of Absence | `%leave%` |
| Manual coding for early departure/long lunch to deduct UTO | `%pto paid dur%` or `%personal unpd dur%` |
| Manual coding of Paid Time Off | `%pto%` |
| Manual coding to prevent UTO (Meal Break) | `%meal break%` |
| Manual coding of Personal Time | `%personal%` |
| Time spent manually coding [PAYCODE_NAME] | All other non-NULL paycodes |

---

## 2.5 Historical Correction Root Cause Categories

| HC Category | Pattern on PAYCODE_NAME | Interpretation |
|:---|:---|:---|
| Attendance Enforcement | `%ncns%`, `%late%`, `%early%`, `%call off%` | Attendance infractions not coded before payroll window closed |
| Core Pay & Missing Time | `%regular%`, `%overtime%`, `%meal%`, `%pto paid%` | Retroactive payroll deposits for missed pay |
| Schedule & Unpaid True-Ups | `%personal%`, `%vto%`, `%weather%`, `%unpaid%` | Operational changes not processed before transmission |
| Leave & Compliance Lag | `%leave%`, `%fmla%`, `%loa%`, `%bereavement%` | Expected lag pending documentation |
| Other | Everything else | Various other discrepancies |

---

## 2.6 Site and Network Groupings

| OBR Site Group | Sites | Count |
|:---|:---|:---|
| FC | AVP1, AVP2, BNA1 (2G), CFC1, CLT1, DAY1, DFW1, HOU1, MCI1, MCO1, MDT1, PHX1, RNO1 | 13 |
| Rx | AVP4, AVP5, AVP6, DFW5, DFW8, MCO4, MCO5, PHX2, PHX5, SDF2, SDF4, SDF5, SDF6 | 13 |
| CVC | ATLA, ATLB, ATLC, ATLD, AUSA, DENA, DENB, DEND, DFWA, DFWB, FLLA, FLLB, FLLC, FLLD, FLLF, IAHA, IAHD, PHXB | 18 |
| CC | AV4V, DF4V, DFW4, FL3V, PH0V, PW0V, SD2V | 7 |
| **Total** | | **51** |

**Excluded:** BOS1, FLL7, SEA1, MSP2 (corporate offices).

**Rx Presentation Groupings:** PHX2/5, MCO4/5, SDF4/5/6, AVP4/5/6, DFW5/8, SDF2 standalone. These are presentation-layer labels only. All KPIs computed at individual site grain.

---

## 2.7 Spike Detection and Traffic Light Rules

### 13-Week UCL
```
UCL = MEAN_13WK_DEFECT_RATE + SD_13WK_DEFECT_RATE
IS_RED_SPIKE = TRUE when current week defect rate > UCL
```

### Traffic Light Thresholds

| Metric | Green | Yellow | Red |
|:---|:---|:---|:---|
| Defect Rate % | <= 25% | 26 to 40% | > 40% |
| Missing Punch Rate % | <= 5% | 6 to 10% | > 10% |
| Hist. Correction Rate % | <= 5% | 6 to 10% | > 10% |
| Comment Compliance Rate % | >= 85% | 70 to 84% | < 70% |
| Site DPMO | TBD (pending baseline calibration at ×1M scale) | TBD | TBD |

---

## 2.8 Missed Punch Engagement Thresholds

| Flag | Rule | Severity |
|:---|:---|:---|
| Single-Shift Spike | 2+ distinct missed punch events in a single day | Medium |
| Weekly Pattern | 3+ distinct missed punch events in the reporting week | High |

Filters: Employee must be Active. Q8 runs directly against `V_TIMECARD_EXCEPTION`.

**First-Week TM Exemption (Unresolved):** TMs in their first week of employment should be exempt from the engagement list. New hires frequently do not receive their badge until the middle of Day 1. Implementation requires a hire date field from `V_PEOPLE` with a filter: `WHERE ENTITY_EVENT_DATE - HIRE_DATE >= 7`. Field availability needs confirmation from data engineering.

---

## 2.9 DPMO Computation

**Formula (v2.0 — standardized to per million):**
```sql
ROUND(s.BUCKET_B_COUNT / NULLIF(s.UNIQUE_TMS * 20, 0) * 1000000, 2) AS DPMO
```

The denominator assumes approximately 20 punch opportunities per employee per week (10 shifts × 2 punches). This is a proxy, not an exact count.

**Note:** The current agent SQL uses `× 1000` (per thousand). The POC agent instructions must be updated to `× 1000000` and DPMO traffic light thresholds recalibrated after 4 weeks of baseline data at the new scale.

---

## 2.10 Comment Compliance Scope

Measured strictly against High-Risk Rework actions:
- All Historical Corrections
- All Punch Add/Edit/Delete
- Pay Code Edits for PTO, Sick, Regular, or Overtime

Compliance Rate = `SUM(HAS_COMMENT WHERE HIGH_RISK_REWORK) / COUNT(HIGH_RISK_REWORK) × 100`

---

## Appendix A: Open Items

| # | Item | Status | Resolution |
|:---|:---|:---|:---|
| 1 | DPMO scale change (×1K → ×1M) | Decided | Update agent SQL multiplier. Recalibrate DPMO thresholds after 4 weeks baseline. |
| 2 | Workers Compensation → Local HR | Decided | Add to OBR_ACTOR_GROUP CASE statement. |
| 3 | Super Access No Wages exclusion | Decided | Filter as automation. Remove from HRSS. |
| 4 | Other excluded from customer OBR | Decided | Keep in Snowflake, exclude from report output. |
| 5 | COE subgroup | Eliminated | HRSS only, everywhere. |
| 6 | First-week TM exemption for missed punches | Unresolved | Need HIRE_DATE from V_PEOPLE. |
| 7 | WoW deltas | Target: production views | Agent reads pre-computed deltas, does not calculate. |
| 8 | WBR → OBR terminology | Complete | All documents updated. |
| 9 | Rx group rollups | Presentation only | No distinct aggregation needed. |
| 10 | BNA1 classification | Confirmed | 2G FC. |

---

## Appendix B: Version History

| Version | Date | Author | Changes |
|:---|:---|:---|:---|
| 1.0 | 2026-03-03 | Kenny Wallace / ORBIT | Initial draft |
| 2.0 | 2026-03-03 | Kenny Wallace / ORBIT | Full rework incorporating 10 correction items: DPMO per-million, actor group restructure, automation exclusion, COE elimination, WoW to production views, OBR terminology pass, Rx presentation-only, BNA1 2G confirmed, first-week TM exemption documented |
