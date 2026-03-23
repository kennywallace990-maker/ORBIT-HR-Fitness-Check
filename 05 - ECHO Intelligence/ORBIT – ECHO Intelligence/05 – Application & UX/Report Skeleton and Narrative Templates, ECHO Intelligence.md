# Report Skeleton & Narrative Templates, ECHO Intelligence

| Field | Value |
| --- | --- |
| **Product** | ECHO Intelligence |
| **Platform** | ORBIT Phoenix |
| **Product Owner** | Kenny Wallace |
| **Version** | 1.0 |
| **Last Updated** | 2026-03-18 |

---

## 1. Purpose

This document defines the structure, section order, narrative conventions, and data presentation standards for the VOC Pulse Report - the primary output of ECHO Intelligence. The **2025 VOC Pulse Report** (`2025_VOC_Pulse_Report.html`) is the primary FC reference implementation, and **2025 VOC Pulse Report Rx Network** (`2025_VOC_Pulse_Report_Rx_Network.html`) is the pharmacy-network companion reference for future iterations.

### Narrative Tone Standard

- Prefer the Core FC report's evidence-first tone: operational, specific, and signal-backed.
- Avoid brand-forward or promotional phrasing such as "mission-driven," "cultural heart," "gold-standard," or similar language unless directly quoting a source.
- Frame strengths as observed operating behaviors, not abstract culture statements.
- Keep recommendations concrete, comparative, and tied to counts, rates, or visible workflow implications.

---

## 2. Report Structure

The VOC Pulse Report follows a fixed section order. Each section has a defined purpose and data requirements.

| # | Section | Purpose | Key Data Elements |
| --- | --- | --- | --- |
| 1 | **Title & Metadata** | Report identity, date, confidentiality notice | Report title, date, "Chewy Confidential" footer |
| 2 | **Table of Contents** | Navigation links to all sections | Anchored section titles |
| 3 | **Executive Overview** | Hero stats and high-level narrative | Total signals, active sites, listening channels, sub-mechanisms |
| 4 | **How We Listened** | Listening channel breakdown | Table of channels with signal counts per mechanism |
| 5 | **Top 5 Positive Themes** | Network-wide positive signal analysis | Theme names, signal counts, representative quotes |
| 6 | **Bottom 5 Opportunity Themes** | Network-wide opportunity areas | Theme names, signal counts, context |
| 7 | **Seasonal Patterns & Trend Analysis** | Monthly signal volumes by category | Table + SVG line chart; key seasonal insights narrative |
| 8 | **From Network Themes to Site-Level Action** | Transition section with network benchmarks | Network average percentages for Safety, Equipment, Facility, Policy, Positive |
| 9 | **Site-Level Analysis** (xN) | Per-site deep dive | Total signals, unique mechanisms, strengths, opportunities, insight boxes |
| 10 | **Site Priority Matrix** | Summary ranking of all sites | Table: Site, Total Signals, Top Priority |
| 11 | **Action Clusters** | Cross-site groupings by shared challenge | Cluster name, member sites, signal evidence, recommended actions |
| 12 | **Final Recommendations** | Strategic recommendations | Numbered recommendations with timelines and ownership |
| 13 | **Appendix A** | Cluster validation (Z-scores) | Methodology, results table, site-level Z-scores |
| 14 | **Appendix B** | Site-to-cluster flow diagram | Sankey visualization + data table |
| 15 | **Appendix C** | Site theme distribution heatmap | Color-coded percentage table with bar visualizations |
| 16 | **Appendix D** | Glossary of terms | Definitions for report-specific terminology |
| 17 | **Appendix E** | Detailed signal breakdowns | Category-level tables (Safety, Equipment, Facility, Policy) |

---

## 3. Hero Stats Block

The Executive Overview opens with four hero stat cards:

| Stat | Source | Format | Example |
| --- | --- | --- | --- |
| **Total Signals** | `COUNT(*)` where `BUSINESS_UNIT = 'FC'` and `ROW_DATE` in reporting period | Comma-formatted integer | 19,058 |
| **Active Sites** | `COUNT(DISTINCT SITE_CODE)` where `BUSINESS_UNIT = 'FC'` | Integer | 13 |
| **Listening Channels** | Count of distinct top-level channel types (VOC Board, CAT Tracker mechanisms, Standups, Surveys) | Integer | 5 |
| **Sub-Mechanisms** | `COUNT(DISTINCT VOICE_MECHANISM)` where `BUSINESS_UNIT = 'FC'` | Integer with "+" suffix | 14+ |

---

## 4. Listening Channel Table

Presented in "How We Listened" section. Lists each top-level channel with sub-mechanisms and signal counts.

| Column | Description |
| --- | --- |
| Channel | Top-level listening channel name (e.g., VOC Board, Gemba Walks) |
| Sub-Mechanisms | Comma-separated list of mechanisms within the channel |
| Total Signals | Sum of signals for this channel across all FC sites |

---

## 5. Monthly Signal Volumes Table & Chart

### Table Format

| Column | Description |
| --- | --- |
| Month | Calendar month (Jan, Feb, Mar, ...) |
| Safety | Signal count for Safety category |
| Equipment | Signal count for Equipment category |
| Facility | Signal count for Facility category |
| Policy | Signal count for Policy category |
| Positive | Signal count for Positive category |
| Other | Signal count for all other categories |
| **Total** | Row total across all categories |

### SVG Chart

- Line chart with one series per category
- X-axis: months; Y-axis: signal count
- Color-coded to match category colors used throughout the report
- Peak month annotated with callout

---

## 6. Site-Level Analysis Template

Each of the 13 FC sites follows this narrative template:

### Header Block

```text
### [SITE_CODE] â€” [City, State]
**Total Signals:** [N] | **Unique Mechanisms:** [N] | **[Site Characterization Tag]**
```

- **Site Characterization Tag**: A brief descriptor (e.g., "Equipment-Heavy", "Policy Crisis Site", "Rotation Hotspot", "Newer Site â€” Leadership Strong, Listening Still Building")

### The [SITE_CODE] Story

A 2â€“3 paragraph narrative that:

1. Opens with the site's defining characteristic and its most notable metric
2. Provides context â€” why the numbers look the way they do
3. Compares key rates to network averages (format: `XX.X% vs. YY.Y% network average`)

### Strengths (2 items)

Each strength follows this format:

```text
**[N]. [Strength Title]**
**Signals:** [count] [mechanism/category] signals ([percentage]% of site total)

[1â€“2 sentence narrative explaining why this is a strength and what it means]
```

### Opportunities (2 items)

Each opportunity follows this format:

```text
**[N]. [Opportunity Title] â€” [Priority Level]**
**Signals:** [count] [category]-related signals ([percentage]% vs. [network avg]% network average)

- [Bullet 1]: **[count]**
- [Bullet 2]: **[count]**
- [Bullet 3]: **[count]**

[1â€“2 sentence narrative explaining impact]
```

### Insight Box (where applicable)

```text
[Insight Box]
[Actionable recommendation specific to this site]
```

---

## 7. Network Benchmark Reference

The following network averages are used as comparison baselines throughout the report:

| Category | Network Average | Calculation |
| --- | --- | --- |
| Safety | 7.2% | Total Safety signals / Total FC signals Ã— 100 |
| Equipment | 10.8% | Total Equipment signals / Total FC signals Ã— 100 |
| Facility | 9.0% | Total Facility signals / Total FC signals Ã— 100 |
| Policy | 11.6% | Total Policy signals / Total FC signals Ã— 100 |
| Positive | 10.9% | Total Positive signals / Total FC signals Ã— 100 |
| Rotation | 2.3% | Total Rotation signals / Total FC signals Ã— 100 |

These benchmarks must be recalculated each reporting period.

---

## 8. Site Priority Matrix Template

| Column | Description |
| --- | --- |
| Site | 4-character site code |
| Total Signals | Total signal count for the site |
| Top Priority | The site's most critical action item (1-line summary) |

Sites are ordered by total signals descending.

---

## 9. Action Cluster Template

Each action cluster groups sites that share a common challenge:

```text
### [Cluster Name] (e.g., "Equipment Crisis Response Cluster")

**Sites:** [SITE1], [SITE2], [SITE3]

**Evidence:** [Specific signal rates and counts that justify the cluster]

**Recommended Actions:**
1. [Action 1]
2. [Action 2]
3. [Action 3]
```

### Standard Cluster Categories

| Cluster | Criteria | Typical Sites |
| --- | --- | --- |
| Equipment Crisis Response | Equipment signal rate significantly above 10.8% network average | Sites with 14%+ equipment rates |
| Policy Transparency Campaign | Policy signal rate significantly above 11.6% network average | Sites with VTO/scheduling frustration |
| Facility & Housekeeping | Facility signal rate significantly above 9.0% network average | Sites with restroom/breakroom issues |
| Safety & Ergonomic Intervention | Safety signal rate significantly above 7.2% network average | Sites with PPE/pallet/PIT concerns |
| Rotation & Cross-Training | Rotation signals elevated; dock/path stagnation | Sites with rotation complaints |
| Listening Infrastructure Build-Out | Mechanism count below network average (11.5) | Newer sites with limited channels |

---

## 10. Heatmap Conventions (Appendix C)

The site theme distribution heatmap uses color-coded bars with percentage labels:

| Color | CSS Class | Meaning |
| --- | --- | --- |
| Green (#A5D6A7) | `bar low` | Below network average |
| Amber (#FFB74D) | `bar mid` | Near network average (within ~1 percentage point) |
| Red (#E57373) | `bar high` | Above network average |
| Blue (#64B5F6) | `bar pos` | Positive category (always blue) |

Bar width is proportional to the percentage value (approximately 4.4px per percentage point).

---

## 11. Narrative Style Guide

### Voice and Tone

- **Analytical but human.** Data-driven claims backed by signal counts, but written for leaders who need to act, not analysts.
- **Balanced.** Every site section includes both strengths and opportunities. Never purely negative.
- **Specific.** Always cite signal counts and percentages. Avoid vague statements like "many TMs feel..."
- **Comparative.** Always reference network averages when discussing site-specific rates.

### Data Citation Format

- Percentages: `XX.X%` (one decimal place)
- Comparisons: `[value]% vs. [network avg]% network average`
- Above/below: `[N]% above/below network average` (calculated as `(site_rate - network_avg) / network_avg Ã— 100`)
- Signal counts: comma-formatted integers (e.g., `1,545`)

### Insight Box Usage

- Use sparingly â€” maximum 1 per site section
- Reserved for the single most actionable recommendation
- Written as a direct instruction, not a suggestion

---

## 12. Reference Implementation

The **2025 VOC Pulse Report** (`2025_VOC_Pulse_Report.html`) is the gold-standard reference stored in this folder (`05 â€“ Application & UX`). It serves as the structural template for all future report iterations.

### What the Reference Covers

- Report structure and section order (17 sections, see Section 2 above)
- Narrative voice and tone (see Section 11)
- Data presentation (tables, SVG line charts, inline SVG Sankey diagram, heatmaps)
- Visual design (CSS styling, color palette, typography)
- Site-level analysis depth and format (13 FC sites)
- Appendices (Z-score validation, flow diagram, heatmap, glossary, signal breakdowns)

### How to Replicate with New Data

| Step | Action | Details |
| --- | --- | --- |
| 1 | **Run the pipeline SQL** | Execute the production SQL (see `04 â€“ Pipelines & Architecture/Technical Design Doc`). Adjust `ROW_DATE` filter for the new reporting period. |
| 2 | **Export CSV** | Export unified dataset from Snowflake. Verify row count and site presence. |
| 3 | **Recalculate network benchmarks** | Compute category percentages (Safety, Equipment, Facility, Policy, Positive, Rotation) as `category_signals / total_FC_signals Ã— 100`. These replace the values in Section 7 above. |
| 4 | **Open the reference HTML** | Open `2025_VOC_Pulse_Report.html` in a text editor. Save a copy with the new reporting period name (e.g., `2026_Q1_VOC_Pulse_Report.html`). |
| 5 | **Update header metadata** | Change report title, date, and reporting period in the `<header>` and `<footer>` sections. |
| 6 | **Update Executive Overview** | Replace hero stats (Total Signals, Active Sites, Listening Channels, Sub-Mechanisms). |
| 7 | **Update Listening Channel table** | Refresh signal counts per channel/mechanism from new CSV. |
| 8 | **Update Top 5 / Bottom 5 themes** | Recalculate from new data; update theme names, counts, and representative quotes. |
| 9 | **Update Monthly Signal Volumes** | Replace table data and regenerate SVG line chart coordinates. |
| 10 | **Update Site-Level Analysis** | For each site: update signal counts, mechanism counts, strengths, opportunities, and narratives. Follow the template in Section 6 above. |
| 11 | **Update Site Priority Matrix** | Recalculate and reorder by total signals descending. |
| 12 | **Update Action Clusters** | Re-run Z-score analysis; regroup sites into clusters based on new data. |
| 13 | **Update Appendix A (Z-scores)** | Recalculate Z-scores per site per category. |
| 14 | **Update Appendix B (Sankey)** | Update the inline SVG Sankey diagram node labels, flow path widths, and value labels to match new data. Flow widths should be proportional to signal counts. |
| 15 | **Update Appendix C (Heatmap)** | Recalculate site theme distribution percentages; update bar widths and color classes. |
| 16 | **Update Appendix E (Signal tables)** | Refresh detailed breakdowns per category. |
| 17 | **Run test cases** | Execute test cases from `06 â€“ Testing & QA/Test Plan` to verify data accuracy. |
| 18 | **Review and distribute** | Peer-review; distribute to authorized FC leadership. |

### Encoding Notes

- The HTML file uses UTF-8 encoding (`<meta charset="UTF-8">`).
- Use HTML entities for special characters: `&ndash;` (en-dash), `&rarr;` (right arrow), `&hellip;` (ellipsis), `&ne;` (not-equal), `&ge;` (greater-or-equal), `&amp;` (ampersand).
- Avoid pasting from Word/Google Docs directly â€” this causes mojibake (garbled UTF-8 characters). Always use plain text or HTML entities.
- The inline SVG Sankey diagram requires no external JavaScript libraries â€” it renders natively in any browser.

### Key Files for Replication

| File | Location | Purpose |
| --- | --- | --- |
| `2025_VOC_Pulse_Report.html` | `05 â€“ Application & UX` | Gold-standard structural template |
| `Report Skeleton and Narrative Templates, ECHO Intelligence.md` | `05 â€“ Application & UX` | Section specs, templates, style guide |
| `Technical Design Doc, ECHO Intelligence.md` | `04 â€“ Pipelines & Architecture` | Production SQL, schema, source tables |
| `Runbook, ECHO Intelligence.md` | `07 â€“ Runbook & Operations` | Step-by-step execution procedures |
| `Test Plan, ECHO Intelligence.md` | `06 â€“ Testing & QA` | 46 test cases for data validation |

