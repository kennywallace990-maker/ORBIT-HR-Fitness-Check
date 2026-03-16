# Phase II ServiceNow Data Processing Runbook

**Date:** 2026-03-05  
**Context:** This runbook details how to ingest, clean, and classify the weekly ServiceNow (SNOW) CSV exports for the Workload Lens Phase II integration. Because this relies on raw email text (`Description1`), the classification engine is keyword-based and **must be actively maintained as TM language and business processes evolve.**

---

## 1. Input Data Profile

The expected input is a CSV export from ServiceNow filtered to `Hr Service = "FC General Inquiry"`.

**Required Columns:**

1. `Hr Service`: Used to verify data scope.
2. `Number`: Unique ticket identifier (e.g., HRCA0123456).
3. `Description1`: The raw text of the ticket/email (crucial for classification).
4. `Opened At`: Start timestamp (MM/DD/YYYY format).
5. `U Resolved`: End timestamp (MM/DD/YYYY format).
6. `Assignment Group`: The queue the ticket was routed to (used for site extraction).

---

## 2. Processing Pipeline

The Python script (`deep_ticket_analysis_v2.py`) performs the following sequential steps to unpack the data:

### Step 1: Date Alignment (OBR Window)

- The report operates on strict Sunday–Saturday windows (OBR standard).
- **Rule:** Filter `Opened At` to fall exactly within the target week.
- *Note: SNOW timestamps are often localized; ensure the export timezone matches the reporting standard (typically EST/EDT).*

### Step 2: Site Extraction

- SNOW does not provide a clean "Site" column; it must be extracted from `Assignment Group`.
- **Rule:** Split the `Assignment Group` string by spaces and take the first token (e.g., "CLT1 HR" → "CLT1").
- **Exceptions to maintain:**
  - Compound sites: "SDF 1/4/6 HR" → Mapped to a single `SDF-Campus` or grouped appropriately.
  - Centralized teams: "HR Team Member Service Center", "LOA/ADA Team" → Flagged as `CENTRALIZED`.

### Step 3: Resolution Tracking

- **Rule:** If `U Resolved` is populated, the ticket is `Resolved`.
- **Calculation:** Resolution Time = `U Resolved` date minus `Opened At` date.
- *Limitation:* If the CSV only contains dates (no times), resolution time is approximate to ±24 hours.

---

## 3. The Classification Engine (Living Artifact)

Because SNOW routes all these tickets under a single bucket ("FC General Inquiry"), we must derive the true intent using keyword matching on the `Description1` field. 

**Logic:** First-Match-Wins. The script evaluates the text against categories in a strict order. The first category that hits a keyword match "claims" the ticket. 

> **MAINTENANCE WARNING:** Keywords *will* change. Seasonal events (like W-2s or I-9 renewals), new system rollouts, or changing TM slang require regular updates to the keyword lists.

### Current Category Hierarchy (Order Matters)

1. **I-9 / Onboarding / Compliance Docs** (High priority — catches process artifacts)
   - *Keywords:* `" i9", " i-9", "form i-9", "e-verify", "work authorization", "pharmacy tech", "license"`
2. **Pay Discrepancy / Missing Pay**
   - *Keywords:* `"missing pay", "not paid", "underpaid", "short on pay", "pay discrepancy", "pay is wrong", "check is short"`
3. **PTO / Time-Off Balance**
   - *Keywords:* `"pto", "paid time off", "vacation", "unpaid time off", " uto ", "negative uto"`
4. **LOA / FMLA / Accommodation**
   - *Keywords:* `"loa", "fmla", "leave of absence", "accommodation", "short term disability", "std", "return to work"`
5. **Attendance / Call-Off / NCNS**
   - *Keywords:* `"call off", "calling off", "late", "tardy", "absent", "sick", "ncns", "no call", "attendance points"`
6. **Timecard / Punch / Schedule**
   - *Keywords:* `"punch", "missed punch", "timecard", "timesheet", "clock in", "clock out", "schedule", "shift"`
7. **Suspension / Termination**
   - *Keywords:* `"suspend", "suspension", "terminated", "fired"`
8. **Transfer / Shift Change**
   - *Keywords:* `"transfer", "shift change", "change shift"`
9. **Benefits / W-2**
   - *Keywords:* `"benefits", "insurance", "w2", "w-2", "tax"`
10. **VTO / VET**
    - *Keywords:* `"vto", "vet", "voluntary time out", "extra time"`
11. **Badge / Access / IT** (Catches Swag requests)
    - *Keywords:* `"badge", "access", "login", "password", "okta", "swag", "jacket"`
12. **Personal Info Change**
    - *Keywords:* `"address change", "direct deposit", "name change"`
13. **Spam / System Noise**
    - *Keywords:* `"efax", "undeliverable", "spotify", "unsubscribe", "amazon.com"`
14. **Other / Unclassified** (Catch-all)

### How to Tune Keywords

1. **False Positives:** If a category is catching the wrong tickets (e.g., "pay" catching "I will pay for a jacket"), add boundary spaces to the keyword (e.g., `" pay "`) or move the category lower in the hierarchy.
2. **False Negatives:** Review the `Other / Unclassified` bucket weekly. If a new trend appears (e.g., 20 tickets mentioning "weather" or "snow storm"), create a new category or add those keywords to an existing one.

---

## 4. Execution

To run the analysis on a new weekly CSV:

1. Place the new export in the `Phase II` folder.
2. Update the filename and the `TARGET_START` / `TARGET_END` variables in `deep_ticket_analysis_v2.py`.
3. Run the script: `python deep_ticket_analysis_v2.py`
4. Review the generated `ticket_analysis_v2.txt` output.
5. Identify the "Unclassified" tickets and update the `CATEGORIES` list in the script as necessary.
