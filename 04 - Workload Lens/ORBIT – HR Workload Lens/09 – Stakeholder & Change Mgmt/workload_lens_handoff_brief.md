# Workload Lens — Session Handoff Brief

**Date:** 2026-03-03
**Purpose:** Complete context transfer for producing 5 Workload Lens deliverables in a new chat session.

---

## Source Files (in uploads)

Upload these three files to the new chat:

1. **PRD PDF** — `Product_Requirement_Document__PRD___Workload_Lens-030326-191658.pdf` (39 pages, comprehensive product requirements)
2. **Phoenix Agent Instructions v2** — `phoenix_agent_instructions__2_.md` (system prompt with 8 immutable SQL queries)
3. **v3 Mock Report** — `v3_mock_report.md` (UTF-16LE encoded, actual generated output from Feb 15-28 2026 data window)

Also upload this handoff brief.

---

## Product Context

- **Product:** ORBIT HR Workload Lens (Phase I = UKG Time & Attendance)
- **Program:** ORBIT (HR AI Transformation at Chewy)
- **Lifecycle Stage:** Pillar 2 (Design & POC)
- **Platform:** Phoenix (Chewy internal LLM platform), Snowflake data infrastructure
- **Owner:** Kenny Wallace, ORBIT Program Lead
- **Workspace:** Windsurf with `.windsurf/rules.md` and `.windsurf/PRODUCT_FOLDER_RULES.md`

---

## 5 Deliverables to Produce

All as separate markdown files:

1. **PRD (Workload Lens)** — Full rework of the existing 39-page PRD incorporating all 10 reconciliation decisions below. OBR terminology throughout. Clean, governed, production-grade.
2. **Technical Design Doc** — New document. Architecture, data flow, Snowflake view specs (current inline CTE state vs target V_HWL_* views), agent orchestration design, error handling.
3. **Value Scorecard** — New document. Baseline metrics, success criteria, measurement framework for Pillar 2 gate review.
4. **Data Map & Classification Declaration** — Rework of the v1.0 draft (produced earlier this session, 747 lines). Part 1 = Data Map, Part 2 = Classification Declaration. Current vs Target state clearly labeled throughout.
5. **POC Agent Instructions** — Separate from the PRD. The actual Phoenix agent system prompt/configuration with updated SQL queries reflecting all decisions below. This replaces the v2 agent instructions.

---

## 10 Reconciliation Decisions (ALL must be reflected across ALL 5 documents)

### 1. DPMO = Per Million
- The glossary in both the agent instructions and mock report correctly defines DPMO as "Defects Per Million Opportunities"
- But the actual SQL computes `× 1000` (per thousand), not `× 1,000,000`
- **Decision:** Standardize on per million. Update the SQL formula to `× 1000000`
- **Traffic light thresholds:** TBD pending baseline data. Leave as placeholders in docs.

### 2. Data Map Accuracy / Agent vs Intent Gaps
- Agent instructions v2 header says "new hires filtered" for the engagement list, but Q8 SQL does NOT implement a hire date filter
- DPMO glossary says per million but SQL says per thousand (see #1)
- **Decision:** Data Map must document what actually runs AND flag where intent differs from implementation. All gaps get explicit callouts.

### 3. Actor Group Changes
Four changes to the OBR_ACTOR_GROUP classification:
- **Add:** `REVISION_USER_FUNCTION_ACCESS_PROFILE = 'Workers Compensation'` → OBR_ACTOR_GROUP = `Local HR`
- **Filter out:** `REVISION_USER_FUNCTION_ACCESS_PROFILE = 'Super Access No Wages'` — this is automation traffic that skews data. Exclude from KPI computation.
- **Filter out:** `REVISION_USER_FUNCTION_ACCESS_PROFILE = 'Workforce Reporting'` from the HR KPI layer — retain as `WFM` in base data only for dependency analysis.
- **"Other" handling:** Do NOT report "Other" in the customer-facing OBR report. Keep it in the Snowflake table for internal research/data quality monitoring.

Current agent SQL groups: Local HR, HRSS, Team Member, Local Ops, WFM, Other
Updated groups for customer HR report: Local HR, HRSS, Local Ops (Team Member, WFM, Automation, and Other excluded from KPI output)

### 4. Service Tier / Misrouting → Phase II
- PRD Section 13 defines full tier mapping with INTENDED_OWNER and misrouting classification
- **Decision:** Defer entirely to Phase II. Remove from Phase I scope in all docs.
- Phase II needs clear guardrails about which group owns which work.

### 5. WoW Delta Framework → Production Views
- PRD defines 7-column display (This Week, Prior Week, WoW Delta, WoW Delta %, 4-Week Avg, vs Baseline, 13-Week Sparkline)
- Current agent only has current week + 13-week UCL spike flag
- **Decision:** Push as much computation as possible to production Snowflake views. The agent should read pre-computed deltas and reason about them, not calculate them.

### 6. No More "COE" — Just "HRSS"
- PRD and earlier reference queries define granular HRSS subgroups (COE/TMDM, TMSC, LOAA, Super Access)
- **Decision:** Eliminate "COE" and "HRSS/COE" from all documents. The only term is "HRSS."
- Kill the user-level drilldown (who in HR did the most work). We don't need to see individual HR user volume.
- **KEEP** the missed punch engagement list (Section 4c / Q8) — this is TM-level, not HR-user-level.
- **Note for 4c:** Hire date must be added to identify first-week TMs. They should be exempt from missed punch flags because TMs often don't get a badge until midday of day 1. This is UNRESOLVED — V_PEOPLE may or may not have a reliable hire date field. Flag as open item.

### 7. Abandon Chronic Missed Punch Flag
- PRD defined: "TM triggered engagement flag in 3+ of last 4 weeks → escalate to HR Director"
- **Decision:** Remove entirely from all documents. Do not implement.

### 8. Full WBR → OBR Terminology Pass
- PRD uses "WBR" (Weekly Business Review) extensively
- Agent instructions and mock report use "OBR" (Operations Business Review) in column names
- **Decision:** OBR is the canonical term. Full find-and-replace across all documents.

### 9. Rx Site Groupings = Presentation Only
- PRD defines grouped Rx locations (PHX2/5, MCO4/5, SDF4/5/6, AVP4/5/6, DFW5/8)
- **Decision:** This is presentation-layer grouping only. No distinct SQL aggregation needed. Agent computes at individual site level; grouping happens in report formatting.

### 10. BNA1 = 2G FC
- PRD had open question about BNA1 classification (1G vs 2G)
- **Decision:** BNA1 is 2G. It stays in FC.

---

## Key Technical Details (from source file analysis)

### Data Sources (Phase I)
- `EDLDB.PEOPLE_ANALYTICS_SANDBOX.UKG_V_TIMECARD_AUDIT` — core audit table, daily incremental loads, requires dedup
- `EDLDB.UKG.V_PEOPLE` — employee profiles, requires dedup (highest PERSON_ID wins)
- `EDLDB.UKG.V_TIMECARD_EXCEPTION` — missed punch exceptions
- `EDLDB.PEOPLE_ANALYTICS_SANDBOX.V_HWL_WEEKLY_SITE_METRICS` — only pre-materialized view (13-week baselines)

### TM Self-Service Reference
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

### Agent SQL Architecture (Current State)
- 8 immutable queries (Q1-Q8) with inline CTEs
- Key CTEs: audit_deduped, people_deduped, comments_by_revision, missed_punch_counts, weekly_missed_totals, base, hr
- Self-edit detection: two methods (PERSON_NUMBER comparison for EDIT_TARGET, name string matching for OBR_ACTOR_GROUP — name match takes precedence)
- Comments excluded from action counts but text linked back via comments_by_revision CTE

### Target State: V_HWL_* View Architecture
8 views defined in PRD Section 15. Only V_HWL_WEEKLY_SITE_METRICS exists today.

### Site Groupings
- FC: 13 sites (AVP1, AVP2, BNA1, CFC1, CLT1, DAY1, DFW1, HOU1, MCI1, MCO1, MDT1, PHX1, RNO1)
- Rx: 13 sites (AVP4, AVP5, AVP6, DFW5, DFW8, MCO4, MCO5, PHX2, PHX5, SDF2, SDF4, SDF5, SDF6)
- CVC: 18 sites (ATLA-PHXB)
- CC: 7 sites (AV4V, DF4V, DFW4, FL3V, PH0V, PW0V, SD2V)
- Excluded Corp: BOS1, FLL7, SEA1, MSP2

### Mock Report Key Numbers (Feb 15-28, 2026)
- 80,693 total actions, 1029.2 FTE hours, 31.4% network defect rate
- 0.3% missing punch rate, 2.7% historical correction rate
- Comment compliance: 3.6% (target 85%)
- Top DPMO sites: ATLD (428.6), CLT1 (221.1), MDT1 (193.9), AVP6 (193.5), MCI1 (193.5)

---

## Writing Style Preferences

- Never use "-" (hyphens/dashes) unless grammatically necessary. Kenny doesn't want documents to look AI-generated.
- No "COE" anywhere. Only "HRSS."
- OBR not WBR.
- Clear, direct language. Production-grade governance documentation.

---

## Suggested Order of Operations

1. **Data Map & Classification Declaration** (gates everything else, already has v1.0 draft to rework)
2. **PRD** (full rework incorporating all 10 decisions)
3. **Technical Design Doc** (architecture flows from PRD decisions)
4. **Value Scorecard** (metrics baseline from Data Map + PRD)
5. **POC Agent Instructions** (updated SQL reflecting all changes, built last since it depends on all upstream decisions)
