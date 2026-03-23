# Product Requirement Document (PRD): ORBIT HR Workload Lens

**Product:** Workload Lens
**Program:** ORBIT (Operations Review & Business Intelligence Transformation)
**Lifecycle Stage:** Pillar 2 — Design & POC
**Owner:** Kenny Wallace, ORBIT Program Lead
**Platform:** Phoenix (Chewy Internal LLM Platform) → Snowflake
**Version:** 2.0
**Last Updated:** 2026-03-03

---

## 1. Problem Statement

Chewy's HR and Operations teams manually manage tens of thousands of UKG timecard actions each week across 51 fulfillment, pharmacy, veterinary care, and contact center sites. There is no centralized view of how much time HR spends on corrective rework versus proactive governance, no standardized way to compare sites of different sizes, and no systematic method for identifying which process breakdowns generate the most downstream cost. Leadership cannot answer basic questions like "how many HR hours were burned last week fixing timecards that should have been right the first time?" without manually pulling data from multiple systems.

Workload Lens solves this by transforming raw UKG timecard audit data into a weekly Operational Business Review (OBR) that quantifies HR workload, classifies every action by type and defect status, flags statistical outliers, and delivers narrative intelligence to VP-level stakeholders. The agent runs every Monday morning, generates the OBR from Snowflake data, and supports interactive drill-down questions for deeper analysis.

---

## 2. Product Phases

### Phase I: Time & Attendance (UKG) — Current

Phase I covers all timecard audit actions flowing through UKG Kronos, including punches, pay code edits, manager justified time, historical corrections, approvals, reviews, and comments. The data source is `EDLDB.PEOPLE_ANALYTICS_SANDBOX.UKG_V_TIMECARD_AUDIT` with supporting joins to `EDLDB.UKG.V_PEOPLE` (employee profiles) and `EDLDB.UKG.V_TIMECARD_EXCEPTION` (missed punch exceptions).

Phase I delivers the full OBR report covering 6 sections plus appendices, with interactive drill-down capability across 5 levels (Network → BU → Site → People/TMs → Root Cause).

### Phase II: HR Ticket Integration (ServiceNow) — Planned

Phase II adds ServiceNow HR case/ticket data to the Workload Lens. This integration will enable measurement of end-to-end HR transaction cost (from ticket creation through timecard resolution) and introduce Service Tier and Ownership classification. Service Tier/Misrouting logic will provide clear guardrails about which OBR Actor Group owns which category of work, enabling identification of misrouted tickets and process breakdowns at the handoff layer.

Phase II scope includes Service Tier classification, Intended Owner mapping, misrouting detection, SLA tracking, and ticket-to-timecard correlation. These capabilities are not in scope for Phase I.

---

## 3. OBR Actor Groups

Every UKG timecard action is attributed to an OBR Actor Group based on the revision user's `ACCESS_PROFILE` in `V_PEOPLE`. A self-edit name-match override takes the highest priority to ensure that anyone editing their own timecard is classified as Team Member regardless of their access profile.

### 3.1 Self-Edit Override (Highest Priority)

If the employee's full name matches the revision user's full name, the action is classified as **Team Member**. This resolves ambiguity for cases like a WFM analyst or manager clocking themselves in.

```
WHEN p.FIRST_NAME||' '||p.LAST_NAME = rev.FIRST_NAME||' '||rev.LAST_NAME THEN 'Team Member'
```

### 3.2 OBR Actor Group Mapping

| OBR Actor Group | ACCESS_PROFILE Values | Role Description |
|:---|:---|:---|
| **Local HR** | `Company Admin Site Specific`, `Workers Compensation` | Site-level field HR. Corrections, documentation, first-line policy guidance, and workers compensation case management. |
| **HRSS** | `Leave Support`, `Company Admin TMDM`, `Team Member Services`, `Super Access` | Centralized HR shared services covering LOA administration, UKG system configuration, and escalated transactions. |
| **Team Member** | `Employee Basic`, `Employee Basic- Pharmacy`, `Training Basic`, `IT Admin`, `Training + Safety`, `Advanced Scheduler Lead`, `Advanced Scheduler Workforce Analyst`, `Facilities` | Employee self-service. Also catches all name-match self-edits via the override above. |
| **Local Ops** | `Manager Basic`, `Manager Basic With Punch&Schedule Edits`, `Practice Manager`, `Facilities Manager` | Field operations managers. Approvals, attendance enforcement, daily execution. |
| **WFM** | `Workforce Reporting` | Workforce Management. Scheduling, forecasting, intraday management. |
| **Other** | Any unmapped or NULL access profile | Data quality catch-all. Retained in Snowflake tables for research and anomaly investigation. Not included in customer-facing OBR output. |

### 3.3 Automation Exclusion

Actions performed by `Super Access No Wages` profiles represent automated system processes and are excluded from all reporting pipelines. These rows skew volume and defect metrics because they are not human-initiated work. They are filtered out at the `hr` CTE level alongside self-service and corporate site exclusions.

### 3.4 HR Reporting Boundary

Workload Lens still classifies `Workforce Reporting` rows as `WFM` in the base dataset so schedule dependencies can be studied, but WFM touches are not counted as HR workload. The HR reporting layer excludes `Team Member`, `Other`, `Automation`, and `WFM`, so customer-facing HR KPI tables show only `Local HR`, `HRSS`, and `Local Ops`.

### 3.5 TM Self-Service Catalog

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

### 3.6 Actor Group Changes from v1

| Change | Rationale |
|:---|:---|
| `Workers Compensation` added to Local HR | Workers comp case work is site-level HR activity |
| `Super Access No Wages` excluded from HRSS, filtered as automation | Not human-initiated; inflates HRSS volume |
| `WFM` excluded from the HR reporting layer | Workforce Management touches are operational partner work, not HR workload |
| `Other` retained in Snowflake but excluded from OBR customer deliverable | Supports research without polluting customer-facing metrics |
| COE subgroup eliminated | No operational need to separate COE from HRSS in reporting |

---

## 4. Work Classification Framework

### 4.1 Bucket Classification

Every UKG timecard audit row is assigned to one Bucket based on the nature of the work performed.

**Bucket A — Governance Population (Defect = No)**

Expected, policy-compliant pay code management. No error or correction involved.

Criteria:
- Pay Code Edit with revision type = Add
- Manager Justified Time with revision type = Add, where the paycode is NOT attendance-related (not late, early, NCNS, call off, or unpaid)

**Bucket B — Correction / Rework (Defect = Yes, always)**

An action that changes a pay or attendance outcome on a record that was previously closed, approved, or accepted. Bucket B is the core defect signal.

Criteria:
- All Punch actions (in HR context, after self-service exclusion)
- All Historical Corrections
- Edits and Deletes on Pay Code Edits and Manager Justified Time
- MJT Adds for attendance-related paycodes (late, early, NCNS, call off, unpaid)

**Bucket G — Governance / Documentation (Defect = No)**

Comment, review, and approval actions. Does not change pay outcomes.

Criteria:
- Comment-type entity types (Exception Comment, Punch Comment, Pay Code Edit Comment, Historical Correction Comment)
- Mark as Reviewed and Manager Approval actions

Note: Comment-type rows are excluded from the main action count pipeline but their text content is linked back to the parent action through the `comments_by_revision` CTE.

**Bucket D — Schedule Touch (Phase I: Not Implemented)**

Defined for future implementation. Will track schedule template changes, shift assignment edits, shift deletions, and shift trades with conditional defect classification based on whether the schedule change cascades into a paycode change within 24 hours.

### 4.2 Work Type Taxonomy

| Work Type | ENTITY_TYPE | Bucket | Notes |
|:---|:---|:---|:---|
| Punch | `Punch` | B (always, in HR context) | Core attendance signal |
| Pay Code Edit | `Pay Code Edit` | A (if Add) or B (if Edit/Delete) | Sub-classified by PAYCODE_NAME |
| Pay Code Edit Comment | `Pay Code Edit Comment` | G (Documentation) | Text linked via CTE; excluded from action counts |
| Punch Comment | `Punch Comment` | G (Documentation) | Text linked via CTE; excluded from action counts |
| Exception Comment | `Exception Comment` | G (Documentation) | Text linked via CTE; excluded from action counts |
| Manager Justified Time | `Manager Justified Time` | A or B (depends on paycode) | Attendance-related paycodes = B |
| Historical Correction | `Historical Correction` | B (always) | Highest friction score (5.0) |
| Mark as Reviewed | `Mark as reviewed` | G (Governance) | Timecard signoff |
| Manager Approval | `Manager Approval` | G (Governance) | Timecard finalization |

### 4.3 Paycode Category Mapping

Translates raw `PAYCODE_NAME` values into operational signals. Pattern matching uses `LOWER()` and `LIKE` with first-match-wins ordering.

| Paycode Category | Pattern on PAYCODE_NAME | Signal |
|:---|:---|:---|
| Manual Punch Correction | NULL or empty | HR manually correcting a missed/incorrect punch |
| Time spent manually coding VTO | `%vto%` or `%voluntary%` | Coding Voluntary Time Off |
| Time spent manually coding weather-related event | `%weather%` | Weather event pay adjustments |
| Manual coding missed late arrival | `%late%` | Late arrival attendance infractions |
| Manual coding missed early departure | `%early%` | Early departure attendance infractions |
| Manual coding No Call No Show | `%ncns%` | NCNS response |
| Manual coding Call Off | `%call off%` | Advance call-off or NCNS variant |
| Manual coding Sick Time | `%sick%` | Sick time usage |
| Manual coding Leave of Absence | `%leave%` | Intermittent leave or LOA |
| Manual coding for early departure/long lunch to deduct UTO | `%pto paid dur%` or `%personal unpd dur%` | Duration-based UTO deduction |
| Manual coding of Paid Time Off | `%pto%` | PTO usage |
| Manual coding to prevent UTO (Meal Break) | `%meal break%` | Meal break adjustments |
| Manual coding of Personal Time | `%personal%` | Personal time usage |
| Time spent manually coding [PAYCODE_NAME] | All other non-NULL paycodes | Fallback wrapping raw name |

### 4.4 Historical Correction Root Cause Categories

Groups Historical Correction paycodes into four insight categories for the Executive Summary.

| HC Category | Pattern on PAYCODE_NAME | Interpretation |
|:---|:---|:---|
| Attendance Enforcement | `%ncns%`, `%late%`, `%early%`, `%call off%` | Local managers or HR failed to code attendance infractions before the payroll window closed |
| Core Pay & Missing Time | `%regular%`, `%overtime%`, `%meal%`, `%pto paid%` | Employees required retroactive payroll deposits for missed regular, premium, or overtime pay |
| Schedule & Unpaid True-Ups | `%personal%`, `%vto%`, `%weather%`, `%unpaid%` | Broad operational changes were not processed prior to payroll transmission |
| Leave & Compliance Lag | `%leave%`, `%fmla%`, `%loa%`, `%bereavement%` | Standard expected lag pending documentation |
| Other | Everything else | Various other discrepancies requiring retroactive correction |

---

## 5. KPI Catalog

### 5.1 Core KPIs

| KPI | Formula | Interpretation |
|:---|:---|:---|
| Total HR Workload | `COUNT(*)` from `hr` CTE | Total actionable touches after self-service, automation, WFM, and corporate site exclusions |
| Defect Rate % | `SUM(BUCKET_B) / COUNT(*) × 100` | Share of all HR actions that are corrections or rework |
| Missing Punch Rate % | `SUM(DAILY_MISSED_PUNCHES) / COUNT(*) × 100` (deduplicated) | Share of actions associated with missed punch patterns |
| Historical Correction Rate % | `SUM(ENTITY_TYPE='Historical Correction') / COUNT(*) × 100` | Share of actions that are retro-corrections to closed pay periods |
| Friction Time Cost (FTE Hours) | `SUM(FRICTION_SCORE) / 60.0` | Estimated HR hours consumed, weighted by action complexity |
| Comment Compliance Rate % | `SUM(HAS_COMMENT WHERE HIGH_RISK_REWORK) / COUNT(HIGH_RISK_REWORK) × 100` | Documentation rate on actions that require a comment |
| DPMO | `(BUCKET_B_COUNT / (UNIQUE_TMS × 20)) × 1,000,000` | Defects Per Million Opportunities. Normalizes defect density across sites of different sizes. Assumes ~20 punch opportunities per employee per week (10 shifts × 2 punches). |

### 5.2 Friction Score Weights

| Action Type | Score | Approximate Manual Time |
|:---|:---|:---|
| Historical Correction | 5.0 | ~5 minutes (reopening closed payroll period) |
| Standard Edit/Delete on Punch, Pay Code Edit, or MJT | 1.0 | ~1 minute |
| All other actions (governance, approvals, reviews, adds) | 0.5 | ~30 seconds |

### 5.3 High-Risk Rework (Comment Required)

Actions classified as High-Risk Rework require a comment for compliance. The set includes:
- All Historical Corrections (any paycode)
- All Punch Add/Edit/Delete actions
- Pay Code Edits for PTO, Sick, Regular, or Overtime paycodes

### 5.4 Spike Detection: 13-Week Upper Control Limit

The primary statistical flagging method computes a 1 standard deviation control limit from the trailing 13-week window:

```
UCL = MEAN_13WK_DEFECT_RATE + SD_13WK_DEFECT_RATE
```

If the current week's defect rate exceeds the UCL, the entity (site, BU, or network) is flagged as a spike (`IS_RED_SPIKE = TRUE`).

Baseline data is sourced from `V_HWL_WEEKLY_SITE_METRICS`. For BU and network rollups, the agent approximates the combined standard deviation by averaging site-level SDs (acknowledged simplification documented in the Technical Design Doc).

### 5.5 Traffic Light Thresholds

| Metric | Green | Yellow | Red |
|:---|:---|:---|:---|
| Defect Rate % | <= 25% | 26 to 40% | > 40% |
| Missing Punch Rate % | <= 5% | 6 to 10% | > 10% |
| Hist. Correction Rate % | <= 5% | 6 to 10% | > 10% |
| Comment Compliance Rate % | >= 85% | 70 to 84% | < 70% |
| Site DPMO | TBD after baseline calibration at ×1M scale | TBD | TBD |

Note: DPMO traffic light thresholds are pending recalibration. The formula has been standardized to per-million (×1,000,000) to align with the Six Sigma DPMO definition. Previous thresholds (Green <= 20, Yellow 21-50, Red > 50) were calibrated for a per-thousand (×1,000) scale and no longer apply. Thresholds will be set after 4 weeks of baseline data collection at the new scale.

---

## 6. OBR Report Structure

The OBR is generated every Monday at 06:00 ET for the prior Sunday through Saturday reporting window.

### 6.1 Table of Contents

1. Executive Summary & KPIs
2. Enterprise Performance & Root Cause Analysis
3. Recommended Actions & Path to Green
4. Historical Corrections (Retro-Pay Risk)
5. Hotspots & High-Friction Drivers
6. Event Documentation (Comment Usage)

Appendix A: Governance Activity by Actor Group
Appendix B: Glossary of Metric Definitions

### 6.2 Section Descriptions

**Section 1: Executive Summary & KPIs**
Network-level KPI dashboard with traffic lights. Includes a 3 to 5 sentence narrative written at VP-level tone covering total touches, defect rate in plain language, actor group work distribution shifts, and top 2 highest-DPMO sites. Sources from Q1.

**Section 2: Enterprise Performance & Root Cause Analysis**
Multi-table section breaking down workload by BU × Actor Group (2.1), BU KPI split with spike flags (2.2), and Top 5 rework drivers by BU (2.3 through 2.7 for FC, Rx, CC, CVC, and HRSS respectively). Each driver table includes an AI Insight with trigger-based interpretation. Sources from Q2, Q3, Q4.

**Section 3: Recommended Actions & Path to Green**
Trigger-based recommendations that only appear when quantitative thresholds are breached. Four possible recommendations covering spike site coaching, elevated missing punch rate, historical correction reduction, and documentation compliance improvement.

**Section 4: Historical Corrections (Retro-Pay Risk)**
Root cause breakdown of Historical Corrections by HC Category with interpretive descriptions. Sources from Q5.

**Section 5: Hotspots & High-Friction Drivers**
Two sub-sections: Statistical Outlier Engagements (sites exceeding 1 SD above network mean for missed punches per 100 TMs) and Highest Burden Sites (Top 5 ranked by DPMO). Sources from Q6.

**Section 6: Event Documentation (Comment Usage)**
Comment compliance rate on High-Risk Rework actions by BU with diagnostic interpretation. Sources from Q7.

### 6.3 Missed Punch Engagement List

Q8 generates the Missed Punch Engagement Opportunities list with columns: BU, Site, TM Name, TM ID, Manager, Missed Count, Logs. This list is PII-sensitive and is delivered separately from the main OBR, restricted to private/1:1 contexts only.

**First-Week TM Exemption (Unresolved):** TMs in their first week of employment should be exempt from the engagement list. New hires frequently do not receive their badge until the middle of Day 1, causing missed punch exceptions that are not behavioral. This requires a hire date field from `V_PEOPLE` to be added to Q8 with a filter excluding TMs where `ENTITY_EVENT_DATE - HIRE_DATE < 7 days`. The hire date column availability in `V_PEOPLE` needs to be confirmed with the data engineering team.

---

## 7. Week-Over-Week Measurement

### 7.1 Target State (Production Views)

The WoW delta framework should be computed in production Snowflake views so the agent reads pre-calculated deltas rather than computing them. The `V_HWL_*` views will store:

- This Week value
- Prior Week value
- WoW Delta (absolute)
- WoW Delta % (percentage change)
- 4-Week Rolling Average
- vs. 13-Week Baseline (current week vs mean)

The agent's role is to read these columns and provide narrative interpretation, not to perform the arithmetic.

### 7.2 Current State (POC)

The current agent SQL computes only current-week values and compares them to the 13-week UCL for spike detection. Full WoW delta comparison is not yet implemented. The agent approximates WoW context by referencing spike flags and baseline deviations in its narrative.

---

## 8. Missed Punch Engagement Thresholds

| Flag | Rule | Severity |
|:---|:---|:---|
| Single-Shift Spike | TM has 2+ distinct missed punch events within a single day | Medium |
| Weekly Pattern | TM has 3+ distinct missed punch events within the reporting week | High |

Filters: Employee must be Active status. First-week TMs should be exempt (pending hire date field implementation).

---

## 9. Site and Network Groupings

### 9.1 OBR Site Groups

| OBR Site Group | Sites | Count |
|:---|:---|:---|
| FC | AVP1, AVP2, BNA1 (2G), CFC1, CLT1, DAY1, DFW1, HOU1, MCI1, MCO1, MDT1, PHX1, RNO1 | 13 |
| Rx | AVP4, AVP5, AVP6, DFW5, DFW8, MCO4, MCO5, PHX2, PHX5, SDF2, SDF4, SDF5, SDF6 | 13 |
| CVC | ATLA, ATLB, ATLC, ATLD, AUSA, DENA, DENB, DEND, DFWA, DFWB, FLLA, FLLB, FLLC, FLLD, FLLF, IAHA, IAHD, PHXB | 18 |
| CC | AV4V, DF4V, DFW4, FL3V, PH0V, PW0V, SD2V | 7 |
| **Total Network** | | **51** |

### 9.2 Excluded Sites

BOS1, FLL7, SEA1, MSP2 — corporate offices. Excluded via `WHERE OBR_SITE_GROUP IS NOT NULL`.

### 9.3 Rx Presentation Groupings

Some Rx sites are displayed as grouped locations in the OBR for readability. This is a presentation-layer grouping only. All KPIs are computed at the individual site level in Snowflake; the agent formats grouped labels when rendering Rx sections.

| Group Label | Sites |
|:---|:---|
| PHX2/5 | PHX2, PHX5 |
| MCO4/5 | MCO4, MCO5 |
| SDF4/5/6 | SDF4, SDF5, SDF6 |
| AVP4/5/6 | AVP4, AVP5, AVP6 |
| DFW5/8 | DFW5, DFW8 |
| SDF2 | SDF2 (standalone) |

---

## 10. Data Architecture

### 10.1 Source Tables (Phase I)

| Table | Purpose |
|:---|:---|
| `EDLDB.PEOPLE_ANALYTICS_SANDBOX.UKG_V_TIMECARD_AUDIT` | Core audit trail: who touched which timecard, when, what they did |
| `EDLDB.UKG.V_PEOPLE` | Employee and revision user profile data |
| `EDLDB.UKG.V_TIMECARD_EXCEPTION` | Missed punch exception events |
| `EDLDB.PEOPLE_ANALYTICS_SANDBOX.V_HWL_WEEKLY_SITE_METRICS` | Pre-materialized 13-week baseline at site-week grain (only production view) |

### 10.2 Target State: V_HWL_* View Architecture

Eight Snowflake views will replace inline CTEs when the product moves to production. These views codify the same logic currently in the agent's SQL into durable, governed data objects and add WoW delta computation so the agent reasons rather than computes.

| View | Grain | Purpose |
|:---|:---|:---|
| `V_HWL_ACTOR_GROUP_WEEK` | Actor Group × Site × Week | Ownership split with WoW deltas |
| `V_HWL_WORK_TYPE_MIX_WEEK` | Work Type × Actor Group × Site × Week | Work type distribution by actor |
| `V_HWL_DEFECT_REWORK_WEEK` | Site × Week | Bucket B / rework KPIs with WoW |
| `V_HWL_SCHEDULE_TOUCH_WEEK` | Site × Week | Schedule-specific KPIs (Bucket D, Phase I: not implemented) |
| `V_HWL_USER_BASELINE_WEEK` | User × Site × Week | Per-user actions, hours, top work types |
| `V_HWL_TM_MISSED_PUNCH_WEEK` | Employee × Site × Week | Engagement flag inputs |
| `V_HWL_SITE_SUMMARY_WEEK` | Site × Week | All KPIs at site grain with WoW |
| `V_HWL_NETWORK_SUMMARY_WEEK` | Network × Week | Network-level rollup |

Currently only `V_HWL_WEEKLY_SITE_METRICS` is materialized.

### 10.3 Deduplication Rules

**Audit Row Deduplication:** Daily incremental loads create duplicate events. Key = `(AUDIT_ID, AUDIT_REVISION_ID)`. Keep earliest load (`ORDER BY LOAD_DTTM ASC`, keep `rn = 1`).

**People Record Deduplication:** `V_PEOPLE` contains multiple records per person. Key = `PERSON_NUMBER`. Keep highest `PERSON_ID` (most recent record).

**Missed Punch Deduplication:** Within the audit pipeline (Q1 through Q7), daily counts use `COUNT(DISTINCT SHIFT_ID)` per `(PERSON_ID, DATE(EVENT_DATE))`. Q8 runs standalone against `V_TIMECARD_EXCEPTION` with the same grain.

### 10.4 Exclusion Filters

| Filter | Applied At | Rationale |
|:---|:---|:---|
| Self-service exclusion (`EDIT_TARGET != 'Self'`) | `hr` CTE | TMs clocking themselves in/out are normal operations, not HR workload |
| Automation exclusion (`Super Access No Wages`) | `hr` CTE (via `OBR_ACTOR_GROUP` filter) | Automated system processes skew volume and defect metrics |
| Corporate site exclusion (`OBR_SITE_GROUP IS NOT NULL`) | `hr` CTE | Corp sites (BOS1, FLL7, SEA1, MSP2) not in scope |
| Non-HR actor exclusion | `hr` CTE (via `OBR_ACTOR_GROUP NOT IN ('Team Member', 'Other', 'Automation', 'WFM')`) | Team Member self-service, unmapped profiles, automation traffic, and Workforce Management work are excluded from HR KPIs |
| Comment-type entity exclusion | `base` CTE WHERE clause | Documentation rows excluded from action counts; text linked back via CTE |

---

## 11. Interactive Drill-Down

After the weekly OBR is generated, users can ask follow-up questions at 5 levels of depth. Responses are capped at Top 5 unless the user requests more.

| Level | Trigger Phrases | Response |
|:---|:---|:---|
| L2: Business Unit | "break down FC", "show me Rx" | BU-filtered KPI snapshot with Top 5 transaction types + spike flag |
| L3: Site | "show me DFW5", "which sites spiked" | Site-filtered defect rate, 13W UCL, spike status, top 5 drivers |
| L4a: People | "who is driving rework at DFW5" | Top 5 revision users by action count at that site |
| L4b: TMs | "who has the most missed punches" | Top 5 TMs by missed punch count |
| L5: Root Cause | "what's causing the spike" | Top 5 PAYCODE_CATEGORY breakdown with narrative interpretation |

Drill-down guardrails: PII (TM names) restricted to private/1:1 contexts only. No speculation when data cannot explain a spike. Redirect to site HR lead when data is insufficient.

---

## 12. Success Metrics

| Metric | Target | Measurement |
|:---|:---|:---|
| Report Generation Reliability | 100% Monday delivery | Automated Monday 06:00 ET trigger with error halting |
| Defect Rate Reduction | 10% reduction in network defect rate within 12 weeks of launch | Baseline from first 4 weeks, measured via `V_HWL_WEEKLY_SITE_METRICS` |
| Comment Compliance | 85% compliance rate on High-Risk Rework | Measured by Q7 output |
| Stakeholder Adoption | 80% of site HR leads engage with the OBR weekly | Tracked via Confluence page views / email opens |
| Historical Correction Reduction | 15% reduction in HC rate within 12 weeks | Baseline from first 4 weeks |

---

## 13. Non-Goals (Phase I)

- Ticket integration (ServiceNow) — Phase II
- Service Tier / Misrouting classification — Phase II
- Schedule Touch tracking (Bucket D) — deferred to production
- Chronic missed punch flags (multi-week escalation) — abandoned
- User-level baselines (per-user actions/hours) — deferred to production views
- Real-time alerting or intra-week notifications

---

## 14. Glossary

| Term | Definition |
|:---|:---|
| OBR | Operational Business Review. The weekly report generated by the Workload Lens agent. |
| Bucket B | Correction/Rework classification. All Bucket B actions are defects. |
| DPMO | Defects Per Million Opportunities. `(Bucket B defects / (Unique TMs × 20)) × 1,000,000`. |
| UCL | Upper Control Limit. `Mean + 1 SD` over the trailing 13-week window. |
| Friction Score | Complexity weight per action (5.0, 1.0, or 0.5). |
| FTE Hours | Friction Time Cost. `SUM(Friction Score) / 60`. |
| High-Risk Rework | Actions requiring comment documentation: Historical Corrections, Punch Add/Edit/Delete, PTO/Sick/Regular/OT Pay Code Edits. |
| Phoenix | Chewy's internal LLM platform that hosts the Workload Lens agent. |

---

## 15. Version History

| Version | Date | Changes |
|:---|:---|:---|
| 1.0 | 2026-02-15 | Initial PRD |
| 2.0 | 2026-03-03 | Full rework. WBR→OBR terminology. DPMO standardized to per-million. Actor Group updates (Workers Comp → Local HR, Super Access No Wages → automation exclusion, Other excluded from customer output, COE eliminated). Chronic missed punch flag abandoned. Service Tier/Misrouting deferred to Phase II. WoW deltas targeted to production views. Rx groupings confirmed as presentation-only. BNA1 confirmed as 2G FC. First-week TM exemption for missed punch engagement documented as unresolved. |
