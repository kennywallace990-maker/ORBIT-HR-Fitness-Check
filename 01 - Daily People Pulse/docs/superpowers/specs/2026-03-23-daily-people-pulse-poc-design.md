# Daily People Pulse - POC Design Spec

**Date:** 2026-03-23
**Status:** In Review
**Author:** Claude Code (from user direction)

---

## Overview

A redesigned proof-of-concept (POC) for the Daily People Pulse product, a daily operational report delivered to HR Partners at each Chewy Fulfillment Center. The report surfaces attendance patterns, timecard exceptions, time-off coverage gaps, and overtime risk. Data is sourced from the UKG API (not Snowflake directly, due to deleted row persistence and data freshness issues). Output is a polished HTML file rendered to PDF via Phoenix (Chrome headless).

**Primary users:** HR Partners (HRAs and TMDMs)
**Legal Disclaimer:** ORBIT is intended as a tool to support HR. As a reminder, HR team members remain accountable for decisions and actions taken and should consult applicable SOPs as appropriate.

**Delivery:** HTML → PDF via Phoenix
**Report frequency:** Daily, automated

---

## Requirements (from POC draft review comments)

### Report Mode Logic

- **Tuesday–Saturday:** Week-to-Date (WTD = Sunday through prior day) + Prior Day detail
- **Sunday–Monday:** Prior Week + Prior Day only (no WTD language)

**"Prior Week" definition:** The full calendar week immediately preceding the current one (Sunday 00:00 through Saturday 23:59). On Sunday, "Prior Day" is Saturday (the final day of the prior week). Saturday therefore appears in both the Prior Week aggregate and the Prior Day detail card. This is intentional: the aggregate gives the full-week picture; the Prior Day card provides shift-level granularity for the most recent day.

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
- Subtitle line: "An ORBIT Product · [Site] · [Date] · [Report Mode] Report"
- Hero description (approved copy): "This report surfaces the signals that need attention and gives you a clear view of what's happening across your site today. Every insight is prioritized, every action is surfaced. Powered by ORBIT, Chewy's AI-powered HR operating layer, Daily People Pulse connects the dots automatically so you can focus on what matters most: your people."
- Summary stats: Location, Departments, Report Mode, NCNS count, OT Critical count
- Data window label (e.g., "WTD: Sunday, March 15 – Tuesday, March 18 | Prior Day: Tuesday, March 18"). Always spell out full day names and use consistent date format throughout.
- **No report-generation timestamp** - this is internal metadata that does not help the HR Partner (KW3)

### How to Read This Report

- Explains day-of-week reporting logic (WTD vs. Prior Week), including the Prior Week definition
- Clarifies UKG vs. PUMA
- Always renders above the fold before any data
- Do not list departments here; the report sections themselves make coverage obvious

### Section 01 - Attendance Summary

**Threshold:** 85% benchmark. Applied to:

- WTD attendance per shift (Day and Night evaluated separately)
- Prior Day attendance per shift
- Threshold applies uniformly across all departments for this POC; site-specific thresholds are out of scope

**Visual treatment:** Attendance percentages are rendered bold black. No color coding (green/amber/red) is applied; the Insight and the numbers themselves communicate what needs attention.

**Per-department subsections, each with a single combined card containing:**

- WTD section: Day % (and Night % if applicable) with worked/scheduled fraction (e.g., "744:30 of 904:30 hrs worked/sched")
- Prior Day section: Day % (and Night % if applicable) with worked/scheduled fraction + hours-lost bullet list (Early Departures, Full Missed Shifts, Late Arrivals, each with total hours in HH:MM format)
- If a department does not have a Night shift, simply omit the Night row. Do not display a "Night shift not active" note or a "Day shift only" label.
- Insight narrative (see Insight Rules below)

**Format:** Hours worked ÷ hours scheduled, expressed as both % and HH:MM fraction (e.g., "78.2% - 312:00 of 399:00 hrs worked/sched")

### Section 02 - No Call No Show (NCNS)

- Only shows TMs with a confirmed NCNS paycode in UKG. Pre-approved PTO, UTO, or any other approved leave code excludes a TM from this section
- EID column required for HRA timecard lookup in UKG
- Columns: EID, TM Name, Department, Schedule Group, Reports To, Date, Insight
- **Sort order:** Primary: TM Name (A–Z). Secondary: Date (most recent first). Rationale: alphabetical grouping clusters all absences for the same TM together, making it easy to identify repeat patterns by scanning down the list. TMs with multiple rows will appear as consecutive rows in name-sorted order.
- **Scope:** WTD (Tue–Sat) or Prior Week (Sun–Mon), stated in section description
- No "Worked Hours" column (confirmed NCNS = 0 hours worked by definition per UKG paycode)
- No "Scheduled Hours" column (noise; TMs are assessed by NCNS count, not scheduled volume)
- No risk rating column

**TMDM Workflow (rendered once in the section description):**

"TMDM Workflow: Validate NCNS on timesheet → Initiate NCNS Comm (Day 1 / Day 2 / Day 3) → Send Term Review Ticket to Site HR within 36 hours of Day 3 comm. Site HR: Respond to each Term Review Ticket with a termination decision or documented feedback."

This workflow text appears once in the section description so the reader understands the full NCNS escalation path. "Day 1 / Day 2 / Day 3" in this workflow refers to the TM's consecutive NCNS instance count (see calculation below), not calendar days.

**Per-row Insight column:** Each row displays the TM's consecutive NCNS instance number and the corresponding workflow step. The text is static per instance count (not AI-generated):

- Instance 1: "NCNS Instance 1 — Validate timesheet; initiate NCNS Comm Day 1"
- Instance 2: "NCNS Instance 2 — Initiate NCNS Comm Day 2; monitor for Day 3 threshold"
- Instance 3+: "NCNS Instance [N] — Day 3+ threshold reached; Term Review Ticket to Site HR within 36 hrs"

**Consecutive NCNS instance calculation:** The pipeline identifies TMs with an NCNS paycode within the report's evaluation window, then looks back through the Prior Week to count additional consecutive NCNS occurrences beyond the current window. This lookback ensures the report reflects the TM's true consecutive NCNS count — a TM may show "Instance 4" even if only 2 NCNS days fall within the current report window, because the pipeline detected 2 earlier consecutive NCNS days in the Prior Week. Gaps (days with approved leave or worked shifts) reset the consecutive count.

### Section 03 - Unscheduled but Worked

- Threshold: 10 or more minutes worked beyond scheduled hours (changed from 6 minutes)
- **Scope: Prior Day only.** Rationale: this section is designed for same-day intervention. A TM who worked unscheduled hours earlier in the WTD window and whose timecard has not been corrected will appear in Section 04 (Paycode Reconciler), which has WTD scope. The two sections have complementary but non-overlapping intent.
- EID column required
- Columns: EID, TM Name, Department, Schedule Group, Reports To, Scheduled, Worked, Over
- Date column omitted (scope is always prior day; stated in section description)
- Observation column omitted
- Red Flag column omitted
- Standard insight for all entries (static text, not AI-generated): "Local HR to review timecard → confirm VET/approval or adjust schedule; document per SOP"

### Section 04 - Paycode Reconciler

- Identifies paycodes that exceed or undershoot scheduled hours
- EID column required
- Columns: EID, TM Name, Department, Schedule Group, Reports To, Date, Scheduled, Applied, Paycodes, Insight
- Column headers use plain labels (no "(HH:MM)" suffix)
- Sorted by TM Name (A–Z), then Date (most recent first)
- Scope: WTD (Tue–Sat) or Prior Week (Sun–Mon), stated in section description
- Insights are static text per mismatch type: over-applied vs. under-applied

### Section 05 - Upcoming Time Off

- Scope: Next 7 calendar days from report date
- Per-department subsections
- **Sort order: Date ascending (earliest first), then TM Name (A-Z) within the same date.** Rationale: HR Partners use this section to labor plan day by day. Showing the most imminent date first, with all TMs for that date grouped together, is the correct read order for coverage planning.
- Columns: EID, TM Name, Reports To, Date, Paycode, Total
- Column headers use plain labels (no "(HH:MM)" suffix)
- **One row per TM per date** - never combine multiple dates into a single row, and never list multiple dates in a single cell. If a TM has time off on two different days, that is two separate rows. (KW27)
- "Planned Time Off Impact by Day" aggregate table removed
- Insight per department (see Insight Rules below)
- Each department clearly labeled with dept name and code where assigned

### Section 06 - 60+ Hour Watch

- EID column required
- **Risk level precedence rule:** CRITICAL takes precedence. If a TM meets the CRITICAL condition, they are assigned CRITICAL and the WATCH condition is not evaluated. WATCH is only assigned when the CRITICAL condition is not met.
  - 🔴 CRITICAL: WTD hours worked ≥ 60
  - 🟡 WATCH: CRITICAL not met, AND (WTD hours worked ≥ 58 OR (WTD worked + remaining scheduled) > 60)
- Columns: EID, TM Name, Department, Schedule Group, Reports To, WTD Worked, Remaining Scheduled, Projected Total, Risk, Insight
- Insights:
  - CRITICAL: "Immediate manager intervention. Adjust remaining schedule to prevent/address exceedance; review and document business justification per SOP"
  - WATCH: "Monitor closely; do not approve additional OT; review upcoming schedule and cap remaining hours below 60"

### Summary of HR Findings

- Table: Category | Finding | Insight
- Categories: Attendance, NCNS, Unscheduled Work, Paycode Errors, Time Off Coverage, Overtime Risk
- One row per category; findings are narrative summaries (e.g., counts, notable TM names)

### Site Narrative: Where We Stand and What's Ahead

- Appears after the Summary of HR Findings table, before the footer
- Two subsections: "Week to Date" (backward-looking) and "Looking Ahead" (forward-looking)
- Purpose: gives the HR manager a ready-made answer if asked "how is your site doing this week and what should we expect?"
- Generated by the AI agent, not static text. Synthesizes all report data into a cohesive overview.
- Tone: observational, factual. Same guardrails as department-level Insights (no benchmark judgments, no prescriptive actions). States what has happened and what is coming; lets HR decide how to frame it.
- WTD paragraph covers: attendance trends across departments, NCNS volume, unscheduled work, paycode issues, overtime risk
- Looking Ahead paragraph covers: planned absences, coverage concentrations, any converging signals (e.g., NCNS + planned leave)

---

## Insight Rules

Insights appear in Section 01 (Attendance) and Section 05 (Upcoming Time Off). They are generated by an AI agent in the Phoenix pipeline at report generation time and are not cached between runs. The label rendered in the report is simply "Insight" (not "AI Insight").

**What Insights MUST do:**

- Use plain, conversational speech. Write as if briefing an HR Partner in person (KW11)
- Synthesize trends across the data already shown in the section (not re-report raw numbers)
- Identify patterns (e.g., multi-day repeat absences, shift-level differences, cross-dept comparisons)
- Surface coverage risks and flag when multiple signals converge (e.g., NCNS + planned leave in same department)
- Reference other report sections when relevant (e.g., "see Section 02" for NCNS follow-up) rather than duplicating recommendations
- Keep tone observational. State what the data shows and let HR decide next steps

**What Insights MUST NOT do:**

- Re-state or parrot numbers already shown in the table or metric cards above. The data is right there; the Insight adds value only by synthesizing across it (KW11: "It should NOT be reporting the numbers. We just did that above. So be smart here.")
- Assume a benchmark or judge what is "good" or "bad." Weekly attendance plans vary by site and week; the report does not have that context. State the numbers and patterns, do not evaluate them against a threshold. (KW28)
- Direct Operations Managers to handle NCNS follow-up. NCNS follow-up is an HR responsibility and is already addressed in Section 02 with insights. (KW28)
- Be overly prescriptive about what actions to take. The insight should surface what is notable; HR decides how to act.
- Make disciplinary recommendations (termination decisions belong to the TMDM workflow, not the Insight)
- Reference an employee by name in a negative context beyond what the data directly states
- Use language that could create legal exposure (e.g., speculating about medical conditions, disability, or protected characteristics)
- Generate content when insufficient data exists. Fallback string: *"Insufficient data to generate an insight for this department this period."*

**Human review:** For the initial POC and pilot phases, insights should be reviewed by the owning HR team lead before the PDF is distributed. Automated distribution without review is out of scope until a review process is established.

---

## Display Format Standards

These standards apply to every date, time, and duration rendered in the report. Consistency is critical. HR Partners are the primary readers and the formats must be immediately legible without interpretation. (Ref: KW2, KW8)

- **Dates:** Spell out the month abbreviation, e.g., "Mar 1, 2026" not "03/01/2026". Use the same format in tables, metric cards, and narrative text.
- **Time durations (hours + minutes):** Use the pattern `Xhr Ymin`, e.g., "10 hrs 30 min", "0 hrs 30 min", "1 hr 15 min". Never use bare `HH:MM` with an "h" suffix (e.g., ~~00:30h~~) as this confuses non-technical readers.
- **Worked / Scheduled fractions:** The pattern `HH:MM of HH:MM hrs worked/sched` is acceptable inside metric cards because the label makes the meaning explicit. In standalone table cells, use the `Xhr Ymin` pattern.
- **Column headers:** Plain labels only. No "(HH:MM)" suffixes (already noted per-section; restated here for emphasis).
- **Singular vs. plural grammar (KW9):** All generated text must use correct singular/plural forms, e.g., "1 Early Departure" not "1 Early Departures"; "3 full missed shifts" not "3 full missed shift". This applies to generated narratives, bullet lists, and summary rows.

---

## Reader-Facing Section Descriptions

Every section rendered in the final HTML/PDF report must open with a **brief, plain-language description** of what the section shows and how to use it. This was requested across multiple review comments (KW1, KW4, KW12R2, KW20R4, KW24, KW30). Descriptions must:

- Be written for HR Partners, not engineers
- State the scope (WTD, Prior Week, Prior Day, or next 7 days) and what drives inclusion in the section
- Appear directly under the section heading, before any data tables or metric cards
- Be static text (not AI-generated)
- Do NOT use a "What this is:" label or similar preamble. Lead directly with the content in plain language (e.g., "Team Members below have exceeded..." or "Employees listed below were scheduled to work..."). (KW29)

The "How to Read This Report" section at the top of the report serves as the master guide; per-section descriptions reinforce context locally so the reader does not have to scroll back.

---

## Visual Design

- **Style:** Chewy masterbrand colors - Chewy Blue (#1C49C2), Royal Blue (#001A70), Sky Blue (#DFEAFF), White (#FFFFFF). See `99 - Program Docs/brand/` for full guidelines.
- **Font:** Gordita (brand typeface) with Roboto (internal fallback) and system-ui fallback for PDF render environments without internet access
- **Hero:** Chewy Blue gradient header with summary stats
- **Tables:** Royal Blue headers (`#001A70`), alternating row backgrounds
- **Insight boxes:** Amber (`#E65100`) left-border callout boxes
- **Attendance percentages:** Bold black text, no color coding. The AI Insight and the numbers themselves communicate what needs attention. (KW28)
- **Risk badges:** Red (CRITICAL), Yellow (WATCH) inline badges in Section 06
- **Print CSS:** `@media print` with `print-color-adjust: exact`, `break-before: page` per section, `break-inside: avoid` on tables and metric cards
- **No JavaScript dependencies** - all layout is CSS-only for reliable Chrome headless PDF render

---

## Technical Architecture

- **Output:** Single self-contained HTML file per site per day
- **Render path:** HTML template + data → Phoenix pipeline → Chrome headless → PDF delivery
- **Data source:** UKG API → Phoenix pipeline → HTML report generation
- **Not Snowflake direct:** Avoids deleted row persistence and data freshness issues inherent in the current Snowflake feed
- **Insights:** Generated by an AI agent (prompt-driven) as part of the Phoenix pipeline; not hardcoded
- **Error handling (to be defined in data contract):** If UKG API returns partial or no data for a section, that section should render with an explicit "Data unavailable for this period. Check UKG directly" message rather than silently omitting the section. Specific endpoint names, call cadence, and retry behavior are documented in the Data Contract (separate document, TBD).

---

## Open Questions (for product owner resolution)

1. Do Vet Services Tech I and Tech II have assigned department codes in UKG? If so, what are they?
2. Should the 85% attendance threshold vary by department (e.g., a different threshold for Pharmacy vs. Outbound)?
3. Should Section 05 show only HR-Partner-visible TMs, or all TMs scheduled at the site?
4. What is the expected UKG API refresh cadence, and what is the acceptable data staleness window before a warning banner appears in the report?
5. Who is the designated reviewer for insights during the pilot phase?

---

## Out of Scope (this POC)

- Interactive filtering or drill-down
- Multi-site comparison
- Historical trend charts
- Email delivery formatting
- Site-specific attendance threshold configuration
