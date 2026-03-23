# Data Map and Classification Declaration, ECHO Intelligence

| Field | Value |
| --- | --- |
| **Product** | ECHO Intelligence |
| **Platform** | ORBIT Phoenix |
| **Product Owner** | Kenny Wallace |
| **Version** | 1.0 |
| **Last Updated** | 2026-03-17 |

---

## 1. Purpose

This document maps every data element used by ECHO Intelligence from source system to unified output, classifies each element by sensitivity, and declares the data handling requirements for the product.

---

## 2. Data Lineage Overview

```text
SOURCE SYSTEMS                          SNOWFLAKE                                  OUTPUT
──────────────                          ─────────                                  ──────

CAT Tracker ──────────────────────────► FULFILLMENT_CAT_TRACKER ───┐
  • Multi-mechanism feedback                                        │
  • Site-level signals                                              │
                                                                    │
VOC Board ────────────────────────────► VOC_BOARD ─────────────────┤
  • Public whiteboard feedback                                      │
  • Deduped against CAT Tracker                                     ├──► Unified SQL
                                                                    │    (ALL_SOURCES CTE)
Standup Meetings ─────────────────────► FULFILLMENT_STAND_UPS ─────┤         │
  • TM feedback responses                                           │         │
  • Filler-filtered                                                 │         ▼
                                                                    │    15-Column
New Hire Surveys ─────────────────────► FULFILLMENT_NEW_HIRE_ ─────┤    Unified Schema
  • Orientation improvement                  SURVEYS                │    + Business Unit
  • Context fields concatenated                                     │    + Regex Escalation
                                                                    │         │
Week 3 Surveys ───────────────────────► FULFILLMENT_WEEK_THREE_ ───┘         │
  • Post-hire improvement                    SURVEY                           ▼
  • Context fields concatenated                                     CSV Export / Report
                                                                    Generation
                                                                         │
                                                                         ▼
                                                                    VOC Pulse Report
                                                                    (Aggregated, no
                                                                     individual signals)
```

All source tables reside in `EDLDB.PEOPLE_ANALYTICS_SANDBOX`.

---

## 3. Source-to-Output Field Map

### 3.1 From FULFILLMENT_CAT_TRACKER

| Source Column | Output Column | Transformation | Data Classification |
| --- | --- | --- | --- |
| `MODIFIED` | `MODIFIED` | Direct pass-through | System Timestamp |
| `CREATED` | `CREATED` | Direct pass-through | System Timestamp |
| `PRIMARY_TEXT` | `PRIMARY_TEXT` | Direct pass-through | **Sensitive — Free-Text TM Feedback** |
| `RESOLUTION` | `RESOLUTION` | Direct pass-through | Business Attribute |
| `ROW_DATE` | `ROW_DATE` | Direct pass-through | Business Attribute |
| `VOICE_MECHANISM` | `VOICE_MECHANISM` | Normalized via CASE (walks → "Site Leadership Walks", gembas → "Gemba Walks", standups → "Standups") | Business Attribute |
| `CATEGORY` | `CATEGORY` | Direct pass-through | Business Attribute |
| `ACTION_COMPLETED` | `ACTION_COMPLETED` | Direct pass-through | Business Attribute |
| `DATE_ARCHIVED` | `DATE_ARCHIVED` | Direct pass-through | Business Attribute |
| `LOAD_DTTM` | `LOAD_DTTM` | Direct pass-through | System Timestamp |
| `SHEET_NAME` | `SITE_CODE` | `LEFT(SHEET_NAME, 4)` — extracts 4-character site code | Business Attribute |

### 3.2 From VOC_BOARD

| Source Column | Output Column | Transformation | Data Classification |
| --- | --- | --- | --- |
| `CREATED_DATE` | `CREATED` | Aliased | System Timestamp |
| `FEEDBACK` | `PRIMARY_TEXT` | Aliased; used in dedup match against CAT Tracker | **Sensitive — Free-Text TM Feedback** |
| `RESOLUTION` | `RESOLUTION` | Direct pass-through | Business Attribute |
| `DATE_POSTED` | `ROW_DATE` | Aliased; filtered to `>= '2025-01-01'` | Business Attribute |
| `CATEGORY` | `CATEGORY` | Direct pass-through | Business Attribute |
| `LOCATION` | `SITE_CODE` | `LEFT(LOCATION, 4)` | Business Attribute |
| (derived) | `VOICE_MECHANISM` | Fixed: `'VOC Board'` | Business Attribute |
| (derived) | `ACTION_COMPLETED` | `CASE WHEN RESOLUTION IS NOT NULL AND TRIM(RESOLUTION) != '' THEN 'Yes' ELSE 'No'` | Business Attribute |

### 3.3 From FULFILLMENT_STAND_UPS

| Source Column | Output Column | Transformation | Data Classification |
| --- | --- | --- | --- |
| `TIME_STAMP` | `CREATED` | Aliased | System Timestamp |
| `TEAM_MEMBER_FEEDBACK` | `PRIMARY_TEXT` | Aliased; filtered for non-null, non-filler | **Sensitive — Free-Text TM Feedback** |
| `DATE` | `ROW_DATE` | Aliased | Business Attribute |
| `CONTENT_ASSESSMENT` | `CATEGORY` | Manager's presentation topic mapped to category for context | Business Attribute |
| `FULFILLMENT_CENTER` | `SITE_CODE` | `LEFT(FULFILLMENT_CENTER, 4)` | Business Attribute |
| (derived) | `VOICE_MECHANISM` | Fixed: `'Standups'` | Business Attribute |

### 3.4 From FULFILLMENT_NEW_HIRE_SURVEYS

| Source Column | Output Column | Transformation | Data Classification |
| --- | --- | --- | --- |
| `CREATED` | `CREATED` | Direct pass-through | System Timestamp |
| `NHO_IMPROVE` | `PRIMARY_TEXT` | Aliased; filtered for non-null, non-filler | **Sensitive — Free-Text TM Feedback** |
| `CREATED` | `ROW_DATE` | `TO_DATE(CREATED)` | Business Attribute |
| `NHO_HAPPY` | `CATEGORY` (partial) | Concatenated: `'Orientation Happiness: ' \|\| NHO_HAPPY \|\| ' \| Top Factor: ' \|\| REC_MOST_IMPORTANT_FACTOR` | Business Attribute |
| `REC_MOST_IMPORTANT_FACTOR` | `CATEGORY` (partial) | Concatenated into CATEGORY string | Business Attribute |
| `LOCATION` | `SITE_CODE` | `LEFT(LOCATION, 4)` | Business Attribute |
| (derived) | `VOICE_MECHANISM` | Fixed: `'New Hire Survey'` | Business Attribute |

### 3.5 From FULFILLMENT_WEEK_THREE_SURVEY

| Source Column | Output Column | Transformation | Data Classification |
| --- | --- | --- | --- |
| `CREATED` | `CREATED` | Direct pass-through | System Timestamp |
| `IMPROVE` | `PRIMARY_TEXT` | Aliased; filtered for non-null, non-filler | **Sensitive — Free-Text TM Feedback** |
| `CREATED` | `ROW_DATE` | `TO_DATE(CREATED)` | Business Attribute |
| `HAPPY` | `CATEGORY` (partial) | Concatenated: `'Happiness: ' \|\| HAPPY \|\| ' \| Physicality: ' \|\| PHYSICALITY \|\| ' \| Preparedness: ' \|\| PREPARED` | Business Attribute |
| `PHYSICALITY` | `CATEGORY` (partial) | Concatenated into CATEGORY string | Business Attribute |
| `PREPARED` | `CATEGORY` (partial) | Concatenated into CATEGORY string | Business Attribute |
| `LOCATION` | `SITE_CODE` | `LEFT(LOCATION, 4)` | Business Attribute |
| (derived) | `VOICE_MECHANISM` | Fixed: `'Week 3 Survey'` | Business Attribute |

### 3.6 Derived Fields (Final SELECT)

| Field | Output Column | Derivation | Data Classification |
| --- | --- | --- | --- |
| `BUSINESS_UNIT` | `BUSINESS_UNIT` | CASE on `SITE_CODE` → FC / Rx / Unknown | Business Attribute |
| `LEGACY_REGEX_ESCALATION` | `LEGACY_REGEX_ESCALATION` | REGEXP_LIKE on `PRIMARY_TEXT` → Level 1/2/3 Priority or NULL | **Sensitive — Escalation Flag** |

---

## 4. Data Classification Summary

### 4.1 Classification Levels

| Level | Definition | Examples in This Product |
| --- | --- | --- |
| **Sensitive — TM Feedback** | Free-text content written by or about team members; may contain incidental PII, complaints, or sensitive workplace observations | `PRIMARY_TEXT`, `RESOLUTION` |
| **Sensitive — Escalation** | Derived flag indicating potential ER-relevant content | `LEGACY_REGEX_ESCALATION` |
| **Business Attribute** | Operational data that is not directly sensitive | `SITE_CODE`, `VOICE_MECHANISM`, `CATEGORY`, `BUSINESS_UNIT`, `ROW_DATE`, `ACTION_COMPLETED` |
| **System** | Technical metadata | `MODIFIED`, `CREATED`, `LOAD_DTTM`, `DATE_ARCHIVED` |

### 4.2 Sensitive Data Inventory

| Element | Source | Classification | Justification for Inclusion | Mitigation |
| --- | --- | --- | --- | --- |
| **PRIMARY_TEXT** | All 5 source tables | Sensitive — TM Feedback | Core signal payload; required for thematic analysis | Aggregated in report output; individual signals not published |
| **RESOLUTION** | CAT Tracker, VOC Board | Sensitive — TM Feedback | May reference specific TMs or situations | Same aggregation approach |
| **LEGACY_REGEX_ESCALATION** | Derived | Sensitive — Escalation | Flags signals for ER review; does not determine action | Human review required before any action; flag is a screening tool only |

### 4.3 PII Considerations

ECHO Intelligence does **not** directly query PII fields (employee names, IDs, SSNs, etc.). However:

- `PRIMARY_TEXT` is free-text TM feedback that **may contain incidental PII** — names of managers, coworkers, or specific individuals mentioned in complaints or praise.
- The VOC Pulse Report output is **aggregated** — it presents signal counts, percentages, and thematic narratives. Individual signal text is not published in the report.
- Raw signal-level data (CSV export) should be treated as sensitive and access-restricted.

---

## 5. Data Handling Requirements

### 5.1 Access Controls

| Requirement | Implementation |
| --- | --- |
| **Who can access raw data** | Product Owner, authorized EPA analysts, and designated ER partners (for escalation review) |
| **Who can access the report** | FC site leadership (GMs, HRMs), FC network leadership, EPA, ER |
| **Access mechanism** | Snowflake RBAC for raw data; report distributed via authorized channels |
| **Authentication** | SSO via corporate identity provider for Snowflake access |

### 5.2 Data Retention

| Requirement | Policy |
| --- | --- |
| **Active data** | Filtered to `ROW_DATE >= '2025-01-01'` in current query; adjustable per reporting period |
| **Historical retention** | Per enterprise data retention policy for `EDLDB.PEOPLE_ANALYTICS_SANDBOX` |
| **Report retention** | Published reports retained per ORBIT product documentation standards |
| **CSV exports** | Treated as sensitive working files; should not be stored in unsecured locations |

### 5.3 Data Transport

| Path | Method | Encryption |
| --- | --- | --- |
| Source systems → Snowflake | EPA-managed ETL pipeline | Encrypted in transit and at rest per enterprise policy |
| Snowflake → Analyst (SQL query) | Snowflake web UI or JDBC/ODBC | TLS encrypted in transit; Snowflake encryption at rest |
| CSV export → Local machine | Downloaded via browser | User's local device; subject to endpoint security policy |
| Report distribution | Authorized channels (email, SharePoint) | Per enterprise communications security policy |

### 5.4 Data Minimization

| Principle | Implementation |
| --- | --- |
| **No direct PII queried** | Query does not join to employee master tables; no names, IDs, or demographics in output |
| **Incidental PII in free text** | Acknowledged; mitigated by aggregated report output and access controls on raw data |
| **Filler filtering** | Non-substantive survey responses excluded to reduce noise |
| **Administrative exclusion** | Non-feedback mechanisms excluded to ensure only genuine TM signals are captured |
| **Site exclusion** | BOS4 and SDF1 excluded as non-active sites |

---

## 6. Compliance Considerations

| Area | Status | Notes |
| --- | --- | --- |
| **Incidental PII in free text** | Review recommended | `PRIMARY_TEXT` may contain names or situations; confirm with Legal that aggregated reporting is sufficient mitigation |
| **Escalation flag usage** | Compliant | Regex flags are screening tools only; ER conducts independent review before action |
| **Survey data usage** | Review recommended | New Hire and Week 3 survey responses used for workforce analysis; confirm alignment with survey consent disclosures |
| **Cross-site comparison** | Compliant | Report compares aggregate metrics; does not identify or rank individual TMs |
| **Data access audit** | Supported | Snowflake supports query audit logging |

---

## 7. Change Control

| Change Type | Process | Owner |
| --- | --- | --- |
| **Add new source table** | Add `UNION ALL` block to `ALL_SOURCES` CTE with appropriate column mapping and filters; update this Data Map | Product Owner |
| **Add new site** | Add site code to `BUSINESS_UNIT` CASE expression; update site list in Data Map and PRD | Product Owner |
| **Change mechanism normalization** | Update CASE expression in CAT Tracker block; update Voice Mechanism Normalization table | Product Owner |
| **Add filler values** | Append to `NOT IN` list in relevant survey block; document in this Data Map | Product Owner |
| **Add excluded mechanism** | Append to `VOICE_MECHANISM NOT IN` filter in final WHERE clause | Product Owner |
| **Modify escalation regex** | Update REGEXP_LIKE patterns in final SELECT; document in this Data Map and coordinate with ER | Product Owner + ER |
| **EPA pipeline migration** | Replace interim SQL with EPA pipeline; validate output schema matches; update Technical Design Doc | EPA + Product Owner |
