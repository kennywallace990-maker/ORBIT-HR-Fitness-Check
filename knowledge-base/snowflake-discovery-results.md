# Snowflake Discovery Results

Status: Draft discovery results
Last updated: 2026-06-19

## Working Local Solution

Use the existing Workload Lens Python virtual environment and read-only query runner for `EDLDB` / `UKG` discovery:

- Python venv: `C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\Codex ORBIT\Workload Lens\.venv`
- Query runner: `C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\Codex ORBIT\Workload Lens\scripts\run_snowflake_query.py`
- Config: `C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\Codex ORBIT\Workload Lens\config\snowflake.toml`

The config uses browser SSO through Okta. No credential value is stored in the Fitness Check repository.

Important boundary: HR DataMart is a different Snowflake environment/profile. The working Workload Lens config should be treated as the `EDLDB` / UKG profile, not as the HRDM connection.

## Confirmed Session Context

The smoke test succeeded with:

- Role: `PEOPLE_ANALYTICS_DEVELOPER`
- Warehouse: `PEOPLE_ANALYTICS_WH`
- Database: `EDLDB`
- Schema: `PEOPLE_ANALYTICS_SANDBOX`
- Secondary roles: `FULFILLMENT_OPTIMIZATION_DEVELOPER`, `OTH_USER`, `DBT_DEMO_DEVELOPER`

## Successful Metadata Outputs

| Output | Rows | Meaning |
|---|---:|---|
| `knowledge-base/discovery-output/snowflake_access_smoke_test.csv` | 1 | Confirms SSO and current role/warehouse/database/schema. |
| `knowledge-base/discovery-output/snowflake_role_context.csv` | 1 | Confirms active role and secondary-role state. |
| `knowledge-base/discovery-output/edldb_candidate_tables.csv` | 817 | Candidate EDLDB tables and views relevant to HR Fitness Check discovery. |
| `knowledge-base/discovery-output/ukg_candidate_columns.csv` | 618 | Candidate columns in `EDLDB.UKG` tables/views. |
| `knowledge-base/discovery-output/hrdm_access_smoke_test.csv` | 1 | Confirms HRDM SSO profile, role, warehouse, database, and schema context. |
| `knowledge-base/discovery-output/hrdm_schemas.csv` | 11 | Confirms accessible HRDM schemas. |
| `knowledge-base/discovery-output/hrdm_candidate_tables.csv` | 173 | Candidate HRDM tables/views relevant to Fitness Check discovery. |
| `knowledge-base/discovery-output/hrdm_candidate_columns.csv` | 1307 | Candidate HRDM columns by table/schema keyword search. |
| `knowledge-base/discovery-output/hrdm_key_object_columns.csv` | 879 | Full column inventory for priority roster and Workday objects. |
| `knowledge-base/discovery-output/hrdm_servicenow_candidate_tables.csv` | 0 | No HRDM tables matched expected ServiceNow case/task name patterns. |

## UKG Objects Confirmed In Metadata

High-value `EDLDB.UKG` objects found:

- `GOLD_V_PEOPLE`
- `GOLD_V_PEOPLE_CUSTOM_DATA`
- `GOLD_V_PEOPLE_EMPLOYMENT_STATUS_BY_DATE`
- `GOLD_V_PEOPLE_EMPLOYMENT_TERM`
- `GOLD_V_TIMECARD_TOTAL`
- `GOLD_V_TIMECARD_TRANSACTION`
- `GOLD_V_TIMECARD_PUNCH`
- `GOLD_V_TIMECARD_EXCEPTION`
- `GOLD_V_TIMECARD_EXCEPTION_COMMENT`
- `GOLD_V_TIMECARD_DURATION_PAYCODE_EDIT`
- `GOLD_V_TIMECARD_DURATION_PAYCODE_EDIT_COMMENT`
- `GOLD_V_TIMECARD_WORK_SHIFT`
- `GOLD_V_SCHEDULE_SHIFT`
- `GOLD_V_SCHEDULE_TOTAL`
- `GOLD_V_SCHEDULE_TRANSACTION`
- `GOLD_V_ACCRUAL_BALANCE`
- `GOLD_V_ACCRUAL_BALANCE_SUMMARY`
- `GOLD_V_ACCRUAL_CODES`
- `GOLD_V_ACCRUAL_TRANSACTION`

View-layer equivalents also exist, including:

- `V_PEOPLE`
- `V_TIMECARD_TOTAL`
- `V_TIMECARD_TRANSACTION`
- `V_TIMECARD_PUNCH`
- `V_TIMECARD_EXCEPTION`
- `V_SCHEDULE_TOTAL`
- `V_SCHEDULE_TRANSACTION`
- `V_SCHEDULE_SHIFT`
- `V_ACCRUAL_BALANCE_SUMMARY`

## V1 Items This Unlocks First

These items can move from source family research into table/field mapping using the generated EDLDB/UKG metadata:

- V1-003 Missing Time Stamps
- V1-005 13h Report
- V1-006 60h Report
- V1-007 Lunch Punch review
- V1-015 VTO Process, if UKG is used for VTO request/action data
- V1-025 Audit schedule groups

These may also benefit indirectly:

- V1-004 Unscheduled, if Roster Health can be rebuilt from UKG schedule/worked-hour data
- V1-011 Attendance Management, if Bubble/attendance source logic is confirmed against UKG

## HRDM Profile Validation

The HR DataMart profile was created locally outside this repository and validated through browser SSO on 2026-06-19.

- Local HRDM config: `C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\Codex ORBIT\Workload Lens\config\snowflake_hrdm.toml`
- Account/environment: `CHEWY-CHEWYHR`
- Role: `HRDATA_STANDARD_ROLE`
- Warehouse: `USERS_WH`
- Database: `D_HRDATAMART`
- Default schema: `S_ANALYTICS`
- Authenticator: `externalbrowser`

The first attempt using the short user value failed because the IdP session user differed from the configured Snowflake user. The config was corrected by copying the already-working SSO user identifier from the existing Workload Lens profile without printing it.

Accessible HRDM schemas found:

- `S_ADMIN`
- `S_ANALYTICS`
- `S_BRIDGE`
- `S_CORNERSTONE`
- `S_CURATED`
- `S_GREENHOUSE`
- `S_HYPERION`
- `S_LMS`
- `S_REFERENCE`
- `S_WORKDAY`

## HRDM Objects Confirmed In Metadata

High-value HRDM objects found for Fitness Check source mapping:

- `D_HRDATAMART.S_ANALYTICS.ROSTER_DAY_END`
- `D_HRDATAMART.S_ANALYTICS.ROSTER_WEEK_END`
- `D_HRDATAMART.S_ANALYTICS.ROSTER_PERIOD_END`
- `D_HRDATAMART.S_CURATED.ROSTER_WEEK_END`
- `D_HRDATAMART.S_CURATED.ROSTER_PERIOD_END`
- `D_HRDATAMART.S_WORKDAY.WD_DATAMARTFEED`
- `D_HRDATAMART.S_WORKDAY.WD_DATAMARTFEED_TRENDED`
- `D_HRDATAMART.S_WORKDAY.WORKDAY_TRENDED`
- `D_HRDATAMART.S_WORKDAY.V_WORKDAY_TRENDED`
- `D_HRDATAMART.S_ANALYTICS.WORKDAY_TRENDED_MANAGER_HIERARCHY`
- `D_HRDATAMART.S_WORKDAY.WD_LOCATION`
- `D_HRDATAMART.S_WORKDAY.WD_SECURITY`

Useful LOA fields were found in Workday/roster objects:

- `LOA`
- `LOA_TYPE`
- `LOA_REFERENCE_ID`
- `LOA_FLAG`

## HRDM Gaps Found

The metadata search did not find obvious beneficiary, emergency-contact, dependent, or benefit-completeness fields in the broad HRDM column search or the priority object column inventory.

The HRDM ServiceNow search returned zero rows for expected table names and patterns such as `sn_hr_core_case`, `sn_hr_core_task`, `SNOW`, and HR case/task names. This means SNOW Tickets and LOAA Management still need a ServiceNow replication schema, alternate database, or source-owner confirmation.

No Talent Management table or column names matched obvious `LEW`, `Quality`, `One on One`, or `Talent` patterns in the searched HRDM schemas. Quality 1:1 and LEWs still need Tableau/EPA source-owner mapping.

## V1 Items This Unlocks First

These items can now move from environment-blocked to table/field mapping:

- V1-004 Unscheduled, using HRDM roster objects with UKG/CLMS validation still required.
- V1-011 Attendance Management, using HRDM roster objects if Bubble/attendance logic maps there.
- V1-016 Ensure site TMs have listed beneficiaries, only after Workday/HRDM owner identifies the field/report because no obvious column was found by name.
- V1-017 Ensure site TMs have listed emergency contacts, only after Workday/HRDM owner identifies the field/report because no obvious column was found by name.

These remain blocked by missing source schema or governance:

- V1-001 SNOW Tickets.
- V1-002 LOAA Management.
- V1-019 Quality 1:1.
- V1-020 LEWs.
- V1-026 Investigations.
