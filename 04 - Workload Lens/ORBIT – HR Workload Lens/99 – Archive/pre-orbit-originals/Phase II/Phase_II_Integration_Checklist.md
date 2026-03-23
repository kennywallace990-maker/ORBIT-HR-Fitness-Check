# Phase II Integration Checklist — Snow Ticket Data into Workload Lens

**Date:** 2026-03-05  
**Author:** Kenny Wallace / ORBIT  
**Status:** Planning  

---

## Context

| Dimension | Phase I (Current) | Phase II (New) |
| --- | --- | --- |
| **Data Source** | UKG Pro / Snowflake (`UKG_V_TIMECARD_AUDIT`) | ServiceNow (Snow) HR Cases — CSV until Snowflake pipeline available |
| **Unit of Work** | Timecard action (touch) | HR ticket (case) |
| **Grain** | 1 row = 1 UKG audit event | 1 row = 1 Snow ticket |
| **Primary Metric** | Defect Rate, DPMO, Friction Hours | Ticket Volume, Resolution Time, Ticket Category |
| **Site Join Key** | `schedule_group_name` → site code | `Assignment Group` → site code (e.g., "CLT1 HR" → CLT1) |
| **Time Window** | Weekly (Sun–Sat) | Weekly (Sun–Sat), matched to Phase I window |
| **Scope** | FC, Rx, CC, CVC (51 sites) | FC only (19+ sites in Snow data), `Hr Service` = "FC General Inquiry" |

### Phase II Data Profile (Snow Ticket Data Week 9.csv)

- **Total rows:** 19,959 tickets (all `FC General Inquiry`)
- **Date range:** Nov 2024 – Feb 2026 (~15 months of history)
- **Week 9 (2/23–3/1/2026):** 365 tickets
- **Columns:** `Hr Service`, `Number`, `Description1`, `Opened At`, `U Resolved`, `Assignment Group`
- **Top sites (Week 9):** SDF2 (89), AVP2 (82), AVP4 (56), MCI1 (20), MCO1 (17), AVP1 (16), SDF 1/4/6 (16), BNA1 (15), RNO1 (14), CLT1 (13)
- **Avg resolution time (Week 9):** 18.9 hours
- **Centralized teams:** HR Team Member Service Center (9), LOA/ADA Team, Payroll Team, HR TMDM, etc.

---

## Unified Report Philosophy

> **Tickets are the primary measure of HR workload. UKG data explains:**
>
> 1. **What drove the tickets** — timekeeping defects that generate downstream case work
> 2. **Other work not captured in tickets** — governance, approvals, and rework that HR performs silently in UKG without a ticket ever being created

This means the report structure **inverts**: tickets become Section 1, and UKG becomes the explanatory/diagnostic layer underneath.

---

## Integration Checklist

### Step 1: Data Preparation (CSV → Structured)

- [ ] **1.1** Parse `Assignment Group` → extract `site_code` (regex: first token before " HR")
  - Handle multi-site groups: "SDF 1/4/6 HR" → SDF1, SDF4, SDF6 (or keep as compound)
  - Handle centralized teams: "HR Team Member Service Center", "LOA/ADA Team" → flag as `CENTRALIZED`
- [ ] **1.2** Parse `Opened At` / `U Resolved` → compute `resolution_hours`
- [ ] **1.3** Classify tickets by category using `Description1` text (NLP or keyword rules):
  - **Timekeeping / Pay** — missing hours, punch issues, PTO, pay discrepancies
  - **Leave / LOA** — FMLA, personal leave, accommodation, return-to-work
  - **Attendance / Discipline** — call-offs, NCNS, suspension, attendance points
  - **Benefits / Payroll** — benefits enrollment, payroll questions, W-2
  - **General Inquiry** — badge, access, transfer, personal info changes
  - **Noise** — spam emails, auto-created junk tickets (Spotify example in data)
- [ ] **1.4** Filter to reporting week window (Sun–Sat) matching Phase I
- [ ] **1.5** Map `site_code` to `Business Unit` (FC/Rx/CC/CVC) using existing site classification

### Step 2: Ticket KPIs (New Section 1 of Unified Report)

- [ ] **2.1** Define ticket KPIs:
  - **Ticket Volume** — total opened, by site, by category
  - **Resolution Rate** — % resolved within the week
  - **Avg/Median Resolution Time** — hours from open to resolved
  - **Backlog** — tickets opened but not resolved by week end
  - **Ticket-to-TM Ratio** — tickets per 100 team members (normalizer, like DPMO)
  - **Timekeeping-Related %** — share of tickets tied to pay/punch issues (connects to Phase I)
- [ ] **2.2** Build Week-over-Week trend table (ticket volume + resolution time)
- [ ] **2.3** Build site-level ticket volume table (maps to Phase I hotspot sites)

### Step 3: Cross-Phase Linkage (The "So What" Layer)

- [ ] **3.1** Create **Site Scorecard** joining Phase I and Phase II at site level:

  | Site | BU | Tickets | Ticket Rate | UKG Actions | Defect Rate | DPMO | Friction Hrs |
  | --- | --- | --- | --- | --- | --- | --- | --- |
  | CLT1 | FC | 13 | X per 100 TM | 5,056 | 58.4% | 197K | ... |
  | MCI1 | FC | 20 | X per 100 TM | 5,488 | 48.3% | 175K | ... |

- [ ] **3.2** Compute **Ticket Conversion Rate**: What % of UKG defects generate a Snow ticket?
  - Formula: `tickets / UKG_corrections` per site
  - High ratio = TMs are escalating; Low ratio = silent rework (HR absorbing without tickets)
- [ ] **3.3** Correlate timekeeping-category tickets with Phase I punch correction volume
- [ ] **3.4** Identify **"dark work"** — sites with high UKG rework but zero/low tickets (work not captured in Snow)

### Step 4: Unified Report Structure
- [ ] **4.1** Design new report template:

  ```
  ORBIT HR Workload Lens — Unified Organizational Business Review
  
  Phase I: UKG Timecard Audit | Phase II: ServiceNow HR Cases
  
  Section 1: Executive Summary (unified)
    - Total HR Workload = Tickets + UKG Actions
    - Top-line KPIs from both phases
    - Signal: Improving / Deteriorating / Stable
  
  Section 2: Ticket Workload (Phase II — PRIMARY)
    2.1 Network ticket volume, resolution time, backlog
    2.2 Ticket categories (what TMs are asking for help with)
    2.3 Site-level ticket table
    2.4 Centralized team workload (TMDM, LOA/ADA, Payroll)
  
  Section 3: Timekeeping Rework (Phase I — EXPLANATORY)
    3.1 UKG defect rate, DPMO, friction hours
    3.2 Root cause drivers (punch corrections, attendance, leave)
    3.3 Actor group workload (Local HR, HRSS, WFM, Local Ops)
  
  Section 4: Cross-Phase Analysis (THE BRIDGE)
    4.1 Site Scorecard (tickets + UKG side by side)
    4.2 Ticket Conversion Rate
    4.3 Dark Work analysis
    4.4 Timekeeping tickets vs. UKG punch correction correlation
  
  Section 5: Recommendations (unified, data-driven)
    - Triggered by BOTH ticket and UKG thresholds
  
  Section 6: Historical Corrections (retro-pay risk)
  Section 7: Hotspots (DPMO + ticket spikes)
  Section 8: Appendices (glossary, governance, methodology)
  ```

- [ ] **4.2** Define unified traffic-light thresholds for ticket metrics (TBD with stakeholders)

### Step 5: Technical Implementation
- [ ] **5.1** Build Python/pandas script to:
  - Load Snow CSV
  - Parse, classify, and filter tickets
  - Compute ticket KPIs
  - Join to Phase I UKG summary data at site level
  - Output unified report data
- [ ] **5.2** Create ticket classification logic (keyword-based v1, upgradeable to LLM later)
- [ ] **5.3** Build unified report markdown generator
- [ ] **5.4** Test with Week 9 data (both Phase I + Phase II)
- [ ] **5.5** Document Phase II data dictionary

### Step 6: Future State (Snowflake Integration)
- [ ] **6.1** When Snow data lands in Snowflake, replace CSV loader with SQL query
- [ ] **6.2** Create Snowflake view for tickets (like `V_HWL_BASE` for UKG)
- [ ] **6.3** Update Phoenix agent instructions with Phase II queries
- [ ] **6.4** Merge into single agent prompt (unified Phase I + II)

---

## Key Design Decisions to Make

| # | Decision | Options | Recommendation |
|---|---|---|---|
| 1 | How to classify tickets? | Keyword rules vs. LLM | Start with keywords (fast, transparent), upgrade to LLM later |
| 2 | Handle "SDF 1/4/6 HR" compound group? | Split to 3 sites vs. keep as-is | Keep as "SDF-Campus" — splitting without assignment data is guessing |
| 3 | Noise tickets (spam, junk)? | Include vs. exclude | Exclude — flag and count separately as "data quality" metric |
| 4 | Scope: FC only or all BUs? | FC-only (Snow data scope) vs. force all | FC-only for Phase II; Phase I continues to cover all BUs |
| 5 | Ticket-to-UKG join level? | Site + Week vs. Site + Week + Category | Start at Site + Week; category join requires ticket classification first |
| 6 | Historical data usage? | Use 15-month history for baselines | Yes — build 13-week trailing ticket baselines (mirrors Phase I UCL approach) |

---

## Immediate Next Steps

1. **Build ticket parser** — Python script to load CSV, extract site codes, compute resolution time, classify tickets
2. **Generate Week 9 ticket summary** — standalone Phase II report for Week 9
3. **Create unified Week 9 report** — merge Phase I (existing .md) + Phase II ticket summary into new unified format
4. **Review with stakeholders** — validate category taxonomy and unified report structure

---

*Phase II integration owned by ORBIT. CSV workflow is temporary — production will use Snowflake once Snow ticket pipeline is available.*
