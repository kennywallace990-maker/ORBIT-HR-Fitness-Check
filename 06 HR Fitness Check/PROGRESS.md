# HR Fitness Check - Project Progress

**Last Updated**: June 19, 2026  
**Status**: Active Development - Discovery Phase

---

## Vision & Problem Statement

**Tagline**: "Fitness check measures the quality of standard work. Is the stated process being followed?"

HR Fitness Check is an ORBIT product that provides an objective, repeatable, and evidence-backed method for FC HR teams to assess the quality and health of HR Standard Work.

### Current State
- Quarterly, spreadsheet-driven exercise
- Combines dashboard lookups, system reports, physical inspections, trackers, and subjective interpretation
- Housed in Smartsheet (sunsetting)
- Manual data collection across multiple sources
- Vulnerable to inconsistent interpretation

### Desired Outcome
- Objective data gathered quickly and accurately for HR Standard Work items
- Consistent scoring at site, regional, Rx, and network levels
- HR leaders receive clear strengths, opportunities, and solution planning prompts
- Less time completing the exercise, more time improving Standard Work execution

### V1 Scope
Automate parts of the exercise that have reliable source data while preserving human accountability for physical and judgment-based inputs.

---

## Remaining Items

### 1. Source Field Research & Data Integration
**Owner**: Kenny Wallace  
**Status**: In Progress

- [ ] Research source fields in Snowflake
- [ ] Author required joins for each Standard Work line item
- [ ] Define business rules for data transformation
- [ ] Develop derived metrics for each Standard Work item
- [ ] Schedule line-item-by-line-item discovery session to walk through source fields (column 4 of Smartsheet)

**Data Sources to Evaluate**:
- Tableau
- ServiceNow
- UKG
- Snowflake
- ECHO

**Deliverable**: Source field mapping document with joins, business rules, and derived metrics

---

### 2. Automation Scope Definition
**Owner**: Kenny Wallace  
**Status**: In Progress

- [ ] Determine which Standard Work items can be sourced from existing data fields
- [ ] Identify which items require manual physical inspection (out of scope for automation)
- [ ] Document automation feasibility for each line item
- [ ] Create source-to-item traceability matrix

**Deliverable**: Automation scope matrix with feasibility assessment

---

### 3. Baseline Performance Data Collection
**Owner**: Kenny Wallace  
**Status**: Pending

- [ ] Collect baseline performance data by site from Smartsheet views
- [ ] Establish pre-automation benchmarks
- [ ] Document baseline data collection methodology
- [ ] Store baseline data in Snowflake datamart

**Deliverable**: Baseline performance dataset by site

---

### 4. Data Architecture & Retention
**Owner**: Kenny Wallace, Data Engineering  
**Status**: Pending

- [ ] Confirm baseline data will reside in Snowflake datamart
- [ ] Confirm result data will reside in Snowflake datamart
- [ ] Define retention policy for quarter-over-quarter comparison
- [ ] Design datamart schema for HR Fitness Check metrics
- [ ] Establish data refresh cadence

**Deliverable**: Snowflake datamart specification and schema

---

### 5. Time-Savings Estimation
**Owner**: Kenny Wallace, Weipan Le  
**Status**: In Progress

**Current Estimates**:
- Check execution: ~2.5 hours per site per quarter
- Setup: TBD
- Communication: TBD
- Q&A: TBD
- Post-check audits: TBD
- Report compilation: TBD

- [ ] Finalize time-savings estimates for all phases
- [ ] Validate estimates with pilot site data
- [ ] Document assumptions and methodology

**Deliverable**: Finalized time-savings analysis

---

## Meetings & Milestones

### Completed
- **Jun 16, 2026**: Review SW checklist with Kenny Wallace

### Upcoming
- **Jun 23, 2026**: Continue defining scope of work
- **TBD**: Line-item-by-line-item discovery session (source fields)
- **TBD**: Data architecture review
- **TBD**: Baseline data collection kickoff

---

## Reference Materials

- **Smartsheet Matrix**: [ORBIT - HR Fitness Check Matrix](https://chewycomllc-my.sharepoint.com/personal/kwallace12_chewy_com/Documents/ORBIT%20-%20HR%20Fitness%20Check%20Matrix.xlsx?d=w1dfa0cda281945afbc8053d46c594575&csf=1&web=1&e=c53ApK)
- **Product Requirements**: See `01 - PRD, HR Fitness Check.md`
- **Technical Design**: See `04 - Technical Design Doc, HR Fitness Check.md`
- **Test Plan**: See `06 - Test Plan, HR Fitness Check.md`

---

## Key Decisions

1. **Data-Driven Approach**: Prioritize automated metrics from reliable sources over manual entry
2. **Human Accountability**: Preserve human judgment for physical inspections and subjective assessments
3. **Snowflake as Source of Truth**: All baseline and result data will reside in Snowflake datamart
4. **Phoenix Platform Integration**: Results surfaced through ORBIT agent on Phoenix platform
5. **Quarterly Cadence**: Assessment runs quarterly with quarter-over-quarter comparison capability

---

## Dependencies

- Snowflake access and datamart provisioning
- Smartsheet data export and baseline collection
- Source system access (UKG, ServiceNow, Tableau, ECHO)
- Phoenix platform integration (ORBIT agent)
- HR stakeholder availability for discovery sessions

---

## Next Steps (Priority Order)

1. **Schedule discovery session** with Kenny Wallace to review Smartsheet column 4 source fields
2. **Complete source field research** in Snowflake and other systems
3. **Define automation scope** for each Standard Work line item
4. **Collect baseline data** from Smartsheet views
5. **Finalize time-savings estimates** with Weipan Le
6. **Design Snowflake datamart** for retention and comparison
7. **Prepare for Jun 23 meeting** with scope definition and discovery findings

---

## Notes

- Current POC demonstrates static Phoenix-style ORBIT workspace with Q3 assessment data
- Data extraction pipeline ready for integration with live Snowflake sources
- Manual input queue capability built into POC for hybrid validation workflows
- Catalog workbench in place for Standard Work governance

