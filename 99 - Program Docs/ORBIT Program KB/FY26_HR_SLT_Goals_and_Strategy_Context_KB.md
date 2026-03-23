---
kb_id: chewy-hr-fy26-slt-goals-strategy
canonical_title: FY26 HR SLT Goals and Strategy Context
version: 0.1
status: working-draft
compiled_date: 2026-03-17
effective_period: FY2026
confidentiality: internal
intended_consumers:
  - internal agents
  - MCP servers
  - knowledge retrieval pipelines
retrieval_tags:
  - chewy
  - hr
  - hrlt
  - slt
  - fy26
  - strategy
  - goals
  - enterprise priorities
  - talent
  - compensation
  - loaa
  - ai
  - self-service
aliases:
  - 2026 hr goals
  - fy26 hr goals
  - fy26 hr slt priorities
  - hr op1 charters
mcp:
  namespace: chewy.hr.strategy
  entity_type: knowledge_base
  schema_version: 0.1
  chunking_hint: split_on_h2_and_h3
  canonical_record_prefix: hr-fy26
  preferred_retrieval_order:
    - executive summary
    - priority themes
    - goal registry
    - detailed goal records
agent_instructions:
  - Use this file as strategic context, not as final policy or legal guidance.
  - Treat goals, timing, and KPIs as working-draft unless revalidated against source charters.
  - When answering broad FY26 HR questions, start with the enterprise context and then summarize the HR themes.
  - When answering detailed questions, use the goal record with the closest title/theme match.
  - If a request is operational or policy-specific, route to the source owner or source system before asserting final guidance.
source_inventory:
  - Enterprise priorities SS.pdf
  - these will change but fyi on 2026 goals.zip
---

# FY26 HR SLT Goals and Strategy Context

## What this file is
This file is a synthesized knowledge base for agents that need quick context on Chewy HR's FY26 goals, draft priorities, and strategic direction. It is designed to be readable by humans now and easy to ingest into MCP-style retrieval flows later.

## Working assumptions
- These goal charters appear to be draft or in-flight planning artifacts and may change.
- Several timelines use fiscal periods (P1-P12) rather than calendar months.
- A few goals extend into FY27 even though they are part of the FY26 planning set.
- Some success metrics are explicit; others are still TBD or dependent on resource approval.

## How agents should answer from this KB
When an agent is asked, "What matters for HR in FY26?", the safest summary is:
1. Scale HR self-service and AI-enabled experiences.
2. Reduce manual HR work through automation, especially in compensation and case management.
3. Modernize culture, leadership expectations, and the HR operating model.
4. Improve frontline access, workforce flexibility, and manager/TM experience.
5. Standardize leave and absence processes while improving operational discipline.

When an agent is asked, "What enterprise context should HR keep in mind?", the answer should start with the four FY26 enterprise focus areas and then connect HR work to those priorities.

## Enterprise context for FY26
Chewy's FY26 enterprise priorities are organized around four focus areas:

1. **Pet Health**
   - Continue disciplined expansion of Chewy Vet Care.
   - Accelerate Pharmacy growth while improving cost structure and purchase/post-purchase experience.
   - Expand telemedicine coverage.
   - Advance product and technology innovation in care delivery.

2. **Expand Core and Emerging Offerings**
   - Grow Equine and Specialty.
   - Accelerate Supplements.
   - Improve Private Brands execution and roadmap discipline.
   - Grow Chewy+ sustainably and profitably.

3. **Enhance Purchase and Post-Purchase Experiences**
   - Continue scaling the mobile app.
   - Modernize search and discovery, including NLP-led interactive experiences.
   - Scale social engagement and commerce.

4. **Data and AI**
   - Build a world-class data foundation.
   - Unify customer signals for personalization.
   - Scale AI Unbound.
   - Lead the pet industry in applied AI.

## What that means for HR
HR's FY26 portfolio is not a mirror of the enterprise priorities, but it clearly supports them in five cross-cutting ways:

### 1) AI, self-service, and digital employee experience
HR is building an internal AI and self-service stack that includes the HR Knowledge Hub, Team Member App, ServiceNow Agent Workspace, AI Recruiter pilot, and AI workforce readiness work. Together, these goals aim to reduce friction, improve access to information, and create a foundation for agentic HR workflows.

### 2) HR operating model and capability transformation
Several goals focus on redefining how HR works: HRBP/HRG transformation, HR Academy, AI fluency, revised Operating Principles, and Leader Expectations. The common thread is a more strategic HR function with clearer expectations, stronger capability models, and more scalable execution.

### 3) Operational discipline and manual work reduction
Compensation automation, severance automation, off-cycle tracking, LOAA improvements, and case management modernization all point to the same strategy: reduce administrative effort, improve data quality, and create more auditable workflows.

### 4) Frontline and workforce flexibility
The Team Member App, flexible staffing pilots, and frontline access improvements are aimed at non-exempt and frontline populations that historically have more fragmented access to HR tools and services.

### 5) Standardization and governance
Across leave, compensation, knowledge content, and case handling, the portfolio emphasizes governance, standardized definitions, consistent processes, and controlled rollout rather than one-off local solutions.

## Priority themes

### Theme A: AI, self-service, and HR tech enablement
Primary goals:
- `hr-fy26-knowledge-hub`
- `hr-fy26-tm-app`
- `hr-fy26-agent-workspace`
- `hr-fy26-ai-recruiter`
- `hr-fy26-ai-workforce-readiness`

### Theme B: Talent, culture, and leadership transformation
Primary goals:
- `hr-fy26-op-refresh`
- `hr-fy26-leader-expectations`
- `hr-fy26-hr-academy`
- `hr-fy26-hrbp-hrg-transformation`

### Theme C: Workforce flexibility and staffing innovation
Primary goals:
- `hr-fy26-flex-staffing-enterprise`
- `hr-fy26-flex-staffing-cc-pilot`

### Theme D: Leave and absence modernization
Primary goals:
- `hr-fy26-loaa-improvement`
- `hr-fy26-loaa-tpa-implementation`

### Theme E: Compensation automation and transparency
Primary goals:
- `hr-fy26-comp-modeling-tool`
- `hr-fy26-comp-model-automation`
- `hr-fy26-off-cycle-tracker`
- `hr-fy26-severance-automation`

## Goal registry
| Goal ID | Goal title | Primary theme | Why it matters |
|---|---|---|---|
| `hr-fy26-knowledge-hub` | HR Knowledge Hub | AI/self-service | Foundational HR knowledge platform for consistent natural-language answers and future integrations. |
| `hr-fy26-tm-app` | Team Member App | AI/self-service | Mobile-first access point for frontline/non-exempt TMs to reach HR systems and support. |
| `hr-fy26-agent-workspace` | ServiceNow Agent Workspace | AI/self-service | Centralizes HR case handling and sets up AI-assisted agent workflows. |
| `hr-fy26-ai-recruiter` | AI Recruiter (Clara pilot) | AI/self-service | Tests agentic AI in FC high-volume hiring to improve speed, quality, and efficiency. |
| `hr-fy26-ai-workforce-readiness` | AI Workforce Readiness & Career Path | Talent/capability | Defines AI fluency expectations and how to embed them into talent systems. |
| `hr-fy26-op-refresh` | Transform and Embed the OPs | Culture/leadership | Refreshes the Operating Principles and drives enterprise-wide embedment. |
| `hr-fy26-leader-expectations` | Define Leadership Expectations | Culture/leadership | Clarifies what effective leadership means at Chewy and ties it to the talent lifecycle. |
| `hr-fy26-hr-academy` | HR Academy | Talent/capability | Upskills HR teams and leaders to operate in the transformed HR model. |
| `hr-fy26-hrbp-hrg-transformation` | HRBP/HRG Transformation | Talent/operating model | Shifts appropriate work from HRBPs to HRGs and clarifies future roles. |
| `hr-fy26-flex-staffing-enterprise` | Enterprise Flex Staffing | Workforce flexibility | Builds flexible staffing models across FC, CC, Rx, and CVC to improve labor agility. |
| `hr-fy26-flex-staffing-cc-pilot` | CC Part-Time Pilot | Workforce flexibility | Controlled first step for flex staffing inside Customer Care. |
| `hr-fy26-loaa-improvement` | Improve TM, HR, and Manager Experience with LOA | LOAA modernization | Improves LOAA operations, policies, and support experience. |
| `hr-fy26-loaa-tpa-implementation` | LOAA TPA Implementation | LOAA modernization | Re-platforms LOAA delivery with a new vendor and stronger reporting/integration. |
| `hr-fy26-comp-modeling-tool` | Compensation Modeling Tool | Compensation automation | Expands visibility and self-service for pay modeling and compensation understanding. |
| `hr-fy26-comp-model-automation` | Automating Compensation Models | Compensation automation | Replaces legacy Excel modelers with more auditable and scalable tooling. |
| `hr-fy26-off-cycle-tracker` | Off-cycle Tracker Transactions | Compensation automation | Automates off-cycle pay request tracking and reporting. |
| `hr-fy26-severance-automation` | Severance Automation | Compensation automation | Automates severance planning, modeling, and execution in Workday. |

## Detailed goal records

### `hr-fy26-knowledge-hub`
**Title:** HR Knowledge Hub  
**Owners:** HRLT owner Greg Arendt; goal owner Gatumbi Gathuka; project owner Wade Sorenson  
**Timing:** FY25 start through P12 FY26  
**Objective:** Deliver an AI-powered HR knowledge platform with governance that gives employees consistent natural-language answers and reduces reliance on HR support channels.  
**Key work:** MVP chatbot release; Moveworks integration; Team Member App integration; quarterly improvements and agentic HRDM capabilities.  
**Success signals:** <4% bad-response rate at launch; P50 API latency under 5 seconds; <0.1% technical failure rate; 10% quarter-over-quarter session growth; target to improve to <2% bad responses by year end.  
**Agent context:** This is the foundational HR knowledge asset in the portfolio and is a dependency/enabler for both TM App and other conversational self-service experiences.

### `hr-fy26-tm-app`
**Title:** Team Member App  
**Owners:** HRLT owner Greg Arendt; goal owner Jason Morga; core team Jason Morga, Michelle Winner, Tabitha Dziak, Marybeth Allen  
**Timing:** Continuation from FY25 through P12 FY26  
**Objective:** Launch a centralized, mobile-first app for frontline and non-exempt FC/Rx team members that brings together Workday, UKG WFM Pro, ServiceNow, and conversational HR support via SSO.  
**Key work:** Platform selection; MVP build; align Knowledge Hub content with AI conversational search; pilot prep; two-market pilot; network-wide launch with Okta Lite.  
**Success signals:** 20-30% improvement in time-on-floor productivity/equity of access; at least 75% adoption within one year of launch; additional 30% YoY reduction in password resets for non-exempt users.  
**Agent context:** This is the frontline digital front door for HR and connects directly to the Knowledge Hub and ServiceNow capabilities.

### `hr-fy26-agent-workspace`
**Title:** ServiceNow Agent Workspace  
**Owners:** HRLT owner Greg Arendt; goal owner Matt Murphy; project owners Matt Murphy and Tabitha Dziak  
**Timing:** P1 through P10 FY26  
**Objective:** Implement ServiceNow Agent Workspace with Now Assist to centralize HR case management, automate triage/routing, and create the foundation for AI-assisted HR service workflows.  
**Key work:** Improve case resolution time; assess and grow AI-aided triage; increase knowledge article utilization.  
**Success signals:** 25% reduction in average HR case handling time (from ~10 minutes to ~7.5 minutes per case); additional automation and knowledge-usage targets to be set after baseline assessment.  
**Agent context:** This is the agent-side companion to self-service channels. It matters when questions relate to HR Shared Services operations or future HR service automation.

### `hr-fy26-ai-recruiter`
**Title:** AI Recruiter (Clara pilot)  
**Owners:** HRLT owner Greg Arendt; goal owner and project owner Jessica Coleman  
**Timing:** December 2025 through June 2026  
**Objective:** Pilot Clara, an agentic AI recruiting agent, in FC high-volume hiring to reduce time-to-hire, improve candidate quality and experience, and preserve compliance/privacy standards.  
**Key work:** Proof of concept; ATS and HR systems integration; controlled rollout at one FC with a 90-day live test.  
**Success signals:** Ethical alignment with interview framework; on-time integration; go/no-go decision after controlled pilot; target operating context is a TA team supporting >50% more hires with 60% fewer staff.  
**Agent context:** This is one of the clearest examples of HR aligning to the company's broader Data and AI priority.

### `hr-fy26-ai-workforce-readiness`
**Title:** AI Workforce Readiness & Career Path  
**Owners:** HRLT owner and goal owner Jess Pizzica; project owner TBD  
**Timing:** P11 FY25 through early FY26 milestones  
**Objective:** Update competency frameworks and talent processes so AI fluency, judgment, and appropriate use are represented in the workforce model.  
**Key work:** Define who is assessable and who needs access; assign ownership for AI learning paths; build core AI proficiency training; define how fluency will be measured; update frameworks; leader enablement.  
**Success signals:** Clear access/exemption decisions; structured AI learning path; fluency proxy/dashboard; frameworks updated to reflect AI expectations; leaders report greater readiness to coach teams on AI use.  
**Agent context:** This goal is about responsible AI fluency, not just tool adoption. The framing explicitly emphasizes judgment and supplementing rather than replacing human decision-making.

### `hr-fy26-op-refresh`
**Title:** Transform and Embed the OPs  
**Owners:** HRLT owner Jess Pizzica; goal owner and project owner Victoria Grzelcyk  
**Timing:** P09 FY25 through P09 FY26  
**Objective:** Refresh the Operating Principles and embed them so they remain the core behavioral foundation of Chewy culture.  
**Key work:** Needs assessment; revised OP design and approval; launch prep; integrated launch with leader expectations; post-launch embedment; measurement and continuous improvement.  
**Success signals:** Revamped OPs launched by P03 FY26; embedment through P09 FY26; >60% VOC response rate in discovery; 80% completion of embedment actions.  
**Agent context:** This is a culture-shaping initiative and should be treated as foundational context for leadership, performance, and behavior-related questions.

### `hr-fy26-leader-expectations`
**Title:** Define Leadership Expectations  
**Owners:** HRLT owner Jess Pizzica; goal owner and project owner Victoria Grzelcyk  
**Timing:** P10 FY25 through P07 FY26  
**Objective:** Define what leadership means at Chewy through a clear expectations/competency framework that can be integrated across the talent lifecycle.  
**Key work:** Scoping; needs assessment; framework design; stakeholder reviews; launch prep; integrated launch with revised OPs.  
**Success signals:** Senior leadership alignment; timely framework approval; readiness materials completed before launch; evidence of leader understanding and adoption in later VOC/engagement/performance signals.  
**Agent context:** This initiative is tightly coupled with the OP refresh and broader talent philosophy.

### `hr-fy26-hr-academy`
**Title:** HR Academy  
**Owners:** HRLT owner Jess Pizzica; goal owner Blair Bekker; project owner Sean Minard  
**Timing:** P09 FY25 through FY26  
**Objective:** Design, launch, and scale an HR Academy that reskills and upskills HR team members and leaders for the HR transformation.  
**Key work:** Four phases: mindset shift, new ways of working, advanced skills, and functional training tied to competency models and HRBP job architecture.  
**Success signals:** >=90% participation for each audience; 80% training satisfaction; 80% learning application 30 days after training.  
**Agent context:** This is the primary capability-building engine for HR transformation and should be linked mentally with HRBP/HRG transformation and the new leadership/OP frameworks.

### `hr-fy26-hrbp-hrg-transformation`
**Title:** Creating Strategic HRBP Potential through HRG Transformation  
**Owners:** HRLT owners John Curtin and Mike Stevens; goal owner and project owner Rich Brady  
**Timing:** FY25 Q2 through FY26 Q4  
**Objective:** Shift appropriate transactional/standardized HRBP work to HRGs, clarify future HRBP/HRG roles, and create a more strategic HRBP model.  
**Key work:** Job architecture; competencies; standard work cataloging; standard work categorization; transition of shiftable work; optimization/elimination of low-value work.  
**Success signals:** 100% of identified standard work categorized; at least 50% of tasks marked for action off HRBP scope; target to shift 100% of identified shiftable work in FY26 and optimize 75% of processes identified for redesign.  
**Agent context:** This is one of the biggest structural changes in the HR portfolio and explains many adjacent capability and training investments.

### `hr-fy26-flex-staffing-enterprise`
**Title:** Enterprise Flex Staffing  
**Owners:** HRLT owner Mike Stevens; goal owner Bradley Campbell; project owner Ashley LaRue  
**Timing:** Q3 FY25 through Q4 FY26  
**Objective:** Design, pilot, and scale non-exempt staffing strategies across FC, CC, Rx, and CVC to improve labor agility, reduce overtime/agency costs, and reduce attrition.  
**Key work:** Seasonal staffing implementation; CC part-time pilot; shift structure optimization; phase 2 enterprise planning; shift swap rollout.  
**Success signals:** 15-20% improvement in labor agility; 10% reduction in overtime/agency usage cost; 5% reduction in attrition among targeted job classes; local KPIs include fill rate, attendance, OT reduction, and net savings.  
**Agent context:** This is a cross-business workforce model initiative, not just a recruiting or scheduling project.

### `hr-fy26-flex-staffing-cc-pilot`
**Title:** Customer Care Flexible Working Strategies (Part-Time Pilot)  
**Owners:** HRLT owner Mike Stevens; goal owner Bradley Campbell; project owners Mandy Stepan and Lyndsey Hover  
**Timing:** P8 2025 through P12 2026  
**Objective:** Run a controlled Customer Care part-time pilot as the first step in a broader flex staffing strategy.  
**Key work:** Define pilot framework; validate systems/compliance across Workday, UKG, NICE, and Payroll; configure schedules; launch with 27 internal PT participants; monitor pilot economics and retention impact.  
**Success signals:** Successful transition of 27 pilot participants; OT reduction target around 2%; finance-validated benefits savings; future enterprise flex options informed by pilot learnings.  
**Agent context:** This is explicitly narrower than the enterprise flex staffing program and should be treated as a first controlled experiment, not the final future-state model.

### `hr-fy26-loaa-improvement`
**Title:** Improve TM, HR, and Manager Experience with LOA  
**Owners:** HRLT owner Libby Posner; goal owner Carl Cudworth; project owner Rosie Blanco  
**Timing:** P1 through P6 FY26  
**Objective:** Improve LOAA operations and experience through reporting, policy/process consistency, and an AI assistant that supports LOAA handling.  
**Key work:** Monthly defect dashboard; standardize bereavement and personal LOA policies/processes across BUs; deploy LOAA AI assistant.  
**Success signals:** 20% reduction in ineligible claims; 5% reduction in denial rates; 5% reduction in LOAA escalations; policy alignment across BUs.  
**Agent context:** This is the process/experience improvement side of the LOAA portfolio and is distinct from the TPA re-platforming work.

### `hr-fy26-loaa-tpa-implementation`
**Title:** LOAA TPA Implementation  
**Owners:** HRLT owner Libby Posner; goal owner Carl Cudworth; project owner Devon McGill  
**Timing:** P1 through P12 FY26  
**Objective:** Select and implement a new LOAA third-party administrator with stronger system integration, reporting, analytics, and cross-business consistency.  
**Key work:** RFP and vendor selection; contracting; systems requirements; implementation/configuration; reporting/dashboard development; process/training materials; change management.  
**Success signals:** 100% business unit transition; zero critical defects at launch; on-time reporting; high data accuracy; structured stakeholder engagement.  
**Agent context:** The charter emphasizes one-system visibility across leave/disability/ADA, strong Workday/UKG integration, analytics, and faster custom communications/reporting.

### `hr-fy26-comp-modeling-tool`
**Title:** Compensation Modeling Tool  
**Owners:** HRLT owner Libby Posner; goal owner Michael Williams; project owner Jamie Fallarino  
**Timing:** P6 FY25 through P12 FY26  
**Objective:** Expand and operationalize the Compensation Modeling Tool to improve transparency, consistency, and self-service in compensation planning.  
**Key work:** HR rollout; LTI grant/vesting visibility; SLT rollout; standardized compensation terminology; broader leader rollout; TM-facing visibility enhancements; UAT; training and communications.  
**Success signals:** 500+ hours of manual compensation work reduced annually; 100% SLT access/training by end of 2025; 100% VP/C09/C08 rollout by end of P2 FY26; at least 50% of eligible TMs use the visibility experience within 60 days; at least 50% satisfaction with clarity/usefulness.  
**Agent context:** This goal is both an operations efficiency play and a compensation transparency/education play.

### `hr-fy26-comp-model-automation`
**Title:** Automating Compensation Models  
**Owners:** HRLT owner Libby Posner; goal owner Michael Williams; project owner Sam Gentile  
**Timing:** P1 FY26 through P3 FY27  
**Objective:** Replace legacy Excel-based compensation modelers with an auditable automated solution for tools such as Target vs. Earnings, Geo Review, and TA Offer.  
**Key work:** Document current modelers; feasibility/cost assessment; platform selection; build; test; go-live; training.  
**Success signals:** Full migration of three legacy modelers by P12 FY26; validated data integrity; 10% increase in Compensation team strategic capacity by P12 FY26; 100% training completion by P3 FY27.  
**Agent context:** This is the back-end automation counterpart to the more user-facing Compensation Modeling Tool work.

### `hr-fy26-off-cycle-tracker`
**Title:** Off-cycle Tracker Transactions  
**Owners:** HRLT owner Libby Posner; goal owner Emily Brown; project owner Stephany Schulz  
**Timing:** FY25 P11 through FY26 P12  
**Objective:** Replace manual Excel-based off-cycle pay transaction tracking with a centralized automated request, approval, and reporting flow.  
**Key work:** Automation readiness assessment; feasibility assessment with HRIS; build prototype; testing/UAT; enterprise deployment; possible future integration into end-to-end offer letter flows.  
**Success signals:** Reduce manual effort from ~400+ hours annually to <50 hours; >=98% data accuracy post-launch; <1% discrepancy in pilot reporting; 100% off-cycle data captured in trend reporting; average entry time <5 minutes.  
**Agent context:** Resource timing and HRIS capacity are explicit dependencies in this charter.

### `hr-fy26-severance-automation`
**Title:** Severance Automation  
**Owners:** HRLT owner Libby Posner; goal owner Michael Williams; project owner Jamie Fallarino  
**Timing:** P6 2025 through P6 2026  
**Objective:** Automate severance planning and execution in Workday by combining employee, compensation, benefits, and tax data with secure modeling and severance-module execution.  
**Key work:** Unified data source; planning worksheet build; current/future-state process design; pilot; security enablement; severance module implementation; audit/reporting enablement.  
**Success signals:** >50 hours annual manual work reduction within Compensation alone; zero security violations; 100% severance cases processed through the Workday severance module; no manual reconciliation for audit reporting.  
**Agent context:** This is a high-control, audit-heavy process modernization effort with clear security and data-governance needs.

## Cross-goal relationships
- **Knowledge Hub -> TM App -> Agent Workspace**: these are best understood as a connected ecosystem rather than separate tools.
- **AI Workforce Readiness -> HR Academy -> Leader Expectations/OP Refresh**: these combine into a single capability-and-behavior change story.
- **HRBP/HRG Transformation -> HR Academy**: Academy supports the model shift.
- **Enterprise Flex Staffing -> CC PT Pilot**: the CC pilot is a controlled first use case within the broader flex staffing strategy.
- **LOAA Improvement -> LOAA TPA Implementation**: one improves internal process/experience while the other re-platforms the external/vendor model.
- **Comp Modeling Tool -> Compensation Model Automation -> Off-cycle Tracker -> Severance Automation**: these are all part of a broader compensation operations automation agenda.

## Suggested one-paragraph summary for agents
In FY26, HR appears to be pursuing a dual agenda: first, modernize the employee and HR service experience through AI, self-service, mobile access, and case-management tooling; second, improve operational discipline by automating manual compensation and leave processes, while also reshaping HR capabilities, leadership expectations, and the HR operating model. The practical outcome HR is aiming for is a function that is more scalable, more data-driven, more standardized, and better able to support frontline, manager, and leadership needs.

## MCP ingestion notes
If this file is ingested into an MCP server later, preferred chunk boundaries are:
1. front matter
2. enterprise context
3. what that means for HR
4. goal registry
5. one chunk per detailed goal record
6. cross-goal relationships
7. suggested one-paragraph summary

Recommended retrieval aliases by user intent:
- "What are HR's 2026 goals?"
- "What is HR focused on in FY26?"
- "What are the HRLT priorities?"
- "How does HR align to FY26 enterprise priorities?"
- "What are the AI-related HR goals?"
- "Which goals are about compensation automation?"
- "What is the leave/LOAA strategy?"
- "What is the frontline/TM app strategy?"

## Source list
Primary inputs used to compile this KB:
- Enterprise priorities PDF from Sumit
- FY26 HR goal charter documents contained in the uploaded zip archive

