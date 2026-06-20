# V1 Ingestion Backlog

Status: Draft source-mapping backlog
Last updated: 2026-06-20

This backlog starts from the 27 V1 in-scope items in `docs/Reviewed-Checklist-Disposition.md`. A row is not ingestion-ready until source fields, date windows, site keys, owner, and validation examples are approved.

## Status Legend

| Status | Meaning |
|---|---|
| Source located | A likely source artifact, pipeline, table, or dashboard has been found. Field-level mapping still required. |
| Candidate | A source family is likely but not enough evidence exists to map fields yet. |
| Hybrid/manual | Some data may exist, but the process requires physical inspection, human judgment, or manual evidence capture. |
| Derived | Metric can be calculated from other Fitness Check results after dependencies are scored. |
| Blocked | Access, governance, or source discovery is blocking ingestion design. |

## Backlog

| V1 ID | Item | Source family | Current evidence | Ingestion status | Next discovery step |
|---|---|---|---|---|---|
| V1-001 | SNOW Tickets | ServiceNow / HR DataMart | ServiceNow SOPs; ServiceNow replication pages; expected tables `sn_hr_core_case`, `sn_hr_core_task`; HRDM first-pass metadata search returned zero matching tables | Blocked | Confirm actual ServiceNow production database/schema with HRDM or ServiceNow owner, then map SLA breach formula, HR service/category filters, suspend handling, assignment group/site key, and production connector status. |
| V1-002 | LOAA Management | ServiceNow / AbsenceOne / HR DataMart | SNOW Case & Task SOP; ServiceNow replication pages; HRDM first-pass metadata search returned zero expected case/task tables | Blocked | Confirm actual ServiceNow production schema/database before defining LOAA case/task filters, AbsenceOne handoff treatment, SLA breach numerator/denominator, and yellow/red threshold overlap. |
| V1-003 | Missing Time Stamps | UKG / Snowflake | UKG Data Pipeline; UKG missed punch job aid; workbook references Punch Lunch Audit | Source located | Test `EDLDB.UKG.GOLD_V_TIMECARD_TRANSACTIONS` and exception tables for missing-punch signals in last 48 hours excluding current shift. |
| V1-004 | Unscheduled (Not Scheduled but Working) | Roster Health / UKG / CLMS / Workday | Roster Health docs and SQL; `hr_fulfillment_roster_health_0830` pipeline | Source located | Confirm whether Roster Health source has NSBW/UBW site counts by 7-day window and reconcile to Tableau. |
| V1-005 | 13h Report | HR Packet / UKG / Snowflake | HR Daily Packet handbook; UKG timecard/schedule tables; HR Packet pipeline | Source located | Confirm Over 12 or 13 Hours view logic, scheduled-shift adjustment, and workbook-noted roster flaw. |
| V1-006 | 60h Report | HR Packet / UKG / Snowflake | HR Daily Packet handbook; `EDLDB.UKG.GOLD_V_TIMECARD_TOTAL` | Source located | Define prior-week week boundary, employee/site grain, and 60-hour calculation from timecard totals. |
| V1-007 | Lunch Punch review | UKG / Snowflake | UKG Punch Lunch Audit workbook lead; UKG timecard transactions; missed punch job aid | Source located | Validate meal-break exceptions and whether current report incorrectly conflates lunch and missing-punch issues. |
| V1-008 | Standup Audits | ECHO / Smartsheet / Tableau | ECHO Dashboard handbook; ECHO Program SOP; FC HR Analytics Stand Ups task | Source located | Locate target table/output for Stand Ups task and map site, week, score, and minimum audit count. |
| V1-009 | VOC Board Management | ECHO / VOC / Smartsheet / Tableau | ECHO Program SOP; VOC Dashboard handbook; FC HR Analytics VOC task | Source located | Confirm whether score and identifiable-comment percentage are in ECHO source, VOC source, or both. |
| V1-010 | TM Experience Walk | Smartsheet or replacement workflow | Fitness Check SOP and workbook source; ECHO mentions site leadership walks/CAT but not exact TM Experience Walk source | Hybrid/manual | Decide Smartsheet replacement and manual evidence workflow. Determine whether historical Smartsheet can be ingested. |
| V1-011 | Attendance Management | Roster Health / UKG | Roster Health docs; Roster Health SQL; workbook says Bubble % and flags Tableau vs UKG discrepancy | Source located | Confirm Bubble % definition, source table, and discrepancy root cause before scoring. |
| V1-012 | Locker Management | New Hire Experience Surveys / Tableau | New Hire Experience Survey Report handbook; new hire survey ETL tasks | Source located | Map Day 1 survey question to locker/resource availability, denominator, site key, and date window. |
| V1-013 | Badge Management | CCure / labor projections / physical inventory | Workbook source; NHO resources mention badges; no durable inventory source found | Hybrid/manual | Separate automated labor projection from physical badge/reel/lanyard/ink inventory. Manual evidence likely required. |
| V1-014 | Swag Management | VOC Dashboard / comments | VOC Dashboard handbook; ECHO Program recognition/upload mechanics | Candidate | Define approved VOC taxonomy or keyword rule for swag comments; decide whether text analytics is acceptable for scoring. |
| V1-015 | VTO Process | Smartsheet / UKG | UKG VET/VTO job aid; FC HR Analytics VTO Hourly task | Source located | Confirm Site VTO No-Match source, master file, site sheets, fields, and rating numerator. |
| V1-016 | Ensure site TMs have listed beneficiaries | Workday / HR DataMart | HRDM profile validated; Workday current/trended and roster objects visible; first-pass broad and key-object metadata searches found no obvious beneficiary, dependent, or benefit-completeness fields | Candidate | Ask Workday/HRDM owner for the exact report/table/field behind `Chewy Employees Missing Beneficiary Report`; confirm exclusion for TMs not enrolled in benefits. |
| V1-017 | Ensure site TMs have listed emergency contacts | Workday / HR DataMart | HRDM profile validated; Workday current/trended and roster objects visible; first-pass broad and key-object metadata searches found no obvious emergency-contact fields | Candidate | Ask Workday/HRDM owner for the exact report/table/field behind `Chewy Employee Emergency Contact Info`; confirm 30-day employment denominator. |
| V1-018 | Audit exempt HR Standard Work | Fitness Check derived results | Product logic only | Derived | Define dependency set of HRBP/exempt items and denominator. Do not source externally unless process owner changes rule. |
| V1-019 | Quality 1:1 | Talent Management Dashboard / Workday / Tableau | Talent Management Dashboard reference; One on One SOP; EPA inventory; HRDM first-pass metadata found no obvious Quality 1:1/Talent table or column matches | Candidate | Inspect Tableau workbook/data source or EPA repo for completion percentage fields and site mapping. |
| V1-020 | LEWs | Talent Management Dashboard / Tableau | Talent Management Dashboard reference; Chewy Locations has `LEW` column as likely expected count, not completion; HRDM first-pass metadata found no obvious LEW/Talent table or column matches | Candidate | Confirm LEW definition, expected denominator, completion source, and whether dashboard table exists outside obvious HRDM names. |
| V1-021 | Site communication & signage | TM Experience Walk / physical site check | Workbook source from TM Experience Walk question | Hybrid/manual | Tie to TM Experience Walk workflow or create manual input evidence requirement. |
| V1-022 | Review and answer VOC board daily (with GM) | ECHO / VOC Dashboard | ECHO Program SOP; VOC Dashboard response-time view; FC HR Analytics VOC task | Source located | Map prior-week VOC score and response-time/completion fields; define GM/HRM partnership requirement as measurable proxy. |
| V1-023 | CAT Tracker | ECHO / CAT / Smartsheet | ECHO Program SOP; FC HR Analytics CAT task; `cat_tracker_snapshot` | Source located | Locate table/output from CAT task/snapshot and map weekly score, open items, closed items, and dwell fields. |
| V1-024 | Roundtables | CAT / ECHO | Roundtables SOP; ECHO Program SOP; FC HR Analytics CAT task | Source located | Confirm roundtable event taxonomy in CAT and calculate monthly/quarterly counts. |
| V1-025 | Audit schedule groups | UKG / Snowflake | UKG schedule-group job aid; UKG schedule tables; Roster Health missing schedule category | Source located | Identify missing schedule group field/table and decide if Roster Health missing schedule is the official source. |
| V1-026 | Investigations | Workday / Ethicspoint/OpenBark / ER Dashboard | Investigations SOP; EPA inventory has OpenBark Dashboard; Workday Investigation Documents | Blocked by sensitivity | Governance/legal must approve inclusion rules, aggregate-only fields, and whether SLA completion average can be used without case detail exposure. |
| V1-027 | FLO Certification management | Smartsheet / Workday / UKG | FLO Certification SOP; site FLO pending/completed Smartsheet workflow; Workday/Kronos verification | Hybrid/manual | Locate FLO Smartsheet master/site sheets or pipeline. Define how to sample five most recent offer letters without exposing individual details. |

## Recommended Ingestion Order

1. Start with source families that already have durable data paths: UKG/HR Packet/Roster Health, ECHO/CAT, ServiceNow, and Workday HRDM.
2. Defer physical evidence and local tracker items until a manual input/evidence workflow is approved.
3. Reconcile against Tableau dashboards only after table-level source extracts are available.
4. Treat Investigations as a governance-first item before any field mapping or sample extraction.
5. Treat the 2026 TM Experience Roadmap as recommendation/action-loop context. Do not use VOC action trackers or project charters as Standard Work scoring inputs unless a specific approved metric, source field, and rule are added to the catalog.
