"""
Deep Ticket Analysis — FC General Inquiry (Snow Ticket Data)
Cross-referenced with Phase I UKG Workload Lens Week 9
Purpose: Answer director questions from HR OBR Supplemental 2026-03-02
"""

import csv
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter

CSV_PATH = r"C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\ORBIT Products\04 - Workload Lens\Phase II\Snow Ticket Data Week 9.csv"
OUTPUT_PATH = r"C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\ORBIT Products\04 - Workload Lens\Phase II\ticket_analysis_output.txt"

# Week 9 2026: Feb 23 - Mar 1
WEEK9_START = datetime(2026, 2, 23)
WEEK9_END = datetime(2026, 3, 1, 23, 59, 59)

# Week 9 2025 (YoY comparison): Feb 23 - Mar 1
WEEK9_2025_START = datetime(2025, 2, 23)
WEEK9_2025_END = datetime(2025, 3, 1, 23, 59, 59)

# ── Ticket Classification Keywords ──
# Each category: (label, keywords_in_description)
# Order matters — first match wins
CATEGORIES = [
    ("Pay Discrepancy / Missing Pay", [
        "missing pay", "not paid", "underpaid", "short on pay", "pay discrepancy",
        "paycheck", "pay stub", "payslip", "didn't get paid", "not showing on my",
        "hours missing", "missing hours", "retro pay", "retro-pay", "retroactive",
        "direct deposit", "dd not", "check not", "wrong pay", "overpaid", "shortage",
        "pay is wrong", "pay is incorrect", "missing from pay", "not on my check",
        "not on paycheck", "money missing", "paid incorrectly", "reimbursement",
        "not received pay", "hours not showing", "missing 5.5", "missing time",
    ]),
    ("PTO / Time-Off Balance", [
        "pto", "paid time off", "vacation", "time off balance", "pto balance",
        "personal time", "holiday pay", "floating holiday", "time off request",
        "pto accrual", "pto payout", "unused pto", "pto not showing",
        "vacation balance", "time-off", "time off",
    ]),
    ("Leave of Absence / FMLA / LOA", [
        "leave of absence", "loa", "fmla", "medical leave", "maternity",
        "paternity", "parental leave", "return to work", "return from leave",
        "accommodation", "ada", "disability", "workers comp", "work comp",
        "worker's comp", "sedgwick", "intermittent", "continuous leave",
        "leave extension", "leave status", "on leave", "personal leave",
        "bereavement", "jury duty", "military leave",
    ]),
    ("Attendance / Call-Off / NCNS", [
        "call off", "call-off", "called off", "calling off", "ncns",
        "no call no show", "attendance", "absent", "tardy", "late arrival",
        "early departure", "left early", "points", "occurrence", "attendance points",
        "termination due to attendance", "final warning", "written warning",
        "coaching", "progressive discipline", "call out", "called out",
        "uto", "unpaid time", "excused absence", "unexcused",
    ]),
    ("Timecard / Punch / Schedule", [
        "timecard", "time card", "punch", "missed punch", "clock in", "clock out",
        "clocked", "swipe", "badge", "time sheet", "timesheet", "schedule",
        "shift", "overtime", "ot ", "worked but not", "hours worked",
        "didn't clock", "forgot to punch", "forgot to clock", "meal break",
        "lunch break", "break violation", "meal penalty", "kronos", "ukg",
        "time adjustment", "timecard adjustment",
    ]),
    ("Suspension / Termination / Discipline", [
        "suspend", "terminated", "termination", "fired", "let go",
        "reinstat", "separation", "final paycheck", "exit", "offboard",
        "discipline", "investigation", "complaint", "grievance", "harassment",
        "hostile", "retaliation",
    ]),
    ("Transfer / Job Change / Position", [
        "transfer", "department change", "position change", "promotion",
        "demotion", "job change", "relocation", "move to", "shift change",
        "schedule change", "different shift", "new role", "new position",
        "internal move",
    ]),
    ("Benefits / Enrollment", [
        "benefits", "enrollment", "health insurance", "dental", "vision",
        "401k", "401(k)", "hsa", "fsa", "life insurance", "open enrollment",
        "cobra", "dependent", "beneficiary", "wellness",
    ]),
    ("VTO / VET / Voluntary Time", [
        "vto", "vet ", "voluntary time off", "voluntary extra time",
        "voluntary overtime", "soliciting vet", "vet for the fc",
    ]),
    ("Badge / Access / IT", [
        "badge", "access", "login", "password", "locked out", "workday",
        "system access", "it issue", "computer", "laptop", "phone",
        "equipment",
    ]),
    ("Personal Info / Verification", [
        "address change", "name change", "personal info", "verification",
        "verify employment", "employment verification", "voe", "w-2", "w2",
        "tax form", "social security", "pii", "update my info",
        "emergency contact", "phone number change", "email change",
    ]),
    ("Noise / Spam / Auto-Generated Junk", [
        "spotify", "unsubscribe", "no-reply@", "noreply@", "marketing",
        "advertisement", "promo", "get 1 month for", "subscription",
        "automated message", "this message originated outside",
    ]),
]

def classify_ticket(description):
    """Classify a ticket by first matching category."""
    desc_lower = description.lower() if description else ""
    for label, keywords in CATEGORIES:
        for kw in keywords:
            if kw in desc_lower:
                return label
    return "Other / Unclassifiable"

def extract_site(assignment_group):
    """Extract site code from assignment group."""
    if not assignment_group:
        return "UNKNOWN"
    m = re.match(r'^(\w+\d+)\s+HR', assignment_group)
    if m:
        return m.group(1).upper()
    if "SDF 1/4/6" in assignment_group:
        return "SDF-CAMPUS"
    if "Team Member Service Center" in assignment_group:
        return "TMSC"
    if "LOA/ADA" in assignment_group:
        return "LOA-ADA"
    if "Data Management" in assignment_group:
        return "TMDM"
    if "Payroll" in assignment_group:
        return "PAYROLL"
    return assignment_group.strip()

def parse_date(date_str):
    """Parse date string, return datetime or None."""
    if not date_str or not date_str.strip():
        return None
    try:
        return datetime.strptime(date_str.strip(), "%m/%d/%Y")
    except ValueError:
        return None

def resolution_hours(opened, resolved):
    """Compute resolution hours."""
    if opened and resolved:
        delta = (resolved - opened).total_seconds() / 3600
        return max(delta, 0)
    return None

# ── Load Data ──
print("Loading CSV...")
rows = []
with open(CSV_PATH, "r", encoding="utf-8", errors="replace") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

print(f"Total rows loaded: {len(rows)}")

# ── Parse all rows ──
parsed = []
for row in rows:
    opened = parse_date(row.get("Opened At", ""))
    resolved = parse_date(row.get("U Resolved", ""))
    desc = row.get("Description1", "") or ""
    ag = row.get("Assignment Group", "") or ""
    number = row.get("Number", "") or ""
    
    parsed.append({
        "number": number,
        "description": desc,
        "opened": opened,
        "resolved": resolved,
        "assignment_group": ag,
        "site": extract_site(ag),
        "category": classify_ticket(desc),
        "res_hours": resolution_hours(opened, resolved),
    })

# ── Filter to Week 9 2026 ──
week9 = [r for r in parsed if r["opened"] and WEEK9_START <= r["opened"] <= WEEK9_END]
week9_2025 = [r for r in parsed if r["opened"] and WEEK9_2025_START <= r["opened"] <= WEEK9_2025_END]

# ── Also compute full-year 2026 and 2025 by quarter ──
y2026 = [r for r in parsed if r["opened"] and r["opened"].year == 2026]
y2025 = [r for r in parsed if r["opened"] and r["opened"].year == 2025]

# ── Analysis Functions ──
def category_summary(tickets, label=""):
    """Return category breakdown."""
    cats = Counter(t["category"] for t in tickets)
    total = len(tickets)
    result = []
    for cat, count in cats.most_common():
        pct = count / total * 100 if total > 0 else 0
        result.append((cat, count, pct))
    return result

def site_summary(tickets, label=""):
    """Return site breakdown."""
    sites = Counter(t["site"] for t in tickets)
    total = len(tickets)
    result = []
    for site, count in sites.most_common():
        pct = count / total * 100 if total > 0 else 0
        result.append((site, count, pct))
    return result

def resolution_stats(tickets):
    """Compute resolution time stats."""
    hours = [t["res_hours"] for t in tickets if t["res_hours"] is not None]
    if not hours:
        return {"count": 0}
    hours_sorted = sorted(hours)
    n = len(hours_sorted)
    return {
        "count": n,
        "avg": sum(hours_sorted) / n,
        "median": hours_sorted[n // 2],
        "p90": hours_sorted[int(n * 0.9)],
        "max": hours_sorted[-1],
        "same_day": sum(1 for h in hours_sorted if h <= 24),
        "same_day_pct": sum(1 for h in hours_sorted if h <= 24) / n * 100,
        "gt_7days": sum(1 for h in hours_sorted if h > 168),
        "gt_7days_pct": sum(1 for h in hours_sorted if h > 168) / n * 100,
    }

def weekly_trend(parsed_all, year=2026, weeks_back=8):
    """Compute weekly ticket counts for last N weeks."""
    # Group by ISO week
    weekly = defaultdict(list)
    for r in parsed_all:
        if r["opened"] and r["opened"].year == year:
            iso = r["opened"].isocalendar()
            weekly[iso[1]].append(r)
    return weekly

# ── YoY Comparison ──
def yoy_category_comparison(wk_2026, wk_2025):
    """Compare categories year-over-year."""
    cats_26 = Counter(t["category"] for t in wk_2026)
    cats_25 = Counter(t["category"] for t in wk_2025)
    all_cats = set(list(cats_26.keys()) + list(cats_25.keys()))
    result = []
    for cat in all_cats:
        c26 = cats_26.get(cat, 0)
        c25 = cats_25.get(cat, 0)
        delta = c26 - c25
        pct_change = ((c26 - c25) / c25 * 100) if c25 > 0 else float("inf")
        result.append((cat, c25, c26, delta, pct_change))
    result.sort(key=lambda x: x[3])  # sort by delta
    return result

# ── Cross-reference with Phase I UKG data ──
# Week 9 UKG site-level data from the Phase I report
UKG_SITES = {
    "CLT1": {"bu": "FC", "actions": 5056, "rework": 2954, "tms": 747, "dpmo": 197724, "defect_pct": 58.4},
    "MCI1": {"bu": "FC", "actions": 5488, "rework": 2649, "tms": 756, "dpmo": 175198, "defect_pct": 48.3},
    "MDT1": {"bu": "FC", "actions": 3539, "rework": 1676, "tms": 484, "dpmo": 173141, "defect_pct": 47.4},
    "BNA1": {"bu": "FC", "actions": 4936, "rework": 2195, "tms": 681, "dpmo": 161160, "defect_pct": 44.5},
    "AVP6": {"bu": "Rx", "actions": 464, "rework": 227, "tms": 62, "dpmo": 183065, "defect_pct": 48.9},
    "HOU1": {"bu": "FC", "actions": 388, "rework": 0, "tms": 0, "dpmo": 0, "defect_pct": 37.9},  # partial from report
}

# Full FC BU UKG totals from Phase I
UKG_FC_TOTAL = {"actions": 41790, "rework": 16553, "defect_pct": 39.6, "friction_hrs": 0}

def cross_reference(week9_tickets):
    """Cross-reference ticket sites with UKG site data."""
    ticket_by_site = Counter(t["site"] for t in week9_tickets)
    result = []
    for site, tkt_count in ticket_by_site.most_common():
        ukg = UKG_SITES.get(site, None)
        if ukg:
            conversion = tkt_count / ukg["rework"] * 100 if ukg["rework"] > 0 else 0
            result.append({
                "site": site,
                "tickets": tkt_count,
                "ukg_actions": ukg["actions"],
                "ukg_rework": ukg["rework"],
                "dpmo": ukg["dpmo"],
                "defect_pct": ukg["defect_pct"],
                "tms": ukg["tms"],
                "ticket_per_100tm": tkt_count / ukg["tms"] * 100 if ukg["tms"] > 0 else 0,
                "conversion_rate": conversion,
            })
        else:
            result.append({
                "site": site,
                "tickets": tkt_count,
                "ukg_actions": "N/A",
                "ukg_rework": "N/A",
                "dpmo": "N/A",
                "defect_pct": "N/A",
                "tms": "N/A",
                "ticket_per_100tm": "N/A",
                "conversion_rate": "N/A",
            })
    return result

# ── Specific deep-dives for director questions ──
def find_tickets_by_keywords(tickets, keywords):
    """Find tickets matching any keyword."""
    results = []
    for t in tickets:
        desc_lower = t["description"].lower()
        for kw in keywords:
            if kw in desc_lower:
                results.append(t)
                break
    return results

# ── Generate Output ──
output = []
def p(line=""):
    output.append(line)

p("=" * 80)
p("DEEP TICKET ANALYSIS — FC General Inquiry")
p("Source: Snow Ticket Data Week 9.csv | Analysis Date: 2026-03-05")
p("Purpose: Answer director questions from HR OBR Supplemental 2026-03-02")
p("=" * 80)

p()
p("=" * 80)
p("SECTION 1: WEEK 9 2026 — FC GENERAL INQUIRY OVERVIEW")
p("=" * 80)
p(f"Total tickets (Week 9, 2/23-3/1/2026): {len(week9)}")
p(f"Total tickets (Week 9, 2/23-3/1/2025): {len(week9_2025)}")
yoy_delta = len(week9) - len(week9_2025)
yoy_pct = (yoy_delta / len(week9_2025) * 100) if len(week9_2025) > 0 else 0
p(f"YoY Change: {yoy_delta:+d} ({yoy_pct:+.1f}%)")

p()
p("--- Resolution Time (Week 9 2026) ---")
rs = resolution_stats(week9)
if rs["count"] > 0:
    p(f"Resolved: {rs['count']} / {len(week9)} ({rs['count']/len(week9)*100:.1f}%)")
    p(f"Avg resolution: {rs['avg']:.1f} hrs")
    p(f"Median resolution: {rs['median']:.1f} hrs")
    p(f"P90 resolution: {rs['p90']:.1f} hrs")
    p(f"Max resolution: {rs['max']:.1f} hrs")
    p(f"Resolved same day (<=24h): {rs['same_day']} ({rs['same_day_pct']:.1f}%)")
    p(f"Open >7 days: {rs['gt_7days']} ({rs['gt_7days_pct']:.1f}%)")

p()
p("=" * 80)
p("SECTION 2: TICKET CATEGORY BREAKDOWN (Week 9 2026)")
p("=" * 80)
cats = category_summary(week9)
p(f"{'Category':<45} {'Count':>6} {'%':>7}")
p("-" * 60)
for cat, count, pct in cats:
    p(f"{cat:<45} {count:>6} {pct:>6.1f}%")

p()
p("--- YoY Category Comparison (Week 9: 2025 vs 2026) ---")
yoy = yoy_category_comparison(week9, week9_2025)
p(f"{'Category':<45} {'2025':>6} {'2026':>6} {'Delta':>6} {'%Chg':>8}")
p("-" * 75)
for cat, c25, c26, delta, pct_chg in yoy:
    pct_str = f"{pct_chg:+.0f}%" if pct_chg != float("inf") else "NEW"
    p(f"{cat:<45} {c25:>6} {c26:>6} {delta:>+6} {pct_str:>8}")

p()
p("=" * 80)
p("SECTION 3: SITE BREAKDOWN (Week 9 2026)")
p("=" * 80)
sites = site_summary(week9)
p(f"{'Site':<15} {'Tickets':>8} {'%':>7}")
p("-" * 32)
for site, count, pct in sites:
    p(f"{site:<15} {count:>8} {pct:>6.1f}%")

p()
p("=" * 80)
p("SECTION 4: CROSS-REFERENCE — TICKETS vs UKG (Week 9 2026)")
p("=" * 80)
p("(Sites with both ticket data AND UKG Phase I data)")
xref = cross_reference(week9)
p(f"{'Site':<10} {'Tix':>5} {'UKG Acts':>9} {'UKG Rwrk':>9} {'Defect%':>8} {'DPMO':>8} {'Tix/100TM':>10} {'Conversion':>11}")
p("-" * 80)
for x in xref:
    if x["ukg_actions"] != "N/A":
        p(f"{x['site']:<10} {x['tickets']:>5} {x['ukg_actions']:>9} {x['ukg_rework']:>9} {x['defect_pct']:>7.1f}% {x['dpmo']:>8,} {x['ticket_per_100tm']:>9.1f}% {x['conversion_rate']:>10.2f}%")

p()
p("=" * 80)
p("SECTION 5: CATEGORY DEEP-DIVES (Week 9 2026 — Sample Tickets)")
p("=" * 80)

for cat, count, pct in cats[:8]:  # Top 8 categories
    cat_tickets = [t for t in week9 if t["category"] == cat]
    p()
    p(f"--- {cat} ({count} tickets, {pct:.1f}%) ---")
    # Site breakdown within category
    cat_sites = Counter(t["site"] for t in cat_tickets)
    p(f"  Sites: {', '.join(f'{s}({c})' for s, c in cat_sites.most_common(10))}")
    # Resolution stats
    cat_rs = resolution_stats(cat_tickets)
    if cat_rs["count"] > 0:
        p(f"  Avg resolution: {cat_rs['avg']:.1f}h | Median: {cat_rs['median']:.1f}h | Same-day: {cat_rs['same_day_pct']:.0f}%")
    # Sample descriptions (truncated)
    p(f"  Sample tickets:")
    for t in cat_tickets[:5]:
        desc = t["description"][:200].replace("\n", " ").strip()
        p(f"    [{t['number']}] {t['site']} | {desc}")

p()
p("=" * 80)
p("SECTION 6: DIRECTOR QUESTION — FC GENERAL INQUIRY VOLUME REDUCTION OPPORTUNITY")
p("=" * 80)
p()
p("OBR Supplemental states: 'FC General Inquiry (412 tickets) — with a roll out of")
p("TM app, I would expect that these decrease.'")
p()
p(f"Our Week 9 2026 data shows {len(week9)} FC General Inquiry tickets.")
p()
p("Top categories that could be reduced with existing processes/technology:")
p()

# Identify automation/self-service candidates
auto_candidates = [
    ("Pay Discrepancy / Missing Pay", "UKG self-service: TMs can view pay stubs, timecard history. TM app rollout reduces need to call TMSC."),
    ("PTO / Time-Off Balance", "UKG self-service: TMs can check PTO balance in app. Automated balance notifications."),
    ("Timecard / Punch / Schedule", "UKG self-service: TMs can submit missed punch requests via app. Supervisor approvals in UKG."),
    ("Attendance / Call-Off / NCNS", "Centralized call-off line or UKG app call-off. Smartsheet automation already removed for FC."),
    ("VTO / VET / Voluntary Time", "Automated VTO/VET solicitation and signup via app or Smartsheet."),
    ("Badge / Access / IT", "Self-service password reset, automated badge provisioning."),
    ("Personal Info / Verification", "Workday self-service for address/name changes, automated VOE via The Work Number."),
]

for cat_name, note in auto_candidates:
    cat_tix = [t for t in week9 if t["category"] == cat_name]
    if cat_tix:
        p(f"  {cat_name}: {len(cat_tix)} tickets/week")
        p(f"    Opportunity: {note}")
        p()

p()
p("=" * 80)
p("SECTION 7: DARK WORK ANALYSIS — UKG REWORK NOT IN TICKETS")
p("=" * 80)
p()
p("Phase I UKG shows 41,790 FC actions / 16,553 rework actions in Week 9.")
p(f"Phase II Snow shows {len(week9)} FC General Inquiry tickets in the same week.")
p(f"Ticket-to-Rework ratio: {len(week9)/16553*100:.2f}% — meaning ~{100-len(week9)/16553*100:.1f}%")
p("of UKG rework is 'dark work' absorbed by HR without a ticket ever being created.")
p()
p("This confirms that tickets capture only a fraction of actual HR workload.")
p("The majority of timekeeping corrections (punch adds, attendance coding, leave")
p("adjustments) happen silently in UKG — no ticket, no tracking, no measurement.")

p()
p("=" * 80)
p("SECTION 8: WEEKLY TREND (FC General Inquiry — 2026)")
p("=" * 80)
wk_trend = weekly_trend(parsed)
for wk_num in sorted(wk_trend.keys()):
    tix = wk_trend[wk_num]
    cats_in_wk = Counter(t["category"] for t in tix)
    top3 = ", ".join(f"{c}({n})" for c, n in cats_in_wk.most_common(3))
    p(f"  2026-W{wk_num:02d}: {len(tix):>4} tickets | Top: {top3}")

p()
p("=" * 80)
p("SECTION 9: NOISE / DATA QUALITY FLAGS")
p("=" * 80)
noise = [t for t in week9 if t["category"] == "Noise / Spam / Auto-Generated Junk"]
p(f"Noise tickets in Week 9: {len(noise)}")
if noise:
    for t in noise:
        desc = t["description"][:150].replace("\n", " ").strip()
        p(f"  [{t['number']}] {t['site']} | {desc}")

other = [t for t in week9 if t["category"] == "Other / Unclassifiable"]
p(f"\nUnclassifiable tickets in Week 9: {len(other)}")
p("Sample unclassifiable (first 15):")
for t in other[:15]:
    desc = t["description"][:200].replace("\n", " ").strip()
    p(f"  [{t['number']}] {t['site']} | {desc}")

# ── Write output ──
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(output))

print(f"\nAnalysis complete. Output written to:\n{OUTPUT_PATH}")
print(f"\nQuick summary:")
print(f"  Week 9 2026 tickets: {len(week9)}")
print(f"  Week 9 2025 tickets: {len(week9_2025)}")
print(f"  Categories found: {len(cats)}")
print(f"  Sites found: {len(sites)}")
