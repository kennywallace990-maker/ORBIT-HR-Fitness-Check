"""
Workload Lens — Ticket Classifier
Codifies the Self-Service Classification Analysis rules.
Each ticket is classified into: Self Service Eligible, Process Optimization,
Process Required, Defect, or Unclear.
Each gets a sub-category label describing the specific issue type.
"""
import re

# ─────────────────────────────────────────────────────────────────────────────
# CLASSIFICATION RULES
# Each rule: (sub_category, classification, patterns_on_description, contact_filter)
#   - patterns_on_description: list of regex applied to Description1 (case-insensitive)
#   - contact_filter: None = any, or a set of contact types to match
# Rules are evaluated TOP-DOWN, first match wins.
# ─────────────────────────────────────────────────────────────────────────────

RULES = [
    # ═══════════════════════════════════════════════════════════════════════
    # RULE ORDERING: 3-tier approach
    # Tier 0: Automation (Smartsheet)
    # Tier 1: Specific PR/Defect keywords that MUST override SS patterns
    #         (FMLA, NCNS, I-9, coding errors, etc.)
    # Tier 2: Self Service patterns (broad)
    # Tier 3: Remaining PR patterns + selective contact-type defaults
    # ═══════════════════════════════════════════════════════════════════════

    # ── TIER 0: AUTOMATION ──
    ("Smartsheet automated notification", "Process Required",
     [r"smartsheet", r"automation@app\.sm"],
     None),

    # ── TIER 1: SPECIFIC PR — must match BEFORE broad SS patterns ──
    ("FMLA/LOA administration", "Process Required",
     [r"\bfmla\b", r"\bloa\b", r"leave\s*of\s*absence", r"intermittent.*leave",
      r"sedgwick", r"absence\s*one", r"short.?term.*disab", r"long.?term.*disab"],
     None),

    ("NCNS documentation", "Process Required",
     [r"ncns", r"no\s*call.*no\s*show", r"no-call.*no-show"],
     None),

    ("Accommodation processing", "Process Required",
     [r"accommodat", r"\bada\b.*(?:request|process|review|paper)"],
     None),

    ("Onboarding/I9 processing", "Process Required",
     [r"\bi-?9\b", r"onboard", r"pharmacy\s*(?:license|renewal|tech)",
      r"kybop", r"\brph\b"],
     None),

    ("Separation/termination processing", "Process Required",
     [r"terminat", r"separation\s*(?:process|request|date)",
      r"resign.*(?:process|date|effect|notice)"],
     None),

    ("Return to work processing", "Process Required",
     [r"return\s*to\s*work", r"\brtw\b", r"release.*(?:to|for)\s*work",
      r"back\s*to\s*work"],
     None),

    ("Bereavement leave processing", "Process Required",
     [r"bereavement"],
     None),

    ("Suspension/investigation inquiry", "Process Required",
     [r"suspend", r"suspension", r"investigation"],
     None),

    ("VET management", "Process Required",
     [r"\bvet\b(?!.*eran)", r"voluntary\s*extra\s*time",
      r"vet\s*(?:shift|sign|slot|offer|accept|manage|request|opportun)",
      r"(?:sign|accept|offer|pick).*\bvet\b"],
     None),

    ("IT incident resolution coding", "Process Required",
     [r"\binc\d{4,}", r"incident\s*(?:ticket|number|resolv|clos|creat)",
      r"(?:it|tech)\s*(?:issue|incident|outage|problem)",
      r"(?:system|app|application)\s*(?:issue|outage|down|error|crash)",
      r"genesys|headset|internet|vpn|citrix|nice\s*(?:issue|outage|down)"],
     None),

    ("Break/lactation coding", "Process Required",
     [r"break\s*(?:cod|time|adjust|deduct|penalty)", r"lactation",
      r"meal\s*(?:break|penalty|deduct|waiv)", r"rest\s*break"],
     None),

    ("Manager submitted timecard adjustment", "Process Required",
     [r"manager\s*(?:adjust|timecard|batch|submit|approv)",
      r"batch\s*adjust", r"timecard\s*adjust",
      r"(?:submit|approv).*(?:on\s*behalf|for\s*tm|for\s*team)"],
     None),

    # ── TIER 1: SPECIFIC DEFECT — explicit error/coding language ──
    ("Time-off reimbursement/correction needed", "Defect",
     [r"(?:reimburse|refund|return|add|put|give).{0,40}\b(?:uto|pto)\b(?:.{0,15}\bback\b)?",
      r"\b(?:uto|pto)\b.{0,15}\bback\b",
     r"\bnegative\s*uto\b",
      r"ticket.{0,20}closed.{0,40}(?:not|never|still).*(?:fixed|updated|reimburs|returned)",
      r"(?:time|timesheet|timecard).{0,30}(?:never\s*fixed|not\s*fixed|not\s*updated|not\s*coded|coded\s*properly)",
      r"(?:should\s*have\s*been|was\s*supposed\s*to\s*be).{0,20}\b(?:vto|pto|uto|leave)\b",
      r"(?:instead\s*of).{0,20}\b(?:vto|pto|uto|leave)\b",
      r"\bvto\b.{0,80}(?:still|hasn'?t|has\s*not|not).{0,20}coded\s*properly",
      r"\bvto\b.{0,50}(?:reimburse|refund|return|negative\s*uto|not\s*show|never\s*fixed|still\s*not|closed|wrong|incorrect|issue|problem|recode|update|switch|should\s*have\s*been)"],
     None),

    ("Improper time off coding", "Defect",
     [r"(?:improper|incorrect|wrong)\s*(?:cod|deduct|time.?off|uto|pto)",
      r"(?:cod|deduct).*(?:improper|incorrect|wrong|error)",
      r"should\s*(?:be|have\s*been)\s*(?:coded|deducted)",
      r"(?:uto|pto)\s*(?:incorrect|wrong|error|should\s*not)",
      r"(?:negative|unexpected)\s*(?:uto|pto)\s*(?:deduct)",
      r"coded\s*(?:wrong|incorrect)",
      r"wrong\s*(?:pay\s*code|code|deduction)"],
     None),

    ("Incorrect coding/deduction", "Defect",
     [r"incorrect\s*(?:coding|deduction|code)", r"wrong\s*(?:code|deduction)"],
     None),

    ("Retro pay correction needed", "Defect",
     [r"retro\s*(?:pay|correct|adjust|active)", r"(?:pay|correct)\s*retro"],
     None),

    ("TM reporting time/coding error", "Defect",
     [r"(?:incorrect|wrong|error)\s*(?:on|in|with)?\s*(?:time|hour|pay|timecard|wage|code)",
      r"(?:time|hour|pay|timecard).*(?:incorrect|wrong|error|missing|short)",
      r"(?:not\s*(?:paid|showing)|missing\s*(?:pay|hour|time))",
      r"(?:over|under)\s*(?:paid|deduct)",
      r"pay\s*(?:discrepan|issue|problem|short)",
      r"(?:timecard|time\s*card)\s*(?:issue|error|incorrect|wrong)"],
     None),

    ("System/badge/timeclock failure", "Defect",
     [r"(?:badge|timeclock|clock|kiosk)\s*(?:fail|error|broke|down|not\s*work|malfunction|jam)",
      r"(?:fail|broke|down|not\s*work|malfunction).*(?:badge|timeclock|clock|kiosk)"],
     None),

    # ═══════════════════════════════════════════════════════════════════════
    # TIER 2: SELF SERVICE — broad patterns for TM-initiated contacts
    # ═══════════════════════════════════════════════════════════════════════

    ("VTO administration/status", "Process Required",
     [r"\bvto\b", r"voluntary\s*time\s*off"],
     None),

    ("Missed punch (TM could use timeclock)", "Self Service Eligible",
     [r"punch", r"clock\s*(?:in|out)", r"missed.*clock", r"forgot.*(?:punch|clock)",
      r"didn.*(?:punch|clock)", r"no.*(?:punch|clock).*(?:in|out)",
      r"clocked", r"time\s*clock"],
     None),

    ("Weather absence (UKG app available)", "Self Service Eligible",
     [r"weather", r"inclement", r"storm", r"ice\s*(?:road|driv|condition)",
      r"snow\s*(?:road|driv|condition)", r"flood", r"road.*(?:condition|closed)"],
     None),

    ("Call out / absence report (UKG app available)", "Self Service Eligible",
     [r"call\s*(?:off|out|in)\b", r"called\s*(?:off|out|in)\b",
      r"calling\s*(?:off|out|in|sick)",
      r"(?:not|won'?t|can'?t|cannot|will\s*not)\s*(?:come|make|coming|be\s*in|be\s*at)",
      r"(?:sick|ill)\s*(?:today|tomorrow|and\s|not\s*com|can'?t)",
      r"not\s*(?:coming|making|able\s*to\s*(?:come|make|work))",
      r"unable\s*to\s*(?:come|work|make|report)",
      r"absent\s*(?:today|from|for|on|due)"],
     None),

    ("Voicemail call out (UKG app available)", "Self Service Eligible",
     [r"voicemail", r"voice\s*mail", r"\bvm\b.*(?:call|from)"],
     None),

    ("Balance inquiry (UKG app/Workday)", "Self Service Eligible",
     [r"(?:pto|uto|time.?off|vacation|sick)\s*balance",
      r"balance\s*(?:pto|uto|time.?off|vacation|sick)",
      r"how\s*(?:much|many)\s*(?:pto|uto|time|hour|day)",
      r"(?:check|verify|see)\s*(?:my\s*)?(?:pto|uto|balance|time.?off)"],
     None),

    ("PTO/UTO/Sick request (UKG app available)", "Self Service Eligible",
     [r"\bpto\b", r"\buto\b", r"sick\s*(?:time|day|leave|request|call)",
      r"personal\s*(?:time|day|unpaid|leave)",
      r"time\s*off", r"vacation"],
     None),

    ("Late/early notification (UKG app available)", "Self Service Eligible",
     [r"(?:going\s*to\s*be|running|will\s*be|gonna\s*be)\s*late",
      r"(?:leaving|left|leave)\s*early",
      r"\blate\b.*(?:today|arrival|coming|to\s*work)",
      r"early\s*(?:departure|out|leaving|release)",
      r"\btardy\b", r"tardiness"],
     None),

    ("Schedule inquiry (Workday/UKG available)", "Self Service Eligible",
     [r"schedule", r"\bshift\b"],
     None),

    # ── SS by Contact Type (specific patterns, not catch-all) ──
    ("Phone: TM time request (UKG app available)", "Self Service Eligible",
     [r"(?:time|hour|day).*(?:request|off|need|want|add|submit)",
      r"(?:request|need|want|submit|add).*(?:time|hour|day)"],
     {"Phone"}),

    ("TM time off request via email (UKG app available)", "Self Service Eligible",
     [r"(?:time|hour|day|off).*(?:request|need|want|submit)",
      r"(?:request|need|want|submit).*(?:time|hour|day|off)"],
     {"Email"}),

    ("TM absence notification via email (UKG app available)", "Self Service Eligible",
     [r"(?:absent|absence|not.*coming|will.*not|won'?t.*be|sick|ill)"],
     {"Email"}),

    ("Self service submission", "Self Service Eligible",
     [r"."],
     {"Self Service"}),

    ("Manager requesting time addition (TM could self serve via UKG)", "Self Service Eligible",
     [r"(?:manager|supervisor).*(?:add|time|hour|request|behalf)",
      r"(?:add|time|request).*(?:for|on\s*behalf)"],
     None),

    # ═══════════════════════════════════════════════════════════════════════
    # TIER 3: REMAINING PR + DEFECT (lower priority)
    # ═══════════════════════════════════════════════════════════════════════

    ("Internal report of error/discrepancy", "Defect",
     [r"(?:error|discrepanc).*(?:report|found|notic)",
      r"(?:report|found|notic).*(?:error|discrepanc)"],
     None),

    ("Shift swap request", "Process Required",
     [r"shift\s*swap", r"swap\s*shift"],
     None),

    ("Internal HR/manager communication", "Process Required",
     [r"(?:manager|supervisor).*(?:request|submit|report|follow|review|document|approv|adjust)",
      r"internal\s*(?:hr|team|request|note|comm)",
      r"(?:hr|manager)\s*(?:follow.?up|note|communication)"],
     None),

    ("Attendance policy/disciplinary action", "Process Required",
     [r"(?:attendance|disciplin).*(?:policy|action|counsel|warning)"],
     None),

    ("Compliance/license processing", "Process Required",
     [r"compliance", r"license", r"renewal", r"certification"],
     None),

    # ── SS catch-all for Phone/Email (after all PR/Defect checked) ──
    ("TM email inquiry (UKG/Workday available)", "Self Service Eligible",
     [r"."],
     {"Email"}),

    ("Phone inquiry (self service tools available)", "Self Service Eligible",
     [r"."],
     {"Phone"}),

    # ── Final catch-all ──
    ("Needs manual review", "Unclear",
     [r"."],
     None),
]


def classify_ticket(description, contact_type, hr_service, assignment_group=""):
    """
    Classify a single ticket.
    Returns: (classification, sub_category)
    """
    ag = (assignment_group or "").strip().lower()
    desc = re.sub(r"\s+", " ", (description or "").lower()).strip()
    ct = (contact_type or "").strip()

    # ── PRE-RULE: Real Time Analyst (WFM → HRSS) ──
    # These are WFM submitting requests to HRSS because NICE and UKG
    # don't sync. This is a process optimization opportunity, not
    # self-service and not a standard HR process.
    if "real time analyst" in ag:
        return "Process Optimization", "WFM/NICE-UKG sync request (Real Time Analyst)"

    if not desc:
        return "Unclear", "Needs manual review"

    for sub_cat, classification, patterns, contact_filter in RULES:
        # Check contact type filter
        if contact_filter is not None:
            if ct not in contact_filter:
                continue
        # Check description patterns
        for pattern in patterns:
            if re.search(pattern, desc, re.IGNORECASE):
                return classification, sub_cat

    return "Unclear", "Needs manual review"


# ─────────────────────────────────────────────────────────────────────────────
# SELF-SERVICE CHANNEL LOOKUP
# Maps sub-category to the self-service tool that was available
# ─────────────────────────────────────────────────────────────────────────────
SS_CHANNEL = {
    "Missed punch (TM could use timeclock)": "Timeclock",
    "Missed punch (timeclock available)": "Timeclock",
    "Call out / absence report (UKG app available)": "UKG App",
    "Phone: Call out (UKG app available)": "UKG App",
    "Phone: TM time request (UKG app available)": "UKG App",
    "Weather absence (UKG app available)": "UKG App",
    "TM email inquiry (UKG/Workday available)": "UKG App / Workday",
    "Balance inquiry (UKG app/Workday)": "UKG App / Workday",
    "Voicemail call out (UKG app available)": "UKG App",
    "TM time off request via email (UKG app available)": "UKG App",
    "Absence notification (UKG app available)": "UKG App",
    "TM absence notification via email (UKG app available)": "UKG App",
    "PTO/UTO/Sick request (UKG app available)": "UKG App",
    "Late/early notification (UKG app available)": "UKG App",
    "Manager requesting time addition (TM could self serve via UKG)": "UKG App (TM)",
    "Phone inquiry (self service tools available)": "UKG App / Workday",
    "Schedule inquiry (Workday/UKG available)": "UKG App / Workday",
    "Phone: Call out (UKG app available)": "UKG App",
}

def get_ss_channel(sub_category):
    return SS_CHANNEL.get(sub_category, "")
