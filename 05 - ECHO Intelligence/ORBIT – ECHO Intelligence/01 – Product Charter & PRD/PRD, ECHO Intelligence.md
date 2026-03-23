# PRD, ECHO Intelligence

| Field | Value |
| --- | --- |
| **Product** | ECHO Intelligence |
| **Platform** | ORBIT Phoenix |
| **Product Owner** | Kenny Wallace |
| **Sponsor** | Enterprise People Analytics |
| **Version** | 1.0 |
| **Last Updated** | 2026-03-17 |
| **Status** | Production; interim SQL pipeline pending EPA automated pipeline |

---

## 1. Executive Summary

ECHO Intelligence is an ORBIT product that aggregates, normalizes, and analyzes Voice of the Chewtopian (VOC) signals across the Fulfillment Center (FC) network to produce actionable, site-level workforce intelligence. It unifies five distinct listening channels — the CAT Tracker, VOC Boards, Standups, New Hire Surveys, and Week 3 Surveys — into a single 15-column schema, enabling cross-source analysis of team member sentiment, safety concerns, equipment issues, policy perceptions, and leadership effectiveness.

The product currently operates on an **interim SQL pipeline** that extracts and unifies data from five Snowflake source tables in `EDLDB.PEOPLE_ANALYTICS_SANDBOX`. This pipeline feeds a manual report-generation workflow that produces the **VOC Pulse Report** — a comprehensive, site-level HTML document with executive narratives, trend analysis, action clusters, and appendices. A production-grade automated pipeline from EPA is planned to replace the interim SQL.

The 2025 VOC Pulse Report covers **13 active FC sites**, **19,058 total signals**, **5 listening channels**, and **14+ sub-mechanisms** across the January–June 2025 reporting period.

---

## 2. Audience

### Primary

- **FC Site Leadership (GMs, HRMs)** — primary consumers of site-level insights and action recommendations.
- **FC Network Leadership (Sr. Directors, VPs)** — consumers of network-wide trends, cross-site comparisons, and strategic prioritization.

### Secondary

- **Enterprise People Analytics** — enablement partner for data pipelines, metrics, and continuous improvement.
- **Employee Relations (ER)** — consumers of escalation signals flagged by legacy regex classification.
- **Phoenix / ORBIT product and engineering teams** — accountable for pipeline, report logic, and future automation.

---

## 3. Purpose

Define the requirements, scope, data flows, report structure, and success measures for ECHO Intelligence. This document aligns FC Leadership, Enterprise People Analytics, ER, and Phoenix / ORBIT on what the product must deliver to reliably aggregate, analyze, and surface VOC intelligence from the FC network.

---

## 4. Partnership / Stakeholders

| Partner | Role |
| --- | --- |
| **FC Site Leadership** | Primary consumers; validate site-level insights and act on recommendations |
| **FC Network Leadership** | Strategic consumers; use cross-site comparisons for investment prioritization |
| **Enterprise People Analytics (EPA)** | Data pipeline owner (future); Snowflake source table stewards |
| **Employee Relations (ER)** | Escalation partner for Level 1–3 flagged signals |
| **Phoenix / ORBIT Product** | Owns report definition, SQL pipeline, narrative generation, and UX |

---

## 5. Background / Problem Statement

FC sites generate thousands of team member (TM) feedback signals each month through multiple listening channels — VOC Boards, Gembas, Roundtables, Standups, Leadership Walks, ECHO submissions, New Hire Surveys, Week 3 Surveys, and more. These signals are captured in separate systems with inconsistent schemas, making it impossible to see the full picture at any single site — let alone compare across sites.

### Current State

- **Five source systems** capture TM feedback in different formats with different column schemas.
- No unified view exists that combines all listening channels for cross-source analysis.
- Site leaders lack a standardized way to understand how their TM sentiment compares to the network.
- Thematic analysis (safety, equipment, facility, policy, positive sentiment) requires manual review of thousands of free-text comments.
- There is no systematic mechanism to identify cross-site patterns (e.g., "5 sites share an equipment problem") or prioritize interventions.

### Consequences

- Site leaders make decisions based on incomplete data — seeing only the signals from channels they directly manage.
- Network leadership cannot identify systemic trends that span multiple sites.
- Positive signals and best practices go unrecognized because there is no mechanism to surface them.
- Resource allocation for safety, equipment, and facility investments is reactive rather than data-driven.

### Problem Statement

> FC leadership lacks a unified, cross-channel, site-level intelligence product that aggregates all TM feedback signals, normalizes them into a common schema, and produces actionable analysis with network benchmarks — resulting in fragmented visibility, missed patterns, and reactive rather than proactive workforce decisions.

---

## 6. Phases and Data Sources

### Phase 1: Interim SQL Pipeline + Manual Report — Current

- Unified SQL query extracts from 5 Snowflake source tables and normalizes into a 15-column schema.
- CSV export feeds manual report generation (VOC Pulse Report in HTML).
- Legacy regex escalation classification applied at query time.
- 13 FC sites, 7 Rx sites in scope (FC is primary analysis focus).

### Phase 2: EPA Automated Pipeline — Planned

- EPA to build a production-grade ETL/ELT pipeline replacing the interim SQL.
- Automated data refresh cadence.
- Materialized views or tables for faster downstream consumption.

### Phase 3: Automated Report Generation — Future

- Phoenix agent-driven report generation from unified dataset.
- Natural-language prompts for ad-hoc site-level and network-level analysis.
- Scheduled report delivery to stakeholders.

---

## 7. Objectives

1. Unify all FC listening channels into a single, normalized dataset that enables cross-source analysis.
2. Produce site-level intelligence reports that compare each site's signal profile against network benchmarks.
3. Identify cross-site action clusters — groups of sites sharing common challenges — to enable targeted interventions.
4. Surface positive signals and best practices alongside opportunity areas for balanced workforce intelligence.
5. Provide a legacy regex escalation classification for ER routing of high-priority signals.

---

## 8. Data and Insight Lifecycle (EDA Loop)

### Observe

- The unified SQL query extracts signals from 5 source tables in `EDLDB.PEOPLE_ANALYTICS_SANDBOX` and normalizes them into a common 15-column schema.
- Voice mechanism names are standardized (e.g., "GM/HRM Floor Walk" → "Site Leadership Walks", "Standup Meetings" → "Standups").
- Duplicate VOC Board comments already present in the CAT Tracker are excluded.
- Administrative/non-feedback mechanisms are filtered out.

### Diagnose

- Signals are aggregated by site, category, mechanism, and month.
- Each site's category distribution is compared against network averages (Safety 7.2%, Equipment 10.8%, Facility 9.0%, Policy 11.6%, Positive 10.9%).
- Z-score validation identifies statistically significant deviations.
- Action clusters group sites by shared challenges (equipment, policy, facility, safety, rotation, listening infrastructure).

### Act

- Site-level narratives provide specific, actionable recommendations with signal counts and context.
- The Site Priority Matrix ranks all sites by total signals and top priority.
- Final recommendations align to strategic pillars with timelines and ownership.

---

## 9. Source Systems

The unified query draws from five tables in `EDLDB.PEOPLE_ANALYTICS_SANDBOX`:

| # | Source Table | Mechanism Label | Primary Feedback Field | Key Filters |
| --- | --- | --- | --- | --- |
| 1 | `FULFILLMENT_CAT_TRACKER` | Various (normalized) | `PRIMARY_TEXT` | Site code derived from `LEFT(SHEET_NAME, 4)` |
| 2 | `VOC_BOARD` | "VOC Board" | `FEEDBACK` | `DATE_POSTED >= '2025-01-01'`; excludes BOS4, SDF1; deduplicates against CAT Tracker |
| 3 | `FULFILLMENT_STAND_UPS` | "Standups" | `TEAM_MEMBER_FEEDBACK` | Non-null, non-filler feedback only |
| 4 | `FULFILLMENT_NEW_HIRE_SURVEYS` | "New Hire Survey" | `NHO_IMPROVE` | Non-null, non-filler responses only |
| 5 | `FULFILLMENT_WEEK_THREE_SURVEY` | "Week 3 Survey" | `IMPROVE` | Non-null, non-filler responses only |

---

## 10. Voice Mechanism Normalization

The SQL pipeline normalizes inconsistent mechanism names into standard labels:

| Source Values | Normalized Label |
| --- | --- |
| `GM/HRM Floor Walk`, `GM/HRM Walks`, `Building Walk` | **Site Leadership Walks** |
| `Gembas`, `Gemba` | **Gemba Walks** |
| `STANDUP MEETINGS`, `FULFILLMENT STANDUPS` | **Standups** |
| All other CAT Tracker mechanisms | Passed through as-is (e.g., ECHO, Roundtable, 1:1, TM Experience Walk) |
| VOC Board entries | **VOC Board** |
| New Hire Survey entries | **New Hire Survey** |
| Week 3 Survey entries | **Week 3 Survey** |

### Excluded Mechanisms (Administrative / Non-Feedback)

| Mechanism | Reason for Exclusion |
| --- | --- |
| Monthly Engagement Calendar | Administrative |
| Chewtopian of the Month (Non-Exempt) | Recognition program, not feedback |
| Fishbowl Display | Administrative |
| All Manager Meeting Slides | Administrative |
| Leader of the Pack (Exempt) | Recognition program, not feedback |
| All Paws | Administrative |

---

## 11. Site and Business Unit Classification

### FC Sites (Primary Scope)

| Site Code | Location |
| --- | --- |
| AVP1 | Wilkes-Barre, PA (FC1) |
| AVP2 | Wilkes-Barre, PA (FC2) |
| BNA1 | Nashville, TN |
| CFC1 | Clayton, IN |
| CLT1 | Charlotte, NC |
| DAY1 | Dayton, OH |
| DFW1 | Dallas–Fort Worth, TX |
| HOU1 | Houston, TX |
| MCI1 | Kansas City, MO |
| MCO1 | Orlando, FL |
| MDT1 | Harrisburg, PA |
| PHX1 | Phoenix, AZ |
| RNO1 | Reno, NV |

### Rx Sites (Secondary Scope)

| Site Code | Business Unit |
| --- | --- |
| MCO4, PHX2, AVP4, DFW8, SDF2, SDF4, SDF6 | Rx |

### Excluded Sites

| Site Code | Reason |
| --- | --- |
| BOS4 | Not an active FC/Rx site in scope |
| SDF1 | Not an active FC/Rx site in scope |

---

## 12. Legacy Regex Escalation Classification

The SQL pipeline applies a three-level regex escalation check against `PRIMARY_TEXT` for ER routing:

| Level | Pattern Examples | Interpretation |
| --- | --- | --- |
| **Level 1 Priority** | discrimination, harassment, retaliation, threat, violence, union, attorney, OSHA, EEOC, suicide, CEO, wrongful termination | Immediate ER/Legal review |
| **Level 2 Priority** | unfair, bully, unsafe, danger, assault, drugs, alcohol, wage, safety, under the influence | Elevated ER review |
| **Level 3 Priority** | dispute, conflict, disrespect, theft, toxic, violation | Standard ER review |

---

## 13. Scope

### In Scope

- All signals from the 5 source tables for FC and Rx business units, filtered to `ROW_DATE >= '2025-01-01'`.
- Unified 15-column schema with voice mechanism normalization and deduplication.
- Legacy regex escalation classification.
- VOC Pulse Report generation with site-level narratives, trend analysis, action clusters, and appendices.

### Out of Scope

- Real-time signal processing. The current pipeline operates on exported CSV data.
- Automated LLM-driven thematic classification (future; currently manual/rule-based).
- CC and Other business unit analysis (pipeline captures them but report focuses on FC).
- Direct integration with ER case management systems.

---

## 14. Output: VOC Pulse Report

The primary output is the **VOC Pulse Report**, an HTML document with the following sections:

| Section | Content |
| --- | --- |
| **Executive Overview** | Hero stats (total signals, active sites, channels, sub-mechanisms), executive narrative |
| **How We Listened** | Listening channel breakdown with signal counts per mechanism |
| **Top 5 Positive Themes** | Network-wide positive signal analysis |
| **Bottom 5 Opportunity Themes** | Network-wide opportunity area analysis |
| **Seasonal Patterns & Trend Analysis** | Monthly signal volumes by category with SVG chart |
| **Site-Level Analysis** (×13) | Per-site narrative with total signals, unique mechanisms, strengths, opportunities, and insight boxes |
| **Site Priority Matrix** | Summary table ranking all 13 sites by total signals and top priority |
| **Action Clusters** | Cross-site groupings by shared challenge (equipment, policy, facility, safety, rotation, listening) |
| **Final Recommendations** | Strategic recommendations with timelines and ownership |
| **Appendix A** | Cluster validation analysis with Z-score methodology |
| **Appendix B** | Site-to-cluster flow diagram (Sankey) with data table |
| **Appendix C** | Site theme distribution heatmap |
| **Appendix D** | Glossary of terms |
| **Appendix E** | Detailed signal breakdowns by category |

### Reference Implementation

The **2025 VOC Pulse Report** (`2025_VOC_Pulse_Report.html`) serves as the gold-standard reference for report structure, narrative style, data presentation, and visual design for all future iterations.

---

## 15. Success Metrics

| Metric | Definition | Target |
| --- | --- | --- |
| **Signal coverage** | % of FC listening channels captured in unified dataset | 100% of active channels |
| **Report accuracy** | All report figures verified against source data | 100% alignment |
| **Site coverage** | Number of FC sites with complete site-level analysis | 13/13 |
| **Stakeholder adoption** | % of site GMs/HRMs who reference the report in action planning | Baseline year; track adoption |
| **Time to insight** | Elapsed time from data extraction to published report | Target: reduce with each iteration |
| **Action cluster utilization** | Number of cross-site interventions initiated from cluster recommendations | Track quarterly |

---

## 16. Non-Goals

- Replacing site-level listening programs (VOC Boards, Gembas, etc.). ECHO Intelligence aggregates and analyzes; it does not replace the listening infrastructure.
- Automated corrective action. The product surfaces intelligence; humans decide and act.
- Individual TM identification in the report. The VOC Pulse Report presents aggregate data only.
- Real-time alerting. The current cadence is periodic (per reporting cycle).

---

## 17. Open Questions / Decisions Needed

1. **EPA pipeline timeline:** When will the automated pipeline replace the interim SQL? What is the target architecture?
2. **Report cadence:** Monthly? Quarterly? Aligned to business review cycles?
3. **LLM integration:** When will Phoenix/ORBIT automate thematic classification and narrative generation?
4. **Rx expansion:** When will the report expand beyond FC to include Rx site-level analysis?
5. **Distribution mechanism:** Will the report be delivered via email, SharePoint, or embedded in a Phoenix agent experience?

---

## 18. Recommended Next Steps

1. Finalize EPA automated pipeline requirements and timeline.
2. Establish report cadence aligned to FC leadership review cycles.
3. Build regression test suite to validate pipeline output against the 2025 reference report.
4. Evaluate Phoenix agent integration for ad-hoc queries against the unified dataset.
5. Expand site coverage to Rx network upon FC stabilization.

---

## 19. Roadmap Alignment

This PRD anchors to the **2026 HR Transformation pillars** — especially **Pillar 1: Leveraging Automation and Intelligence to Scale HR** — by proving that fragmented TM feedback can be unified into a single intelligence product that drives proactive, data-informed workforce decisions at the site and network level. ECHO Intelligence creates a repeatable pattern for listening-channel aggregation across all Chewy business units.
