# ORBIT Product Folder Standard

> **Canonical source:** `ORBIT Product Folder Templates.docx` (this folder)
> **Last synced:** 2026-03-16

---

## 1. Standard Folder Structure

Every ORBIT product has one root folder: **ORBIT – [Product Name]**

Inside that root, these **10 top-level folders** are required:

| # | Folder Name |
|---|-------------|
| 01 | Product Charter & PRD |
| 02 | Governance & Risk |
| 03 | Data Contract & Schema |
| 04 | Pipelines & Architecture |
| 05 | Application & UX |
| 06 | Testing & QA |
| 07 | Runbook & Operations |
| 08 | Metrics & WBR Artifacts |
| 09 | Stakeholder & Change Mgmt |
| 99 | Archive |

---

## 2. Required Files per Folder

### 01 – Product Charter & PRD
- ORBIT [Product Name] – Product Charter.docx
- Product Requirement Document (PRD), [Product Name].docx
- Roadmap & Phasing – [Product Name].pptx
- RACI – [Product Name].xlsx

### 02 – Governance & Risk
- ORBIT [Product Name] – Governance Sign-Off Checklist.xlsx
- ORBIT [Product Name] – Risk Assessment & NIST AI RMF Mapping.docx
- Data Classification Mapping – [Product Name].xlsx
- Legal / ER / Compliance Approvals – [Product Name].pdf

### 03 – Data Contract & Schema
- ORBIT [Product Name] – Data Contract v1.0.docx
- ORBIT [Product Name] – Specs & Schema.xlsx
- Source Systems & Lineage – [Product Name].drawio

### 04 – Pipelines & Architecture
- End-to-End Architecture Diagram – [Product Name].drawio
- ETL / ELT Pipeline Spec – [Product Name].docx
- Snowflake Objects Inventory – [Product Name].xlsx
- AI / Agent Orchestration Flows – [Product Name].docx *(when product uses AI agents)*

### 05 – Application & UX
- User Journeys – [Product Name].pptx
- Wireframes & Interaction Flows – [Product Name].pptx
- Copy & Narrative Templates – [Product Name].docx
- Access & Permissions Model – [Product Name].docx

### 06 – Testing & QA
- Test Plan – [Product Name].docx
- Test Cases & Scenarios – [Product Name].xlsx
- UAT Plan & Sign-Off – [Product Name].docx
- Model / Agent Evaluation Logs – [Product Name].xlsx *(where applicable)*

### 07 – Runbook & Operations
- Runbook – [Product Name].docx *(includes on-call, SLAs, rotations)*
- Incident Playbook – [Product Name].docx
- Monitoring & Alerts – [Product Name].xlsx
- Release Notes – [Product Name].md

### 08 – Metrics & WBR Artifacts
- Success Metrics & KPIs – [Product Name].xlsx
- Baseline & Time Series – [Product Name].xlsx
- WBR Report Template – [Product Name].pptx
- Voice of the Customer Log – [Product Name].docx

### 09 – Stakeholder & Change Mgmt
- Stakeholder Map & Comms Plan – [Product Name].docx
- Training Deck – [Product Name].pptx
- FAQ & Guardrails – [Product Name].docx
- Adoption & Feedback Tracker – [Product Name].xlsx

### 99 – Archive
- Quarterly subfolders: `2026-Q1`, `2026-Q2`, `2026-Q3`, `2026-Q4`, etc.
- Holds superseded specs, schemas, decks, and retired artifacts.

---

## 3. Product-Specific Overrides

### HR Workload Lens
- **01:** Product Requirement Document (PRD), Workload Lens.docx
- **03:** ORBIT HR Workload Lens – Specs & Schema.xlsx *(timecard audit fields, ownership mapping, defect/rework classifications)*
- **04:** Time & Attendance WBR Architecture – Workload Lens.drawio
- **08:** Time & Attendance WBR Template – Workload Lens.pptx; Workload Lens – Voice of the Customer Log.docx

### ECHO Intelligence
- **01:** Product Requirement Document (PRD), ORBIT ECHO Intelligence.docx
- **03:** ORBIT ECHO Intelligence – Fulfillment Employee Voice Signal Specs & Schema.xlsx
- **04:** Layered System Architecture – ORBIT ECHO Intelligence.drawio; AI Agent Prompt & Governance Templates – ORBIT ECHO Intelligence.docx
- **05:** Report Skeleton & Narrative Templates – ORBIT ECHO Intelligence.docx
- **08:** POC Evaluation Metrics – ORBIT ECHO Intelligence.xlsx; ECHO Intelligence – Voice of the Customer Log.docx

---

## 4. Current ORBIT Products

| # | Product | Root Folder |
|---|---------|-------------|
| 01 | Daily People Pulse | ORBIT – Daily People Pulse |
| 02 | Bubble Report Generator | ORBIT – Bubble Report Generator |
| 03 | TMDM Paycode Reconciler | ORBIT – TMDM Paycode Reconciler |
| 04 | HR Workload Lens | ORBIT – HR Workload Lens |
| 05 | ECHO Intelligence | ORBIT – ECHO Intelligence |
