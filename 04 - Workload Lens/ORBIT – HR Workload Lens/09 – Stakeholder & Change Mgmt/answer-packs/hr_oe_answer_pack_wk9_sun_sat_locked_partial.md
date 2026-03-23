# HR Operational Excellence Answer Pack

## Week Lock
- Week 8: 2026-02-15 to 2026-02-21 (Sunday to Saturday)
- Week 9: 2026-02-22 to 2026-02-28 (Sunday to Saturday)

## Inputs Used
- Phase I CSV: `C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\ORBIT Products\04 - Workload Lens\test-data\hr_dataset_3wk_2026-02-09_to_2026-03-01.csv`
- Phase II CSVs:
  - `C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\ORBIT Products\04 - Workload Lens\Phase II\Snow Ticket Data.csv`
  - `C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\ORBIT Products\04 - Workload Lens\Phase II\Timesheet Inquiry Week 9.csv`

## Week 8 vs Week 9 Snapshot

| Metric | Week 8 | Week 9 | Delta |
|---|---:|---:|---:|
| Phase II total tickets | 489 | 514 | +25 |
| Phase II resolved tickets | 479 | 462 | -17 |
| Phase II resolved percent | 97.96% | 89.88% | -8.07 pp |
| Phase I total UKG touches | 9411 | 70981 | +61570 |
| Phase I UKG rework touches | 2452 | 22885 | +20433 |

## HR Operational Excellence Answers

### Q1
What is our plan to establish accurate SLA commitments and measurements?

The current CSV inputs do not include SLA target definitions, SLA clocks, or breach flags, so adherence accuracy cannot be validated from this dataset alone.

Required data to answer this fully:
- SLA policy table by HR Service
- Ticket level SLA target at open time
- Ticket level within_SLA or breach indicator
- Timestamp-level lifecycle events if business-hour clocks are used

### Q2
Which ticket types account for the volume change?

Week over week change is driven by the services with the largest absolute deltas between Week 8 and Week 9.

Largest decreases:
| Service | Week 8 | Week 9 | Delta | Delta % |
|---|---:|---:|---:|---:|
| Timesheet Inquiry | 120 | 105 | -15 | -12.50% |

Largest increases:
| Service | Week 8 | Week 9 | Delta | Delta % |
|---|---:|---:|---:|---:|
| FC General Inquiry | 369 | 409 | +40 | 10.84% |

### Q3
What is the biggest remaining opportunity, using existing process and technology, to reduce volume?

The biggest immediate opportunity is concentrated in the highest volume services in Week 9, where standardized self service and intake routing can reduce avoidable ticket creation.

| Service | Week 9 Volume | Opportunity | Source Type |
|---|---:|---|---|
| FC General Inquiry | 409 | Use guided intake and triage macros to route recurring requests to self service paths. | inference |
| Timesheet Inquiry | 105 | Increase missed punch self service and same day approval to reduce delayed inquiries. | inference |

## Cross Phase Coverage Proxy
Ticket to touch mapping is not one to one. The following values are directional coverage proxies to estimate dark work.

| Metric | Week 9 Value |
|---|---:|
| Phase II ticket visibility vs all Phase I work | 0.7241% |
| Phase II ticket visibility vs Phase I rework | 2.2460% |
| Non ticket work proxy count | 70467 |
| Non ticket rework proxy count | 22371 |

## Data Gaps
- SLA adherence commitments and breach logic cannot be validated from current CSV columns.
- Proxy coverage cannot identify true ticket linkage without a shared ticket identifier in UKG touch records.
