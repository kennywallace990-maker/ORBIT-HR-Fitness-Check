# Snowflake Discovery Playbook

Status: Draft technical discovery guide
Last updated: 2026-06-19

## Current Access Status

An existing Snowflake Python + browser SSO setup was located on 2026-06-19 in the Workload Lens project on this machine. The default Python in the Fitness Check workspace does not have the connector installed, but the Workload Lens virtual environment does.

Known working context from the existing setup for `EDLDB` / `UKG`:

- Role: `PEOPLE_ANALYTICS_DEVELOPER`
- Warehouse: `PEOPLE_ANALYTICS_WH`
- Database: `EDLDB`
- Schema: `PEOPLE_ANALYTICS_SANDBOX`
- Authenticator: `externalbrowser`

Successful discovery runs:

- `snowflake_access_smoke_test.sql` wrote `knowledge-base/discovery-output/snowflake_access_smoke_test.csv`.
- `snowflake_role_context.sql` wrote `knowledge-base/discovery-output/snowflake_role_context.csv`.
- `edldb_candidate_tables.sql` wrote `knowledge-base/discovery-output/edldb_candidate_tables.csv`.
- `ukg_candidate_columns.sql` wrote `knowledge-base/discovery-output/ukg_candidate_columns.csv`.
- `hrdm_access_smoke_test.sql` wrote `knowledge-base/discovery-output/hrdm_access_smoke_test.csv`.
- `hrdm_schemas.sql` wrote `knowledge-base/discovery-output/hrdm_schemas.csv`.
- `hrdm_candidate_tables.sql` wrote `knowledge-base/discovery-output/hrdm_candidate_tables.csv`.
- `hrdm_candidate_columns.sql` wrote `knowledge-base/discovery-output/hrdm_candidate_columns.csv`.
- `hrdm_key_object_columns.sql` wrote `knowledge-base/discovery-output/hrdm_key_object_columns.csv`.
- `hrdm_servicenow_candidate_tables.sql` wrote `knowledge-base/discovery-output/hrdm_servicenow_candidate_tables.csv`.

Current environment boundary:

- HR DataMart is a different Snowflake environment/profile from the working Workload Lens `EDLDB` profile.
- A separate local HRDM profile has been created and validated through browser SSO.
- Keep the EDLDB and HRDM configs separate; do not use the Workload Lens `EDLDB` profile for HRDM.

This playbook can be run from the existing Workload Lens venv for `EDLDB`/`UKG`. HRDM queries require a separate HRDM Snowflake profile. Do not paste secrets into this repository.

## Local Run Pattern

Use the existing read-only query runner with the `EDLDB` profile:

```powershell
& "C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\Codex ORBIT\Workload Lens\.venv\Scripts\python.exe" `
  "C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\Codex ORBIT\Workload Lens\scripts\run_snowflake_query.py" `
  --config "C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\Codex ORBIT\Workload Lens\config\snowflake.toml" `
  --sql "C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Documents\Agentic HR Fitness Check\knowledge-base\discovery-sql\edldb_candidate_tables.sql" `
  --out "C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Documents\Agentic HR Fitness Check\knowledge-base\discovery-output\edldb_candidate_tables.csv"
```

The Snowflake connector warns that `keyring` is not installed. Installing secure local storage in that venv should reduce repeated browser prompts:

```powershell
& "C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\Codex ORBIT\Workload Lens\.venv\Scripts\python.exe" -m pip install "snowflake-connector-python[secure-local-storage]"
```

## HRDM Profile

The local HRDM config lives outside this repository:

```text
C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\Codex ORBIT\Workload Lens\config\snowflake_hrdm.toml
```

Runner-compatible shape:

```toml
[connection]
account = "CHEWY-CHEWYHR"
user = "<sso-user>"
role = "HRDATA_STANDARD_ROLE"
warehouse = "USERS_WH"
database = "D_HRDATAMART"
schema = "S_ANALYTICS"
authenticator = "externalbrowser"
```

Use the same Python runner but point `--config` at the HRDM profile instead of the Workload Lens `EDLDB` profile. The user field should match the already-working SSO identity on this machine; do not print or commit it.

## Priority Databases And Schemas

Start with these discovered database/schema leads:

- `D_HRDATAMART.S_ANALYTICS`
- `D_HRDATAMART.S_WORKDAY`
- `D_HRDATAMART.S_CURATED`
- `D_HRDATAMART.S_CURATED_SENSITIVE`
- `D_HRDATAMART.S_ADMIN`
- `EDLDB.UKG`

ServiceNow replication is confirmed as a data initiative, but the production Snowflake database/schema name was not found in the source docs. Search for the table names `sn_hr_core_case` and `sn_hr_core_task`.

## Safety Guidance

- Run metadata queries first.
- Avoid selecting employee-, case-, comment-, or document-level detail until governance confirms access.
- For initial mapping, prefer row counts, column names, max/min dates, and distinct non-sensitive categorical values.
- For any sample output, aggregate by site and period unless a source owner approves record-level inspection.
- Never store credentials, raw PII, case narratives, comments, work notes, or direct contact details in this repository.

## Metadata Search Templates

List accessible databases and schemas:

```sql
show databases;
show schemas in database D_HRDATAMART;
show schemas in database EDLDB;
```

Find candidate table names across a database:

```sql
select
  table_catalog,
  table_schema,
  table_name,
  table_type,
  created,
  last_altered
from <DATABASE>.information_schema.tables
where upper(table_name) like any (
  '%UKG%',
  '%WORKDAY%',
  '%SNOW%',
  '%SERVICE%NOW%',
  '%ROSTER%',
  '%TIME%',
  '%TIMECARD%',
  '%SCHEDULE%',
  '%ACCRUAL%',
  '%ATTENDANCE%',
  '%ECHO%',
  '%CAT%',
  '%VOC%',
  '%STAND%',
  '%ROUND%',
  '%SURVEY%',
  '%BENEFICIARY%',
  '%EMERGENCY%',
  '%LOA%',
  '%LOAA%',
  '%FLO%'
)
order by table_catalog, table_schema, table_name;
```

Find candidate columns:

```sql
select
  table_catalog,
  table_schema,
  table_name,
  column_name,
  data_type
from <DATABASE>.information_schema.columns
where upper(column_name) like any (
  '%SITE%',
  '%LOCATION%',
  '%LOCATION_CODE%',
  '%FC%',
  '%REGION%',
  '%EMPLOYEE%',
  '%WORKER%',
  '%USER%',
  '%MANAGER%',
  '%BENEFICIARY%',
  '%EMERGENCY%',
  '%CONTACT%',
  '%SCHEDULE%',
  '%SCHEDULE_GROUP%',
  '%MISSING%',
  '%PUNCH%',
  '%MEAL%',
  '%LUNCH%',
  '%PAYCODE%',
  '%HOURS%',
  '%SLA%',
  '%CASE%',
  '%TASK%',
  '%STATE%',
  '%ASSIGNMENT%',
  '%HR_SERVICE%',
  '%LOA%',
  '%LOAA%',
  '%VOC%',
  '%CAT%',
  '%ECHO%',
  '%ROUND%',
  '%STAND%',
  '%FLO%'
)
order by table_catalog, table_schema, table_name, ordinal_position;
```

## UKG Discovery

Known candidates:

- `EDLDB.UKG.GOLD_V_TIMECARD_TOTAL`
- `EDLDB.UKG.GOLD_V_TIMECARD_TRANSACTIONS`
- `EDLDB.UKG.GOLD_V_SCHEDULE_TOTAL`
- `EDLDB.UKG.GOLD_V_SCHEDULE_TRANSACTIONS`
- `EDLDB.UKG.GOLD_V_ACCRUAL_BALANCE_SUMMARY`

Column inventory:

```sql
select table_name, column_name, data_type
from EDLDB.information_schema.columns
where table_schema = 'UKG'
  and table_name in (
    'GOLD_V_TIMECARD_TOTAL',
    'GOLD_V_TIMECARD_TRANSACTIONS',
    'GOLD_V_SCHEDULE_TOTAL',
    'GOLD_V_SCHEDULE_TRANSACTIONS',
    'GOLD_V_ACCRUAL_BALANCE_SUMMARY'
  )
order by table_name, ordinal_position;
```

Freshness and row counts:

```sql
select 'GOLD_V_TIMECARD_TOTAL' as table_name, count(*) as row_count from EDLDB.UKG.GOLD_V_TIMECARD_TOTAL
union all
select 'GOLD_V_TIMECARD_TRANSACTIONS', count(*) from EDLDB.UKG.GOLD_V_TIMECARD_TRANSACTIONS
union all
select 'GOLD_V_SCHEDULE_TOTAL', count(*) from EDLDB.UKG.GOLD_V_SCHEDULE_TOTAL
union all
select 'GOLD_V_SCHEDULE_TRANSACTIONS', count(*) from EDLDB.UKG.GOLD_V_SCHEDULE_TRANSACTIONS
union all
select 'GOLD_V_ACCRUAL_BALANCE_SUMMARY', count(*) from EDLDB.UKG.GOLD_V_ACCRUAL_BALANCE_SUMMARY;
```

V1 items to validate from UKG:

- V1-003 Missing Time Stamps
- V1-005 13h Report
- V1-006 60h Report
- V1-007 Lunch Punch review
- V1-015 VTO Process, if UKG is used instead of Smartsheet no-match source
- V1-025 Audit schedule groups

## Roster Health Discovery

Known source leads:

- FC HR Analytics `hr_fulfillment_roster_health_0830`
- Roster Health Assessment uses CLMS, UKG, and Workday
- Historical Confluence SQL referenced `chewybi.employees`, `chewybi.accrual_balance_time_off`, `chewybi.time_entry_timesheet_summary`, `chewybi.employee_attendance`, `sandbox_fulfillment.t_clms_data`, and `sandbox_fulfillment.warehouses`

Search for modern Snowflake equivalents:

```sql
select table_catalog, table_schema, table_name
from <DATABASE>.information_schema.tables
where upper(table_name) like any (
  '%ROSTER%HEALTH%',
  '%ROSTER%',
  '%CLMS%',
  '%EMPLOYEE_ATTENDANCE%',
  '%TIME_ENTRY%',
  '%BUBBLE%',
  '%NCNS%'
)
order by table_catalog, table_schema, table_name;
```

V1 items to validate from Roster Health:

- V1-004 Unscheduled
- V1-011 Attendance Management
- V1-025 Audit schedule groups, if using missing schedule output

## ECHO, CAT, VOC, And Survey Discovery

Known source leads:

- FC HR Analytics `hr_fulfillment_smartsheet_etl_0630`
- ECHO Tableau data source
- CAT Tracker task
- VOC task
- Stand Ups task
- Week 3 Surveys task
- New Hire Surveys task
- `cat_tracker_snapshot`

Search:

```sql
select table_catalog, table_schema, table_name
from <DATABASE>.information_schema.tables
where upper(table_name) like any (
  '%ECHO%',
  '%CAT%',
  '%VOC%',
  '%STAND%',
  '%ROUND%',
  '%FISH%',
  '%SURVEY%',
  '%NEW%HIRE%',
  '%WEEK%3%'
)
order by table_catalog, table_schema, table_name;
```

V1 items to validate:

- V1-008 Standup Audits
- V1-009 VOC Board Management
- V1-012 Locker Management
- V1-014 Swag Management
- V1-022 Review and answer VOC board daily
- V1-023 CAT Tracker
- V1-024 Roundtables

## Workday / HRDM Discovery

Known candidates:

- `D_HRDATAMART.S_WORKDAY.wd_datamartfeed`
- `D_HRDATAMART.S_WORKDAY.wd_datamartfeed_trended`
- `D_HRDATAMART.S_WORKDAY.workday_trended`
- `D_HRDATAMART.S_WORKDAY.workday_trended_stage`
- `D_HRDATAMART.S_ANALYTICS.ROSTER_WEEK_END`

Search for beneficiary and emergency contact columns:

```sql
select
  table_schema,
  table_name,
  column_name,
  data_type
from D_HRDATAMART.information_schema.columns
where table_schema in ('S_WORKDAY', 'S_ANALYTICS', 'S_CURATED', 'S_CURATED_SENSITIVE')
  and upper(column_name) like any (
    '%BENEFICIARY%',
    '%BENEFIT%',
    '%EMERGENCY%',
    '%CONTACT%',
    '%DEPENDENT%',
    '%WORKER%',
    '%LOCATION%',
    '%HIRE%',
    '%TENURE%'
  )
order by table_schema, table_name, ordinal_position;
```

V1 items to validate:

- V1-016 Ensure site TMs have listed beneficiaries
- V1-017 Ensure site TMs have listed emergency contacts
- V1-026 Investigations, only if governance approves Workday Investigation Documents metadata use

## ServiceNow Discovery

Known source objects:

- `sn_hr_core_case`
- `sn_hr_core_task`

Find database/schema:

```sql
select table_catalog, table_schema, table_name
from <DATABASE>.information_schema.tables
where lower(table_name) in ('sn_hr_core_case', 'sn_hr_core_task')
   or upper(table_name) like '%SN_HR_CORE%';
```

Column inventory:

```sql
select table_catalog, table_schema, table_name, column_name, data_type
from <DATABASE>.information_schema.columns
where lower(table_name) in ('sn_hr_core_case', 'sn_hr_core_task')
order by table_catalog, table_schema, table_name, ordinal_position;
```

Fields to confirm for Fitness Check:

- Case/task number
- `sys_id`
- `sys_updated_on`
- opened date
- closed/resolved date
- state
- HR service
- assignment group
- assigned to
- subject person
- short description
- source
- SLA fields or joinable SLA table
- active flag
- site/location key or derivable assignment group/site relationship

V1 items to validate:

- V1-001 SNOW Tickets
- V1-002 LOAA Management

## Talent Management Discovery

Source status is weaker than UKG/ECHO/SNOW. Known leads:

- Talent Management Dashboard workbook from reviewed matrix
- One on One SOP says completed 1:1s after July 2022 are stored in Workday profile Performance tab
- EPA Team Product Inventory lists Operations Talent Management Dashboard as HR Datamart/Tableau
- Jira issue exists for LEW/Quality 1:1 dashboard updates

Search:

```sql
select table_catalog, table_schema, table_name
from <DATABASE>.information_schema.tables
where upper(table_name) like any (
  '%TALENT%',
  '%ONE%ON%ONE%',
  '%1%1%',
  '%LEW%',
  '%QUALITY%',
  '%PERFORMANCE%',
  '%DEVELOPMENT%'
)
order by table_catalog, table_schema, table_name;
```

V1 items to validate:

- V1-019 Quality 1:1
- V1-020 LEWs

## Minimum Source Mapping Output

Each item should end discovery with one approved row like this:

| Field | Description |
|---|---|
| `sw_item_id` | Stable Fitness Check item ID. |
| `source_system` | System of record or governed reporting layer. |
| `source_database` | Snowflake database, if applicable. |
| `source_schema` | Snowflake schema, if applicable. |
| `source_object` | Table, view, file, API, report, or manual workflow. |
| `site_key` | Field used to map to canonical site. |
| `measurement_window` | Prior 48 hours, prior week, prior month, quarter, current state, or custom. |
| `filters` | Population and exclusion logic. |
| `measured_value` | Exact metric value used for rating. |
| `rating_rule_version` | Rule version that maps value to green/yellow/red. |
| `data_owner` | Business/data owner accountable for definition. |
| `classification` | Approved data classification and output treatment. |
| `validation_sample` | SME-approved site/period result to reconcile. |
