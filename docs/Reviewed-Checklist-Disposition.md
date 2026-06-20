# Reviewed Checklist Disposition

Version: 0.1
Status: Draft discovery artifact
Source workbook: ORBIT - HR Fitness Check Matrix.xlsx
Reviewed by: Weipan Le, Kenny Wallace, Ashley Larue
Last Updated: 2026-06-19

## Purpose

This file translates the reviewed Excel matrix into product scope language for HR Fitness Check. It is not a final source-to-target map. A row marked "V1 in scope" means the business wants the item measured in V1 if data mapping, ownership, rating logic, and validation are completed. It does not mean the item is already automated.

Workbook readiness gaps:

- `Current Owner` is blank for all rows.
- `Snowflake Table` is blank for all rows.
- `Reviewer(s)` is blank for all rows.
- Rating bands are human-readable and still need conversion into executable rules.

## Disposition Summary

| Disposition | Count |
|---|---:|
| V1 in scope | 27 |
| Remove / out of scope | 5 |
| Needs research before scope | 13 |
| Future candidate, not V1 | 3 |
| Manual / physical check research | 1 |
| Total reviewed rows | 49 |

Owner distribution across all reviewed rows:

| Previous owner | Row count |
|---|---:|
| HRA | 23 |
| HRBP | 11 |
| HRM | 15 |

## V1 In-Scope Rows

| V1 ID | Previous owner | HR task | Evidence source from workbook | Rating band summary | Product implication |
|---|---|---|---|---|---|
| V1-001 | HRA | SNOW Tickets | SNOW Site Dashboard; prior-month SLA breach percentage | Green <2%; Yellow 2-5%; Red >5% | Candidate automatable after ServiceNow metric definition, suspend behavior, and network-partner hold handling are confirmed. |
| V1-002 | HRBP | LOAA Management | SNOW Site LOAA Dashboard; prior-month LOAA SLA breach percentage | Green <1%; Yellow 2-3%; Red 3%+ | Candidate automatable; yellow/red boundary overlap and Absence One dependency need confirmation. |
| V1-003 | HRA | Missing Time Stamps | UKG Pro Punch Lunch Audit; last 48 hours excluding current shift | Green 0; Yellow 1-2; Red 3+ | Candidate automatable; report logic needs validation because workbook note says it may surface lunch exceptions more than missing punches. |
| V1-004 | HRA | Unscheduled (Not Scheduled but Working) | Roster Health Report; last 7 days; NSBW column | Green 0-1; Yellow 2-5; Red 6+ | Candidate automatable if Tableau/Snowflake source fields are approved. |
| V1-005 | HRA | 13h Report (or +1h over scheduled shift) | HR Packet; last 7 days; Over 12 or 13 Hours tab | Green 0; Yellow 1-2; Red 3+ | Candidate automatable; workbook note flags roster/report flaw. |
| V1-006 | HRA | 60h Report | HR Packet; prior week | Green 0; Yellow 1; Red 2 | Candidate automatable if source fields and prior-week window are approved. |
| V1-007 | HRA | Lunch Punch (Meal Break) review | UKG Pro Punch Lunch Audit; last 7 days | Green 0-1; Yellow 2-5; Red 6+ | Candidate automatable, but SOP/report behavior must be validated before scoring. |
| V1-008 | HRA | Standup Audits | ECHO Dashboard; prior-week standup audit score | Green 80-100%; Yellow 60-80%; Red <60% | Candidate automatable if ECHO score grain and site key are available. |
| V1-009 | HRA | VOC Board Management | ECHO Dashboard VOC; prior-week score | Green 100% and 50% identifiable comments; Yellow 90-99% and 45% identifiable comments; Red <90% or under 45% identifiable comments | Candidate automatable; rule must represent both follow-up and identifiable-comment thresholds. |
| V1-010 | HRA | TM Experience Walk | Most recent TM Experience Walk in Smartsheet | Green 0-2 No; Yellow 3-4 No; Red 5+ No or walk older than 7 days | Hybrid/manual until Smartsheet replacement and physical-check workflow are decided. |
| V1-011 | HRA | Attendance Management | Roster Health Report; Bubble % column | Green <=3.5%; Yellow 3.5-4.5%; Red >=4.5% | Candidate automatable, but Tableau vs UKG discrepancy requires source-owner reconciliation. |
| V1-012 | HRA | Locker Management | Day 1 Surveys | Green >=90% yes; Yellow 80-90% yes; Red <80% yes | Candidate automatable or hybrid depending on survey data availability and survey denominator. |
| V1-013 | HRA | Badge Management | Labor projections and physical badge, reel/lanyard, and ink inventory | Green at/above target for all three; Yellow 90% of target for all three; Red <90% on any | Hybrid/manual because physical inventory evidence is required unless a durable inventory source exists. |
| V1-014 | HRA | Swag Management | VOC comments from prior 30 days | Green 0-1; Yellow 2-3; Red 4+ | Needs text/source mapping; likely hybrid until VOC taxonomy or search rules are approved. |
| V1-015 | HRA | VTO Process | Site VTO No-Match Sheet | Green 0-4; Yellow 5-9; Red 10+ | Candidate automatable only if no-match sheet has a durable governed source. |
| V1-016 | HRM | Ensure site TMs have listed beneficiaries | Workday Missing Beneficiary Report for TMs employed 30+ days | Green <10% missing; Yellow 10-20%; Red >20% | Candidate automatable; report must exclude or correctly handle TMs not enrolled in benefits. |
| V1-017 | HRM | Ensure site TMs have listed emergency contacts | Workday Employee Emergency Contact Info report for TMs employed 30+ days | Green <10% missing; Yellow 10-20%; Red >20% | Candidate automatable after eligibility, denominator, and aggregation rules are approved. |
| V1-018 | HRM | Audit exempt HR Standard Work | Review completed HRBP item rankings | Green >=90%; Yellow >=70%; Red <70% | Derived metric; depends on HRBP-item scoring and denominator policy. |
| V1-019 | HRBP | Quality 1:1 | Talent Management Dashboard; Quality Completion Percentages | Green 100%; Yellow 50%; Red 0% | Candidate automatable if dashboard source fields are available. |
| V1-020 | HRBP | LEWs | Talent Management Dashboard; LEW Completion Percentages | Green 100%; Yellow 50%; Red 0% | Candidate automatable if dashboard source fields are available. |
| V1-021 | HRM | Site communication & signage | TM Experience Walk question: job posters current and up to date | Green Yes; Red No | Hybrid/manual until Smartsheet replacement and evidence workflow are approved. |
| V1-022 | HRM | Review and answer VOC board daily (with GM) | ECHO Dashboard; prior-week VOC score | Green >=95%; Yellow 80-95%; Red <80% | Candidate automatable if ECHO source grain and site key are approved. |
| V1-023 | HRM | CAT Tracker | ECHO Dashboard; prior-week CAT score | Green >=80%; Yellow 60-80%; Red <60% | Candidate automatable if ECHO/CAT source fields are approved. |
| V1-024 | HRM | Roundtables | CAT TM Roundtables; additional roundtables held last quarter | Green 2+; Yellow 1; Red 0 | Candidate automatable or hybrid depending on CAT data quality and event taxonomy. |
| V1-025 | HRA | Audit schedule groups | UKG Pro; missing schedule groups | Green 0 missing; Yellow 1-5; Red 6+ | Candidate automatable if UKG source fields are approved. |
| V1-026 | HRBP | Investigations | ER Dashboard; site SLA completion average | Green within 14 days; Yellow within 30 days; Red 30+ days | Candidate automatable after ER source ownership and case inclusion rules are approved. |
| V1-027 | HRA | FLO Certification management | Site FLO tracker Archive/Completed sheet; five most recently processed OLs | Green 5; Yellow 4; Red 3 or less | Hybrid unless FLO tracker is in a governed data source. |

## Remove / Out-Of-Scope Rows

These rows should not appear in the V1 denominator unless a later decision reverses the disposition.

| Previous owner | HR task | Workbook status |
|---|---|---|
| HRBP | Reflections Questions | Remove - Out of scope |
| HRA | HR Front Desk 5S | Remove - Out of scope |
| HRA | Answer Phones | Remove - Out of scope |
| HRBP | Review HR shift handoffs | Remove. Out of Scope. |
| HRM | Sr. Team Engagements | Remove. Out of Scope. |

## Needs Research Before Scope

These rows require SME, data-source, workflow, or source-of-truth research before they can be included in V1.

| Previous owner | HR task | Workbook status | Product research question |
|---|---|---|---|
| HRM | Fishbowl Display | Review with Weipan. Needs research. | Does a durable evidence source exist, or is this a physical-display manual check? |
| HRM | Chewtopian of the Month/Leader of the Pack | Review with Weipan. Needs research. | Is recognition-board evidence captured in a system or only physical/local artifacts? |
| HRA | VET Process | Review with Weipan. Needs research. | Is the Site VET No-Match Sheet governed enough for V1 scoring? |
| HRBP | Inspect HR/support office workspaces | Review with Weipan. Needs research. | Is this a physical 5S check requiring manual input? |
| HRM | Labor Planning | Review with Weipan. Needs research. | Which source is authoritative for planned vs actual variance, and should attrition/LOA be included? |
| HRM | Prepare Ops training/development (such as in AMMs) | Review with Weipan. Needs research. | Is AM feedback collected in a durable source or only through interviews/check-ins? |
| HRA | NHO Administration | Review with Weipan. Needs Research. | Can UKG and CCure mismatch/error data be joined and validated? |
| HRA | Review Temporary Schedule Adjustments | Review with Weipan. Needs Research. | Is there a governed approved-accommodations tracker and UKG schedule comparison path? |
| HRA | Shift Transfers / Includes site-to-site transfers | Review with Weipan. Needs Research. | Can UKG MET/schedule-group mismatch rules be automated safely? |
| HRA | Review Daily HR Metrics | Review with Weipan. Needs Research. | What is the source of Daily Deep Dive entries and completeness? |
| HRBP | Audit hourly HR standard work | Review with Weipan. Needs Research. | Should this be a derived metric from HRA item rankings? |
| HRM | Monthly Engagement Calendar | Review with Weipan. Needs research. | Is there a durable source for public calendar postings and freshness? |
| HRM | HR Floor Engagement & Follow-Ups | Review with Weipan. Needs research. | Is calendar scheduling data accessible and appropriate for this measure? |

## Future Candidate, Not V1

| Previous owner | HR task | Workbook status | Product implication |
|---|---|---|---|
| HRBP | Performance Improvement Plan (PIP) primary POC | Review with Weipan. Not is V1 scope. Potentially in future versions. | Exclude from V1; revisit after document-template evidence path is approved. |
| HRBP | Memorandum of Expectation (MOE) primary POC | Review with Weipan. Not is V1 scope. Potentially in future versions. | Exclude from V1; revisit after document-template evidence path is approved. |
| HRM | Direct onboarding for new HR | Review with Weipan. Not is V1 scope. Potentially in future versions. | Exclude from V1; revisit after HR onboarding evidence is standardized. |

## Manual / Physical Check Research

| Previous owner | HR task | Workbook status | Product implication |
|---|---|---|---|
| HRBP | Prepare HR team meetings | Review with Weipan. Physical check. No existing data flow. | Exclude from automated V1 scoring unless a manual input workflow is approved. |

## Required Next Decisions

| Decision ID | Decision needed | Recommended owner |
|---|---|---|
| DEC-001 | Assign stable `sw_item_id` values to all 49 reviewed rows. | Kenny / Weipan |
| DEC-002 | Assign current owner for every V1 item. | Weipan |
| DEC-003 | Confirm whether any needs-research rows move into V1 before MVP. | Weipan / Ashley |
| DEC-004 | Confirm V1 denominator and missing-data treatment. | Kenny / Weipan / Data Governance |
| DEC-005 | Confirm automation mode for every V1 row. | Kenny / Data Engineering / Weipan |
| DEC-006 | Confirm new launch or scope decision date after the missed 2026-06-14 target. | Kenny / Ashley |
