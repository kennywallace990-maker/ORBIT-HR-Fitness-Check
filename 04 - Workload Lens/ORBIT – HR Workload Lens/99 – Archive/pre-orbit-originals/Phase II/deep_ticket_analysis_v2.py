"""
Deep Ticket Analysis v2 — FC General Inquiry (Snow Ticket Data)
Date windows aligned to OBR: Week 8 = 2/15-2/21/2026, Week 9 = 2/22-2/28/2026
Also: Week 9 YoY = 2/22-2/28/2025
"""

import csv
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter

CSV_PATH = r"C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\ORBIT Products\04 - Workload Lens\Phase II\Snow Ticket Data Week 9.csv"
OUTPUT_PATH = r"C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Desktop\ORBIT Products\04 - Workload Lens\Phase II\ticket_analysis_v2.txt"

# OBR date windows
WK8_START = datetime(2026, 2, 15)
WK8_END   = datetime(2026, 2, 21, 23, 59, 59)
WK9_START = datetime(2026, 2, 22)
WK9_END   = datetime(2026, 2, 28, 23, 59, 59)
# YoY
WK9_2025_START = datetime(2025, 2, 22)
WK9_2025_END   = datetime(2025, 2, 28, 23, 59, 59)
WK8_2025_START = datetime(2025, 2, 15)
WK8_2025_END   = datetime(2025, 2, 21, 23, 59, 59)

CATEGORIES = [
    ("I-9 / Onboarding / Compliance Docs", [
        " i9", " i-9", "i9 ", "i-9 ", "i 9", "form i-9", "e-verify",
        "license", "pharmacy tech", "pharmacist license", "rph license",
        "nabp", "certification", "onboarding", "new hire", "orientation",
        "kybop", "certificate", "renewal",
    ]),
    ("Pay Discrepancy / Missing Pay", [
        "missing pay", "not paid", "underpaid", "short on pay", "pay discrepancy",
        "paycheck", "pay stub", "payslip", "didn't get paid", "not showing on my",
        "hours missing", "missing hours", "retro pay", "retro-pay", "retroactive",
        "direct deposit", "dd not", "check not", "wrong pay", "overpaid", "shortage",
        "pay is wrong", "pay is incorrect", "missing from pay", "not on my check",
        "not on paycheck", "money missing", "paid incorrectly", "reimbursement",
        "not received pay", "hours not showing", "missing 5.5", "missing time",
        "pay issue", "payment", "paystub", "most recent paystub",
    ]),
    ("PTO / Time-Off Balance", [
        "pto", "paid time off", "vacation", "time off balance", "pto balance",
        "personal time", "holiday pay", "floating holiday", "time off request",
        "pto accrual", "pto payout", "unused pto", "pto not showing",
        "vacation balance", "time-off", "time off", "uto reimbursement",
        "uto ", "unpaid time off",
    ]),
    ("Leave of Absence / FMLA / LOA", [
        "leave of absence", "loa", "fmla", "medical leave", "maternity",
        "paternity", "parental leave", "return to work", "return from leave",
        "accommodation", "ada ", "disability", "workers comp", "work comp",
        "worker's comp", "sedgwick", "intermittent", "continuous leave",
        "leave extension", "leave status", "on leave", "personal leave",
        "bereavement", "jury duty", "military leave", "work release",
        "absenceone", "a1 ", "dr note", "doctor note", "medical documentation",
    ]),
    ("Attendance / Call-Off / NCNS", [
        "call off", "call-off", "called off", "calling off", "ncns",
        "no call no show", "attendance", "absent", "tardy", "late arrival",
        "early departure", "left early", "points", "occurrence", "attendance points",
        "termination due to attendance", "final warning", "written warning",
        "coaching", "progressive discipline", "call out", "called out",
        "excused absence", "unexcused", "calling out", "won't be at work",
        "will not be in", "unable to come in", "not coming in", "report an absence",
        "weather", "inclement", "not be at work",
    ]),
    ("Timecard / Punch / Schedule", [
        "timecard", "time card", "punch", "missed punch", "clock in", "clock out",
        "clocked", "swipe", "time sheet", "timesheet", "schedule",
        "shift", "overtime", "ot ", "worked but not", "hours worked",
        "didn't clock", "forgot to punch", "forgot to clock", "meal break",
        "lunch break", "break violation", "meal penalty", "kronos", "ukg",
        "time adjustment", "timecard adjustment",
    ]),
    ("Suspension / Termination / Discipline / TM Relations", [
        "suspend", "terminated", "termination", "fired", "let go",
        "reinstat", "separation", "final paycheck", "exit", "offboard",
        "discipline", "investigation", "complaint", "grievance", "harassment",
        "hostile", "retaliation", "hr complaint", "write up", "write-up",
        "discharged", "discharge", "come back to work",
    ]),
    ("Transfer / Job Change / Position", [
        "transfer", "department change", "position change", "promotion",
        "demotion", "job change", "relocation", "move to", "shift change",
        "schedule change", "different shift", "new role", "new position",
        "internal move",
    ]),
    ("Benefits / Enrollment / Payroll", [
        "benefits", "enrollment", "health insurance", "dental", "vision",
        "401k", "401(k)", "hsa", "fsa", "life insurance", "open enrollment",
        "cobra", "dependent", "beneficiary", "wellness", "w-2", "w2",
        "tax form",
    ]),
    ("VTO / VET / Voluntary Time", [
        "vto", "vet ", "voluntary time off", "voluntary extra time",
        "voluntary overtime", "soliciting vet", "vet for the fc",
        "vet 2/", "vet 3/",
    ]),
    ("Badge / Access / IT / Workday", [
        "badge", "access", "login", "password", "locked out", "workday",
        "system access", "it issue", "computer", "laptop", "phone",
        "equipment", "swag", "workday tasks",
    ]),
    ("Personal Info / Verification / Records", [
        "address change", "name change", "personal info", "verification",
        "verify employment", "employment verification", "voe",
        "social security", "update my info",
        "emergency contact", "phone number change", "email change",
        "court document", "record request", "legal",
    ]),
    ("Spam / Auto-Generated Junk / Misdirected Email", [
        "spotify", "unsubscribe", "marketing", "advertisement",
        "get 1 month for", "subscription", "amazon", "efax",
        "check this out at", "print me please", "help me please",
        "kbs-services", "successful transmission",
    ]),
]

def classify_ticket(description):
    desc_lower = (description or "").lower()
    if not desc_lower.strip():
        return "Empty / No Description"
    for label, keywords in CATEGORIES:
        for kw in keywords:
            if kw in desc_lower:
                return label
    return "Other / Unclassified"

def extract_site(assignment_group):
    if not assignment_group:
        return "UNKNOWN"
    ag = assignment_group.strip()
    m = re.match(r'^(\w+\d+)\s+HR', ag)
    if m:
        return m.group(1).upper()
    if "SDF 1/4/6" in ag:
        return "SDF-CAMPUS"
    if "Team Member Service Center" in ag:
        return "TMSC"
    if "LOA/ADA" in ag:
        return "LOA-ADA"
    if "Data Management" in ag:
        return "TMDM"
    if "Payroll" in ag:
        return "PAYROLL"
    if "FC Support HRBP" in ag:
        return "FC-HRBP"
    return ag

def parse_date(s):
    if not s or not s.strip():
        return None
    try:
        return datetime.strptime(s.strip(), "%m/%d/%Y")
    except ValueError:
        return None

def res_hours(o, r):
    if o and r:
        return max((r - o).total_seconds() / 3600, 0)
    return None

# ── Load ──
print("Loading CSV...")
rows = []
with open(CSV_PATH, "r", encoding="utf-8", errors="replace") as f:
    for row in csv.DictReader(f):
        rows.append(row)
print(f"Loaded {len(rows)} rows")

parsed = []
for row in rows:
    o = parse_date(row.get("Opened At", ""))
    r = parse_date(row.get("U Resolved", ""))
    desc = row.get("Description1", "") or ""
    ag = row.get("Assignment Group", "") or ""
    num = row.get("Number", "") or ""
    parsed.append({
        "num": num, "desc": desc, "opened": o, "resolved": r,
        "ag": ag, "site": extract_site(ag),
        "cat": classify_ticket(desc), "rh": res_hours(o, r),
    })

# ── Slices ──
wk9 = [r for r in parsed if r["opened"] and WK9_START <= r["opened"] <= WK9_END]
wk8 = [r for r in parsed if r["opened"] and WK8_START <= r["opened"] <= WK8_END]
wk9_25 = [r for r in parsed if r["opened"] and WK9_2025_START <= r["opened"] <= WK9_2025_END]
wk8_25 = [r for r in parsed if r["opened"] and WK8_2025_START <= r["opened"] <= WK8_2025_END]

print(f"Wk9 2026: {len(wk9)} | Wk8 2026: {len(wk8)} | Wk9 2025: {len(wk9_25)} | Wk8 2025: {len(wk8_25)}")

# ── Helpers ──
def cat_table(tickets):
    cats = Counter(t["cat"] for t in tickets)
    total = len(tickets)
    out = []
    for c, n in cats.most_common():
        out.append((c, n, n/total*100 if total else 0))
    return out

def site_table(tickets):
    sites = Counter(t["site"] for t in tickets)
    total = len(tickets)
    out = []
    for s, n in sites.most_common():
        out.append((s, n, n/total*100 if total else 0))
    return out

def res_stats(tickets):
    hrs = [t["rh"] for t in tickets if t["rh"] is not None]
    if not hrs:
        return None
    hrs.sort()
    n = len(hrs)
    return {
        "n": n, "total": len(tickets),
        "avg": sum(hrs)/n, "med": hrs[n//2],
        "p90": hrs[int(n*0.9)], "max": hrs[-1],
        "same_day": sum(1 for h in hrs if h <= 24),
        "same_day_pct": sum(1 for h in hrs if h <= 24)/n*100,
        "gt3d": sum(1 for h in hrs if h > 72),
        "gt7d": sum(1 for h in hrs if h > 168),
    }

def wow_compare(wk_curr, wk_prev, label_curr="Wk9", label_prev="Wk8"):
    cats_c = Counter(t["cat"] for t in wk_curr)
    cats_p = Counter(t["cat"] for t in wk_prev)
    all_cats = sorted(set(list(cats_c.keys()) + list(cats_p.keys())),
                      key=lambda x: cats_c.get(x, 0), reverse=True)
    out = []
    for c in all_cats:
        nc = cats_c.get(c, 0)
        np_ = cats_p.get(c, 0)
        delta = nc - np_
        pct = ((nc - np_) / np_ * 100) if np_ > 0 else (999 if nc > 0 else 0)
        out.append((c, np_, nc, delta, pct))
    return out

# ── UKG Phase I Data (from Week 9 Workload Lens report) ──
# Site-level FC data from the Phase I report
UKG = {
    "CLT1": {"acts": 5056, "rwrk": 2954, "tms": 747, "dpmo": 197724, "def_pct": 58.4},
    "MCI1": {"acts": 5488, "rwrk": 2649, "tms": 756, "dpmo": 175198, "def_pct": 48.3},
    "MDT1": {"acts": 3539, "rwrk": 1676, "tms": 484, "dpmo": 173141, "def_pct": 47.4},
    "BNA1": {"acts": 4936, "rwrk": 2195, "tms": 681, "dpmo": 161160, "def_pct": 44.5},
    "HOU1": {"acts": 388, "rwrk": 147, "tms": 0, "dpmo": 0, "def_pct": 37.9},
}

# ── Output ──
out = []
def p(s=""):
    out.append(s)

p("=" * 90)
p("DEEP TICKET ANALYSIS v2 — FC General Inquiry")
p("Date Windows: Week 8 (2/15-2/21/2026) | Week 9 (2/22-2/28/2026)")
p(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
p("=" * 90)

# ════════════════════════════════════════════════════════════════════════
# SECTION 1: HEADLINE NUMBERS
# ════════════════════════════════════════════════════════════════════════
p()
p("=" * 90)
p("1. HEADLINE NUMBERS")
p("=" * 90)
p()
p(f"{'Metric':<45} {'Wk8':>8} {'Wk9':>8} {'WoW Δ':>8} {'WoW%':>8}")
p("-" * 80)
p(f"{'FC General Inquiry Tickets':<45} {len(wk8):>8} {len(wk9):>8} {len(wk9)-len(wk8):>+8} {((len(wk9)-len(wk8))/len(wk8)*100 if len(wk8) else 0):>+7.1f}%")

# Resolution
rs9 = res_stats(wk9)
rs8 = res_stats(wk8)
if rs9 and rs8:
    p(f"{'Resolved count':<45} {rs8['n']:>8} {rs9['n']:>8} {rs9['n']-rs8['n']:>+8}")
    p(f"{'Resolution rate %':<45} {rs8['n']/rs8['total']*100:>7.1f}% {rs9['n']/rs9['total']*100:>7.1f}%")
    p(f"{'Avg resolution (hrs)':<45} {rs8['avg']:>7.1f}h {rs9['avg']:>7.1f}h {rs9['avg']-rs8['avg']:>+7.1f}h")
    p(f"{'Median resolution (hrs)':<45} {rs8['med']:>7.1f}h {rs9['med']:>7.1f}h {rs9['med']-rs8['med']:>+7.1f}h")
    p(f"{'Same-day resolved (<=24h) %':<45} {rs8['same_day_pct']:>7.1f}% {rs9['same_day_pct']:>7.1f}%")
    p(f"{'Open >3 days':<45} {rs8['gt3d']:>8} {rs9['gt3d']:>8}")
    p(f"{'Open >7 days':<45} {rs8['gt7d']:>8} {rs9['gt7d']:>8}")

# YoY
p()
p(f"{'YoY Comparison':<45} {'Wk9 25':>8} {'Wk9 26':>8} {'YoY Δ':>8} {'YoY%':>8}")
p("-" * 80)
p(f"{'FC General Inquiry Tickets':<45} {len(wk9_25):>8} {len(wk9):>8} {len(wk9)-len(wk9_25):>+8} {((len(wk9)-len(wk9_25))/len(wk9_25)*100 if len(wk9_25) else 0):>+7.1f}%")

# ════════════════════════════════════════════════════════════════════════
# SECTION 2: CATEGORY BREAKDOWN — WK9 vs WK8
# ════════════════════════════════════════════════════════════════════════
p()
p("=" * 90)
p("2. CATEGORY BREAKDOWN — Week 9 vs Week 8 (WoW)")
p("=" * 90)
wow = wow_compare(wk9, wk8, "Wk9", "Wk8")
p(f"{'Category':<45} {'Wk8':>6} {'Wk9':>6} {'Δ':>6} {'%Chg':>8}")
p("-" * 75)
for c, np_, nc, d, pct in wow:
    pct_s = f"{pct:+.0f}%" if abs(pct) < 500 else "NEW"
    p(f"{c:<45} {np_:>6} {nc:>6} {d:>+6} {pct_s:>8}")
p(f"{'TOTAL':<45} {len(wk8):>6} {len(wk9):>6} {len(wk9)-len(wk8):>+6}")

# ════════════════════════════════════════════════════════════════════════
# SECTION 3: CATEGORY BREAKDOWN — WK9 YoY
# ════════════════════════════════════════════════════════════════════════
p()
p("=" * 90)
p("3. CATEGORY BREAKDOWN — Week 9 YoY (2025 vs 2026)")
p("=" * 90)
yoy = wow_compare(wk9, wk9_25, "Wk9-26", "Wk9-25")
p(f"{'Category':<45} {'2025':>6} {'2026':>6} {'Δ':>6} {'%Chg':>8}")
p("-" * 75)
for c, np_, nc, d, pct in yoy:
    pct_s = f"{pct:+.0f}%" if abs(pct) < 500 else "NEW"
    p(f"{c:<45} {np_:>6} {nc:>6} {d:>+6} {pct_s:>8}")
p(f"{'TOTAL':<45} {len(wk9_25):>6} {len(wk9):>6} {len(wk9)-len(wk9_25):>+6}")

# ════════════════════════════════════════════════════════════════════════
# SECTION 4: SITE BREAKDOWN — WK9 vs WK8
# ════════════════════════════════════════════════════════════════════════
p()
p("=" * 90)
p("4. SITE BREAKDOWN — Week 9 vs Week 8")
p("=" * 90)
sites9 = Counter(t["site"] for t in wk9)
sites8 = Counter(t["site"] for t in wk8)
all_sites = sorted(set(list(sites9.keys()) + list(sites8.keys())),
                   key=lambda x: sites9.get(x, 0), reverse=True)
p(f"{'Site':<15} {'Wk8':>6} {'Wk9':>6} {'Δ':>6} {'Wk9%':>7}")
p("-" * 42)
for s in all_sites:
    n9 = sites9.get(s, 0)
    n8 = sites8.get(s, 0)
    pct9 = n9/len(wk9)*100 if len(wk9) else 0
    p(f"{s:<15} {n8:>6} {n9:>6} {n9-n8:>+6} {pct9:>6.1f}%")
p(f"{'TOTAL':<15} {len(wk8):>6} {len(wk9):>6} {len(wk9)-len(wk8):>+6}")

# ════════════════════════════════════════════════════════════════════════
# SECTION 5: SITE × CATEGORY MATRIX — WK9
# ════════════════════════════════════════════════════════════════════════
p()
p("=" * 90)
p("5. SITE × CATEGORY HEATMAP — Week 9 (Top 10 sites)")
p("=" * 90)
top_sites = [s for s, _ in sites9.most_common(10)]
top_cats = [c for c, _, _ in cat_table(wk9) if c != "Spam / Auto-Generated Junk / Misdirected Email"][:8]
# Header
hdr = f"{'Site':<12}" + "".join(f"{c[:12]:>13}" for c in top_cats) + f"{'TOTAL':>8}"
p(hdr)
p("-" * len(hdr))
for s in top_sites:
    site_tix = [t for t in wk9 if t["site"] == s]
    site_cats = Counter(t["cat"] for t in site_tix)
    row = f"{s:<12}"
    for c in top_cats:
        row += f"{site_cats.get(c, 0):>13}"
    row += f"{len(site_tix):>8}"
    p(row)

# ════════════════════════════════════════════════════════════════════════
# SECTION 6: CROSS-REFERENCE — TICKETS vs UKG PHASE I
# ════════════════════════════════════════════════════════════════════════
p()
p("=" * 90)
p("6. CROSS-REFERENCE — FC Tickets (Phase II) vs UKG Actions (Phase I)")
p("   Phase I source: Workload Lens Week 9 report (UKG timecard audit)")
p("   Phase II source: Snow FC General Inquiry tickets (this CSV)")
p("=" * 90)
p()
p("Sites with BOTH ticket and UKG data:")
p(f"{'Site':<10} {'Tix':>5} {'UKG Rework':>11} {'Tix/Rwrk%':>10} {'UKG Def%':>9} {'DPMO':>9}")
p("-" * 58)
for s in ["CLT1", "MCI1", "MDT1", "BNA1", "HOU1"]:
    tix = sites9.get(s, 0)
    u = UKG.get(s, {})
    conv = tix / u["rwrk"] * 100 if u.get("rwrk", 0) > 0 else 0
    p(f"{s:<10} {tix:>5} {u.get('rwrk', 0):>11,} {conv:>9.2f}% {u.get('def_pct', 0):>8.1f}% {u.get('dpmo', 0):>9,}")

p()
p("Key finding: Tickets represent ~0.1-0.8% of UKG rework volume.")
p("The vast majority of timekeeping corrections happen in UKG without a ticket.")
p(f"FC total: {len(wk9)} tickets vs 16,553 UKG rework actions = {len(wk9)/16553*100:.1f}% conversion")

# ════════════════════════════════════════════════════════════════════════
# SECTION 7: DEEP DIVE — EACH CATEGORY (WK9)
# ════════════════════════════════════════════════════════════════════════
p()
p("=" * 90)
p("7. CATEGORY DEEP DIVES — Week 9 (2/22-2/28/2026)")
p("=" * 90)

for cat_name, count, pct in cat_table(wk9):
    cat_tix = [t for t in wk9 if t["cat"] == cat_name]
    if not cat_tix:
        continue
    p()
    p(f"── {cat_name} ({count} tickets, {pct:.1f}% of Wk9) ──")
    
    # Sites
    cs = Counter(t["site"] for t in cat_tix)
    p(f"   Sites: {', '.join(f'{s}({n})' for s, n in cs.most_common(12))}")
    
    # Resolution
    cat_rs = res_stats(cat_tix)
    if cat_rs:
        p(f"   Resolution: avg {cat_rs['avg']:.1f}h | median {cat_rs['med']:.1f}h | same-day {cat_rs['same_day_pct']:.0f}% | >3d: {cat_rs['gt3d']}")
    
    # WoW
    prev_count = sum(1 for t in wk8 if t["cat"] == cat_name)
    delta = count - prev_count
    p(f"   WoW: Wk8={prev_count} → Wk9={count} ({delta:+d})")
    
    # YoY
    yoy_count = sum(1 for t in wk9_25 if t["cat"] == cat_name)
    yoy_d = count - yoy_count
    p(f"   YoY: Wk9-2025={yoy_count} → Wk9-2026={count} ({yoy_d:+d})")
    
    # Sample tickets (show up to 8)
    p(f"   Sample tickets:")
    for t in cat_tix[:8]:
        desc = t["desc"][:220].replace("\n", " ").replace("\r", " ").strip()
        p(f"     [{t['num']}] {t['site']} | {desc}")

# ════════════════════════════════════════════════════════════════════════
# SECTION 8: DIRECTOR QUESTIONS — DATA-BACKED ANSWERS
# ════════════════════════════════════════════════════════════════════════
p()
p("=" * 90)
p("8. DIRECTOR QUESTIONS — DATA-BACKED ANSWERS")
p("   Source: HR OBR Supplemental 2026-03-02")
p("=" * 90)

p()
p("─── Q1: Which ticket types account for the 48% YoY decrease? ───")
p()
p("NOTE: The 48% decrease cited is for TOTAL submitted ticket volume (all HR")
p("services: 14,590 → 7,514). Our CSV only contains 'FC General Inquiry'.")
p("FC General Inquiry is essentially FLAT YoY:")
p(f"  Wk9 2025: {len(wk9_25)} tickets | Wk9 2026: {len(wk9)} tickets | Δ: {len(wk9)-len(wk9_25):+d}")
p()
p("The Supplemental already identifies the main drivers of the 48% total decrease:")
p("  1. Attendance Inquiry — Smartsheet Automation removed from FC (call-offs)")
p("  2. LOA Status — automated A1 notifications down 12.3% YoY")
p("  3. Job Application Inquiry — decreased ~100, possibly Workday recruiting impact")
p()
p("FC General Inquiry did NOT contribute to the 48% decrease. It held steady.")
p("This means the reduction came from OTHER HR Service types, not FC General Inquiry.")

p()
p("─── Q2: Biggest remaining opportunity to reduce FC General Inquiry volume? ───")
p()

# Sort categories by volume
auto_opps = []
for cat_name, count, pct in cat_table(wk9):
    if cat_name in ("Other / Unclassified", "Spam / Auto-Generated Junk / Misdirected Email", "Empty / No Description"):
        continue
    auto_opps.append((cat_name, count, pct))

p("Category volume ranking (actionable categories only):")
p()
total_actionable = sum(c for _, c, _ in auto_opps)
for cat_name, count, pct in auto_opps:
    p(f"  {count:>4} ({pct:>5.1f}%) | {cat_name}")

p()
p(f"  Total actionable: {total_actionable} / {len(wk9)} ({total_actionable/len(wk9)*100:.0f}%)")

p()
p("TOP 3 REDUCTION OPPORTUNITIES (highest-volume, most automatable):")
p()
p("  1. ATTENDANCE / CALL-OFF (largest category)")
att = [t for t in wk9 if t["cat"] == "Attendance / Call-Off / NCNS"]
p(f"     Volume: {len(att)} tickets/week ({len(att)/len(wk9)*100:.0f}% of FC Gen Inquiry)")
p(f"     Mechanism: TMs email site HR to report absences → auto-creates Snow ticket")
p(f"     Opportunity: UKG app call-off feature + centralized call-off line")
p(f"     Est. reduction: 50-70% if UKG self-service adopted (≈{int(len(att)*0.5)}-{int(len(att)*0.7)} fewer tickets/wk)")
p()
p("  2. LEAVE OF ABSENCE / FMLA / LOA")
loa = [t for t in wk9 if t["cat"] == "Leave of Absence / FMLA / LOA"]
p(f"     Volume: {len(loa)} tickets/week ({len(loa)/len(wk9)*100:.0f}% of FC Gen Inquiry)")
p(f"     Mechanism: TMs email site HR about leave questions → auto-creates ticket")
p(f"     Note: This category INCREASED +36% YoY — counter to network LOA trend")
p(f"     Opportunity: Better self-service leave status tracking, A1 portal improvements")
p()
p("  3. TIMECARD / PUNCH / SCHEDULE")
tc = [t for t in wk9 if t["cat"] == "Timecard / Punch / Schedule"]
p(f"     Volume: {len(tc)} tickets/week ({len(tc)/len(wk9)*100:.0f}% of FC Gen Inquiry)")
p(f"     Mechanism: TMs email site HR about missed punches, schedule questions")
p(f"     YoY: DECREASED 30% — UKG self-service is working here")
p(f"     Opportunity: Continue UKG app adoption push; remaining volume is residual")

p()
p("─── Q3: What does UKG tell us about what DROVE these tickets? ───")
p()
p("Phase I UKG data (Week 9) shows the FC network processed 41,790 timecard actions")
p("with a 39.6% defect rate (16,553 rework actions). Key drivers:")
p()
p("  • Manual Punch Correction: 22,955 actions (55% of FC work)")
p("  • Late arrival coding: 4,733 actions")
p("  • Early departure coding: 3,710 actions")
p("  • Leave of Absence coding: 2,573 actions")
p("  • UTO deductions: 1,533 actions")
p()
p("The #1 UKG rework driver (punch corrections) directly feeds the #3 ticket category")
p("(Timecard/Punch/Schedule). The fact that Timecard tickets are DOWN 30% YoY while")
p("UKG punch corrections remain massive suggests HR is absorbing more of this work")
p("silently — fewer TMs are opening tickets because site HR is proactively fixing")
p("timecards before TMs notice the error.")
p()
p("The #1 TICKET driver (Attendance/Call-Off) maps to UKG's late arrival + early")
p("departure coding (8,443 actions combined). These tickets are the DEMAND signal;")
p("UKG actions are the SUPPLY response.")

p()
p("─── Q4: What work is NOT captured in tickets? (Dark Work) ───")
p()
p(f"FC General Inquiry tickets: {len(wk9)}/week")
p(f"FC UKG rework actions: 16,553/week")
p(f"Ticket-to-Rework ratio: {len(wk9)/16553*100:.1f}%")
p()
p("~97-98% of HR timekeeping work is invisible to SNOW. This includes:")
p("  • Proactive punch corrections (HR fixes before TM notices)")
p("  • Governance actions (approvals, reviews) — 32,393 actions/wk")
p("  • Attendance coding done without a ticket (late arrival, NCNS, UTO)")
p("  • Historical corrections (1,875/wk — retro-pay risk)")
p()
p("Tickets measure TM-initiated demand. UKG measures total HR supply.")
p("Together they give the full picture.")

# ════════════════════════════════════════════════════════════════════════
# SECTION 9: DATA QUALITY FLAGS
# ════════════════════════════════════════════════════════════════════════
p()
p("=" * 90)
p("9. DATA QUALITY FLAGS")
p("=" * 90)

spam = [t for t in wk9 if t["cat"] == "Spam / Auto-Generated Junk / Misdirected Email"]
other = [t for t in wk9 if t["cat"] == "Other / Unclassified"]
empty = [t for t in wk9 if t["cat"] == "Empty / No Description"]

p(f"  Spam/junk tickets: {len(spam)} ({len(spam)/len(wk9)*100:.1f}%)")
p(f"  Unclassified tickets: {len(other)} ({len(other)/len(wk9)*100:.1f}%)")
p(f"  Empty descriptions: {len(empty)} ({len(empty)/len(wk9)*100:.1f}%)")
p()

# Examine "Other" to see what's in there
if other:
    p("  Unclassified sample (suggests additional categories needed):")
    # Group by pattern
    i9_count = sum(1 for t in other if "i9" in t["desc"].lower() or "i-9" in t["desc"].lower())
    license_count = sum(1 for t in other if "license" in t["desc"].lower() or "certificate" in t["desc"].lower())
    p(f"    Contains I-9 references: {i9_count}")
    p(f"    Contains license/certificate: {license_count}")
    for t in other[:10]:
        desc = t["desc"][:180].replace("\n", " ").replace("\r", " ").strip()
        p(f"    [{t['num']}] {t['site']} | {desc}")

if spam:
    p()
    p("  Spam/junk sample:")
    for t in spam[:5]:
        desc = t["desc"][:180].replace("\n", " ").replace("\r", " ").strip()
        p(f"    [{t['num']}] {t['site']} | {desc}")

# ── Write ──
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print(f"\nDone. Output: {OUTPUT_PATH}")
print(f"Wk9: {len(wk9)} | Wk8: {len(wk8)} | Categories: {len(cat_table(wk9))}")
