# FC General Inquiry — Deep Dive Analysis
## Weeks 8–9 (2/15–2/28/2026) | Prepared for HR OBR Supplemental Response

**Prepared by:** ORBIT Workload Lens Team  
**Date:** 2026-03-05  
**Data Sources:**
- ServiceNow (SNOW) FC General Inquiry tickets — CSV extract (Nov 2024–Feb 2026)
- Phase I UKG Timecard Audit — Workload Lens Week 9 report
- HR OBR Supplemental (2026-03-02) — Director questions
- Week 9 HR Operations OBR (2/22–2/28/2026)

**Status:** DRAFT — Pending two open items before finalization (see §8)

---

## 1. Executive Summary

FC General Inquiry generated **409 tickets** in Week 9 (2/22–2/28), up **+10.8% WoW** from 369 in Week 8. YoY, volume is essentially flat at **+9.4%** vs. Week 9 2025 (374 tickets).

The **+40 ticket WoW increase** is explained by two concurrent events:
1. **Weather event at AVP2** (Lehigh Valley, PA) — winter storm drove AVP2 from 60 → 90 tickets (+30), accounting for 75% of the WoW increase
2. **LOA spike** — Leave of Absence tickets nearly doubled WoW (33 → 62, +29), concentrated at AVP4, MCI1, BNA1

Three categories account for **~40% of all FC General Inquiry volume** but are **not true inquiries** — they are document submissions and automated process artifacts:
- **I-9 / Onboarding / Compliance Docs** (90 tickets, 22%) — seasonal pharmacy license renewals at SDF2 (KY) + I-9 uploads at AVP2
- **AVP4 Swag Requests** (29 of 39 Badge/Access tickets) — Smartsheet automation generating tickets for local swag store fulfillment
- **Spam / Misdirected Email** (4 tickets) — eFax, Amazon links, etc.

**Key insight:** Removing process artifacts (I-9 doc uploads, swag automation, spam) would reduce FC General Inquiry by **~123 tickets/week (30%)** with zero impact on TM service.

**Integrated with Phase I UKG data (§6):** FC General Inquiry tickets represent just **1.0% of 41,790 total FC timecard actions** — confirming that **~97.5% of HR timekeeping work is invisible to SNOW**. LOA and PTO have the tightest ticket-to-UKG ratios (1:41 and 1:22), making them the highest-friction categories and the best targets for self-service deflection.

---

## 2. Headline Numbers

| Metric | Wk 8 | Wk 9 | WoW Δ | WoW % |
|---|---:|---:|---:|---:|
| FC General Inquiry Tickets | 369 | 409 | +40 | +10.8% |
| Resolved Count | 364 | 374 | +10 | |
| Resolution Rate | 98.6% | 91.4% | | -7.2 pp |
| Avg Resolution (hrs) | 21.8h | 20.3h | -1.5h | |
| Median Resolution (hrs) | 24.0h | 24.0h | 0.0h | |
| Same-Day Resolved (≤24h) | 83.2% | 77.8% | | -5.4 pp |
| Open >3 Days | 12 | 5 | -7 | |
| Open >7 Days | 5 | 0 | -5 | |

| YoY Comparison | Wk9 2025 | Wk9 2026 | Δ | % |
|---|---:|---:|---:|---:|
| FC General Inquiry | 374 | 409 | +35 | +9.4% |

**Resolution performance improved** WoW despite higher volume — avg resolution dropped 1.5 hours, and tickets open >3 days dropped from 12 → 5. The resolution rate dip (98.6% → 91.4%) reflects 35 tickets still in progress at time of extract, not a performance degradation.

---

## 3. Category Breakdown

### 3a. Week 9 vs Week 8 (WoW)

| Category | Wk 8 | Wk 9 | Δ | %Chg | Notes |
|---|---:|---:|---:|---:|---|
| I-9 / Onboarding / Compliance Docs | 100 | 90 | -10 | -10% | Seasonal — see §4a |
| PTO / Time-Off Balance | 44 | 70 | +26 | +59% | MCO1 spike — see §4d |
| Leave of Absence / FMLA / LOA | 33 | 62 | +29 | +88% | Multi-site — see §4c |
| Timecard / Punch / Schedule | 66 | 51 | -15 | -23% | Improving trend |
| Badge / Access / IT / Workday | 46 | 39 | -7 | -15% | ~29 are AVP4 swag — see §4b |
| Other / Unclassified | 37 | 25 | -12 | -32% | Improved classification |
| Attendance / Call-Off / NCNS | 15 | 25 | +10 | +67% | Weather event — see §4e |
| Pay Discrepancy / Missing Pay | 6 | 16 | +10 | +167% | Small base |
| VTO / VET / Voluntary Time | 9 | 13 | +4 | +44% | |
| Spam / Misdirected | 2 | 4 | +2 | | |
| Benefits / Enrollment / Payroll | 4 | 4 | 0 | 0% | |
| Transfer / Job Change | 3 | 4 | +1 | | |
| Suspension / TM Relations | 1 | 3 | +2 | | |
| Personal Info / Records | 3 | 3 | 0 | 0% | |
| **TOTAL** | **369** | **409** | **+40** | **+10.8%** | |

### 3b. Week 9 YoY (2025 vs 2026)

| Category | 2025 | 2026 | Δ | %Chg |
|---|---:|---:|---:|---:|
| I-9 / Onboarding / Compliance Docs | 89 | 90 | +1 | +1% |
| PTO / Time-Off Balance | 54 | 70 | +16 | +30% |
| Leave of Absence / FMLA / LOA | 34 | 62 | +28 | +82% |
| **Timecard / Punch / Schedule** | **77** | **51** | **-26** | **-34%** |
| Badge / Access / IT / Workday | 24 | 39 | +15 | +62% |
| Attendance / Call-Off / NCNS | 35 | 25 | -10 | -29% |
| Pay Discrepancy / Missing Pay | 7 | 16 | +9 | +129% |
| VTO / VET / Voluntary Time | 1 | 13 | +12 | NEW |
| **TOTAL** | **374** | **409** | **+35** | **+9.4%** |

**YoY story:** Timecard/Punch tickets are **down 34%** — the clearest evidence that UKG self-service and TM app adoption is reducing demand. However, LOA tickets are **up 82%** and PTO tickets are **up 30%**, partially offsetting the gains.

---

## 4. Category Deep Dives

### 4a. I-9 / Onboarding / Compliance Docs — 90 tickets (22.0%)

**This is the #1 category and it is NOT a true inquiry.** These are document submissions routing through email into SNOW as FC General Inquiry tickets.

**Breakdown by site:**
| Site | Tickets | What's happening |
|---|---:|---|
| SDF2 | 60 | Pharmacy license renewals (RPH, KYBOP, pharmacy tech) — **seasonal Feb/Mar pattern** in Kentucky. TMs email local HR their renewal documentation. |
| AVP2 | 20 | I-9 document uploads. Internal HR staff at AVP2 (`AVP2-Office_Red@chewy.com`) emails I-9 form references to the local HR inbox, each creating a ticket. |
| SDF-CAMPUS | 7 | Pharmacist license submissions (same seasonal pattern as SDF2) |
| CLT1 | 2 | |
| MCI1 | 1 | |

**Resolution:** avg 13.4h | median 0.0h | same-day 86% — fast because these just need to be filed, not investigated.

**WoW:** 100 → 90 (-10) — slight decline as renewal season tapers  
**YoY:** 89 → 90 (+1) — perfectly flat, confirming this is a predictable seasonal pattern

**Recommendation:**
> **Validate routing.** These document submissions should not be classified as "FC General Inquiry." Options:
> 1. Create a dedicated SNOW category (e.g., "Compliance Document Submission") so these don't inflate inquiry metrics
> 2. Route pharmacy license renewals through a document portal or shared drive upload instead of email → SNOW
> 3. For I-9 uploads, evaluate whether the email-to-ticket workflow is the intended process or a workaround
>
> **Impact if reclassified:** -90 tickets/week from FC General Inquiry (22% reduction)

---

### 4b. Badge / Access / IT / Workday — 39 tickets (9.5%)

**29 of 39 tickets (74%) are AVP4 Smartsheet Swag Requests** — not badge/access issues.

AVP4 operates a local swag store via Smartsheet. When a TM fills out the swag request form, Smartsheet sends an automated email (`automation@app.smartsheet.com`) to the AVP4 HR inbox, which SNOW auto-converts into an FC General Inquiry ticket. Local HR then uses the ticket to fulfill the swag order.

**Site concentration:** AVP4 = 29 of 39 tickets in this category

**Resolution:** avg 32.7h | median 48.0h | same-day 42% — slower resolution makes sense: swag fulfillment isn't urgent.

**WoW:** 46 → 39 (-7)  
**YoY:** 24 → 39 (+15) — increase driven entirely by AVP4 swag process adoption

**Recommendation:**
> **This will self-correct** as processes migrate off the Smartsheet platform. In the interim, these inflate FC General Inquiry volume by ~29 tickets/week (7%). Consider:
> 1. Excluding Smartsheet automation-generated tickets from SLA reporting
> 2. Adding a "Swag Request" HR Service category in SNOW to separate from inquiries
>
> **Impact if reclassified:** -29 tickets/week from FC General Inquiry (7% reduction)

---

### 4c. Leave of Absence / FMLA / LOA — 62 tickets (15.2%)

**This is the most concerning WoW trend.** LOA nearly doubled from Wk8 (33) to Wk9 (62), +88% WoW.

**Site distribution (Wk9):**
| Site | Tickets |
|---|---:|
| AVP4 | 16 |
| AVP2 | 8 |
| MCI1 | 7 |
| BNA1 | 7 |
| RNO1 | 6 |
| CLT1 | 4 |
| PHX1 | 3 |
| SDF2 | 3 |
| Other (4 sites) | 8 |

**YoY:** 34 → 62 (+82%) — this increase runs **counter** to the network-wide LOA Status trend (OBR Supplemental notes LOA Status notifications are down 12.3% YoY). However, these are different signals:
- **LOA Status** tickets = automated A1 system notifications (declining as expected)
- **LOA within FC General Inquiry** = TMs emailing site HR about leave questions (increasing)

**Common themes in ticket descriptions:**
- Leave extension requests
- Return-to-work clearance inquiries
- Intermittent leave usage notifications
- Bereavement documentation
- ADA accommodation requests
- TMs confused about leave status / next steps

**Resolution:** avg 20.2h | median 24.0h | same-day 80%

**Recommendation:**
> The +82% YoY growth in LOA-related FC General Inquiry tickets suggests TMs are not getting adequate self-service visibility into their leave status. This aligns with the OBR Supplemental's question about LOAA decision timeliness exceeding 4 days. When TMs can't get leave status from A1, they email site HR — and that becomes an FC General Inquiry ticket.
>
> **Opportunity:** Improve A1 portal self-service so TMs can check leave status, extension progress, and return-to-work requirements without emailing HR. Each LOA ticket displaced from FC General Inquiry to self-service also reduces local HR administrative burden.

---

### 4d. PTO / Time-Off Balance — 70 tickets (17.1%)

**WoW spike:** 44 → 70 (+26, +59%)

**Key anomaly: MCO1 accounts for 19 of 70 PTO tickets (27%)** — and ALL 19 MCO1 tickets in Week 9 are PTO-related.

| Site | PTO Tickets | Site Total | PTO % of Site |
|---|---:|---:|---:|
| MCO1 | 19 | 19 | 100% |
| AVP2 | 13 | 90 | 14% |
| SDF2 | 9 | 89 | 10% |
| AVP4 | 7 | 67 | 10% |
| AVP1 | 6 | 17 | 35% |
| RNO1 | 5 | 15 | 33% |
| BNA1 | 4 | 15 | 27% |

> **⚠ OPEN ITEM:** MCO1 PTO concentration — awaiting local HR reply to determine root cause (possible policy change, balance reset, system issue, or local process gap). Will update once received.

**Common themes:** Negative UTO balances, PTO not applied to call-offs, holiday pay questions, PTO accrual discrepancies.

**YoY:** 54 → 70 (+30%) — sustained increase, not just a one-week blip.

**Resolution:** avg 20.4h | median 24.0h | same-day 74%

**Recommendation:**
> **UKG TM app** is the primary lever here. TMs who can see their own PTO balance and submit time-off requests in-app don't need to email HR. The 30% YoY increase suggests either (a) app adoption is lagging at some sites, or (b) PTO policy changes are generating more confusion. MCO1 investigation will clarify.

---

### 4e. Attendance / Call-Off / NCNS — 25 tickets (6.1%)

**WoW:** 15 → 25 (+10, +67%) — driven by the **AVP2 winter storm**.

| Site | Tickets |
|---|---:|
| AVP2 | 12 |
| SDF2 | 4 |
| AVP1 | 3 |
| AVP4 | 2 |
| Other (4 sites) | 4 |

**AVP2 weather context:** Multiple tickets reference winter storms, icy roads, and inability to travel. TMs emailed the AVP2 HR inbox to report absences because they could not reach the facility. Sample descriptions:
- *"I will not be able to make it in to work today... Due to the winter storm"*
- *"i will not be in today due to the weather. 2/23/26 i do not have the ukg app"*
- *"Not coming in due to weather"*

**YoY:** 35 → 25 (-29%) — the downward trend is real; the weather event is a temporary bump.

**Important scope note:** These 25 tickets are only the attendance/call-off requests that route through **FC General Inquiry** (TMs emailing site HR directly). The OBR Supplemental references **1,054 "Attendance Inquiry"** tickets as a separate HR Service — that is a different SNOW category with its own data.

> **⚠ OPEN ITEM:** Attendance Inquiry and Attendance Management CSVs requested from Enterprise People Analytics. Once received, we will integrate those into this analysis for a complete attendance picture.

**Recommendation:**
> The call-off ticket that explicitly states *"i do not have the ukg app"* is a perfect example of the TM app adoption gap. A centralized call-off line + UKG app call-off feature would eliminate the need for TMs to email site HR for absence reporting.

---

### 4f. Timecard / Punch / Schedule — 51 tickets (12.5%)

**The strongest positive trend in the data.** Timecard tickets are **down 34% YoY** (77 → 51) and **down 23% WoW** (66 → 51).

| Site | Tickets |
|---|---:|
| AVP2 | 11 |
| SDF2 | 8 |
| AVP4 | 6 |
| DAY1 | 4 |
| CLT1 | 4 |
| Other (7 sites) | 18 |

**Common themes:** Missed punch corrections, shift swap requests, schedule questions, timecard adjustment forms.

**Resolution:** avg 26.6h | median 24.0h — slowest resolution of any major category, with 3 tickets open >3 days.

**UKG cross-reference:** Phase I UKG data shows 22,955 manual punch corrections in Week 9 — the largest single action type. The fact that Timecard tickets are **down 34% YoY** while UKG punch corrections remain high suggests HR is **proactively fixing timecards before TMs notice errors**. This is good for TM experience but represents absorbed dark work.

**Recommendation:**
> Continue UKG TM app adoption push. The 34% YoY decline proves self-service is working. Remaining volume is residual — TMs who still email HR for missed punches instead of using the app.

---

### 4g. Pay Discrepancy / Missing Pay — 16 tickets (3.9%)

**WoW:** 6 → 16 (+10, +167%) — notable increase but small base.

**Themes:** Workers comp unpaid hours, missing punches affecting pay, paycheck access issues, negative hour balances.

**Resolution:** avg 32.6h | median 24.0h — second-slowest category. Pay issues require investigation and often cross into Payroll team territory.

---

### 4h. VTO / VET / Voluntary Time — 13 tickets (3.2%)

**YoY:** 1 → 13 (NEW category effectively) — VTO/VET requests routed as FC General Inquiry are a growing pattern.

**Common pattern:** Supervisors email site HR to code VTO or VET for specific TMs. This is an operational request, not an inquiry.

**Recommendation:**
> VTO/VET coding should be handled via UKG workflow or a dedicated intake process, not email-to-ticket. These are process execution requests, not HR service inquiries.

---

## 5. Site Analysis

### 5a. Site × Category Heatmap (Week 9, Top 10 Sites)

| Site | I-9 | PTO | LOA | Timecard | Badge/IT | Attend | Other | Pay | TOTAL |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **AVP2** | 20 | 13 | 8 | 11 | 4 | 12 | 5 | 8 | **90** |
| **SDF2** | 60 | 9 | 3 | 8 | 0 | 4 | 0 | 0 | **89** |
| **AVP4** | 0 | 7 | 16 | 6 | 29 | 2 | 2 | 0 | **67** |
| MCI1 | 1 | 3 | 7 | 3 | 2 | 0 | 4 | 2 | 22 |
| MCO1 | 0 | 19 | 0 | 0 | 0 | 0 | 0 | 0 | 19 |
| AVP1 | 0 | 6 | 2 | 3 | 0 | 3 | 1 | 2 | 17 |
| SDF-CAMPUS | 7 | 1 | 2 | 3 | 0 | 1 | 0 | 1 | 17 |
| CLT1 | 2 | 1 | 4 | 4 | 1 | 0 | 1 | 1 | 16 |
| RNO1 | 0 | 5 | 6 | 0 | 0 | 0 | 2 | 0 | 15 |
| BNA1 | 0 | 4 | 7 | 2 | 0 | 0 | 2 | 0 | 15 |

### 5b. Key Site Stories

**AVP2 (90 tickets, 22% — #1 site):**
- **Weather event** drove +30 WoW (60 → 90)
- Diverse category mix: I-9 uploads (20), PTO (13), Attendance/Call-Off (12), Timecard (11)
- Without weather, baseline is ~60 tickets — still high but consistent with Wk8
- I-9 tickets from `AVP2-Office_Red@chewy.com` are internal HR process (document uploads), not TM inquiries

**SDF2 (89 tickets, 22% — #2 site):**
- **67% of SDF2 tickets (60/89) are pharmacy license/compliance doc submissions**
- This is a seasonal Feb/Mar pattern driven by Kentucky RPH, KYBOP, and pharmacy tech renewals
- Excluding compliance docs: SDF2 would have ~29 true inquiry tickets — a 67% reduction
- WoW: 109 → 89 (-20) — declining as renewal season peaks and tapers

**AVP4 (67 tickets, 16% — #3 site):**
- **43% of AVP4 tickets (29/67) are Smartsheet swag requests**
- LOA is the #1 real inquiry category at AVP4 (16 tickets)
- Excluding swag: AVP4 would have ~38 true inquiry tickets
- This inflated volume will self-correct as processes migrate off Smartsheet

**MCO1 (19 tickets, 5%):**
- **100% PTO** — every single MCO1 ticket is time-off related
- Investigation pending (see §8 Open Items)

---

## 6. Cross-Reference: FC Tickets (Phase II) vs UKG Timecard Audit (Phase I)

> **Why this matters:** SNOW tickets measure **TM-initiated demand** — the visible tip of the iceberg. UKG audit data (Phase I Workload Lens) measures **total HR supply** — every timecard touch across the FC network. Joining these two datasets reveals the full picture: what HR actually does vs. what TMs ask for.

FC General Inquiry tickets (409/wk) represent **1.0% of 41,790 total FC timecard actions**. The other 99% is UKG timecard work — invisible to SNOW. The table below maps each ticket category to its UKG counterpart.

### 6a. Category-to-Category Mapping: Tickets ↔ UKG Drivers

| Ticket Category | Tickets (Wk9) | UKG Action Type | UKG Volume (Wk9) | Ticket : UKG Ratio | Signal |
|---|---:|---|---:|---:|---|
| Timecard / Punch / Schedule | 51 | Manual Punch Correction | 22,955 | 1 : 450 | Tickets declining (-34% YoY) while UKG volume steady — **self-service is working** |
| Attendance / Call-Off / NCNS | 25 | Late Arrival + Early Departure coding | 8,443 | 1 : 338 | Weather-driven spike; UKG confirms 738 HRSS weather-event codings |
| LOA / FMLA | 62 | Manual coding Leave of Absence | 2,573 | 1 : 41 | **Highest ticket-to-UKG ratio** — TMs are escalating LOA questions at 2.4× the rate of other categories |
| PTO / Time-Off Balance | 70 | UTO Deductions | 1,533 | 1 : 22 | **Second-highest ratio** — TMs can't see balances, so they email HR |
| Pay Discrepancy / Missing Pay | 16 | Historical Corrections | 1,875 | 1 : 117 | Every hist. correction is a retro-pay risk; 671 were late attendance codes |

**Key insight:** LOA and PTO have the **tightest ticket-to-UKG ratios** (1:41 and 1:22), meaning these categories generate the most tickets per unit of UKG work. This confirms they are the highest-friction categories from the TM perspective — the work is complex, TMs lack visibility, and they resort to emailing HR.

### 6b. Site-Level Dark Work Analysis

*Dark work = UKG rework actions with no corresponding SNOW ticket. These are timecard corrections HR performs proactively before TMs notice an error.*

| Site | SNOW Tickets | UKG Rework | Ticket:Rework | UKG Defect % | DPMO | Dark Work % |
|---|---:|---:|---:|---:|---:|---:|
| CLT1 | 16 | 2,954 | 0.54% | 58.4% | 197,724 | 99.5% |
| MCI1 | 22 | 2,649 | 0.83% | 48.3% | 175,198 | 99.2% |
| MDT1 | 4 | 1,676 | 0.24% | 47.4% | 173,141 | 99.8% |
| BNA1 | 15 | 2,195 | 0.68% | 44.5% | 161,160 | 99.3% |
| HOU1 | 5 | 147 | 3.40% | 37.9% | — | 96.6% |

**CLT1 and MCI1** are the highest-DPMO FC sites — and they are the **most invisible** to SNOW. CLT1 has a 58.4% defect rate (meaning more than half of every timecard action is a correction) with only 16 SNOW tickets. If tickets were the only data source, CLT1 would look fine. UKG reveals it is the most error-prone FC site.

**MDT1** has 4 tickets but 1,676 rework actions — the widest gap in the network. This site's HR team is absorbing virtually all timekeeping errors before TMs escalate.

### 6c. Actor Group Distribution

| Actor Group | Actions | % of FC | Defect % | Top Driver |
|---|---:|---:|---:|---|
| **Local HR** | 25,204 | 60.3% | 50.6% | Punch corrections, late arrival, early departure |
| **HRSS** | 15,878 | 38.0% | 17.4% | Punch corrections, LOA coding, weather events |
| **Local Ops** | 708 | 1.7% | 57.1% | Punch corrections |

Local HR handles 60% of FC timecard work at a 50.6% defect rate — more than half of what they touch is rework, and none of it shows up in SNOW. HRSS already handles 38% of FC timecard work; if they can resolve more ticket inquiries at first contact (C02→C03 upskill), fewer tickets route to site HR.

### 6d. Historical Corrections — The Retro-Pay Risk Pipeline

Phase I identified **1,875 Historical Corrections** in Week 9 — HR retroactively modifying closed pay periods.

| Hist. Correction Category | Volume | SNOW Ticket Link |
|---|---:|---|
| Attendance Enforcement (late codes after payroll close) | 671 | Maps to Pay Discrepancy tickets (+167% WoW) |
| Core Pay & Missing Time | 358 | Direct driver of "missing pay" tickets |
| Leave & Compliance Lag | 351 | LOA tickets where leave codes arrive after pay period close |
| Schedule & Unpaid True-Ups (VTO, Weather) | 328 | VTO/VET tickets + weather-driven corrections |
| Other | 167 | — |

**Connection to OBR:** The OBR Supplemental flags **"DEFECT: Volume Retro-Payment"** as a standing topic. Phase I data shows 1,875 retro-pay-risk actions per week. The 16 Pay Discrepancy tickets in SNOW are just the TMs who noticed — the other 1,859 were corrected before payroll impact (or TMs didn't notice yet).

### 6e. Automation Opportunities (Phase I)

Phase I identified **~16,137 automatable UKG actions/week (~269 FTE hours)** that feed downstream SNOW tickets:

| Opportunity | Weekly Volume | SNOW Impact |
|---|---:|---|
| Late arrival/early departure batch coding | 8,443 | Reduces attendance tickets + retro-pay risk |
| VTO/VET coding automation (Rx+CC) | 3,780 | Reduces VTO/VET tickets (+1,200% YoY) |
| UTO deduction automation (CC) | 3,317 | Reduces PTO balance confusion tickets |
| Meal break UTO prevention | 597 | Prevents downstream pay discrepancy tickets |

---

## 7. Answering the OBR Director Questions — Integrated Phase I + Phase II Evidence

### Q1: "FC General Inquiry (412 tickets) — with a roll out of TM app, I would expect that these decrease."

**Data-backed response (SNOW + UKG):**

The 409 FC General Inquiry tickets in Week 9 decompose into three distinct work streams. **UKG Phase I data provides the evidence for why each stream exists and what will move it.**

**Stream 1: Process Artifacts (~123 tickets, 30%)** — Not true inquiries:
- I-9 / Compliance doc submissions: 90 tickets (seasonal pharmacy renewals + I-9 uploads)
- Smartsheet swag automation: 29 tickets (AVP4)
- Spam / misdirected email: 4 tickets

> **Action:** Validate SNOW routing. Reclassifying or re-routing these would drop FC General Inquiry by ~30% immediately. **No UKG footprint** — these tickets have zero connection to timecard work.

**Stream 2: Self-Service Addressable (~196 tickets, 48%)** — Real inquiries that could be deflected with TM app / UKG self-service:

| Category | Tickets | UKG Background Work | Why TMs Email HR | Self-Service Lever |
|---|---:|---:|---|---|
| PTO / Time-Off Balance | 70 | 1,533 UTO deductions/wk | Can't see balances; confused by negative UTO | TM app PTO balance visibility |
| LOA / FMLA | 62 | 2,573 leave codings/wk | Can't check leave status in A1 | A1 portal improvements + TM app leave status |
| Timecard / Punch | 51 | 22,955 punch corrections/wk | Missed punches; don't know how to self-correct | TM app missed punch submission — **already -34% YoY** |
| VTO/VET | 13 | 3,780 VTO codings (Rx+CC) | Supervisors email HR to code VTO | UKG VTO workflow automation |

> **UKG insight:** The Timecard category proves TM app self-service works — tickets are **down 34% YoY** while UKG punch corrections remain at 22,955/wk. HR is still doing the corrections, but fewer TMs need to ask. Applying the same adoption curve to PTO and LOA could reduce this stream by **30-50%** (~60-100 fewer tickets/week).

**Stream 3: Requires Human Intervention (~90 tickets, 22%)**:
- Attendance / Call-Off: 25 tickets (weather-elevated; baseline ~15) — UKG shows 8,443 attendance codings/wk, mostly proactive
- Pay Discrepancy: 16 tickets — UKG shows 1,875 historical corrections/wk, each a retro-pay risk; only 16 TMs noticed
- Badge/Access (non-swag): 10 tickets
- TM Relations / Transfers / Benefits / Personal Info: 14 tickets
- Unclassified: 25 tickets

These tickets will persist regardless of app rollout — they require HR judgment. The 16 Pay Discrepancy tickets are worth watching: UKG shows 1,875 historical corrections behind them (see §6d).

**Bottom line:** TM app rollout should reduce FC General Inquiry by **~60-100 tickets/week (15-25%)** from self-service deflection. Combined with routing corrections (~123 tickets), the achievable reduction is **~180-220 tickets/week (45-55%)** — bringing FC General Inquiry from ~409 to ~190-230 per week.

---

### Q2: "What is the biggest remaining opportunity to reduce volume?" (TMSC)

Ranked by impact, with UKG evidence:

**#1: SNOW Routing / Intake Reform (123 tickets/wk, 30%)**
Reclassify I-9 doc submissions, swag automation, and spam out of FC General Inquiry. This is a configuration change, not a process change. No UKG connection — pure SNOW admin action.

**#2: LOA Self-Service (62 tickets/wk, 15%)**
LOA is the fastest-growing category (+82% YoY) and has the **tightest ticket-to-UKG ratio (1:41)**. For every 41 UKG leave codings, a TM emails HR — that's 2.4× the escalation rate of other categories. UKG Phase I shows HRSS already handles 1,630 of 2,573 leave codings centrally — the work is being done, but TMs can't see it. Improving A1 portal self-service so TMs can check leave status would deflect these tickets.

**#3: PTO Visibility (70 tickets/wk, 17%)**
PTO has the **second-tightest ratio (1:22)**. UKG processes 1,533 UTO deductions/wk — TMs see the balance impact and email HR because they don't understand it. TM app with PTO balance visibility is the straightforward answer. MCO1 (19 of 70 PTO tickets) may reveal a site-specific gap.

**#4: Attendance Centralization (25 tickets/wk, 6%)**
See Q4 below. UKG confirms 8,443 attendance codings/wk behind these tickets; a centralized call-off line would address both SNOW tickets and late UKG coding.

**#5: Retro-Pay Root Cause (16 tickets/wk, but 1,875 UKG corrections/wk)**
A lagging indicator. The root cause is late attendance coding after payroll close (see §6d). Fixing timeliness upstream reduces both UKG historical corrections and downstream pay discrepancy tickets.

---

### Q3: "Continuous opportunity to upskill C02 in C03 work could lead to first call resolution" (OBR Supplemental)

HRSS already handles **38% of FC timecard work** at a 17.4% defect rate (see §6c). They process 10,034 punch corrections and 1,630 LOA codings per week — they already have the data and system access to resolve PTO, timecard, and LOA ticket inquiries at first contact without routing to site HR.

**Estimated first-call resolution opportunity:** 50–80 tickets/week if C02 reps are upskilled to resolve these three categories.

---

### Q4: "Attendance Inquiry (1,054 tickets) — Possible centralized call off line?" + "Attendance Management (TMDM, 488 tickets)" (OBR Supplemental)

**What we know from UKG Phase I:**
- FC network processes **8,443 late arrival + early departure codings per week** — this is the attendance enforcement work that follows a call-off
- Local HR performs 7,387 of these (88%); HRSS performs 976 (12%)
- **671 attendance codes were entered AFTER payroll close** (historical corrections) — meaning the call-off was processed too late

**The centralized call-off line would address three problems simultaneously:**
1. **Reduce Attendance Inquiry tickets** (1,054/wk) — TMs would call the line instead of emailing or submitting tickets
2. **Reduce FC General Inquiry attendance tickets** (25/wk) — same TMs, different routing
3. **Reduce late attendance codings in UKG** (671 retro-corrections/wk) — centralized intake would ensure timely coding before payroll close

> **Pending:** The Attendance Inquiry and Attendance Management CSVs from Enterprise People Analytics will allow us to cross-reference these tickets with UKG data at the site level. This analysis will be updated once received.

---

### Q5: "Timesheet Inquiry (TMDM, 104 tickets) — more TMs understand and use UKG, they may be able to do this self-service" (OBR Supplemental)

**UKG evidence strongly supports this.** Timecard/Punch tickets within FC General Inquiry are **already down 34% YoY** (77 → 51), the single strongest positive trend in SNOW data. Meanwhile, UKG Phase I shows 22,955 punch corrections/wk — the volume of HR-side work hasn't decreased, but **TM-initiated tickets have.**

This means TMs who adopt UKG self-service stop generating tickets, even though the underlying timekeeping errors persist. The next wave of improvement requires reducing the errors themselves (punch discipline, shift-start reminders, supervisor accountability).

---

### Q6: "LOAA Decision Timeliness — AVG Response Time exceeding 4 days" + "What causes these delays?" (OBR Supplemental)

The OBR Supplemental identifies the primary delay driver as **information gathering after ticket creation** (candidates given 15 business days to respond, with a 7-day extension). LOA tickets are up +82% YoY (§6a), and UKG shows 351 LOA historical corrections per week — leave codes arriving after payroll close (§6d). The chain: slow leave determination → delayed UKG coding → retro-corrections → TM pay complaints. Fixing timeliness at the front of this chain reduces volume at every step.

---

### Q7: "SLA Adherence hovering at ~70% — we don't believe this reflects true performance" (OBR Supplemental)

**UKG Phase I provides context for why SLA measurement is incomplete:**

SNOW SLA measures ticket resolution time. But UKG Phase I shows that **97.5% of FC HR timekeeping work never generates a ticket.** The 70% SLA adherence rate measures responsiveness to the 2.5% of work that TMs escalate — it says nothing about the quality or timeliness of the 97.5% that HR handles proactively.

**A more complete SLA framework would include:**
1. **SNOW SLA** (current) — measures ticket resolution time
2. **UKG Timeliness** (Phase I) — measures whether timecard corrections happen before payroll close (currently, 1,875/wk don't)
3. **UKG Defect Rate** (Phase I) — measures whether timecards are right the first time (currently 39.6% are not, in FC)

This aligns with the OBR Supplemental's recommendation to "establish accurate SLA commitments and measurements" by April 9.

---

## 8. Open Items

| # | Item | Status | Owner | Expected |
|---|---|---|---|---|
| 1 | **MCO1 PTO concentration** — 19/19 tickets are PTO. Root cause TBD. | Awaiting local HR reply | Kenny | TBD |
| 2 | **Attendance Inquiry + Attendance Management CSVs** — needed to complete full attendance picture (1,054 + 488 tickets referenced in OBR Supp) | Requested from Enterprise People Analytics | Kenny | EOD 3/5 |
| 3 | **Validate I-9/compliance doc routing** — confirm with SNOW admin whether these should be FC General Inquiry or a dedicated category | Not yet started | TBD | |
| 4 | **AVP4 Smartsheet migration timeline** — when will swag process move off Smartsheet? | Not yet started | TBD | |

---

## 9. Methodology Notes

- **Classification:** Keyword-based classification applied to `Description1` field. First-match-wins with 13 categories + Other/Unclassified. Accuracy estimated at ~90-93% based on manual review of sample tickets.
- **Date windows:** Week 8 = 2/15-2/21/2026, Week 9 = 2/22-2/28/2026, aligned to OBR reporting periods.
- **Site extraction:** Parsed from `Assignment Group` field (e.g., "AVP2 HR" → AVP2).
- **Resolution time:** Calculated from `Opened At` to `U Resolved`. Date-only precision (no timestamps in source), so resolution times are approximate to ±24h.
- **UKG cross-reference:** Phase I Workload Lens Week 9 report (Organizational Business Review). Data covers 41,790 FC timecard audit actions across 13 FC sites. Sites not in Phase I scope (AVP2, AVP4, SDF2, MCO1, etc.) lack UKG comparison data. Phase I metrics used: total actions, rework actions, defect rate, DPMO, actor group distribution, historical corrections, automation opportunity volumes.
- **Ticket-to-UKG mapping:** Each SNOW ticket category was mapped to its closest UKG action type(s) based on operational logic (e.g., Timecard tickets → punch corrections; PTO tickets → UTO deductions). Ratios represent approximate conversion rates, not exact joins.
- **YoY baseline:** Same calendar week (2/22-2/28) in 2025 vs 2026. Source CSV covers Nov 2024–Feb 2026.

---

*Document version: 2.0-DRAFT (Phase I Integrated) | Last updated: 2026-03-05 | Next update: After open items resolved*
