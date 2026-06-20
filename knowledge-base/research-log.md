# Research Log

Status: Draft discovery log
Last updated: 2026-06-20

## Local Repository And Workbook

Actions completed:

- Connected the local repo to `https://github.com/kennywallace990-maker/ORBIT-HR-Fitness-Check`.
- Read the reviewed workbook content via SharePoint and local workbook inspection.
- Confirmed reviewed workbook gaps: blank Snowflake table, current owner, and reviewer cells.
- Created draft PRD and reviewed checklist disposition docs.

Key output:

- 27 V1 in-scope items.
- 5 remove/out-of-scope items.
- 13 research-before-scope items.
- 3 future candidates.
- 1 manual/physical-check research item.

## Local Snowflake Capability Check

Actions completed:

- Checked for `snow` CLI.
- Checked for `snowsql`.
- Checked environment variable names matching Snowflake patterns without printing secret values.
- Checked bundled Python for `snowflake.connector` and Snowpark packages.
- Located the prior Workload Lens Python virtual environment and Snowflake SSO config.
- Verified that the Workload Lens venv has `snowflake.connector` installed.
- Ran a Snowflake browser SSO smoke test through the existing Workload Lens query runner.
- Ran `EDLDB` and `EDLDB.UKG` metadata discovery queries.
- Tested `D_HRDATAMART` through the working Workload Lens `EDLDB` profile and searched locally for a separate HRDM profile.
- Created a separate local HRDM Snowflake profile outside this repository using approved browser SSO values.
- Ran HRDM smoke test, schema inventory, candidate table search, candidate column search, ServiceNow table-name search, and priority object column inventory.

Result:

- Existing Python + SSO access works through the Workload Lens project.
- Current active role is `PEOPLE_ANALYTICS_DEVELOPER`.
- Current active database is `EDLDB`.
- Current secondary roles include `FULFILLMENT_OPTIMIZATION_DEVELOPER`, `OTH_USER`, and `DBT_DEMO_DEVELOPER`.
- `EDLDB` candidate table discovery succeeded with 817 metadata rows.
- `EDLDB.UKG` candidate column discovery succeeded with 618 metadata rows.
- HR DataMart is a different Snowflake environment/profile from the working Workload Lens `EDLDB` profile.
- HRDM SSO profile is now validated for `D_HRDATAMART` metadata discovery.
- HRDM schema discovery succeeded with 11 metadata rows.
- HRDM candidate table discovery succeeded with 173 metadata rows.
- HRDM candidate column discovery succeeded with 1307 metadata rows.
- HRDM priority object column inventory succeeded with 879 metadata rows.
- HRDM ServiceNow table-name search returned zero expected case/task table matches.
- First-pass HRDM metadata did not find obvious beneficiary, emergency-contact, dependent, benefit-completeness, Quality 1:1, LEW, or Talent table/field names.
- The connector warns that `keyring` is not installed, causing repeated browser SSO prompts.

## SharePoint Searches And Fetches

Located:

- ORBIT - HR Fitness Check Matrix.xlsx.
- HR Standard Work Fitness Check SOP.
- ORBIT intake form.
- HR SW Fitness Check historical planning document.
- Fulfillment Center & Pharmacy Human Resources Reporting Job Aid.
- Chewy Locations.csv.
- HR Daily Packet handbook.
- Roster Health Dashboard handbook.
- ECHO Dashboard handbook.
- VOC Dashboard handbook.
- New Hire Experience Survey Report handbook.
- ServiceNow SOP.
- SNOW Case & Task Management SOP.
- UKG Standard Reporting and Dataview/Report Library SOPs.
- UKG VET/VTO Management job aid.
- UKG missed punch job aid.
- UKG schedule group job aid.
- FLO Certification SOP.
- Investigations SOP.
- ECHO Program SOP.
- Roundtables SOP.
- HR Onboarding Heatmap workbook.
- FC Ops Library of Docs / 2026 Roadmap / TM Experience Roadmap folder.
- `2025 VOC Pulse , Core FC Network Review.pdf`.
- `2026 TM Focus Areas.xlsx`.
- VOC Pulse action workstream charters for Equipment, Facility Comfort and Housekeeping, Leader Presence, Recognition, Performance Management, Safety, VET/VTO Fairness, and X-Training Rotation.

Key TM Experience roadmap finding:

- The new FC Ops Library source is a post-2025 VOC Pulse action-planning hub. It should be treated as downstream action-loop evidence and recommendation-library context rather than primary Fitness Check scoring data. It links VOC themes to 2026 workstreams, pilot controls, playbooks, SOPs, and candidate metrics for future reporting.

Not located by SharePoint search:

- 2025 Q3 HR Fitness Check workbook by exact name.
- 2025 Q3 SW Quality Index workbook by exact name.
- 2025 Q3 Fitness Assessment workbook by exact name.
- Workday Missing Beneficiary Report by exact name.
- Workday Employee Emergency Contact Info report by exact name.
- Field-level Talent Management Dashboard mapping for Quality 1:1 and LEWs.

## Atlassian / Rovo Searches And Fetches

Located:

- Existing HR Fitness Check Confluence PRD page.
- ORBIT Program Home Page.
- Jira FCA-333 HR Engagement Tracking: Tableau request for FC-HRE, VOC, and Stand Up Audits from HR engagement SharePoint with daily refresh and 30-day timeframe.
- FC HR Analytics Documentation.
- Roster Health Assessment technical documentation.
- EDS - UKG Pro Data Ingestion into Snowflake.
- UKG Data Pipeline.
- ServiceNow Data Replication into HR DataMart.
- ServiceNow Data Ingestion Progress.
- EPA - HR Datamart (Snowflake) Overview.
- HRDM Workday pipeline documentation.
- EPA Team Product Inventory.
- Jira issue reference for LEW/Quality 1:1 dashboard update.

Important source leads:

- `https://github.com/Chewy-Inc/fc_hr_analytics`
- `D_HRDATAMART.S_ANALYTICS`
- `D_HRDATAMART.S_WORKDAY`
- `EDLDB.UKG`
- `EDLDB.UKG.GOLD_V_TIMECARD_TOTAL`
- `EDLDB.UKG.GOLD_V_TIMECARD_TRANSACTIONS`
- `EDLDB.UKG.GOLD_V_SCHEDULE_TOTAL`
- `EDLDB.UKG.GOLD_V_SCHEDULE_TRANSACTIONS`
- `EDLDB.UKG.GOLD_V_ACCRUAL_BALANCE_SUMMARY`
- `sn_hr_core_case`
- `sn_hr_core_task`
- `hr_fulfillment_etl_0630`
- `hr_fulfillment_roster_health_0830`
- `hr_fulfillment_smartsheet_etl_0630`
- `cat_tracker_snapshot`

GitHub access check:

- Read-only `git ls-remote` against `https://github.com/Chewy-Inc/fc_hr_analytics.git` returned repository not found from this local context. Treat the repo as a located lead with access blocked until Chewy GitHub permissions are confirmed.

Snowflake output files created:

- `knowledge-base/discovery-output/snowflake_access_smoke_test.csv`
- `knowledge-base/discovery-output/snowflake_role_context.csv`
- `knowledge-base/discovery-output/edldb_candidate_tables.csv`
- `knowledge-base/discovery-output/ukg_candidate_columns.csv`
- `knowledge-base/discovery-output/hrdm_access_smoke_test.csv`
- `knowledge-base/discovery-output/hrdm_schemas.csv`
- `knowledge-base/discovery-output/hrdm_candidate_tables.csv`
- `knowledge-base/discovery-output/hrdm_candidate_columns.csv`
- `knowledge-base/discovery-output/hrdm_key_object_columns.csv`
- `knowledge-base/discovery-output/hrdm_servicenow_candidate_tables.csv`

## Privacy And Sensitive-Data Handling Notes

The research surfaced some source content that may include direct contacts, case details, employee-level fields, or credential-adjacent material. This knowledge base intentionally does not copy personal contact values, credentials, passcodes, raw employee data, case narratives, or work notes.

Use source docs for context, but perform ingestion work only through approved governed access paths.

## Next Research Actions

1. Install Snowflake connector secure local storage in the existing Workload Lens venv if repeated browser prompts become disruptive.
2. Continue EDLDB/UKG discovery using the generated metadata outputs.
3. Ask Workday/HRDM owners to identify the exact beneficiary and emergency-contact report/table/fields because HRDM first-pass metadata did not reveal obvious columns.
4. Confirm the actual ServiceNow production connector schema/database because HRDM first-pass search did not reveal `sn_hr_core_case` or `sn_hr_core_task`.
5. Confirm whether the FC HR Analytics GitHub repo is accessible and inspect source SQL for the HR Packet, Roster Health, ECHO, CAT, VOC, and survey pipelines.
6. Ask EPA/Talent Management owners for Quality 1:1 and LEW source tables or Tableau workbook metadata.
7. Ask Governance/Legal whether Investigations can be measured using aggregate SLA metadata only.
8. Confirm which 2026 TM Experience Roadmap workstream artifacts are approved for ORBIT citation and which are still draft planning material.
