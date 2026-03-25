# DPP POC – Changes Checklist for Mandy

**Date:** 2026-03-24
**Purpose:** This is the full list of design changes from the original Daily Pulse Report (KW1–KW30 comments) that need to be implemented in the pipeline. The HTML mock (`DPP_POC_Mock.html`) reflects the target state — use it as your visual reference.

Use this as a dev checklist. Check off each item as you implement it in the pipeline.

---

## HERO / HEADER

- [ ] Product name: **"Daily People Pulse"** (not "Daily Pulse Report")
- [ ] Subtitle line: `An ORBIT Product · [Site] · [Date] · [Report Mode] Report`
- [ ] Hero description: use the approved copy from the spec
- [ ] Legal disclaimer: `ORBIT is intended as a tool to support HR. As a reminder, HR team members remain accountable for decisions and actions taken and should consult applicable SOPs as appropriate.`
- [ ] Summary stats tiles (in this order): Location, Today's Date, NCNS, Unscheduled Work, Paycode Errors, 60+ Risk
- [ ] Data window label: `WTD: Sunday, March 15 – Tuesday, March 18 | Prior Day: Tuesday, March 18` — spell out full day names, consistent date format
- [ ] **No report-generation timestamp** — remove "Generated:" from the header (KW3). HR Partners don't need it.
- [ ] **No "Rows processed" count** — internal metadata, not useful to HR Partners. Remove entirely.
- [ ] Data source: `Data source: UKG API` (keep this line)
- [ ] **Data freshness timestamp:** `Data as of: [Weekday], [Mon DD, YYYY] at [H:MM AM/PM] ET` — rendered as a third span in the hero-meta row, same white subdued style. Pulled from the UKG API response timestamp.
- [ ] **Hero-meta text must be white** (`color: #fff`) — the hero is a dark blue gradient; the data window, data source, and freshness lines sit on top of it and must render in white

---

## HOW TO READ THIS REPORT

- [ ] Explain report mode logic: Tue–Sat = WTD (Sunday through prior day) + Prior Day. Sun–Mon = Prior Week + Prior Day only (no WTD language) (KW4, KW5)
- [ ] Clarify: **all hours are UKG hours, not PUMA** (KW4R3)
- [ ] This section always renders before any data sections
- [ ] Do NOT list departments here

---

## CHEWY BRAND COMPLIANCE

All Phoenix-rendered HTML output must use Chewy masterbrand colors and typography. Full guidelines are in `99 - Program Docs/brand/ORBIT_Brand_Compliance.md`.

- [ ] **Primary color:** Chewy Blue `#1C49C2` — use for links, primary buttons, section borders, chart fills, hero gradient
- [ ] **Dark color:** Royal Blue `#001A70` — use for table headers, headings, `--ink` text, gradient start
- [ ] **Light/background color:** Sky Blue `#DFEAFF` — use for badges, hover states, callout fills
- [ ] **Font stack:** `'Gordita', 'Roboto', system-ui, sans-serif` — Gordita is the brand typeface; Roboto is the approved internal fallback
- [ ] **No Inter, Georgia, Aptos, Segoe UI, or Calibri** — these are off-brand
- [ ] **No accent colors in CTAs or buttons** — use Chewy Blue or Royal Blue for all button/CTA elements
- [ ] **Never pair two accent colors** in the same layout
- [ ] **Sentence case everywhere** — headlines, CTAs, section titles. No all-caps for emphasis.
- [ ] **Rounded shapes** — use `border-radius: 10px` or higher on cards and containers; avoid sharp corners

---

## GLOBAL FORMATTING RULES (apply everywhere)

- [ ] **Date format:** Always spell out month abbreviation — `Mar 1, 2026` not `03/01/2026`. Use this in ALL tables, metric cards, and narrative text. (KW2)
- [ ] **Time durations:** Use `Xhr Ymin` pattern — e.g., `10 hrs 30 min`, `0 hrs 30 min`, `1 hr 15 min`. Never use bare `HH:MM` with an "h" suffix (e.g., ~~00:30h~~, ~~08:30 hrs~~). (KW8)
  - **Attendance fraction format:** Use `X hrs worked out of Y hrs scheduled` (e.g., `581 hrs worked out of 740 hrs scheduled`). When minutes are non-zero, include them: `744 hrs 30 min worked out of 904 hrs 30 min scheduled`. Drop `0 min` — never show `:00` or `0 min`.
- [ ] **Column headers:** Plain labels only. No `(HH:MM)` suffix anywhere. (KW28)
- [ ] **Terminology throughout every section:**
  - "Cohort" → **"Department"** (KW13)
  - "Employee Full Name" → **"TM Name"** (KW14)
  - "Schedule Group Name" → **"Schedule Group"** (KW15)
- [ ] **Grammar:** Use correct singular/plural — "1 Early Departure" not "1 Early Departures"; "3 full missed shifts" not "3 full missed shift" (KW9)
- [ ] **EID column** required in ALL sections (KW12R3)
- [ ] **EID zero-padding:** All Employee IDs must be 6 digits. If the EID from UKG is 5 digits, pad with a leading `0` (e.g., `12034` → `012034`). Apply this in the pipeline before rendering.
- [ ] **Omit inactive departments and shifts (BACKEND LOGIC):** If a site does not have a particular department (e.g., Pharmacy, Vet Services), omit that department's subsection entirely — do not render an empty section or a "no data" placeholder. Same for shifts: if a department has no Night shift, omit the Night row. The pipeline must check which departments and shifts have active data for the site and only render those.

---

## SECTION 01 – ATTENDANCE SUMMARY

- [ ] Section description under the heading (before data) — plain English, no "What this is:" preamble (KW4, KW29)
- [ ] **Departments to show:** Outbound (2300), Inbound (2100), Replenishment (2200), Inventory Control (2400), Pharmacy (3300), Vet Services – Tech I, Vet Services – Tech II. Only show departments active at the site. (KW4R2)
- [ ] **Day and Night shift evaluated separately** per department (KW4R2)
- [ ] If a department has no Night shift, **omit the Night row entirely** — no "Night shift not active" note (KW10)
- [ ] Per department: single combined card with WTD section (Day %, Night % if applicable, worked/sched fraction) + Prior Day section (same + Hours Lost breakdown)
- [ ] **Hours Lost breakdown** (Prior Day): Early Departures, Full Missed Shifts, Late Arrivals — each with total hours in `Xhr Ymin` format
- [ ] **85% benchmark** — threshold shown in "How to Read"; attendance percentages are **bold black** (no color coding)
- [ ] **Insight per department** — AI-generated. Must:
  - Use plain conversational speech (KW11)
  - **Synthesize** patterns — NOT re-state numbers already shown in the card above (KW11)
  - Reference other sections when relevant (e.g., "see Section 02" for NCNS)
  - State what the data shows; let HR decide next steps
  - Fallback if no data: `"Insufficient data to generate an insight for this department this period."`
- [ ] Insight label: **"Insight"** — not "AI Insight"

---

## SECTION 02 – NO CALL NO SHOW (NCNS)

- [ ] Section name: **"No Call No Show (NCNS)"** (not "Scheduled but Not Worked") (KW12)
- [ ] Section description under heading (KW12R2): brief plain-language explanation of what it is and how to use it
- [ ] **Only confirmed NCNS paycode instances** — TMs with pre-approved PTO, UTO, or any other approved leave code are excluded (KW12R4)
- [ ] **Columns:** EID, TM Name, Department, Schedule Group, Reports To, Date, Insight
- [ ] **Remove:** Worked Hours column (KW17), Scheduled Hours column, Red Flag column (KW18), Risk Rating column (KW18)
- [ ] **Sort:** TM Name A–Z, then Date most recent first (KW16)
- [ ] **Scope:** WTD (Tue–Sat) or Prior Week (Sun–Mon), stated in section description (KW12R5)
- [ ] **TMDM Workflow (rendered once in the section description, not per row):** `"TMDM Workflow: Validate NCNS on timesheet → Initiate NCNS Comm (Day 1 / Day 2 / Day 3) → Send Term Review Ticket to Site HR within 36 hours of Day 3 comm. Site HR: Respond to each Term Review Ticket with a termination decision or documented feedback."`
- [ ] **Consecutive NCNS instance calculation (BACKEND CHANGE):** The pipeline must identify TMs with an NCNS paycode within the evaluation window, then **look back through the Prior Week** to count additional consecutive NCNS occurrences beyond the current window. This ensures the report reflects the TM's true consecutive NCNS count — e.g., a TM may show "Instance 4" even if only 2 NCNS days fall within the current report window. Gaps (approved leave, worked shifts) reset the count.
- [ ] **Per-row Insight column — static text per instance count** (KW19):
  - Instance 1: `"NCNS Instance 1 — Validate timesheet; initiate NCNS Comm Day 1"`
  - Instance 2: `"NCNS Instance 2 — Initiate NCNS Comm Day 2; monitor for Day 3 threshold"`
  - Instance 3+: `"NCNS Instance [N] — Day 3+ threshold reached; Term Review Ticket to Site HR within 36 hrs"`

---

## SECTION 03 – UNSCHEDULED BUT WORKED

- [ ] Section name: **"Unscheduled but Worked"** (not "Unscheduled Work") (KW20)
- [ ] Section description under heading (KW20R4): states this covers Prior Day only; explains what drives inclusion
- [ ] **Threshold: 10+ minutes** worked beyond scheduled hours (changed from 6 minutes) (KW20R2). **⚠️ BACKEND CHANGE REQUIRED:** Update the threshold in the Python pipeline code from 6 minutes to 10 minutes.
- [ ] **Scope: Prior Day only** (KW20R3)
- [ ] **Columns:** EID, TM Name, Department, Schedule Group, Reports To, Scheduled, Worked, Over
- [ ] **Remove:** Date column (scope is always prior day — stated in description) (KW21), Observation column (KW22), Red Flag column (KW23)
- [ ] **No per-row Insight column** — single static insight shown in section description, not per row (KW23)
- [ ] Static insight text: `"Local HR to review timecard → confirm VET/approval or adjust schedule; document per SOP"`
- [ ] Hours in Scheduled/Worked/Over columns: use `Xhr Ymin` format (e.g., `10 hrs 18 min`, `+18 min`)

---

## SECTION 04 – PAYCODE RECONCILER

- [ ] Section description under heading (KW24): explains what it is (paycodes that exceed or undershoot scheduled hours); states WTD or Prior Week scope
- [ ] **Columns:** EID, TM Name, Department, Schedule Group, Reports To, Date, Scheduled, Applied, Paycodes, Insight
- [ ] No `(HH:MM)` suffix in any column header (KW28)
- [ ] **Sort:** TM Name A–Z, then Date most recent first (KW24)
- [ ] **Scope:** WTD (Tue–Sat) or Prior Week (Sun–Mon), stated in description
- [ ] Insights: static text per mismatch type (over-applied vs. under-applied)
- [ ] Hours in Scheduled/Applied columns and in Paycodes cell values: use `Xhr Ymin` format

---

## SECTION 05 – UPCOMING TIME OFF

- [ ] Section name: **"Upcoming Time Off"** (not "Upcoming PTO and UTO by Person") (KW25)
- [ ] Section description under heading
- [ ] **Scope:** Next 7 calendar days from report date
- [ ] **Per-department subsections**, each labeled with department name and code (KW26)
- [ ] **Sort:** Date ascending (earliest first), then TM Name A–Z within same date (KW27)
- [ ] **Columns:** EID, TM Name, Reports To, Date, Paycode, Total
- [ ] No `(HH:MM)` suffix in column headers (KW28)
- [ ] **One row per TM per date** — never combine multiple dates into a single cell or row. If a TM has time off on two days, that is two rows. (KW27)
- [ ] **Remove:** "Planned Time Off Impact by Day" aggregate table (KW29)
- [ ] **Insight per department** (AI-generated) — same rules as Section 01 insights. Reference other sections when relevant (e.g., NCNS + planned leave in same dept) (KW29)
- [ ] Hours in Total column: use `Xhr Ymin` format (e.g., `10 hrs`, `8 hrs`)

---

## SECTION 06 – 60+ HOUR WATCH

- [ ] Section description under heading (KW30): explains CRITICAL vs WATCH criteria
- [ ] **Risk levels with precedence rule:**
  - 🔴 **CRITICAL:** WTD hours worked ≥ 60 (KW30)
  - 🟡 **WATCH:** CRITICAL not met, AND (WTD hours worked ≥ 58 OR (WTD worked + remaining scheduled) > 60) (KW30)
  - If CRITICAL is met, assign CRITICAL only — do not evaluate WATCH
- [ ] **Columns:** EID, TM Name, Department, Schedule Group, Reports To, WTD Worked, Remaining Scheduled, Projected Total, Risk, Insight
- [ ] **Insights (static):**
  - CRITICAL: `"Immediate manager intervention. Adjust remaining schedule to prevent/address exceedance; review and document business justification per SOP"`
  - WATCH: `"Monitor closely; do not approve additional OT; review upcoming schedule and cap remaining hours below 60"`
- [ ] Hours in WTD Worked / Remaining Scheduled / Projected Total columns: use `Xhr Ymin` format

---

## SUMMARY OF HR FINDINGS

- [ ] Table: Category | Finding | Insight
- [ ] **Categories:** Attendance, NCNS, Unscheduled Work, Paycode Errors, Time Off Coverage, Overtime Risk
- [ ] One row per category; findings are narrative summaries (AI-generated counts + notable TM names)

---

## SITE NARRATIVE

- [ ] Appears after the Summary table, before the footer
- [ ] Two subsections: **"Week to Date"** (backward-looking) and **"Looking Ahead"** (forward-looking)
- [ ] AI-generated — synthesizes all report data
- [ ] Tone: observational, factual. States what happened and what is coming. Does NOT evaluate or prescribe.
- [ ] WTD paragraph covers: attendance trends, NCNS volume, unscheduled work, paycode issues, overtime risk
- [ ] Looking Ahead paragraph covers: planned absences, coverage gaps, converging signals

---

## FOOTER

- [ ] Footer line: `Daily People Pulse · [Site] · [Date] · Data source: UKG API · Chewy Confidential - Internal Use Only`
- [ ] Second line: `Generated by ORBIT · Daily People Pulse · An ORBIT Product`

---

## INSIGHT RULES (applies to Section 01 and Section 05)

- [ ] Use plain, conversational speech — brief the HR Partner as if in person
- [ ] **Synthesize** trends across the data shown; do NOT re-state or parrot numbers already visible in the card/table above
- [ ] Surface patterns (multi-day repeats, shift-level differences, cross-dept comparisons)
- [ ] Surface coverage risks; flag when multiple signals converge (e.g., NCNS + planned leave in same dept)
- [ ] Cross-reference other sections when relevant (e.g., "see Section 02")
- [ ] State what the data shows; let HR decide next steps. Do NOT be prescriptive about specific actions.
- [ ] Do NOT assume a benchmark is "good" or "bad" — just state patterns
- [ ] Do NOT direct Operations Managers — NCNS follow-up is HR's responsibility (Section 02 handles it)
- [ ] Do NOT make disciplinary recommendations
- [ ] Do NOT reference an employee by name in a negative context beyond what the data directly states
- [ ] Do NOT use language that could create legal exposure (medical conditions, protected characteristics)
- [ ] Fallback: `"Insufficient data to generate an insight for this department this period."`

---

## OPEN QUESTIONS (need product owner answers before pipeline build)

1. Do Vet Services Tech I and Tech II have assigned department codes in UKG?
2. Should the 85% attendance threshold vary by department?
3. Should Section 05 show only HR-Partner-visible TMs, or all TMs at the site?
4. What is the UKG API refresh cadence, and what is the acceptable staleness window before a warning banner appears?
5. Who is the designated reviewer for AI insights during the pilot phase?
