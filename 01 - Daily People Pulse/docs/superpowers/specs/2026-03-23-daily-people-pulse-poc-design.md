# Daily People Pulse — POC Design Spec

**Date:** 2026-03-23
**Status:** In Review
**Author:** Claude Code (from user direction)

---

## Overview

A redesigned proof-of-concept (POC) for the Daily People Pulse product — a daily operational report delivered to HR Partners at each Chewy Fulfillment Center. The report surfaces attendance patterns, timecard exceptions, time-off coverage gaps, and overtime risk. Data is sourced from the UKG API (not Snowflake directly, due to deleted row persistence and data freshness issues). Output is a polished HTML file rendered to PDF via Phoenix (Chrome headless).

**Primary users:** HR Partners (HRAs and TMDMs)
**Delivery:** HTML → PDF via Phoenix
**Report frequency:** Daily, automated

---

## Requirements (from POC draft review comments)

### Report Mode Logic

- **Tuesday–Saturday:** Week-to-Date (WTD = Sunday through prior day) + Prior Day detail
- **Sunday–Monday:** Prior Week + Prior Day only (no WTD language)

**"Prior Week" definition:** The full calendar week immediately preceding the current one — Sunday 00:00 through Saturday 23:59. On Sunday, "Prior Day" is Saturday (the final day of the prior week). Saturday therefore appears in both the Prior Week aggregate and the Prior Day detail card. This is intentional: the aggregate gives the full-week picture; the Prior Day card provides shift-level granularity for the most recent day.

### Terminology Standards

- "Cohort" → "Department" throughout
- "Employee Full Name" → "TM Name" throughout
- "Schedule Group Name" → "Schedule Group" throughout
- "Scheduled but Not Worked" → "No Call No Show (NCNS)"
- "Unscheduled Work" → "Unscheduled but Worked"
- "Upcoming PTO and UTO by Person" → "Upcoming Time Off"

### Departments (varies by site)

- Outbound (2300)
- Inbound (2100)
- Replenishment (2200)
- Inventory Control (2400)
- Pharmacy (3300)
- Vet Services – Tech I (no dept code currently assigned; confirm with product owner)
- Vet Services – Tech II (no dept code currently assigned; confirm with product owner)

Not every site has all departments; the report should only show departments active at the site.

**Assumption:** "Worked hours" in the NCNS section are always 0 for confirmed NCNS records. If UKG ever records partial hours against an NCNS paycode, that record should be routed to the Paycode Reconciler (Section 04) instead, not shown in the NCNS section.

### Data Source Note

All hours are UKG hours, not PUMA. This must be surfaced clearly to readers in the "How to Read" section and in the hero metadata.

---

## Section-by-Section Design

### Hero / Header

- Product name: "Daily People Pulse"
- Site, date, report mode (WTD or Prior Week), data source (UKG API)
- Summary stats: Location, Departments, Report Mode, NCNS count, OT Critical count
- Report generation timestamp
- Data window label (e.g., "WTD: Sun 3/15 – Tue 3/18 | Prior Day: Tue 3/18")

### How to Read This Report

- Explains day-of-week reporting logic (WTD vs. Prior Week), including the Prior Week definition
- Lists departments covered at this site
- Clarifies UKG vs. PUMA
- Always renders above the fold before any data

### Section 01 — Attendance Summary

**Threshold:** 85% benchmark. Applied to:

- WTD attendance per shift (Day and Night evaluated separately)
- Prior Day attendance per shift
- Threshold applies uniformly across all departments for this POC; site-specific thresholds are out of scope

**Visual treatment for breached threshold:** Attendance percentage is rendered in amber (≥ 80% and < 85%) or red (< 80%). Green is used for ≥ 85%. The att-pct CSS classes (`good`, `warn`, `bad`) implement this.

**Per-department subsections, each with:**

- WTD card: Day % and Night % with worked/scheduled fraction (e.g., "744:30 of 904:30 hrs worked/sched")
- Prior Day card: Day % and Night % with worked/scheduled fraction + hours-lost bullet list (Early Departures, Full Missed Shifts, Late Arrivals, each with total hours in HH:MM format)
- Night-shift note if night shift is not active at this site for this department
- AI Insight narrative (see AI Insight Rules below)

**Format:** Hours worked ÷ hours scheduled, expressed as both % and HH:MM fraction (e.g., "78.2% — 312:00 of 399:00 hrs worked/sched")

### Section 02 — No Call No Show (NCNS)

- Only shows TMs with a confirmed NCNS paycode in UKG — pre-approved PTO, UTO, or any other approved leave code excludes a TM from this section
- EID column required for HRA timecard lookup in UKG
- Columns: EID, TM Name, Department, Schedule Group, Reports To, Date, Recommended Action
- **Sort order:** Primary: TM Name (A–Z). Secondary: Date (most recent first). Rationale: alphabetical grouping clusters all absences for the same TM together, making it easy to identify repeat patterns by scanning down the list. TMs with multiple rows will appear as consecutive rows in name-sorted order.
- **Scope:** WTD (Tue–Sat) or Prior Week (Sun–Mon), stated in section description
- No "Worked Hours" column (confirmed NCNS = 0 hours worked by definition per UKG paycode)
- No "Scheduled Hours" column (noise; TMs are assessed by NCNS count, not scheduled volume)
- No risk rating column

**TMDM Recommended Action — static text per NCNS day number (not AI-generated):**

- Day 1: "Validate NCNS on timesheet → Initiate NCNS Comm Day 1"
- Day 2: "NCNS Comm Day 2 sent → monitor for Day 3 threshold. If absent again, initiate Term Review Ticket within 36 hrs of Day 3 comm"
- Day 3+: "Day 3 threshold reached → Send Term Review Ticket to Site HR within 36 hrs of this comm"
- Site HR action (after Term Review Ticket): Respond with termination decision or documented feedback

**Day number calculation:** Consecutive calendar days with NCNS paycode within the current report scope window. Gaps (days with approved leave or worked shifts) reset the consecutive count.

### Section 03 — Unscheduled but Worked

- Threshold: 10 or more minutes worked beyond scheduled hours (changed from 6 minutes)
- **Scope: Prior Day only.** Rationale: this section is designed for same-day intervention. A TM who worked unscheduled hours earlier in the WTD window and whose timecard has not been corrected will appear in Section 04 (Paycode Reconciler), which has WTD scope. The two sections have complementary but non-overlapping intent.
- EID column required
- Columns: EID, TM Name, Department, Schedule Group, Reports To, Scheduled, Worked, Over
- Date column omitted (scope is always prior day; stated in section description)
- Observation column omitted
- Red Flag column omitted
- Standard recommendation for all entries (static text, not AI-generated): "Local HR to review timecard → confirm VET/approval or adjust schedule; document per SOP"

### Section 04 — Paycode Reconciler

- Identifies paycodes that exceed or undershoot scheduled hours
- EID column required
- Columns: EID, TM Name, Department, Schedule Group, Reports To, Date, Scheduled, Applied, Paycodes, Action
- Column headers use plain labels (no "(HH:MM)" suffix)
- Sorted by TM Name (A–Z), then Date (most recent first)
- Scope: WTD (Tue–Sat) or Prior Week (Sun–Mon), stated in section description
- Recommendations are static text per mismatch type: over-applied vs. under-applied

### Section 05 — Upcoming Time Off

- Scope: Next 7 calendar days from report date
- Per-department subsections
- **Sort order: Date ascending (earliest first).** Rationale: HR Partners use this section to labor plan. Showing the most imminent absences first is the correct read order for coverage planning.
- Columns: EID, TM Name, Reports To, Date(s), PTO, UTO, Total
- Column headers use plain labels (no "(HH:MM)" suffix)
- Multi-day blocks shown as comma-separated dates in a single row
- "Planned Time Off Impact by Day" aggregate table removed
- AI Insight per department (see AI Insight Rules below)
- Each department clearly labeled with dept name and code where assigned

### Section 06 — 60+ Hour Watch

- EID column required
- **Risk level precedence rule:** CRITICAL takes precedence. If a TM meets the CRITICAL condition, they are assigned CRITICAL and the WATCH condition is not evaluated. WATCH is only assigned when the CRITICAL condition is not met.
  - 🔴 CRITICAL: WTD hours worked ≥ 60
  - 🟡 WATCH: CRITICAL not met, AND (WTD hours worked ≥ 58 OR (WTD worked + remaining scheduled) > 60)
- Columns: EID, TM Name, Department, Schedule Group, Reports To, WTD Worked, Remaining Scheduled, Projected Total, Risk, Recommendation
- Recommendations:
  - CRITICAL: "Immediate manager intervention — adjust remaining schedule to prevent/address exceedance; review and document business justification per SOP"
  - WATCH: "Monitor closely; do not approve additional OT; review upcoming schedule and cap remaining hours below 60"

### Summary of HR Findings

- Table: Category | Finding | Recommended Action
- Categories: Attendance, NCNS, Unscheduled Work, Paycode Errors, Time Off Coverage, Overtime Risk
- One row per category; findings are narrative summaries (e.g., counts, notable TM names)

---

## AI Insight Rules

AI Insights appear in Section 01 (Attendance) and Section 05 (Upcoming Time Off). They are generated by an AI agent in the Phoenix pipeline at report generation time and are not cached between runs.

**What AI Insights MUST do:**

- Synthesize trends across the data already shown in the section (not re-report raw numbers)
- Identify patterns (e.g., multi-day repeat absences, shift-level differences, cross-dept comparisons)
- Surface coverage risks before they occur
- Recommend specific, actionable steps for the HR Partner (e.g., "Recommend Tweed review staffing before shift start")

**What AI Insights MUST NOT do:**

- Re-state numbers already shown in the table or metric cards above
- Make disciplinary recommendations (termination decisions belong to the TMDM workflow, not the Insight)
- Reference an employee by name in a negative context beyond what the data directly states
- Use language that could create legal exposure (e.g., speculating about medical conditions, disability, or protected characteristics)
- Generate content when insufficient data exists — fallback string: *"Insufficient data to generate an insight for this department this period."*

**Human review:** For the initial POC and pilot phases, AI-generated insights should be reviewed by the owning HR team lead before the PDF is distributed. Automated distribution without review is out of scope until a review process is established.

---

## Visual Design

- **Style:** Chewy brand colors — Blue (#0046BE), Dark Navy (#002E7D), matching VOC Pulse Report language
- **Font:** Inter (Google Fonts) with system-ui fallback for PDF render environments without internet access
- **Hero:** Blue gradient header with summary stats
- **Tables:** Dark navy headers (`#002E7D`), alternating row backgrounds
- **Insight boxes:** Amber (`#E65100`) left-border callout boxes
- **Attendance color coding:** Green ≥ 85%, Amber 80–84%, Red < 80%
- **Risk badges:** Red (CRITICAL), Yellow (WATCH) inline badges in Section 06
- **Print CSS:** `@media print` with `print-color-adjust: exact`, `break-before: page` per section, `break-inside: avoid` on tables and metric cards
- **No JavaScript dependencies** — all layout is CSS-only for reliable Chrome headless PDF render

---

## Technical Architecture

- **Output:** Single self-contained HTML file per site per day
- **Render path:** HTML template + data → Phoenix pipeline → Chrome headless → PDF delivery
- **Data source:** UKG API → Phoenix pipeline → HTML report generation
- **Not Snowflake direct:** Avoids deleted row persistence and data freshness issues inherent in the current Snowflake feed
- **AI Insights:** Generated by an AI agent (prompt-driven) as part of the Phoenix pipeline; not hardcoded
- **Error handling (to be defined in data contract):** If UKG API returns partial or no data for a section, that section should render with an explicit "Data unavailable for this period — check UKG directly" message rather than silently omitting the section. Specific endpoint names, call cadence, and retry behavior are documented in the Data Contract (separate document, TBD).

---

## Open Questions (for product owner resolution)

1. Do Vet Services Tech I and Tech II have assigned department codes in UKG? If so, what are they?
2. Should the 85% attendance threshold vary by department (e.g., a different threshold for Pharmacy vs. Outbound)?
3. Should Section 05 show only HR-Partner-visible TMs, or all TMs scheduled at the site?
4. What is the expected UKG API refresh cadence, and what is the acceptable data staleness window before a warning banner appears in the report?
5. Who is the designated reviewer for AI-generated insights during the pilot phase?

---

## Out of Scope (this POC)

- Interactive filtering or drill-down
- Multi-site comparison
- Historical trend charts
- Email delivery formatting
- Site-specific attendance threshold configuration
