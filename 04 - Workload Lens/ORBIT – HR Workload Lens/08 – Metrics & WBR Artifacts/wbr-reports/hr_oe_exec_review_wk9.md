# HR Operational Excellence Report

Preview this file in the IDE Markdown preview pane to review and comment.

## Review Header
- Week 8: 2026-02-15 to 2026-02-21 (Sunday to Saturday)
- Week 9: 2026-02-22 to 2026-02-28 (Sunday to Saturday)
- Generated UTC: 2026-03-06T13:45:42+00:00

## VP Summary
Week 9 closed at 1828 HR Operational Excellence tickets, up 65 from Week 8 (3.69%).
Resolved rate moved from 99.04% to 92.18% (-6.86 pp).
The largest growth driver was CC Time and Attendance (+128, 25.00%).
Ticketed Rework Coverage % was 7.9878%, which should be the primary cross-phase KPI.

## Data Caveat
Phase I Week 8 is retained as directional context only because event-date coverage is incomplete.
Retained sample: 9411 UKG touches and 2452 rework touches.
Missing Phase I Week 8 dates: 2026-02-16, 2026-02-17, 2026-02-18, 2026-02-19, 2026-02-20, 2026-02-21

## Full Working Report

# HR Operational Excellence Answer Pack

## Week Lock
- Week 8: 2026-02-15 to 2026-02-21 (Sunday to Saturday)
- Week 9: 2026-02-22 to 2026-02-28 (Sunday to Saturday)

## Inputs Used
- Phase I CSV: `C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\ORBIT Products\04 - Workload Lens\Phase I\Phase I CSV\Snowflake UKG data.csv`
- Phase II CSVs:
  - `C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\ORBIT Products\04 - Workload Lens\Phase II\Phase II CSVs\Attendance Inquiry.csv`
  - `C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\ORBIT Products\04 - Workload Lens\Phase II\Phase II CSVs\CS Time and Attendance.csv`
  - `C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\ORBIT Products\04 - Workload Lens\Phase II\Phase II CSVs\FC General Inquiry.csv`
  - `C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\ORBIT Products\04 - Workload Lens\Phase II\Phase II CSVs\Timesheet Inquiry.csv`

## Source Caveats
Phase I prior-week data is retained in this report, but the Week 8 event-date coverage is incomplete. Use the prior-week Phase I values as directional signal rather than full-week equivalent.

- Phase I min event date: 2026-02-09
- Phase I max event date: 2026-03-01
- Phase I Week 8 missing dates: 2026-02-16, 2026-02-17, 2026-02-18, 2026-02-19, 2026-02-20, 2026-02-21
- Phase I Week 9 missing dates: None
- Retained Phase I Week 8 sample: 9411 UKG touches and 2452 rework touches from the available rows.

## Supplemental Response Draft

Week 9 HR Operational Excellence ticket demand closed at 1828, up 65 from Week 8 (3.69%). Resolution performance weakened at the same time, with resolved rate moving from 99.04% in Week 8 to 92.18% in Week 9 (-6.86 pp).

Based on the supplied ticket service labels, the net increase was driven primarily by CC Time and Attendance (+128 tickets, 25.00%).
The largest offsetting decline came from Attendance inquiry (-33 tickets, -3.26%).

Phase I shows 70981 UKG touches and 22885 rework touches in Week 9. Against that workload, the Phase II ticket stream covers 2.5753% of all UKG touches and 7.9878% of UKG rework touches.

This supports using rework coverage as the primary cross-phase KPI, while treating the all-work view as secondary context.

The most actionable near-term reduction opportunity remains attendance and timekeeping demand.

Attendance Inquiry plus Time and Attendance work accounts for 1618 of 1828 Week 9 tickets (88.51%). Standardizing intake, self-service usage, and same-day correction should produce the highest immediate impact.

## Executive Summary

- Week 9 tickets: 1828 (+65 WoW, 3.69%).
- Week 9 resolved rate: 92.18% (-6.86 pp vs Week 8).
- Largest growth driver: CC Time and Attendance (+128, 25.00%).
- Largest offsetting decline: Attendance inquiry (-33, -3.26%).
- Primary cross-phase KPI recommendation: Ticketed Rework Coverage % = 7.9878%.
- Unticketed Rework Proxy % = 92.0122% (21057 rework touches beyond the ticket count proxy).

## Week 8 vs Week 9 Snapshot

| Metric | Week 8 | Week 9 | Delta |
|---|---:|---:|---:|
| Phase II total tickets | 1763 | 1828 | +65 |
| Phase II resolved tickets | 1746 | 1685 | -61 |
| Phase II resolved percent | 99.04% | 92.18% | -6.86 pp |
| Phase I total UKG touches | 9411 (partial prior-week sample) | 70981 | directional only |
| Phase I UKG rework touches | 2452 (partial prior-week sample) | 22885 | directional only |

## HR Operational Excellence Answers

### Q1
What is our plan to establish accurate SLA commitments and measurements?

Direct answer: SLA adherence cannot be measured accurately from the current weekly files because the input set does not contain ticket-level SLA targets, SLA clocks, or breach flags.

Recommended plan: define the SLA commitment by HR Service, stamp the target on each ticket at open, calculate within-SLA or breach status on close and on aging backlog, and only then publish SLA attainment as an enterprise metric.

Required data to answer this fully:
- SLA policy table by HR Service
- Ticket level SLA target at open time
- Ticket level within_SLA or breach indicator
- Timestamp-level lifecycle events if business-hour clocks are used

### Q2
Which ticket types account for the volume change?

Direct answer: Week 9 volume increased by 65 tickets (3.69%). Based on the supplied service labels, the increase was concentrated in Time and Attendance demand rather than broad-based growth across all services.

The primary growth driver was CC Time and Attendance at 640 tickets, up 128 (25.00%) from Week 8.
The largest offset came from Attendance inquiry, down 33 (-3.26%) from Week 8.

Largest decreases:
| Service | Week 8 | Week 9 | Delta | Delta % |
|---|---:|---:|---:|---:|
| Attendance inquiry | 1011 | 978 | -33 | -3.26% |
| Timesheet Inquiry | 240 | 210 | -30 | -12.50% |

Largest increases:
| Service | Week 8 | Week 9 | Delta | Delta % |
|---|---:|---:|---:|---:|
| CC Time and Attendance | 512 | 640 | +128 | 25.00% |

### Q3
What is the biggest remaining opportunity, using existing process and technology, to reduce volume?

Direct answer: the biggest near-term opportunity is to reduce avoidable attendance and timekeeping contacts with existing tools and process controls. Those demand types represent 1618 of 1828 Week 9 tickets (88.51%).

Immediate focus should be one standardized intake path, stronger manager adoption of self-service and approvals, and same-day correction before work converts into inquiries or rework.

| Service | Week 9 Volume | Opportunity | Source Type |
|---|---:|---|---|
| Attendance inquiry | 978 | Drive one standardized call off intake path through UKG self service and enforce manager adoption. | inference |
| CC Time and Attendance | 640 | Drive one standardized call off intake path through UKG self service and enforce manager adoption. | inference |
| Timesheet Inquiry | 210 | Increase missed punch self service and same day approval to reduce delayed inquiries. | inference |

## HR Operational Excellence Focus

Use this section as the direct Supplemental response for the weekly HR Operational Excellence discussion.

### Narrative
Week 9 ticket demand increased modestly, but the increase was concentrated in Time and Attendance work. At the same time, closure performance fell from 99.04% to 92.18%, indicating more work remained open at week close.

Phase I reinforces that the ticket queue is only a partial view of workload. Week 9 recorded 70981 UKG touches and 22885 rework touches, compared with 1828 tickets.

The rework-based coverage view is the better primary KPI because it aligns more closely to effort that likely required investigation or correction.

### Recommended Actions This Week
- Stand up ticket-level SLA measurement design before reporting SLA attainment to leadership.
- Target CC Time and Attendance and Attendance Inquiry first because they dominate Week 9 demand.
- Use Ticketed Rework Coverage % as the primary dark-work KPI for cross-phase reporting.
- Keep Phase I Week 8 in the narrative as directional context until EPA refreshes the missing event dates.

## Cross Phase Coverage Proxy
Ticket to touch mapping is not one to one. The following values are directional coverage proxies to estimate dark work.

| Metric | Week 9 Value |
|---|---:|
| Ticketed Rework Coverage % (recommended primary KPI) | 7.9878% |
| Unticketed Rework Proxy % | 92.0122% |
| Phase II ticket visibility vs all Phase I work | 2.5753% |
| Phase II ticket visibility vs Phase I rework | 7.9878% |
| Non ticket work proxy count | 69153 |
| Non ticket rework proxy count | 21057 |

## Data Gaps
- SLA adherence commitments and breach logic cannot be validated from current CSV columns.
- Proxy coverage cannot identify true ticket linkage without a shared ticket identifier in UKG touch records.
- Phase I event-date coverage is incomplete, so Phase I WoW comparisons are provisional.

## Review Notes
- Add comments directly below the section you want changed.
- Treat this file as the review surface for tonight's discussion.