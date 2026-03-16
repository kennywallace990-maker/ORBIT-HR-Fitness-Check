# ROI Narrative, TMDM Paycode Reconciler

| Field | Value |
| --- | --- |
| **Product** | TMDM Paycode Reconciler |
| **Platform** | ORBIT Phoenix |
| **Product Owner** | Kenny Wallace |
| **Version** | 1.0 |
| **Last Updated** | 2026-03-04 |

---

## 1. ROI Framework

The return on investment for the TMDM Paycode Reconciler is not limited to time savings. It is driven by three compounding value layers:

1. **Comprehensive coverage** — The product examines every instance where time-off paycodes may have been over-applied and explains what drove each defect, replacing targeted spot-checks with full-population reconciliation.
2. **Defect prevention before payroll close** — Every over-applied paycode instance that is not corrected before payroll closes generates downstream rework across multiple teams. Each defect prevented is rework eliminated.
3. **Faster detection cadence** — Daily automated surfacing replaces weekly or periodic manual audits, shrinking the window in which leakage can occur undetected.

These layers are additive. Even if audit time savings were modest, the value of catching defects that would otherwise be missed — and catching them earlier — produces meaningful ROI on its own.

---

## 2. How TMDM Operates Today

TMDM is the enterprise backstop for timecard accuracy. Ideally, local HR catches and corrects paycode issues daily as part of normal timekeeping oversight. TMDM's role is to catch the instances that local HR did not — ensuring nothing reaches payroll close uncorrected.

To fulfill this responsibility, TMDM currently performs two primary audit activities:

### 2.1 Meal Break Audit (Primary Weekly Audit)

TMDM runs a UKG report and exports it to CSV to identify instances where approximately 30 minutes or more of time was over-applied, which can indicate that a meal break was taken but the corresponding time was not properly deducted. This is the audit that accounts for the bulk of the ~22 hours/week of manual effort.

**How it works:**

- The report surfaces rows where total hours appear higher than expected based on the schedule.
- TMDM manually filters, sorts, and reviews individual timecards in UKG to determine whether an actual over-application occurred.
- The report does not show which time-off paycodes were applied, so TMDM cannot distinguish between paycode-driven issues and benign situations (e.g., a team member clocking in a few minutes early or staying slightly late).

**What this approach covers well:**

- High-volume scan of the enterprise population for meal-break-related overages.

**Where coverage gaps exist:**

- Because the audit is oriented around a ~30-minute threshold associated with meal breaks, over-applications that do not fit this pattern — such as a full PTO day applied on a day the team member also worked a full shift — may not be flagged.
- Without paycode-level detail, TMDM cannot prioritize by risk type (e.g., PTO overpayment vs. unpaid time compliance).

### 2.2 Twelve-Hour Time-Off Audit (Secondary Weekly Audit)

Separately, TMDM runs a weekly audit that identifies team members with 12 or more hours of time-off applied in a single entry. This audit is designed to catch coding errors — for example, a time-off entry keyed as PM instead of AM, resulting in a duration that spans far longer than intended.

**How it works:**

- The audit is run once per week.
- It is a quick review and does not consume significant time.

**Where coverage gaps exist:**

- The 12-hour threshold means coding errors that produce smaller but still incorrect durations (e.g., 8 or 10 hours over-applied) are not surfaced by this audit.
- The weekly cadence means an error entered on Monday may not be reviewed until the following week, leaving several days for the defect to persist uncorrected through payroll close.

---

## 3. What the Paycode Reconciler Changes

The TMDM Paycode Reconciler does not replace TMDM's judgment or expertise — it replaces the manual discovery process with a comprehensive, automated one. The key differences:

| Dimension | Current State | With Paycode Reconciler |
| --- | --- | --- |
| **Scope of detection** | Meal-break-oriented threshold (~30 min) + 12-hour outlier check | Every instance where time-off applied exceeds the gap between scheduled and worked hours, regardless of magnitude |
| **Paycode visibility** | UKG report does not show which paycodes were applied | Every defect row includes the specific paycodes and durations, enabling instant diagnosis |
| **Root cause clarity** | TMDM must open each timecard in UKG to determine what happened | The product tells the user what drove the over-application (which paycodes, how many hours, recommended reduction) |
| **Risk prioritization** | No risk tiering; all rows treated equally | PTO-driven defects ranked highest; high-priority flag for >= 4 hours over-applied |
| **Detection cadence** | Meal break audit: weekly manual. 12-hour audit: weekly. | Daily automated refresh (target: by 7 AM ET) |
| **Population coverage** | Full enterprise population, but filtered through threshold-based heuristics | Full enterprise population with no threshold floor — any over-application is surfaced |

---

## 4. The Three ROI Dimensions

### 4.1 Audit Efficiency (Time Savings)

This is the most visible ROI dimension and the one TMDM validated during the pilot.

| Metric | Value |
| --- | --- |
| Baseline weekly audit hours | ~22 hrs/week |
| Estimated reduction | ~60% |
| Projected weekly hours saved | ~13 hrs/week |
| Projected annual hours saved | ~676 hrs/year |
| FTE equivalent (at 2,080 hrs/yr) | ~0.33 FTE capacity reinvested |

The time savings come from eliminating manual CSV filtering, removing the need to open timecards that do not actually have issues, and grouping all defects per team member so each timecard is visited only once.

### 4.2 Expanded Defect Coverage (Quality Improvement)

This is the highest-impact ROI dimension. The current audit process is effective within its design parameters, but those parameters create natural coverage boundaries:

- **Meal break audit** is optimized for ~30-minute overages. Over-applications that are larger or smaller than this pattern — such as a full PTO day applied on a day the team member worked, or a 15-minute coding error — may not be surfaced.
- **12-hour audit** catches extreme outliers but misses coding errors in the 1–11 hour range.
- **Neither audit** provides paycode-level detail, so even when a row is flagged, TMDM must manually investigate to determine whether it is a true defect and what type of correction is needed.

The Paycode Reconciler eliminates these coverage gaps by evaluating every team member, every day, against the full reconciliation formula:

```sql
over_applied_hours = MAX(0, timeoff_applied - MAX(0, scheduled_eligible - worked))
```

Any non-zero result is a defect — regardless of magnitude, paycode type, or pattern. During the pilot, TMDM confirmed that the Paycode Reconciler surfaced defects that did not appear on the legacy UKG report at all.

**Why this matters for ROI:**

Every defect that is not caught before payroll close generates downstream work:

- **TMDM** must investigate and initiate a correction after the fact.
- **Field HR** must coordinate with the team member and their leader.
- **Payroll** must process a refund or adjustment.
- **The team member** experiences a paycheck correction, which impacts trust and creates additional inquiries.

This multi-team rework is estimated at 1–3 hours per incident. By catching defects that the current process misses — not because the current process is flawed, but because its design scope does not cover every scenario — the Paycode Reconciler prevents rework that would otherwise be invisible until after payroll close.

### 4.3 Faster Detection Cadence (Leakage Reduction)

Even for defects that the current process would eventually catch, the Paycode Reconciler catches them sooner.

- The meal break audit runs weekly. A defect entered on Monday may not be reviewed until the following week.
- The 12-hour audit runs once per week.
- The Paycode Reconciler refreshes daily, surfacing new defects each morning.

This matters because payroll has a fixed close window. A defect that exists for 5 days before detection has 5 days of risk that it will not be corrected in time. A defect detected the next morning has a much higher probability of pre-payroll correction.

**Leakage** in this context means: defects that existed, were theoretically detectable, but were not surfaced in time to be corrected before payroll closed. The daily cadence of the Paycode Reconciler shrinks this leakage window from up to 7 days to approximately 1 day (T-1 data latency).

---

## 5. Combined ROI Impact

| ROI Dimension | Value Driver | Measurement Approach |
| --- | --- | --- |
| **Audit Efficiency** | ~13 hrs/week saved; TMDM capacity reinvested into higher-value work | TMDM self-reported time tracking, before vs. after |
| **Expanded Coverage** | Net-new defects caught that current audits do not surface; each prevented defect avoids 1–3 hrs of multi-team rework | Compare ORBIT defect list to legacy UKG report per pay period; track post-payroll ticket volume |
| **Faster Cadence** | Defects surfaced daily instead of weekly; higher pre-payroll capture rate | Pre-payroll corrections / total corrections × 100; trend over time |

### Illustrative Scenario

Assume the Paycode Reconciler catches just **5 additional defects per week** that the current process would have missed. At an estimated **2 hours of cross-team rework per defect**:

- **10 hours/week** of rework avoided = **520 hours/year** across TMDM, Field HR, Payroll, and the affected team members.
- Combined with the **676 hours/year** of direct audit time savings, the total capacity impact approaches **~1,200 hours/year** — more than **0.5 FTE equivalent** of capacity returned to the organization.

This is a conservative estimate. The actual number of missed defects and rework hours per defect may be higher once post-payroll ticket data is integrated for measurement.

---

## 6. What This Is Not

This ROI narrative does not suggest that TMDM's current process is inadequate. The meal break audit and 12-hour audit are well-established practices that have served the organization effectively. They were designed to catch specific, high-frequency defect patterns — and they do.

The opportunity is that paycode over-application is a broader problem than any single heuristic can fully cover. The Paycode Reconciler applies a comprehensive, formula-based approach that covers the full spectrum of over-application scenarios — including those the existing audits were not designed to detect. It is an evolution of the same mission TMDM already owns: ensuring enterprise timecards are accurate before payroll close.

---

## 7. Recommended ROI Measurement Plan

| Phase | Timing | Action |
| --- | --- | --- |
| **Baseline** | Pre-production (now) | Document current weekly audit hours, current defect counts from UKG reports, and current post-payroll ticket volume from Payroll |
| **Week 1–4** | Post-production launch | Track TMDM audit hours weekly; run ORBIT and legacy UKG report in parallel to measure defect coverage delta |
| **Week 4–8** | Steady state | Discontinue parallel UKG run if coverage delta is consistently positive; begin tracking pre- vs. post-payroll capture rate |
| **Week 8+** | Ongoing | Integrate Payroll ticket data; calculate rework reduction; report monthly ROI to stakeholders |

---

## 8. Key Assumptions

1. Local HR is the first line of defense for daily timecard accuracy. TMDM serves as the enterprise backstop to catch what local HR did not address.
2. Every over-applied paycode instance not corrected before payroll close generates measurable downstream rework.
3. The Paycode Reconciler's comprehensive, formula-based detection will surface a meaningful number of defects beyond what the current threshold-based audits catch.
4. Daily data refresh (T-1) provides sufficient timeliness for pre-payroll correction.
5. Rework cost estimates (1–3 hours per defect across teams) are conservative and will be refined with actual Payroll ticket data.
