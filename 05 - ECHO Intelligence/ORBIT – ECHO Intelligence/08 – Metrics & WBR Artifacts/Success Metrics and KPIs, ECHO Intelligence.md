# Success Metrics & KPIs, ECHO Intelligence

| Field | Value |
| --- | --- |
| **Product** | ECHO Intelligence |
| **Platform** | ORBIT Phoenix |
| **Product Owner** | Kenny Wallace |
| **Version** | 1.0 |
| **Last Updated** | 2026-03-17 |

---

## 1. Purpose

This document defines the success metrics, KPIs, and measurement approach for ECHO Intelligence. Metrics are organized into four categories: pipeline health, report quality, stakeholder adoption, and workforce impact.

---

## 2. Pipeline Health Metrics

| Metric | Definition | Calculation | Target | Frequency |
| --- | --- | --- | --- | --- |
| **Source Coverage** | % of active FC listening channels captured | Sources with > 0 rows / Total active sources × 100 | 100% | Per pipeline run |
| **Site Coverage** | Number of FC sites with data in output | `COUNT(DISTINCT SITE_CODE) WHERE BUSINESS_UNIT = 'FC'` | 13/13 | Per pipeline run |
| **Signal Volume** | Total FC signals in reporting period | `COUNT(*) WHERE BUSINESS_UNIT = 'FC'` | Track trend; no fixed target | Per pipeline run |
| **Dedup Effectiveness** | VOC Board duplicates successfully excluded | Count of VOC Board rows removed by `NOT EXISTS` / Total VOC Board rows before dedup × 100 | > 0% (confirms dedup is active) | Per pipeline run |
| **Filler Filter Rate** | Survey filler responses excluded | Count of excluded filler rows / Total raw survey rows × 100 | Track; validate exclusion list completeness | Quarterly |
| **Null Rate** | % of output rows with NULL in required columns | Count of NULLs in `SITE_CODE`, `VOICE_MECHANISM`, `ROW_DATE`, `PRIMARY_TEXT` / Total rows × 100 | 0% | Per pipeline run |
| **Escalation Flag Rate** | % of signals flagged for ER review | Count of non-NULL `LEGACY_REGEX_ESCALATION` / Total rows × 100 | Track trend; review with ER | Per pipeline run |

---

## 3. Report Quality Metrics

| Metric | Definition | Calculation | Target | Frequency |
| --- | --- | --- | --- | --- |
| **Data Accuracy** | All report figures verified against source CSV | Number of verified figures / Total figures in report × 100 | 100% | Per report |
| **Narrative Consistency** | All narrative percentage and count references match data | Number of consistent references / Total references × 100 | 100% | Per report |
| **Structural Completeness** | All required report sections present | Sections present / Sections in template × 100 | 100% | Per report |
| **Time to Publish** | Elapsed time from data extraction to published report | Calendar days from pipeline execution to final distribution | Reduce each iteration | Per report |
| **Correction Rate** | Number of post-publication corrections needed | Count of corrections after initial distribution | 0 | Per report |

---

## 4. Stakeholder Adoption Metrics

| Metric | Definition | Calculation | Target | Frequency |
| --- | --- | --- | --- | --- |
| **Distribution Reach** | Number of unique stakeholders who receive the report | Count of recipients | All FC GMs + HRMs + Network Leadership | Per report |
| **Engagement Rate** | % of recipients who open/reference the report | Self-reported or tracked via distribution platform | Baseline year; track trend | Per report |
| **Action Plan References** | Number of site action plans that cite ECHO Intelligence data | Count of plans referencing report insights | Track; establish baseline | Quarterly |
| **Feedback Received** | Stakeholder feedback on report usefulness | Count and themes of feedback submissions | Collect systematically | Per report |

---

## 5. Workforce Impact KPIs

These are lagging indicators that measure whether ECHO Intelligence insights translate into workforce outcomes.

| KPI | Definition | Measurement Approach | Timeline |
| --- | --- | --- | --- |
| **Signal Trend Improvement** | Reduction in opportunity-area signal rates at sites that received targeted interventions | Compare category percentages pre- vs. post-intervention | 6–12 month lag |
| **Listening Infrastructure Growth** | Increase in unique mechanisms at sites identified as having listening gaps | Track mechanism counts per site over time | Quarterly |
| **Cross-Site Pattern Resolution** | Action cluster recommendations acted upon and resolved | Track cluster membership changes; sites moving out of high-alert clusters | Quarterly |
| **Positive Signal Growth** | Increase in positive signal rate network-wide | Compare positive signal % period-over-period | Per reporting period |
| **Safety Incident Correlation** | Relationship between safety signal rates and actual safety incidents | Cross-reference ECHO safety signals with safety incident data (if available) | Annual |

---

## 6. Network Benchmark KPIs (2025 Baseline)

These baseline values serve as comparison points for future reporting periods:

| Category | 2025 Baseline (% of FC Signals) | Direction for Improvement |
| --- | --- | --- |
| Safety | 7.2% | Decrease (fewer safety concerns) |
| Equipment | 10.8% | Decrease (better equipment availability) |
| Facility | 9.0% | Decrease (improved facility conditions) |
| Policy | 11.6% | Decrease (better policy perception) |
| Rotation | 2.3% | Decrease (better cross-training) |
| Positive | 10.9% | Increase (more positive sentiment) |

---

## 7. Site-Level KPIs (2025 Baseline)

| Site | Total Signals | Unique Mechanisms | Top Opportunity Category | Top Rate |
| --- | --- | --- | --- | --- |
| RNO1 | 2,203 | 12 | Facility | 15.9% |
| MCO1 | 2,031 | 14 | Rotation | 4.2% |
| AVP2 | 1,828 | 13 | Equipment | 18.6% |
| AVP1 | 1,866 | 13 | Policy | 16.8% |
| BNA1 | 1,636 | 12 | Facility | 10.8% |
| PHX1 | 1,545 | 13 | Equipment | 16.1% |
| CLT1 | 1,580 | 14 | Equipment | 16.0% |
| MCI1 | 1,378 | 13 | Policy | 24.2% |
| HOU1 | 1,224 | 5 | Listening Gap | 5 mechanisms |
| DAY1 | 1,311 | 13 | Rotation | 4.4% |
| MDT1 | 1,120 | 13 | Equipment | 17.4% |
| CFC1 | 939 | 13 | Facility | 11.9% |
| DFW1 | 397 | 2 | Listening Gap | 2 mechanisms |

---

## 8. Measurement Cadence

| Timeframe | Activities |
| --- | --- |
| **Per pipeline run** | Validate pipeline health metrics (source coverage, site coverage, null rate) |
| **Per report** | Validate report quality metrics (accuracy, consistency, completeness) |
| **Quarterly** | Review stakeholder adoption; assess filler filter effectiveness; review mechanism names |
| **Semi-annually** | Assess workforce impact KPIs; update network benchmarks |
| **Annually** | Full product review: ROI assessment, pipeline evolution planning, stakeholder satisfaction |
