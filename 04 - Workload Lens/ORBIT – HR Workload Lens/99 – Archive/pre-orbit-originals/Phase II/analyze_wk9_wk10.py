"""
Week 9 vs Week 10 Ticket Variance Analysis
Reads the four 2.22-3.7.26 CSVs, classifies tickets, and produces
a comprehensive WoW variance analysis.
"""
import csv
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta

BASE = os.path.dirname(__file__)
CSV_DIR = os.path.join(BASE, "Phase II CSVs")

FILES = {
    "Attendance Inquiry": "Attendance Inquiry 2.22-3.7.26.csv",
    "FC General Inquiry": "FC General Inquiry 2.22-3.7.26.csv",
    "CC Time and Attendance": "CC Time and Attendance 2.22-3.7.26.csv",
    "Timesheet Inquiry": "Timesheet Inquiry 2.22-3.7.26.csv",
}

# Week boundaries (Sun-Sat)
WK9_START = datetime(2026, 2, 22)
WK9_END = datetime(2026, 2, 28)
WK10_START = datetime(2026, 3, 1)
WK10_END = datetime(2026, 3, 7)

def parse_date(s):
    """Parse date from Opened At field."""
    if not s:
        return None
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y"):
        try:
            return datetime.strptime(s.strip(), fmt)
        except ValueError:
            continue
    return None

def parse_resolved(s):
    if not s:
        return None
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y"):
        try:
            return datetime.strptime(s.strip(), fmt)
        except ValueError:
            continue
    return None

def get_week(dt):
    if not dt:
        return None
    if WK9_START <= dt <= WK9_END:
        return "W9"
    elif WK10_START <= dt <= WK10_END:
        return "W10"
    return None

def extract_site(assignment_group):
    """Extract site code from Assignment Group."""
    if not assignment_group:
        return "UNKNOWN"
    ag = assignment_group.strip()
    # Common patterns: "AVP2 HR", "Real Time Analyst Tier I", "HR Team Member Data Management"
    # Centralized teams
    centralized = [
        "Real Time Analyst Tier I", "Real Time Analyst Tier II",
        "HR Team Member Data Management", "HR Team Member Service Center",
        "LOA/ADA Team", "Payroll Team", "HR TMDM"
    ]
    for c in centralized:
        if c.lower() in ag.lower():
            return "CENTRALIZED"
    # Site extraction: first token before " HR" or first token
    m = re.match(r'^([A-Z]{2,4}\d{0,2}(?:-[A-Z]+)?)', ag)
    if m:
        return m.group(1)
    return ag[:20]

def is_automation(desc):
    """Check if ticket is automation-generated (Smartsheet, automation@app)."""
    if not desc:
        return False
    dl = desc.lower()
    return "smartsheet" in dl or "automation@app" in dl

# Classification keywords for Attendance Inquiry sub-categories
# (Excluding LOA per user request)
ATTEND_CATEGORIES = [
    ("UTO Balance / Negative UTO", [
        r"uto", r"negative.*balance", r"balance.*negative", r"unscheduled time off",
        r"uto.*balance", r"balance.*uto"
    ]),
    ("Late Arrival / Tardy", [
        r"\blate\b", r"tardy", r"tardiness", r"late arrival", r"late.*in\b"
    ]),
    ("Early Departure", [
        r"early out", r"early departure", r"left early", r"leaving early", r"early.*leave"
    ]),
    ("NCNS", [
        r"ncns", r"no call.*no show", r"no-call.*no-show"
    ]),
    ("PTO / Time Off Coding", [
        r"\bpto\b", r"paid time off", r"time.?off.*cod", r"sick time", r"personal.*unpaid"
    ]),
    ("Schedule / Shift", [
        r"schedule", r"shift.*swap", r"shift.*change", r"swap.*shift"
    ]),
    ("Punch / Clock", [
        r"punch", r"clock", r"missed.*punch", r"clock.*in", r"clock.*out"
    ]),
    ("Call Off / Absence Report", [
        r"call.?off", r"call.?out", r"absent", r"not.*coming.*in", r"will not.*make it"
    ]),
    ("IT / System Issue", [
        r"\bit\b.*issue", r"system.*issue", r"ukg.*issue", r"nice.*issue",
        r"application.*issue", r"inc\d{6,}"
    ]),
    ("Weather", [
        r"weather", r"storm", r"ice", r"snow", r"inclement"
    ]),
]

FC_CATEGORIES = [
    ("I-9 / Onboarding / Compliance Docs", [
        r"i-?9", r"onboard", r"compliance", r"pharmacy.*license", r"renewal",
        r"kybop", r"rph", r"pharmacy.*tech", r"license"
    ]),
    ("PTO / Time-Off Balance", [
        r"\bpto\b", r"time.?off.*balance", r"uto", r"paid time off",
        r"negative.*balance", r"balance.*negative", r"personal.*unpaid"
    ]),
    ("Timecard / Punch / Schedule", [
        r"timecard", r"punch", r"schedule", r"shift", r"clock", r"time.*sheet"
    ]),
    ("Badge / Access / IT / Swag", [
        r"badge", r"access", r"swag", r"smartsheet", r"workday", r"\bit\b"
    ]),
    ("Attendance / Call-Off / NCNS", [
        r"attendance", r"call.?off", r"ncns", r"no call.*no show", r"absent",
        r"not.*coming.*in", r"weather"
    ]),
    ("Pay Discrepancy / Missing Pay", [
        r"pay.*discrepan", r"missing.*pay", r"underpaid", r"overpaid",
        r"pay.*issue", r"workers.*comp", r"paycheck"
    ]),
    ("VTO / VET / Voluntary Time", [
        r"\bvto\b", r"\bvet\b", r"voluntary.*time", r"voluntary.*extra"
    ]),
    ("Transfer / Job Change", [
        r"transfer", r"job.*change", r"promotion", r"demotion"
    ]),
    ("Termination / Separation", [
        r"terminat", r"separation", r"resign", r"voluntary.*quit"
    ]),
    ("Benefits / Enrollment / Payroll", [
        r"benefit", r"enrollment", r"payroll", r"401k", r"insurance"
    ]),
    ("Personal Info / Records", [
        r"personal.*info", r"name.*change", r"address.*change", r"records"
    ]),
]

CC_CATEGORIES = [
    ("UTO / Time-Off Coding", [
        r"uto", r"time.?off.*cod", r"personal.*unpaid", r"sick", r"coding"
    ]),
    ("PTO", [
        r"\bpto\b", r"paid time off"
    ]),
    ("IT / System Issue", [
        r"\bit\b", r"incident", r"inc\d", r"system", r"oracle", r"genesys",
        r"headset", r"internet", r"computer", r"nice.*issue"
    ]),
    ("Schedule / Shift", [
        r"schedule", r"shift", r"huddle", r"release", r"swap"
    ]),
    ("Punch / Clock / Missed Punch", [
        r"punch", r"clock", r"missed.*punch", r"lunch"
    ]),
    ("FMLA / Leave", [
        r"fmla", r"leave", r"intermittent"
    ]),
    ("Balance Inquiry", [
        r"balance", r"inquiry", r"inquiring"
    ]),
]

TIMESHEET_CATEGORIES = [
    ("Timecard Correction", [
        r"correction", r"adjust", r"hours", r"pay.*period", r"timesheet"
    ]),
    ("Workers Comp / PAWS", [
        r"workers.*comp", r"wc", r"paws"
    ]),
    ("PTO / Sick", [
        r"\bpto\b", r"sick", r"time.?off"
    ]),
]

def classify(desc, categories):
    if not desc:
        return "Other / Unclassified"
    dl = desc.lower()
    for cat_name, patterns in categories:
        for p in patterns:
            if re.search(p, dl):
                return cat_name
    return "Other / Unclassified"

def get_category_set(service):
    if service == "Attendance Inquiry":
        return ATTEND_CATEGORIES
    elif service == "FC General Inquiry":
        return FC_CATEGORIES
    elif service == "CC Time and Attendance":
        return CC_CATEGORIES
    elif service == "Timesheet Inquiry":
        return TIMESHEET_CATEGORIES
    return []

# ── Load all tickets ──
all_tickets = []
for service, fname in FILES.items():
    fpath = os.path.join(CSV_DIR, fname)
    with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        # Track multi-line descriptions
        rows = list(reader)
    
    # Because descriptions span multiple lines, we need to re-parse
    # Actually csv.DictReader handles quoted multi-line fields correctly
    # Let's just count unique ticket numbers
    seen = set()
    for row in rows:
        num = row.get('Number', '').strip()
        if not num or not num.startswith('HRC'):
            continue
        if num in seen:
            continue
        seen.add(num)
        
        opened = parse_date(row.get('Opened At', ''))
        resolved = parse_resolved(row.get('U Resolved', ''))
        week = get_week(opened)
        if not week:
            continue
        
        desc = row.get('Description1', '')
        ag = row.get('Assignment Group', '')
        contact = row.get('Contact Type', '')
        site = extract_site(ag)
        auto = is_automation(desc)
        cat = classify(desc, get_category_set(service))
        
        all_tickets.append({
            'service': service,
            'number': num,
            'opened': opened,
            'resolved': resolved,
            'week': week,
            'description': desc[:500],
            'assignment_group': ag,
            'contact_type': contact,
            'site': site,
            'is_automation': auto,
            'category': cat,
        })

print(f"Total unique tickets loaded: {len(all_tickets)}")

# ── Aggregate by week and service ──
print("\n" + "="*80)
print("SECTION 1: WEEK 9 vs WEEK 10 — SERVICE-LEVEL SUMMARY")
print("="*80)

svc_week = defaultdict(lambda: defaultdict(int))
for t in all_tickets:
    svc_week[t['service']][t['week']] += 1

total_w9 = sum(v.get('W9', 0) for v in svc_week.values())
total_w10 = sum(v.get('W10', 0) for v in svc_week.values())

print(f"\n{'Service':<30} {'Wk9':>6} {'Wk10':>6} {'Delta':>7} {'%Chg':>8}")
print("-"*60)
for svc in ["Attendance Inquiry", "CC Time and Attendance", "FC General Inquiry", "Timesheet Inquiry"]:
    w9 = svc_week[svc].get('W9', 0)
    w10 = svc_week[svc].get('W10', 0)
    delta = w10 - w9
    pct = (delta / w9 * 100) if w9 else 0
    print(f"{svc:<30} {w9:>6} {w10:>6} {delta:>+7} {pct:>+7.1f}%")
print("-"*60)
print(f"{'TOTAL':<30} {total_w9:>6} {total_w10:>6} {total_w10-total_w9:>+7} {((total_w10-total_w9)/total_w9*100) if total_w9 else 0:>+7.1f}%")

# ── Resolution rates ──
print("\n" + "="*80)
print("SECTION 2: RESOLUTION RATES")
print("="*80)

for svc in ["Attendance Inquiry", "CC Time and Attendance", "FC General Inquiry", "Timesheet Inquiry"]:
    for wk in ["W9", "W10"]:
        tickets = [t for t in all_tickets if t['service'] == svc and t['week'] == wk]
        total = len(tickets)
        resolved = sum(1 for t in tickets if t['resolved'])
        rate = (resolved/total*100) if total else 0
        print(f"{svc:<30} {wk}: {total:>5} total, {resolved:>5} resolved ({rate:.1f}%)")

# ── Automation vs Manual ──
print("\n" + "="*80)
print("SECTION 3: AUTOMATION vs MANUAL TICKET SPLIT")
print("="*80)

for svc in ["Attendance Inquiry", "FC General Inquiry"]:
    for wk in ["W9", "W10"]:
        tickets = [t for t in all_tickets if t['service'] == svc and t['week'] == wk]
        auto = sum(1 for t in tickets if t['is_automation'])
        manual = len(tickets) - auto
        print(f"{svc:<30} {wk}: Auto={auto:>4}, Manual={manual:>4}, Total={len(tickets):>4}")

# ── Category breakdown by service ──
print("\n" + "="*80)
print("SECTION 4: CATEGORY BREAKDOWN BY SERVICE — WoW")
print("="*80)

for svc in ["Attendance Inquiry", "CC Time and Attendance", "FC General Inquiry", "Timesheet Inquiry"]:
    print(f"\n--- {svc} ---")
    cat_week = defaultdict(lambda: defaultdict(int))
    for t in all_tickets:
        if t['service'] == svc:
            cat_week[t['category']][t['week']] += 1
    
    rows = []
    for cat, weeks in cat_week.items():
        w9 = weeks.get('W9', 0)
        w10 = weeks.get('W10', 0)
        delta = w10 - w9
        rows.append((cat, w9, w10, delta))
    
    rows.sort(key=lambda x: x[2], reverse=True)
    print(f"{'Category':<45} {'Wk9':>5} {'Wk10':>5} {'Delta':>6}")
    for cat, w9, w10, delta in rows:
        print(f"{cat:<45} {w9:>5} {w10:>5} {delta:>+6}")

# ── Site breakdown ──
print("\n" + "="*80)
print("SECTION 5: SITE-LEVEL VOLUME — TOP 15 SITES")
print("="*80)

site_week = defaultdict(lambda: defaultdict(int))
for t in all_tickets:
    site_week[t['site']][t['week']] += 1

site_rows = []
for site, weeks in site_week.items():
    w9 = weeks.get('W9', 0)
    w10 = weeks.get('W10', 0)
    delta = w10 - w9
    site_rows.append((site, w9, w10, delta))

site_rows.sort(key=lambda x: x[2], reverse=True)
print(f"\n{'Site':<20} {'Wk9':>5} {'Wk10':>5} {'Delta':>6}")
print("-"*40)
for site, w9, w10, delta in site_rows[:20]:
    print(f"{site:<20} {w9:>5} {w10:>5} {delta:>+6}")

# ── Daily volume pattern ──
print("\n" + "="*80)
print("SECTION 6: DAILY VOLUME PATTERN")
print("="*80)

day_svc = defaultdict(lambda: defaultdict(int))
for t in all_tickets:
    day_key = t['opened'].strftime('%Y-%m-%d %A') if t['opened'] else 'Unknown'
    day_svc[day_key][t['service']] += 1

print(f"\n{'Date':<22} {'Attend':>7} {'CC T&A':>7} {'FC Gen':>7} {'TS Inq':>7} {'Total':>7}")
for day in sorted(day_svc.keys()):
    vals = day_svc[day]
    total = sum(vals.values())
    print(f"{day:<22} {vals.get('Attendance Inquiry',0):>7} {vals.get('CC Time and Attendance',0):>7} {vals.get('FC General Inquiry',0):>7} {vals.get('Timesheet Inquiry',0):>7} {total:>7}")

# ── Contact type analysis ──
print("\n" + "="*80)
print("SECTION 7: CONTACT TYPE BREAKDOWN")
print("="*80)

for svc in ["Attendance Inquiry", "CC Time and Attendance", "FC General Inquiry", "Timesheet Inquiry"]:
    print(f"\n--- {svc} ---")
    ct_week = defaultdict(lambda: defaultdict(int))
    for t in all_tickets:
        if t['service'] == svc:
            ct = t['contact_type'] if t['contact_type'] else 'Unknown'
            ct_week[ct][t['week']] += 1
    
    print(f"{'Contact Type':<25} {'Wk9':>5} {'Wk10':>5} {'Delta':>6}")
    for ct, weeks in sorted(ct_week.items(), key=lambda x: x[1].get('W10', 0), reverse=True):
        w9 = weeks.get('W9', 0)
        w10 = weeks.get('W10', 0)
        print(f"{ct:<25} {w9:>5} {w10:>5} {w10-w9:>+6}")

# ── Attendance Inquiry deep dive: keyword frequency ──
print("\n" + "="*80)
print("SECTION 8: ATTENDANCE INQUIRY — KEYWORD FREQUENCY")
print("="*80)

keywords = {
    'uto': r'\buto\b',
    'smartsheet/automation': r'smartsheet|automation@app',
    'late': r'\blate\b|tardy|tardiness',
    'early out': r'early out|early departure|left early|leaving early',
    'ncns': r'ncns|no call.*no show',
    'negative balance': r'negative.*balance|balance.*negative',
    'schedule': r'\bschedule\b',
    'clock/punch': r'clock|punch',
    'pto': r'\bpto\b',
    'call off': r'call.?off|call.?out',
    'weather': r'weather|storm|ice|snow|inclement',
    'sick': r'\bsick\b',
}

for wk in ["W9", "W10"]:
    print(f"\n--- {wk} ---")
    attend_tickets = [t for t in all_tickets if t['service'] == 'Attendance Inquiry' and t['week'] == wk]
    total = len(attend_tickets)
    print(f"Total tickets: {total}")
    kw_counts = {}
    for kw, pattern in keywords.items():
        count = sum(1 for t in attend_tickets if re.search(pattern, (t['description'] or '').lower()))
        kw_counts[kw] = count
    
    for kw, count in sorted(kw_counts.items(), key=lambda x: x[1], reverse=True):
        pct = count/total*100 if total else 0
        print(f"  {kw:<25} {count:>5} ({pct:.1f}%)")

# ── FC General Inquiry: site × category for W10 ──
print("\n" + "="*80)
print("SECTION 9: FC GENERAL INQUIRY — SITE × CATEGORY (Week 10)")
print("="*80)

fc_w10 = [t for t in all_tickets if t['service'] == 'FC General Inquiry' and t['week'] == 'W10']
site_cat = defaultdict(lambda: defaultdict(int))
for t in fc_w10:
    site_cat[t['site']][t['category']] += 1

# Get all categories
all_cats = sorted(set(t['category'] for t in fc_w10))
print(f"{'Site':<15}", end='')
for c in all_cats:
    print(f" {c[:12]:>12}", end='')
print(f" {'TOTAL':>7}")

for site in sorted(site_cat.keys(), key=lambda s: sum(site_cat[s].values()), reverse=True)[:15]:
    print(f"{site:<15}", end='')
    for c in all_cats:
        print(f" {site_cat[site].get(c,0):>12}", end='')
    print(f" {sum(site_cat[site].values()):>7}")

# ── Variance drivers summary ──
print("\n" + "="*80)
print("SECTION 10: VARIANCE DRIVER SUMMARY — Wk9→Wk10")
print("="*80)

print(f"\nTotal tickets: Wk9={total_w9}, Wk10={total_w10}, Delta={total_w10-total_w9:+d} ({(total_w10-total_w9)/total_w9*100:+.1f}%)")

print("\n--- Largest WoW movements by service ---")
for svc in ["Attendance Inquiry", "CC Time and Attendance", "FC General Inquiry", "Timesheet Inquiry"]:
    w9 = svc_week[svc].get('W9', 0)
    w10 = svc_week[svc].get('W10', 0)
    delta = w10 - w9
    print(f"  {svc}: {delta:+d} tickets ({delta/w9*100 if w9 else 0:+.1f}%)")

print("\n--- Key observations from your xlsx comments ---")
print("  1. Attendance Inquiry automation volume FLAT (205 both weeks)")
print("     → Entire -147 decline came from MANUAL submissions (predominantly phone)")
print("  2. FC General Inquiry automation dropped -21 (AVP4 HR: 29→6)")
print("  3. CC T&A essentially flat (+10)")
print("  4. Timesheet Inquiry declined modestly (-12)")

print("\n--- Resolution rate degradation ---")
for svc in ["Attendance Inquiry", "CC Time and Attendance", "FC General Inquiry", "Timesheet Inquiry"]:
    for wk in ["W9", "W10"]:
        tickets = [t for t in all_tickets if t['service'] == svc and t['week'] == wk]
        total = len(tickets)
        resolved = sum(1 for t in tickets if t['resolved'])
        rate = (resolved/total*100) if total else 0
        if wk == "W9":
            w9_rate = rate
        else:
            delta_pp = rate - w9_rate
            print(f"  {svc}: {w9_rate:.1f}% → {rate:.1f}% ({delta_pp:+.1f} pp)")
