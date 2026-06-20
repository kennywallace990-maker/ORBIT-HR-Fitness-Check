# HR Fitness Check Knowledge Base

Status: Draft discovery knowledge base
Last updated: 2026-06-20
Product: ORBIT HR Fitness Check

## Purpose

This knowledge base captures source-discovery findings for HR Fitness Check ingestion. It translates the reviewed PRD/checklist into data-source leads, ingestion candidates, open blockers, and Snowflake discovery steps.

Tagline: Fitness check measures the quality of standard work. Is the stated process being followed?

## How To Use This Knowledge Base

Start with these files:

- `knowledge-base/source-inventory.md` for the located systems, documents, dashboards, data marts, and pipeline leads.
- `knowledge-base/voc-pulse-action-roadmap.md` for the 2025 VOC Pulse action-loop context and 2026 TM Experience roadmap workstreams.
- `knowledge-base/ingestion-backlog.md` for the 27 V1 in-scope checklist items and their current ingestion status.
- `knowledge-base/snowflake-discovery-playbook.md` for SQL templates and access checks to run once Snowflake access is available.
- `knowledge-base/research-log.md` for what has already been searched and what was not found.

## Current Discovery Summary

Most V1 data appears to sit in one of these source families:

- HR DataMart / Snowflake, especially Workday and ServiceNow HR case/task data.
- EDLDB / UKG Snowflake tables for timecard, schedule, and accrual data.
- Existing FC HR Analytics / Pipewiser jobs for HR Packet, Roster Health, ECHO, New Hire Surveys, CAT, VET/VTO, and Smartsheet roster feeds.
- SharePoint and Smartsheet artifacts for SOPs, trackers, physical-evidence uploads, and older workflow sources.
- FC Ops Library 2026 TM Experience Roadmap artifacts for VOC Pulse action-loop context, approved-intervention candidates, and future-report recommendations.
- Tableau dashboards fed by the sources above, useful for reconciliation but not preferred as the durable ingestion source.

## Important Controls

Do not treat any source as ingestion-ready until these are known:

- Source system and source object/table/report.
- Source fields, filters, joins, and site key.
- Date window and measurement cadence.
- Data owner and approval status.
- Data classification, retention, and output aggregation policy.
- Validation examples that reconcile against the current workbook or SME-approved expected output.

Associate-level and case-level detail may exist in source systems even when Fitness Check output is aggregate. The ingestion design must keep rating outputs separate from raw source access.

## Current Snowflake Access Status

An existing Python + Snowflake SSO setup was located in the Workload Lens project on this machine. It uses browser SSO through Okta and the Snowflake Python connector.

Current working context for `EDLDB` / `UKG`:

- Role: `PEOPLE_ANALYTICS_DEVELOPER`
- Warehouse: `PEOPLE_ANALYTICS_WH`
- Database: `EDLDB`
- Schema: `PEOPLE_ANALYTICS_SANDBOX`
- Secondary roles reported by Snowflake: `FULFILLMENT_OPTIMIZATION_DEVELOPER`, `OTH_USER`, `DBT_DEMO_DEVELOPER`

Discovery completed from that context:

- Snowflake SSO smoke test succeeded.
- `EDLDB` table metadata query succeeded and returned 817 candidate rows.
- `EDLDB.UKG` column metadata query succeeded and returned 618 candidate rows.

HRDM context:

- HR DataMart is a different Snowflake environment/profile from the Workload Lens `EDLDB` profile.
- A local HRDM profile was created outside this repository and validated through browser SSO.
- HRDM metadata discovery now has schema, table, and column outputs.
- HRDM roster and Workday current/trended objects are visible.
- No obvious beneficiary, emergency-contact, dependent, benefit-completeness, ServiceNow case/task, LEW, or Quality 1:1 fields/tables were found by first-pass metadata search.

Practical solution:

1. Reuse the existing Workload Lens Python virtual environment and SSO config for EDLDB/UKG discovery.
2. Use the local HRDM profile for `D_HRDATAMART` metadata discovery and approved aggregate-only queries.
3. Ask HRDM/Workday owners for beneficiary and emergency-contact field/report mapping because those fields were not discoverable by obvious column names.
4. Ask ServiceNow/HRDM owners for the actual production schema or database containing HR case/task replication.
5. Optionally install `snowflake-connector-python[secure-local-storage]` in the existing venv to reduce repeated browser SSO prompts.
