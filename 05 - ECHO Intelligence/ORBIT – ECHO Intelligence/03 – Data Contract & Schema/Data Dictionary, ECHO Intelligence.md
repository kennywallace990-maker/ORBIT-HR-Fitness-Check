# ECHO Intelligence — Data Dictionary

| Field | Value |
| --- | --- |
| **Product** | ECHO Intelligence |
| **Platform** | ORBIT Phoenix |
| **Product Owner** | Kenny Wallace |
| **Version** | 1.0 |
| **Last Updated** | 2026-03-17 |

---

## 1. Source Tables

| # | Table | Database.Schema | Purpose |
| --- | --- | --- | --- |
| 1 | `FULFILLMENT_CAT_TRACKER` | `EDLDB.PEOPLE_ANALYTICS_SANDBOX` | Primary feedback tracker; multi-mechanism signals per site |
| 2 | `VOC_BOARD` | `EDLDB.PEOPLE_ANALYTICS_SANDBOX` | VOC Board public whiteboard feedback |
| 3 | `FULFILLMENT_STAND_UPS` | `EDLDB.PEOPLE_ANALYTICS_SANDBOX` | Standup meeting TM feedback responses |
| 4 | `FULFILLMENT_NEW_HIRE_SURVEYS` | `EDLDB.PEOPLE_ANALYTICS_SANDBOX` | New hire orientation improvement suggestions |
| 5 | `FULFILLMENT_WEEK_THREE_SURVEY` | `EDLDB.PEOPLE_ANALYTICS_SANDBOX` | Week 3 post-hire improvement suggestions |

---

## 2. Unified Output Schema (15 Columns)

The unified SQL query normalizes all five source tables into this common schema:

| # | Column | Data Type | Nullable | Source(s) | Description | Example |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `MODIFIED` | TIMESTAMP | No | CAT Tracker: `MODIFIED`; Others: `CURRENT_TIMESTAMP()` | Last modification timestamp | 2025-06-15 14:32:00 |
| 2 | `CREATED` | TIMESTAMP | No | CAT: `CREATED`; VOC: `CREATED_DATE`; Standups: `TIME_STAMP`; Surveys: `CREATED` | Creation/submission timestamp | 2025-06-15 08:00:00 |
| 3 | `PRIMARY_TEXT` | VARCHAR | No | CAT: `PRIMARY_TEXT`; VOC: `FEEDBACK`; Standups: `TEAM_MEMBER_FEEDBACK`; NHO: `NHO_IMPROVE`; W3: `IMPROVE` | Core TM feedback text — the signal payload | "We need more ladders on the mezzanine level" |
| 4 | `RESOLUTION` | VARCHAR | Yes | CAT: `RESOLUTION`; VOC: `RESOLUTION`; Others: NULL | Resolution or response text | "Ordered 3 additional ladders" |
| 5 | `ROW_DATE` | DATE | No | CAT: `ROW_DATE`; VOC: `DATE_POSTED`; Standups: `DATE`; Surveys: `TO_DATE(CREATED)` | Date the signal was recorded | 2025-06-15 |
| 6 | `VOICE_MECHANISM` | VARCHAR | No | CAT: normalized via CASE; VOC: `'VOC Board'`; Standups: `'Standups'`; NHO: `'New Hire Survey'`; W3: `'Week 3 Survey'` | Normalized listening mechanism label | Site Leadership Walks |
| 7 | `CATEGORY` | VARCHAR | Yes | CAT: `CATEGORY`; VOC: `CATEGORY`; Standups: `CONTENT_ASSESSMENT`; NHO: concatenated context; W3: concatenated context | Signal category or contextual metadata | Safety |
| 8 | `ACTION_COMPLETED` | VARCHAR | Yes | CAT: `ACTION_COMPLETED`; VOC: derived from RESOLUTION presence; Others: NULL | Whether action was taken | Yes |
| 9 | `DATE_ARCHIVED` | DATE | Yes | CAT: `DATE_ARCHIVED`; Others: NULL | Archive date if applicable | 2025-07-01 |
| 10 | `LOAD_DTTM` | TIMESTAMP | No | CAT: `LOAD_DTTM`; Others: `CURRENT_TIMESTAMP()` | Data load timestamp | 2025-06-15 22:00:00 |
| 11 | `SITE_CODE` | VARCHAR(4) | No | CAT: `LEFT(SHEET_NAME, 4)`; VOC: `LEFT(LOCATION, 4)`; Standups: `LEFT(FULFILLMENT_CENTER, 4)`; Surveys: `LEFT(LOCATION, 4)` | 4-character site identifier | PHX1 |
| 12 | `BUSINESS_UNIT` | VARCHAR | No | Derived from `SITE_CODE` via CASE expression | Business unit classification | FC |
| 13 | `LEGACY_REGEX_ESCALATION` | VARCHAR | Yes | Derived from `PRIMARY_TEXT` via REGEXP_LIKE | ER escalation level or NULL | Level 1 Priority |

---

## 3. Voice Mechanism Reference

### 3.1 Normalized Mechanism Labels

| Label | Source(s) | Original Values Mapped |
| --- | --- | --- |
| **Site Leadership Walks** | CAT Tracker | `GM/HRM Floor Walk`, `GM/HRM Walks`, `Building Walk` |
| **Gemba Walks** | CAT Tracker | `Gembas`, `Gemba` |
| **Standups** | CAT Tracker, Standup table | `STANDUP MEETINGS`, `FULFILLMENT STANDUPS` (CAT); fixed label (Standup table) |
| **VOC Board** | VOC Board table | Fixed label |
| **New Hire Survey** | New Hire Survey table | Fixed label |
| **Week 3 Survey** | Week 3 Survey table | Fixed label |
| **ECHO** | CAT Tracker | Passed through as-is |
| **Roundtable** | CAT Tracker | Passed through as-is |
| **1:1** | CAT Tracker | Passed through as-is |
| **TM Experience Walk** | CAT Tracker | Passed through as-is |
| **Recognition** | CAT Tracker | Passed through as-is |
| **CAT Tracker** | CAT Tracker | Default when `VOICE_MECHANISM` is NULL |
| (Other) | CAT Tracker | Any unmatched value passed through as-is |

### 3.2 Excluded Mechanisms (Not in Output)

| Mechanism | Reason |
| --- | --- |
| Monthly Engagement Calendar | Administrative artifact |
| Chewtopian of the Month (Non-Exempt) | Recognition program, not TM feedback |
| Fishbowl Display | Administrative artifact |
| All Manager Meeting Slides | Meeting material |
| Leader of the Pack (Exempt) | Recognition program, not TM feedback |
| All Paws | Administrative artifact |

---

## 4. Business Unit Classification

| Site Code | Business Unit | Location |
| --- | --- | --- |
| AVP1 | FC | Wilkes-Barre, PA (FC1) |
| AVP2 | FC | Wilkes-Barre, PA (FC2) |
| BNA1 | FC | Nashville, TN |
| CFC1 | FC | Clayton, IN |
| CLT1 | FC | Charlotte, NC |
| DAY1 | FC | Dayton, OH |
| DFW1 | FC | Dallas–Fort Worth, TX |
| HOU1 | FC | Houston, TX |
| MCI1 | FC | Kansas City, MO |
| MCO1 | FC | Orlando, FL |
| MDT1 | FC | Harrisburg, PA |
| PHX1 | FC | Phoenix, AZ |
| RNO1 | FC | Reno, NV |
| MCO4 | Rx | Orlando, FL (Pharmacy) |
| PHX2 | Rx | Phoenix, AZ (Pharmacy) |
| AVP4 | Rx | Wilkes-Barre, PA (Pharmacy) |
| DFW8 | Rx | Dallas–Fort Worth, TX (Pharmacy) |
| SDF2 | Rx | Louisville, KY (Pharmacy) |
| SDF4 | Rx | Louisville, KY (Pharmacy) |
| SDF6 | Rx | Louisville, KY (Pharmacy) |
| (other) | Unknown | Unclassified site code |

### Excluded Sites

| Site Code | Reason |
| --- | --- |
| BOS4 | Not an active FC/Rx site in scope |
| SDF1 | Not an active FC/Rx site in scope |

---

## 5. Legacy Regex Escalation Classification

| Level | Condition | Key Pattern Terms | Use Case |
| --- | --- | --- | --- |
| **Level 1 Priority** | `REGEXP_LIKE(PRIMARY_TEXT, ...)` | discrimination, harassment, retaliation, hostile, threat, racist, sexual, union, organize, strike, protest, violence, attorney, counsel, illegal, suicide, touch, EEOC, DOL, OSHA, ADA, FLSA, FMLA, law, CEO, Sumit, CTO, CHRO, CMO, wrongful termination | Immediate ER/Legal review |
| **Level 2 Priority** | `REGEXP_LIKE(PRIMARY_TEXT, ...)` | inconsistent, unfair, favoritism, unjust, bully, abuse, unsafe, risk, danger, inappropriate, intimidate, aggressive, assault, drunk, drug, alcohol, marijuana, pot, falsify, hot, temperature, heat, freeze, burn, wage, safety, under the influence | Elevated ER review |
| **Level 3 Priority** | `REGEXP_LIKE(PRIMARY_TEXT, ...)` | dispute, conflict, berate, disrespect, demean, hate, violation, steal, theft, toxic, unresponsive, tease | Standard ER review |
| **NULL** | No match | — | No escalation flag |

---

## 6. Signal Categories (CATEGORY Field)

The `CATEGORY` field varies by source:

| Source | CATEGORY Content | Examples |
| --- | --- | --- |
| **CAT Tracker** | Pre-assigned category from site leaders | Safety, Equipment, Facility, Policy, Leadership, Positive, Rotation |
| **VOC Board** | Pre-assigned category | Safety, Equipment, Facility, Policy |
| **Standups** | Manager's presentation topic (`CONTENT_ASSESSMENT`) | Various topics presented during standup |
| **New Hire Survey** | Concatenated context string | `Orientation Happiness: Very Happy \| Top Factor: Benefits` |
| **Week 3 Survey** | Concatenated context string | `Happiness: Happy \| Physicality: Just Right \| Preparedness: Very Prepared` |

### Network Benchmark Percentages (2025 FC Network)

| Category | Network Average | Description |
| --- | --- | --- |
| Safety | 7.2% | PPE, pallet hazards, PIT/forklift, heat/HVAC, falls, spills |
| Equipment | 10.8% | Carts, ladders/OPs, scanners, batteries, printers, pallet jacks, tapers |
| Facility | 9.0% | Restrooms, breakrooms, water leaks, parking, trash, lighting, microwaves, odor |
| Policy | 11.6% | VET/overtime, scheduling, VTO, compensation, attendance, fairness, breaks |
| Rotation | 2.3% | Cross-training, path stagnation, dock rotation |
| Positive | 10.9% | Leadership, ECHO, recognition, TM Experience Walk |

---

## 7. Filler Value Exclusion Lists

### 7.1 Standup Filler Values

```text
n/a, none, nothing to add, no feedback, yes, yes!
```

### 7.2 New Hire Survey Filler Values

```text
n/a, na, none, nothing, no, yes, all good, it was great, good, it was good,
everything was good, nothing at this time, nothing it was great, none., .,
nothing., n/a., idk, na., nothing to add, all fine
```

### 7.3 Week 3 Survey Filler Values

```text
n/a, na, none, nothing, no, yes, all good, it was great, good, it was good,
everything was good, nothing at this time, nothing it was great, none., .,
nothing., n/a., idk, na., nothing to add, all fine, not really, nope,
none at this time, none at all, not at the moment
```

---

## 8. Deduplication Logic

| Scenario | Strategy |
| --- | --- |
| **VOC Board → CAT Tracker overlap** | `NOT EXISTS` subquery matches on `SITE_CODE = LOCATION`, `ROW_DATE = DATE_POSTED`, and `LOWER(TRIM(PRIMARY_TEXT)) = LOWER(TRIM(FEEDBACK))`. Prevents double-counting when site leaders copy VOC Board comments into the CAT Tracker. |
| **Survey filler responses** | Explicit exclusion lists (see Section 7) filter non-substantive responses before they enter the unified dataset. |
| **Administrative mechanisms** | Excluded via `VOICE_MECHANISM NOT IN (...)` in the final WHERE clause. |

---

## 9. Sort Order

Production output is sorted by:

1. `SITE_CODE` ASC — grouped by site
2. `ROW_DATE` DESC — most recent signals first within each site
3. `PRIMARY_TEXT` ASC — alphabetical within date
4. `CREATED` ASC — chronological for same-text entries

---

## 10. Data Quality Notes

| Issue | Impact | Mitigation |
| --- | --- | --- |
| Inconsistent mechanism naming in CAT Tracker | Multiple labels for same mechanism type | CASE-based normalization in SQL (see Section 3.1) |
| VOC Board duplicates in CAT Tracker | Double-counting of signals | `NOT EXISTS` dedup (see Section 8) |
| Filler responses in surveys | Noise in signal counts | Explicit exclusion lists (see Section 7) |
| NULL `VOICE_MECHANISM` in CAT Tracker | Unknown mechanism type | Defaulted to `'CAT Tracker'` via `COALESCE` |
| Incidental PII in `PRIMARY_TEXT` | Sensitive content in free text | Report output is aggregated; raw data access-restricted |
| `CATEGORY` semantics differ by source | Not directly comparable across sources | CAT Tracker and VOC Board use standard categories; survey categories are contextual strings |
| New sites not in CASE expression | Classified as `'Unknown'` | Review and update CASE expression when new sites are added |
