# TMDM Paycode Reconciler — Quick Start User Guide

## Who This Is For

TMDM reps and HRSS users who use the TMDM Paycode Reconciler in Phoenix / ORBIT to audit over-applied time-off paycodes on FC and Rx timecards before payroll close.

---

## Getting Started

1. **Open Phoenix** and navigate to the TMDM Paycode Reconciler agent.
2. **Type a prompt** in plain language. The agent understands natural English — no SQL required.
3. **Review results** in the table or summary the agent returns.
4. **Open UKG** to make corrections based on the agent's recommendations.

---

## Your Weekly Workflow

### Step 1 — Pull Your Defect List

Type:

> **"Show me defects that need attention"**

This returns the full list of team members with over-applied time-off paycodes for the previous week through the current week, where weeks are defined Sunday through Saturday. Results are sorted by risk (High first), then by over-applied hours (largest first), then alphabetically.

### Step 2 — Focus on High-Risk Items First

Type:

> **"Just show me high-risk defects"**

High-risk defects are cases where the over-application is significant (typically 4+ hours or full-day mismatches). These should be corrected first to prevent payroll defects.

### Step 3 — Filter by Your Assignment

If you're assigned to a specific network or set of locations:

> **"Show me FC only"**
> **"Show me PHX1"**
> **"Show me BNA1"**

### Step 4 — Work Through the List

The table surfaces the most material defects first. For each row:

- Note the **employee name and ID**
- Note the **date**, **hours worked**, and **paycodes applied**
- Note the **Recommendation** and **Root Cause** fields (e.g., "Time-off on unscheduled day - reduce by 5 hrs")
- Open the TM's timecard in UKG **once** and make all needed corrections for that employee
- Move to the next row

### Step 5 — Monitor Progress

Re-run the defect query periodically as you work. Corrected timecards will drop off the list after the next data refresh.

### Step 6 — Review Summary Before Payroll Close

Type:

> **"Give me an executive summary"**

This gives you KPIs, root cause breakdown, and a summary of what's left to address.

---

## Prompt Examples

### Basic Queries

| What You Want | What to Type |
| --- | --- |
| Full defect list | "Show me defects that need attention" |
| Executive overview | "Give me an executive summary" |
| KPIs only | "Show me the KPIs" |
| What's driving issues | "What's driving the defects?" |

### Filtering

| What You Want | What to Type |
| --- | --- |
| FC network only | "Show me FC only" |
| Rx network only | "Show me Rx only" |
| Specific location | "Show me PHX1" or "Show me BNA1" |
| Specific supervisor's team | "Show me John Smith's team" |
| Specific employee | "Look up employee 123456" |
| High-risk only | "Just show me high-risk defects" |
| Specific pattern | "Show me all NCNS defects" |
| Specific date | "Show me defects for 2026-03-02" |

### Analysis

| What You Want | What to Type |
| --- | --- |
| Day-of-week patterns | "Are there patterns by day of week?" |
| Tenure/new hire analysis | "Is this a new hire problem?" |
| FC vs Rx comparison | "How does FC compare to Rx?" |
| Repeat offenders | "Who has multiple defects in this report window?" |

### Combining Filters

You can combine filters in a single prompt:

> **"Show me high-risk FC defects at PHX1"**
> **"Show me John Smith's team in Rx"**
> **"Who has multiple defects in FC?"**

### Export

> **"Export to Excel"**

---

## Understanding the Output

### Table Columns

| Column | What It Means |
| --- | --- |
| **Business Unit** | Business unit / network value shown in the export |
| **Employee ID** | 6-digit UKG ID — use this to find the TM in UKG |
| **Employee Full Name** | Last, First format |
| **Schedule Group Name** | UKG schedule group (contains location code for FC) |
| **Supervisor** | Direct supervisor (Reports To) |
| **Date** | The date of the flagged timecard entry |
| **Hours Scheduled** | How many hours the TM was scheduled to work that day |
| **Hours Worked** | How many hours the TM actually worked that day |
| **Time-Off Applied** | Total time-off paycode hours applied to that day |
| **Paycodes** | Which paycodes were applied and for how long (e.g., "PTO PAID: 05:00") |
| **Over-Applied Hrs** | The amount of time-off that exceeded the available gap |
| **Recommendation** | What the agent recommends based on the defect pattern |
| **Root Cause** | Why the row was flagged (for example, unscheduled day vs. excess time-off applied) |
| **Schedule Anomaly** | Additional schedule-related flag when applicable |

### Risk Levels

| Level | Meaning | Action |
| --- | --- | --- |
| **High** | Large over-application or full-day mismatch. Reflected in the Recommendation field. | Correct immediately — highest payroll risk. |
| **Standard** | Smaller over-application detected. | Review and correct before payroll close. |

### Defect Patterns

| Pattern | What It Means |
| --- | --- |
| **PTO Over-Application** | PTO hours applied exceed what's appropriate given the schedule — direct overpayment risk |
| **Personal Unpaid** | Personal unpaid hours over-applied — compliance concern |
| **NCNS** | No-call no-show paycode applied — may be a coding error or attendance issue |
| **Intermittent Leave** | FMLA/intermittent leave hours over-applied — handle with care per leave policy |
| **Mixed (PTO + Personal)** | Multiple paycode types over-applied — may need itemized review |

---

## Tips for Efficiency

1. **Work alphabetically within risk tiers.** The agent sorts High-risk first, then Standard. Within each tier, names are alphabetical so you can open UKG timecards in order.

2. **Single-touch per employee.** The report groups all defect dates for each TM. Open the timecard once, fix all dates, and move on.

3. **Start with High-risk on Monday/Tuesday.** High-risk items have the greatest payroll impact. Get these done early in the week.

4. **Use the executive summary on Thursday/Friday.** Before payroll close, run the summary to see what's left and confirm your coverage.

5. **Bookmark common filters.** If you always work FC at a specific set of locations, note your prompt (e.g., "Show me FC defects at AVP1") and reuse it each week.

---

## FAQ

**Q: How fresh is the data?**
A: Data refreshes daily. It reflects up to the end of the previous day (T-1). If you made corrections in UKG today, they'll show in tomorrow's refresh.

**Q: Why do some employees appear multiple times?**
A: Each row is one employee + one date. If an employee has over-applied paycodes on multiple days, they'll have multiple rows. Use "Who has multiple defects?" to find these.

**Q: What if the agent says "no defects found"?**
A: Either all timecards are clean for your filter, or you may need to broaden your criteria. Try removing a filter or checking a different network/location.

**Q: Can the agent fix timecards for me?**
A: No. The agent is read-only. It tells you what needs fixing and by how much. You make the actual corrections in UKG.

**Q: What paycodes does this cover?**
A: PTO PAID, PTO PAID PTO Sick, Personal UNPAID, Personal UNPD Call Off, and Intermittent Leave-Unpaid. Additional paycodes may be added over time.

**Q: I see CC and Other network records. Should I work those?**
A: The primary scope is FC and Rx. CC and Other records are included in the data but are outside the initial TMDM audit scope. Check with your team lead for guidance.

---

## Need Help?

- Type **"What can you help me with?"** in the agent for a full list of capabilities.
- Contact **Kenny Wallace** (Product Owner) for product questions.
- Contact **Jen Hudson** (TMDM Sponsor) for business process questions.
