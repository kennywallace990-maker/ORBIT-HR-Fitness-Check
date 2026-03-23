# Release Notes, ECHO Intelligence

---

## v1.0 — 2026-03-17

### Summary

Initial production release of the ECHO Intelligence pipeline and VOC Pulse Report.

### Pipeline

- **Unified SQL query** aggregating 5 source tables from `EDLDB.PEOPLE_ANALYTICS_SANDBOX` into a 15-column schema
- **Voice mechanism normalization**: GM/HRM walks → Site Leadership Walks, Gembas → Gemba Walks, Standup variants → Standups
- **VOC Board deduplication** against CAT Tracker (case-insensitive, trim-aware text matching)
- **Filler filtering** for Standup, New Hire Survey, and Week 3 Survey responses
- **Administrative mechanism exclusion** (6 non-feedback mechanisms removed)
- **Business unit classification** for 13 FC sites and 7 Rx sites
- **Legacy regex escalation** with 3 priority levels for ER routing
- **Site exclusion** for BOS4 and SDF1

### Report: 2025 VOC Pulse Report

- **13 FC sites** with full site-level analysis
- **19,058 total signals** across January–June 2025
- **5 listening channels**, **14+ sub-mechanisms**
- Executive Overview, Seasonal Trends, Site-Level Analysis, Action Clusters, Final Recommendations
- Appendices: Z-score validation, Sankey flow diagram, Theme heatmap, Glossary, Detailed breakdowns
- Network benchmarks: Safety 7.2%, Equipment 10.8%, Facility 9.0%, Policy 11.6%, Positive 10.9%

### Documentation

- PRD (01)
- Data Map & Classification Declaration (02)
- Data Dictionary (03)
- Technical Design Doc with full production SQL (04)
- Report Skeleton & Narrative Templates (05)
- Test Plan with 46 test cases (06)
- Runbook (07)
- Success Metrics & KPIs (08)
- Stakeholder Map & Comms Plan (09)

### Known Limitations

- Pipeline is interim SQL executed manually; EPA automated pipeline pending
- Report generation is manual/assisted; Phoenix agent automation planned
- Thematic classification relies on source `CATEGORY` field and manual analysis; LLM-driven classification is future
- Rx sites captured in pipeline but not included in the VOC Pulse Report site-level analysis

### Next Steps

- EPA automated pipeline development
- Establish recurring report cadence
- Evaluate Phoenix agent integration for ad-hoc queries
- Expand to Rx network site-level analysis
