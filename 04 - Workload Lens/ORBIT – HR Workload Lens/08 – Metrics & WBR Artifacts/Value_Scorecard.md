# Value Scorecard: ORBIT HR Workload Lens

**Product:** Workload Lens (Phase I — Time & Attendance / UKG)
**Program:** ORBIT · Pillar 2 (Design & POC)
**Status:** Baseline (Pre-Launch)
**Version:** 1.0
**Last Updated:** 2026-03-03
**Owner:** Kenny Wallace, ORBIT Program Lead

---

## 1. Purpose

The Value Scorecard tracks whether Workload Lens is delivering measurable operational improvements after launch. It establishes baseline metrics during Pillar 2 (from early OBR runs against real data), sets targets for Pillar 4 (Launch & Measure), and provides a framework for ongoing reporting to ORBIT program leadership.

This document is a required gate artifact for Pillar 2 exit.

---

## 2. Value Thesis

Workload Lens creates value in three ways:

**Visibility:** Before Workload Lens, there was no centralized view of HR timecard workload. Stakeholders could not answer basic questions about defect rates, rework distribution, or site-level performance without manually pulling and analyzing data. The OBR provides this visibility weekly, automatically.

**Defect Reduction:** By surfacing which sites, actors, and processes generate the most rework, the OBR enables targeted coaching and process improvement. The hypothesis is that consistent visibility into defect rates drives behavioral change at the site level within 12 weeks.

**Time Recovery:** Every Bucket B (defect) action represents HR time spent correcting something that should have been right the first time. Reducing defect rates directly recovers HR capacity that can be redirected to proactive work (onboarding, engagement, training).

---

## 3. KPI Scorecard

### 3.1 Operational Metrics (Measured by the OBR)

| KPI | Baseline | 4-Week Target | 12-Week Target | Measurement Source |
|:---|:---|:---|:---|:---|
| Network Defect Rate % | TBD (first 4 weeks of OBR data) | Establish baseline | 10% reduction from baseline | Q1: DEFECT_RATE_PCT |
| Historical Correction Rate % | TBD | Establish baseline | 15% reduction from baseline | Q1: HIST_CORR_RATE_PCT |
| Comment Compliance Rate % | TBD (Feb 2026 data shows ~3.6%) | 25% | 85% | Q7: DOCUMENTATION_RATE_PCT |
| Friction Time Cost (FTE Hours/Week) | TBD | Establish baseline | 10% reduction from baseline | Q1: TOTAL_FRICTION_HRS |
| Sites Breaching UCL (Count/Week) | TBD | Establish baseline | 30% fewer breach sites from baseline | Q6: COUNT(IS_RED_SPIKE = TRUE) |

### 3.2 Product Delivery Metrics

| KPI | Target | Measurement |
|:---|:---|:---|
| Report Generation Reliability | 100% Monday delivery | Automated trigger success rate |
| Report Accuracy | Zero manual corrections to published OBR | Error count per week |
| Time to Publish | < 15 minutes from trigger to delivery | Elapsed time from Q1 start to report post |
| Query Execution Success | 100% (all 8 queries complete without error) | Agent halt rate |

### 3.3 Adoption Metrics

| KPI | 4-Week Target | 12-Week Target | Measurement |
|:---|:---|:---|:---|
| Stakeholder Engagement | 50% of site HR leads read the OBR weekly | 80% weekly readership | Confluence page views or email open rate |
| Drill-Down Usage | At least 10 interactive drill-down queries per week | 25+ per week | Phoenix conversation log count |
| Action Completion Rate | TBD | 50% of triggered recommendations result in documented actions | Manual tracking via Confluence comments or linked JIRA items |

---

## 4. Baseline Collection Plan

### 4.1 Baseline Window

The first 4 weeks of production OBR runs establish baseline values for all operational KPIs. During this window, no improvement targets apply. The purpose is to capture steady-state performance before any intervention.

### 4.2 Early Signal from POC Data

The v3 mock report (Feb 15 to 28, 2026 data window) provides an early signal, but it should not be treated as a formal baseline because the data window is 2 weeks (not a full reporting cycle), there is a known data gap from Jan 19 to Feb 15 that may affect 13-week baseline calculations, and the DPMO formula and actor group classifications have since been updated (v2.0 changes).

Early signal values from the mock report:
- Network Defect Rate: 31.4%
- Missing Punch Rate: 0.3%
- Historical Correction Rate: 2.7%
- Comment Compliance: 3.6% (well below 85% target — indicates either data extraction issue or widespread non-compliance)
- Total HR Workload: 80,693 actions
- Friction Time Cost: 1,029.2 FTE hours
- Top DPMO sites: ATLD (428.6), CLT1 (221.1), MDT1 (193.9) — note these are at ×1K scale, will be ×1M after update

### 4.3 Baseline Refresh

After the first 4 weeks of production data with the v2.0 classification rules applied, the baseline column in this scorecard will be updated and improvement targets will be finalized.

---

## 5. Value Attribution Model

### 5.1 Defect Reduction → Time Recovery

Each percentage point reduction in network defect rate translates to recovered HR capacity:

```
FTE Hours Recovered per Week = (Defect Rate Reduction %) × (Total Actions) × (Avg Friction Score) / 60
```

At the early signal volume of ~80,000 actions per week, each 1% reduction in defect rate with an average friction score of ~0.8 would recover approximately 10.7 FTE hours per week — roughly a quarter of a full-time equivalent redirected from rework to proactive HR work.

### 5.2 Comment Compliance → AI Insight Quality

Comment compliance directly affects the quality of AI-generated insights. Without comments, the agent can only describe what happened (action type, volume) but not why. Higher compliance enables root cause pattern detection, more specific coaching recommendations, and eventually predictive capabilities.

The target path is 3.6% (current) → 25% (4-week) → 85% (12-week). The 25% 4-week target reflects that much of the initial improvement will come from process communication and training, not system changes.

---

## 6. Risk Factors

| Risk | Impact | Mitigation |
|:---|:---|:---|
| Data gap (Jan 19 to Feb 15) distorts 13-week baseline | Spike flags may be inaccurate for first several weeks after backfill | Track backfill status with EDS; recalculate baselines after backfill |
| Comment compliance stays near 0% | AI insights remain shallow; stakeholder value perception drops | Investigate whether this is a data extraction issue vs. behavioral; if behavioral, run targeted training with site HR leads |
| Low OBR readership | Defect reduction hypothesis fails due to lack of engagement | Partner with HR Ops leadership to integrate OBR into existing Monday meeting cadence |
| DPMO threshold recalibration takes too long | Sites cannot be meaningfully ranked during calibration window | Use defect rate (%) as the primary ranking metric during the 4-week calibration period |
| Hire date field unavailable in V_PEOPLE | First-week TMs cannot be exempted from engagement list | Accept false positives during POC; escalate data engineering request |

---

## 7. Reporting Cadence

| Report | Frequency | Audience | Content |
|:---|:---|:---|:---|
| OBR (generated by agent) | Weekly (Monday) | Site HR leads, HR Ops leadership, ORBIT program team | Full 6-section report with appendices |
| Value Scorecard Update | Monthly | ORBIT program leadership, executive sponsors | This document updated with actuals vs targets |
| Quarterly Business Review | Quarterly | VP-level stakeholders | Cumulative value delivered, adoption trends, roadmap update |

---

## 8. Version History

| Version | Date | Author | Changes |
|:---|:---|:---|:---|
| 1.0 | 2026-03-03 | Kenny Wallace / ORBIT | Baseline scorecard. Operational, delivery, and adoption KPIs defined. Early signal values captured from v3 mock report. Value attribution model and risk factors documented. |
