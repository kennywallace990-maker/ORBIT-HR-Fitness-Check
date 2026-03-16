# Value Scorecard, TMDM Paycode Reconciler

| Field | Value |
| --- | --- |
| **Product** | TMDM Paycode Reconciler |
| **Platform** | ORBIT Phoenix |
| **Product Owner** | Kenny Wallace |
| **TMDM Sponsor** | Jen Hudson |
| **Version** | 1.0 |
| **Last Updated** | 2026-03-03 |

---

## 1. Value Proposition

The TMDM Paycode Reconciler replaces a manual, 22-hour/week enterprise timecard audit with an automated, exception-driven workflow that detects over-applied time-off paycodes before payroll close. It reduces audit effort, catches defects the legacy UKG report misses, and eliminates multi-team post-payroll rework.

---

## 2. Business Problem Quantified

| Metric | Current State | Source |
| --- | --- | --- |
| Weekly audit hours | ~22 hours/week | TMDM team tracking |
| Rows reviewed manually per week | ~19,000 rows | UKG export volume |
| Defect detection method | Manual CSV review in UKG; no paycode-level visibility | TMDM process documentation |
| Defects missed by legacy report | Unknown (pilot revealed net-new defects) | Pilot observation, 2026-02-25 |
| Post-payroll rework teams involved | TMDM + Field HR + Payroll + TM | Payroll escalation process |
| Rework cost per defect (estimated) | Multi-hour effort across 4 teams per incident | Operational estimate |

---

## 3. ROI Model

> For the full ROI narrative including current-state audit details, coverage gap analysis, and illustrative scenarios, see **ROI Narrative, TMDM Paycode Reconciler.md**.

ROI is driven by three compounding value layers:

### 3.1 Audit Efficiency (Direct Time Savings)

| Input | Value | Notes |
| --- | --- | --- |
| Baseline weekly audit hours | 22 hrs/week | TMDM current state |
| Target reduction | 60% | Based on pilot feedback |
| Projected weekly hours saved | ~13 hrs/week | 22 × 0.60 |
| Projected annual hours saved | ~676 hrs/year | 13 × 52 |
| FTE equivalent (at 2,080 hrs/yr) | ~0.33 FTE | Capacity reinvested, not headcount reduction |

### 3.2 Expanded Defect Coverage (Quality Improvement)

TMDM currently performs two targeted audits — a meal break audit (~30 min threshold) and a 12+ hour time-off audit (weekly, catches coding errors like PM vs. AM). These are effective within their design scope but leave coverage gaps for over-applications outside those patterns. The Paycode Reconciler evaluates every team member, every day, against the full reconciliation formula — surfacing defects the current audits were not designed to detect.

| Input | Value | Notes |
| --- | --- | --- |
| Estimated net-new defects caught per week | TBD — measure post-productionization | Pilot confirmed net-new defects vs. UKG report |
| Estimated rework hours avoided per defect | 1–3 hrs across TMDM + Field HR + Payroll + TM | Cross-team resolution estimate |
| Estimated financial risk per defect | Varies by over-applied hours × hourly rate | PTO over-application = direct overpayment |
| Illustrative impact (5 net-new defects/week × 2 hrs) | ~520 hrs/year of rework avoided | Conservative estimate |

### 3.3 Faster Detection Cadence (Leakage Reduction)

Current audits run weekly, leaving up to 7 days for a defect to persist uncorrected through payroll close. The Paycode Reconciler refreshes daily (T-1), shrinking the leakage window to ~1 day and increasing the pre-payroll capture rate.

### 3.4 Combined Impact

| Dimension | Annual Hours Impact | Source |
| --- | --- | --- |
| Audit efficiency | ~676 hrs/year saved | Direct TMDM time savings |
| Expanded coverage | ~520 hrs/year rework avoided | Conservative: 5 net-new defects/week × 2 hrs |
| **Total** | **~1,200 hrs/year (~0.5+ FTE)** | Combined capacity returned to the organization |

### 3.5 Intangible Value

- **Improved compliance posture:** Proactive detection reduces regulatory and audit risk.
- **Standardized workflow:** Exception-driven queue replaces ad hoc CSV review.
- **Scalable pattern:** Validates the ORBIT Phoenix model for future HRSS/COE products.
- **Team member experience:** Faster resolution means fewer surprise paycheck adjustments for TMs.

---

## 4. Success Metrics

| Metric | Definition | Baseline | Target | Measurement Method |
| --- | --- | --- | --- | --- |
| **Audit Time Reduction** | Weekly TMDM hours spent on paycode audits for FC and Rx | 22 hrs/week | ~9 hrs/week (60% reduction) | TMDM self-reported time tracking, before vs. after |
| **Pre-Payroll Capture Rate** | % of defects resolved before payroll close vs. discovered after | Unknown (no baseline) | >80% of defects resolved pre-payroll | Compare ORBIT defect list to post-payroll Payroll tickets |
| **Total Over-Applied Hours** | Sum of all over-applied hours detected per pay period | Not previously tracked | Track trend; reduce period-over-period | `SUM(over_applied_hours)` from reconciliation query |
| **Defect Coverage Delta** | Net new defects found by ORBIT that were absent from the legacy UKG report | 0 (UKG-only baseline) | >0 net new per pay period | Side-by-side comparison: ORBIT output vs. UKG export |
| **Rework Reduction** | Decrease in post-payroll Payroll/HR tickets for time-off over-application | TBD — baseline from Payroll ticket data | Meaningful % reduction | Payroll ticket system (ServiceNow or equivalent) |

---

## 5. KPI Definitions

| KPI | Calculation | Owner | Frequency |
| --- | --- | --- | --- |
| **Audit Time Reduction** | `baseline_hours (22) - actual_hours_spent` | TMDM | Weekly |
| **Pre-Payroll Capture Rate** | `pre_payroll_corrections / (pre + post_corrections) × 100` | TMDM + Payroll | Per pay period |
| **Total Over-Applied Hours** | `SUM(over_applied_hours)` from production query | Phoenix / ORBIT | Per pay period |
| **Defect Coverage Delta** | `ORBIT_defects - UKG_report_defects` | Phoenix / ORBIT | Per pay period |
| **High-Risk Defect Rate** | `COUNT(high_risk) / COUNT(total) × 100` | Phoenix / ORBIT | Per pay period |
| **Defects per Location** | `COUNT(*) GROUP BY location` | Phoenix / ORBIT | Per pay period |
| **Repeat Offender Rate** | `COUNT(employees with 2+ defects) / COUNT(total unique employees) × 100` | Phoenix / ORBIT | Per pay period |
| **Average Over-Applied Hours per Defect** | `SUM(over_applied_hours) / COUNT(defects)` | Phoenix / ORBIT | Per pay period |

---

## 6. Pilot Results Summary

| Finding | Detail |
| --- | --- |
| **Pilot period** | Pay period ending week of 2026-02-25 |
| **Defects surfaced** | ~492 defect rows across FC, Rx, CC, and Other |
| **Networks covered** | FC (majority), Rx, CC, Other |
| **High-priority defects** | Multiple cases with 8–16+ hours over-applied (HIGH PRIORITY classification) |
| **Net new defects** | TMDM confirmed defects found by ORBIT that did not appear on the legacy UKG report |
| **TMDM feedback** | Report correctly prioritized cases; workflow significantly faster than manual CSV review |
| **Estimated time savings** | ~60% reduction in weekly audit effort indicated by TMDM validation partners |

---

## 7. Value Realization Timeline

| Phase | Timeframe | Value Delivered |
| --- | --- | --- |
| **Phase 1: Pilot** (Complete) | 2026-02 | Proof of concept; validated detection accuracy and workflow fit; demonstrated net-new defect coverage |
| **Phase 2: Productionization** (In Progress) | 2026-Q1/Q2 | Daily automated refresh; hardened agent with 16 prompt types; FC + Rx primary scope with CC/Other secondary |
| **Phase 3: ROI Measurement** | 2026-Q2/Q3 | Integrate Payroll ticket data; quantify pre- vs. post-payroll capture rate; calculate financial impact |
| **Phase 4: Expansion** | 2026-Q3+ | Extend to additional paycode types; automated routing; potential expansion to additional populations |

---

## 8. Cost to Build and Operate

| Cost Category | Estimate | Notes |
| --- | --- | --- |
| **Initial build** | ~2 hours (pilot) | Leveraged existing Phoenix paycode reconciliation logic |
| **Productionization** | TBD | Includes agent hardening, SQL optimization, refresh automation, documentation |
| **Ongoing compute** | Minimal | Single Snowflake query per agent invocation; no persistent materialization (yet) |
| **Maintenance** | Low | Paycode list review quarterly; SQL updates as UKG schema evolves |

---

## 9. Strategic Alignment

| 2026 HR Transformation Pillar | How This Product Contributes |
| --- | --- |
| **Pillar 1: Leveraging Automation and Intelligence to Scale HR** | Proves exception-driven, automation-first workflow on Phoenix for HRSS/TMDM. Creates a repeatable pattern for future COE ORBIT products. |
| **Operational Discipline** | Shifts paycode reconciliation from reactive post-payroll rework to proactive pre-payroll correction. |
| **Scalable HR Infrastructure** | Eliminates manual CSV processing; capacity gains reinvested into field coaching, engagement, and risk mitigation. |
| **Data-Driven Decision Making** | Surfaces structured insights (KPIs, root cause, patterns) from raw UKG data that were previously invisible to TMDM. |

---

## 10. Risks to Value Realization

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Payroll ticket data unavailable for ROI measurement | Cannot quantify pre- vs. post-payroll capture rate | Partner with Payroll early to identify ticket data source and integration path |
| TMDM process change resistance | Adoption slower than expected; time savings not realized | Involve TMDM validation partners in design; provide user guide and training |
| Data refresh latency | TMDM works with stale data; corrections not reflected promptly | Target daily refresh by 7 AM ET; surface data freshness warnings in agent |
| Paycode list drift | New UKG paycodes not captured; false negatives | Quarterly review cadence with TMDM; monitoring for unknown paycode IDs |
