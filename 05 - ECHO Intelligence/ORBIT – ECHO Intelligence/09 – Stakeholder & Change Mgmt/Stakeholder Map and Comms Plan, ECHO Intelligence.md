# Stakeholder Map & Comms Plan, ECHO Intelligence

| Field | Value |
| --- | --- |
| **Product** | ECHO Intelligence |
| **Platform** | ORBIT Phoenix |
| **Product Owner** | Kenny Wallace |
| **Version** | 1.0 |
| **Last Updated** | 2026-03-17 |

---

## 1. Purpose

This document identifies ECHO Intelligence stakeholders, defines their relationship to the product, and outlines the communications plan for report distribution, feedback collection, and change management.

---

## 2. Stakeholder Map

### 2.1 Stakeholder Categories

| Category | Role | Engagement Level | Information Need |
| --- | --- | --- | --- |
| **Product Owner** | Owns pipeline, report generation, documentation, and product roadmap | Active — builds and maintains | Full technical and business context |
| **FC Site Leadership (GMs, HRMs)** | Primary consumers; act on site-level insights | Active — reads and acts | Site-specific data, benchmarks, actionable recommendations |
| **FC Network Leadership (Sr. Directors, VPs)** | Strategic consumers; use cross-site insights for investment decisions | Informed — reads and decides | Network trends, cross-site comparisons, priority matrix, strategic recommendations |
| **Enterprise People Analytics (EPA)** | Data pipeline steward; future automated pipeline owner | Collaborative — builds data infrastructure | Schema requirements, data quality, pipeline specifications |
| **Employee Relations (ER)** | Escalation partner for flagged signals | Consulted — reviews flagged content | Escalation flags, regex pattern effectiveness, individual signal review |
| **Phoenix / ORBIT Engineering** | Platform team for future agent integration | Informed — plans future work | Technical architecture, integration requirements |

### 2.2 RACI Matrix

| Activity | Product Owner | FC Site Leadership | FC Network Leadership | EPA | ER | Phoenix/ORBIT |
| --- | --- | --- | --- | --- | --- | --- |
| Pipeline execution | **R/A** | — | — | C | — | — |
| Report generation | **R/A** | — | — | — | — | — |
| Report review & approval | **R** | — | **A** | — | — | — |
| Report distribution | **R** | I | I | I | I | — |
| Site-level action planning | I | **R/A** | I | — | — | — |
| Escalation review | I | — | — | — | **R/A** | — |
| Pipeline maintenance | **R/A** | — | — | C | — | C |
| EPA pipeline migration | C | — | I | **R/A** | — | C |
| Regex pattern updates | **R** | — | — | — | **A** | — |
| New source integration | **R/A** | — | I | C | — | — |

**R** = Responsible, **A** = Accountable, **C** = Consulted, **I** = Informed

---

## 3. Communications Plan

### 3.1 Report Distribution

| Audience | Channel | Frequency | Format | Owner |
| --- | --- | --- | --- | --- |
| FC Site Leadership | Email + SharePoint | Per reporting cycle | HTML report (or PDF export) | Product Owner |
| FC Network Leadership | Email + SharePoint | Per reporting cycle | HTML report + executive summary | Product Owner |
| EPA | SharePoint | Per reporting cycle | HTML report + pipeline run summary | Product Owner |
| ER | Direct email | As needed (when escalation signals flagged) | Filtered signal list | Product Owner |

### 3.2 Feedback Collection

| Mechanism | Audience | Frequency | Purpose |
| --- | --- | --- | --- |
| Post-distribution survey (2–3 questions) | FC Site Leadership | Per report | Measure usefulness, accuracy perception, actionability |
| Direct feedback channel (email or Teams) | All stakeholders | Ongoing | Ad-hoc questions, corrections, enhancement requests |
| Quarterly review meeting | FC Network Leadership + EPA | Quarterly | Review product effectiveness, discuss roadmap, align priorities |

### 3.3 Change Notifications

| Change Type | Notification Audience | Lead Time | Channel |
| --- | --- | --- | --- |
| New site added to report | FC Network Leadership, affected site GM/HRM | 1 week before next report | Email |
| New source table integrated | All stakeholders | 2 weeks before next report | Email + documentation update |
| Report format/structure change | All stakeholders | 1 week before next report | Email with changelog |
| EPA pipeline migration | All stakeholders | 4 weeks before cutover | Email + meeting |
| Escalation regex pattern change | ER | Before deployment | Direct coordination |

---

## 4. Adoption Strategy

### 4.1 Phase 1: Introduction (Current)

| Activity | Target | Timeline |
| --- | --- | --- |
| Distribute 2025 VOC Pulse Report to FC leadership | All 13 site GMs and HRMs | Immediately |
| Walkthrough session with Network Leadership | Sr. Directors, VPs | Within 1 week of distribution |
| Collect initial feedback | Site Leadership | Within 2 weeks of distribution |

### 4.2 Phase 2: Integration into Workflows

| Activity | Target | Timeline |
| --- | --- | --- |
| Align report cadence with FC business review cycle | Network Leadership | Q2 2026 |
| Include ECHO Intelligence data in site action planning templates | Site Leadership | Q2 2026 |
| Establish recurring report distribution process | Product Owner | Q2 2026 |

### 4.3 Phase 3: Expansion

| Activity | Target | Timeline |
| --- | --- | --- |
| Expand to Rx network site-level analysis | Rx Leadership | Q3 2026 (pending FC stabilization) |
| Integrate with Phoenix agent for ad-hoc queries | All stakeholders | Pending EPA pipeline + Phoenix integration |
| Automated report delivery | All stakeholders | Pending automation development |

---

## 5. FAQ & Guardrails

### 5.1 Frequently Asked Questions

| Question | Answer |
| --- | --- |
| **Where does the data come from?** | Five Snowflake tables capturing TM feedback from VOC Boards, CAT Tracker, Standups, New Hire Surveys, and Week 3 Surveys. |
| **How current is the data?** | Data reflects the reporting period specified in the query (currently Jan–Jun 2025). Source tables are updated by EPA's data loads. |
| **Can I see individual TM comments?** | The report presents aggregated data only. Raw signal-level data is available to authorized users via Snowflake. |
| **How are categories assigned?** | Categories come from the source systems (site leaders assign them in the CAT Tracker and VOC Board). Survey categories are contextual metadata. |
| **What does the escalation flag mean?** | The legacy regex flag is a screening tool that identifies signals potentially relevant to ER. It does not confirm any violation — ER conducts independent review. |
| **How do I request a change to the report?** | Contact the Product Owner (Kenny Wallace) with specific feedback or enhancement requests. |
| **Will there be a next version?** | Yes. The pipeline will be automated by EPA, and future reports will follow the same structure with updated data. |

### 5.2 Guardrails

| Guardrail | Rationale |
| --- | --- |
| **Do not share raw signal data outside authorized channels** | `PRIMARY_TEXT` may contain incidental PII and sensitive workplace observations |
| **Do not use escalation flags as evidence of wrongdoing** | Regex flags are screening tools only; false positives are expected |
| **Do not compare sites solely on total signal volume** | Higher volume may indicate better listening infrastructure, not worse conditions |
| **Do not use report data for individual TM performance evaluation** | Report is aggregate workforce intelligence, not individual assessment |
| **Always cite the reporting period when referencing data** | Data is time-bound; trends may change in subsequent periods |
