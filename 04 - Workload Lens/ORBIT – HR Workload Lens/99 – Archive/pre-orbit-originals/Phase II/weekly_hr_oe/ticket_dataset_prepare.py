from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

from phase2_scope import WFM_ASSIGNMENT_GROUP_SCOPE_NOTE, is_wfm_assignment_group


DATE_FORMATS = (
    "%m/%d/%Y",
    "%m/%d/%Y %H:%M:%S",
    "%m/%d/%Y %H:%M",
    "%Y-%m-%d",
    "%Y-%m-%d %H:%M:%S",
)


CATEGORY_RULES = [
    ("I-9 / Onboarding / Compliance Docs", [
        " i9", " i-9", "i9 ", "i-9 ", "i 9", "form i-9", "e-verify",
        "onboarding", "new hire", "orientation", "work authorization", "license", "nabp",
    ]),
    ("Pay Discrepancy / Missing Pay", [
        "missing pay", "not paid", "underpaid", "short on pay", "pay discrepancy",
        "paycheck", "pay stub", "payslip", "didn't get paid", "retro pay", "overpaid",
        "pay is wrong", "pay is incorrect", "not on my check",
    ]),
    ("PTO / Time-Off Balance", [
        "pto", "paid time off", "vacation", "time off balance", "pto balance",
        "holiday pay", "floating holiday", "time off request", "uto ", "unpaid time off",
    ]),
    ("Leave of Absence / FMLA / LOA", [
        "leave of absence", "loa", "fmla", "medical leave", "maternity", "accommodation",
        "ada ", "disability", "workers comp", "work comp", "sedgwick", "intermittent",
        "return to work", "bereavement",
    ]),
    ("Attendance / Call-Off / NCNS", [
        "call off", "call-off", "called off", "calling off", "ncns", "attendance",
        "absent", "tardy", "late arrival", "early departure", "attendance points", "call out",
        "called out", "report an absence",
    ]),
    ("Timecard / Punch / Schedule", [
        "timecard", "time card", "punch", "missed punch", "clock in", "clock out",
        "timesheet", "schedule", "shift", "kronos", "ukg", "time adjustment",
    ]),
    ("Suspension / Termination / Discipline / TM Relations", [
        "suspend", "suspension", "terminated", "termination", "fired", "discipline",
        "investigation", "harassment", "grievance", "retaliation",
    ]),
    ("Transfer / Job Change / Position", [
        "transfer", "department change", "position change", "promotion", "demotion",
        "job change", "shift change",
    ]),
    ("Benefits / Enrollment / Payroll", [
        "benefits", "enrollment", "health insurance", "401k", "401(k)", "w-2", "w2", "tax form",
    ]),
    ("VTO / VET / Voluntary Time", [
        "vto", "vet ", "voluntary time off", "voluntary overtime",
    ]),
    ("Badge / Access / IT / Workday", [
        "badge", "access", "login", "password", "locked out", "workday", "okta", "swag",
    ]),
    ("Personal Info / Verification / Records", [
        "address change", "name change", "employment verification", "verify employment", "voe",
        "social security", "emergency contact",
    ]),
    ("Noise / Spam / Auto-Generated Junk", [
        "spotify", "unsubscribe", "advertisement", "amazon", "efax", "successful transmission",
        "check this out", "print me please", "help me please", "kbs-services",
    ]),
]


def normalize_header(header: str) -> str:
    header = (header or "").replace("\ufeff", "").strip().lower()
    return re.sub(r"\s+", " ", header)


def parse_datetime(value: str) -> dt.datetime | None:
    text = (value or "").strip()
    if not text:
        return None
    text = text.replace("\u200f", "").replace("\u200e", "")
    for fmt in DATE_FORMATS:
        try:
            return dt.datetime.strptime(text, fmt)
        except ValueError:
            pass
    if " " in text:
        token = text.split()[0]
        for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
            try:
                return dt.datetime.strptime(token, fmt)
            except ValueError:
                pass
    return None


def safe_pct(num: float, den: float) -> float:
    if den == 0:
        return 0.0
    return (num / den) * 100.0


def pick_first(row: dict[str, str], aliases: list[str]) -> str:
    for alias in aliases:
        key = normalize_header(alias)
        if key in row and (row[key] or "").strip():
            return row[key].strip()
    return ""


def extract_site(assignment_group: str) -> str:
    text = (assignment_group or "").strip()
    upper = text.upper()
    if not upper:
        return "UNKNOWN"
    if "SDF 1/4/6" in upper:
        return "SDF-CAMPUS"
    if "TEAM MEMBER SERVICE CENTER" in upper:
        return "TMSC"
    if "LOA/ADA" in upper:
        return "LOA-ADA"
    if "PAYROLL" in upper:
        return "PAYROLL"
    match = re.search(r"\b([A-Z]{3,4}\d{1,2}[A-Z]?)\b", upper)
    if match:
        return match.group(1)
    return "CENTRALIZED"


def normalize_description(description: str) -> str:
    text = (description or "").strip()
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text


def classify_description(description: str) -> tuple[str, str]:
    desc = f" {description.lower()} "
    if not description:
        return "Empty / No Description", "empty"
    for category, keywords in CATEGORY_RULES:
        for keyword in keywords:
            if keyword in desc:
                return category, keyword.strip()
    return "Other / Unclassified", "fallback"


def to_slug(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug or "dataset"


def hours_between(start: dt.datetime | None, end: dt.datetime | None) -> float | None:
    if not start or not end:
        return None
    hours = (end - start).total_seconds() / 3600.0
    if hours < 0:
        return None
    return round(hours, 2)


def summarize_resolution(records: list[dict[str, object]]) -> dict[str, float]:
    values = [record["resolution_hours"] for record in records if record["resolution_hours"] is not None]
    if not values:
        return {
            "resolved_count": 0,
            "resolved_pct": 0.0,
            "avg_hours": 0.0,
            "median_hours": 0.0,
            "p90_hours": 0.0,
            "over_72h": 0,
            "over_168h": 0,
        }
    values.sort()
    p90_idx = min(len(values) - 1, int(math.ceil(len(values) * 0.9)) - 1)
    return {
        "resolved_count": len(values),
        "resolved_pct": round(safe_pct(len(values), len(records)), 2),
        "avg_hours": round(sum(values) / len(values), 2),
        "median_hours": round(values[len(values) // 2], 2),
        "p90_hours": round(values[p90_idx], 2),
        "over_72h": sum(1 for value in values if value > 72),
        "over_168h": sum(1 for value in values if value > 168),
    }


def build_date_sequence(start: dt.date, end: dt.date) -> list[dt.date]:
    dates = []
    current = start
    while current <= end:
        dates.append(current)
        current += dt.timedelta(days=1)
    return dates


def latest_completed_saturday(pull_date: dt.date) -> dt.date:
    # Python weekday: Monday=0 ... Sunday=6, Saturday=5
    days_since_saturday = (pull_date.weekday() - 5) % 7
    return pull_date - dt.timedelta(days=days_since_saturday)


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare and classify one EPA ticket CSV without combining raw datasets.")
    parser.add_argument("--input-csv", required=True)
    parser.add_argument("--service-name", required=True, help="Logical service name for outputs.")
    parser.add_argument("--week8-start", default="2026-02-15")
    parser.add_argument("--week8-end", default="2026-02-21")
    parser.add_argument("--week9-start", default="2026-02-22")
    parser.add_argument("--week9-end", default="2026-02-28")
    parser.add_argument("--pull-date", default=dt.date.today().isoformat())
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    week8_start = dt.date.fromisoformat(args.week8_start)
    week8_end = dt.date.fromisoformat(args.week8_end)
    week9_start = dt.date.fromisoformat(args.week9_start)
    week9_end = dt.date.fromisoformat(args.week9_end)
    pull_date = dt.date.fromisoformat(args.pull_date)

    input_csv = Path(args.input_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    slug = to_slug(args.service_name)
    cleaned_path = out_dir / f"{slug}_cleaned.csv"
    summary_path = out_dir / f"{slug}_summary.json"
    llm_compact_path = out_dir / f"{slug}_llm_compact.json"

    input_rows = 0
    missing_opened = 0
    deduped_out = 0
    wfm_excluded = 0
    raw_records: list[dict[str, object]] = []
    dedupe_keys: set[tuple[str, str, str, str]] = set()
    hr_service_counter: Counter[str] = Counter()
    excluded_assignment_groups: Counter[str] = Counter()

    with input_csv.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        reader = csv.DictReader(handle)
        for raw_row in reader:
            input_rows += 1
            row = {normalize_header(key): (value or "").strip() for key, value in raw_row.items() if key is not None}
            ticket_number = pick_first(row, ["Number", "Ticket Number", "Case Number"]) or f"row_{input_rows}"
            opened_at = parse_datetime(pick_first(row, ["Opened At", "Opened", "Created At"]))
            if not opened_at:
                missing_opened += 1
                continue
            resolved_at = parse_datetime(pick_first(row, ["U Resolved", "Resolved At", "Closed At"]))
            raw_hr_service = pick_first(row, ["Hr Service", "Service", "Ticket Type"])
            if raw_hr_service:
                hr_service_counter[raw_hr_service] += 1
            assignment_group = pick_first(row, ["Assignment Group", "AssignmentGroup"])
            if is_wfm_assignment_group(assignment_group):
                wfm_excluded += 1
                excluded_assignment_groups[assignment_group or "UNKNOWN"] += 1
                continue
            description = normalize_description(pick_first(row, ["Description1", "Description", "Short Description"]))
            dedupe_key = (ticket_number, opened_at.isoformat(), assignment_group, description)
            if dedupe_key in dedupe_keys:
                deduped_out += 1
                continue
            dedupe_keys.add(dedupe_key)

            category, rule_hit = classify_description(description)
            site = extract_site(assignment_group)
            opened_date = opened_at.date()
            if week8_start <= opened_date <= week8_end:
                week_bucket = "week8"
            elif week9_start <= opened_date <= week9_end:
                week_bucket = "week9"
            else:
                week_bucket = "outside"

            raw_records.append(
                {
                    "service_name": args.service_name,
                    "ticket_number": ticket_number,
                    "opened_at": opened_at.isoformat(sep=" "),
                    "resolved_at": resolved_at.isoformat(sep=" ") if resolved_at else "",
                    "opened_date": opened_date.isoformat(),
                    "week_bucket": week_bucket,
                    "assignment_group": assignment_group,
                    "site": site,
                    "description_clean": description,
                    "category": category,
                    "rule_hit": rule_hit,
                    "is_noise": "yes" if category == "Noise / Spam / Auto-Generated Junk" else "no",
                    "resolution_hours": hours_between(opened_at, resolved_at),
                }
            )

    week8_records = [record for record in raw_records if record["week_bucket"] == "week8"]
    week9_records = [record for record in raw_records if record["week_bucket"] == "week9"]
    all_dates_present = Counter(record["opened_date"] for record in raw_records)
    all_dates = sorted(dt.date.fromisoformat(value) for value in all_dates_present.keys())

    week8_expected_dates = build_date_sequence(week8_start, week8_end)
    week9_expected_dates = build_date_sequence(week9_start, week9_end)
    week8_missing_dates = [date.isoformat() for date in week8_expected_dates if date.isoformat() not in all_dates_present]
    week9_missing_dates = [date.isoformat() for date in week9_expected_dates if date.isoformat() not in all_dates_present]

    required_week9_end = latest_completed_saturday(pull_date)
    required_week9_start = required_week9_end - dt.timedelta(days=6)
    required_week8_end = required_week9_start - dt.timedelta(days=1)
    required_week8_start = required_week8_end - dt.timedelta(days=6)
    required_dates = build_date_sequence(required_week8_start, required_week9_end)
    required_missing_dates = [date.isoformat() for date in required_dates if date.isoformat() not in all_dates_present]

    min_opened_date = all_dates[0].isoformat() if all_dates else None
    max_opened_date = all_dates[-1].isoformat() if all_dates else None
    required_window_range_covered = bool(
        all_dates and all_dates[0] <= required_week8_start and all_dates[-1] >= required_week9_end
    )
    locked_window_missing_total = len(week8_missing_dates) + len(week9_missing_dates)
    locked_window_coverage_pct = round(
        safe_pct(len(week8_expected_dates) + len(week9_expected_dates) - locked_window_missing_total, len(week8_expected_dates) + len(week9_expected_dates)),
        2,
    )
    required_window_coverage_pct = round(
        safe_pct(len(required_dates) - len(required_missing_dates), len(required_dates)),
        2,
    )

    week8_categories = Counter(record["category"] for record in week8_records)
    week9_categories = Counter(record["category"] for record in week9_records)
    week9_sites = Counter(record["site"] for record in week9_records)
    category_deltas = []
    for category in sorted(set(week8_categories.keys()) | set(week9_categories.keys())):
        count8 = week8_categories.get(category, 0)
        count9 = week9_categories.get(category, 0)
        category_deltas.append(
            {
                "category": category,
                "week8": count8,
                "week9": count9,
                "delta": count9 - count8,
                "delta_pct": round(safe_pct(count9 - count8, count8), 2) if count8 else None,
            }
        )
    category_deltas.sort(key=lambda item: (abs(item["delta"]), item["category"]), reverse=True)

    summary = {
        "service_name": args.service_name,
        "input_csv": str(input_csv),
        "week_lock": {
            "week8_start": week8_start.isoformat(),
            "week8_end": week8_end.isoformat(),
            "week9_start": week9_start.isoformat(),
            "week9_end": week9_end.isoformat(),
            "definition": "Sunday through Saturday",
        },
        "data_quality": {
            "input_rows": input_rows,
            "clean_rows": len(raw_records),
            "missing_opened_at_rows": missing_opened,
            "deduplicated_rows_removed": deduped_out,
            "wfm_excluded_rows": wfm_excluded,
            "wfm_assignment_groups_excluded": dict(excluded_assignment_groups),
            "hr_service_values": dict(hr_service_counter),
        },
        "date_coverage": {
            "min_opened_date": min_opened_date,
            "max_opened_date": max_opened_date,
            "locked_window_missing_dates": {
                "week8": week8_missing_dates,
                "week9": week9_missing_dates,
            },
            "locked_window_coverage_pct": locked_window_coverage_pct,
            "required_trailing_two_week_window": {
                "pull_date": pull_date.isoformat(),
                "required_week8_start": required_week8_start.isoformat(),
                "required_week8_end": required_week8_end.isoformat(),
                "required_week9_start": required_week9_start.isoformat(),
                "required_week9_end": required_week9_end.isoformat(),
                "range_covered": required_window_range_covered,
                "missing_dates": required_missing_dates,
                "coverage_pct": required_window_coverage_pct,
            },
        },
        "week8": {
            "ticket_count": len(week8_records),
            "resolution": summarize_resolution(week8_records),
            "category_counts": dict(week8_categories),
        },
        "week9": {
            "ticket_count": len(week9_records),
            "resolution": summarize_resolution(week9_records),
            "category_counts": dict(week9_categories),
            "top_sites": [{"site": site, "count": count} for site, count in week9_sites.most_common(10)],
        },
        "wow_category_deltas": category_deltas,
    }

    # Compact artifact for LLM context efficiency.
    top_week9_categories = [item for item in sorted(week9_categories.items(), key=lambda item: (-item[1], item[0]))[:8]]
    evidence_samples = []
    category_sample_counts = defaultdict(int)
    for record in sorted(week9_records, key=lambda item: (item["category"], item["ticket_number"])):
        category = record["category"]
        if category_sample_counts[category] >= 2:
            continue
        if category not in dict(top_week9_categories):
            continue
        desc = record["description_clean"]
        evidence_samples.append(
            {
                "ticket_number": record["ticket_number"],
                "site": record["site"],
                "category": category,
                "opened_date": record["opened_date"],
                "resolution_hours": record["resolution_hours"],
                "description_excerpt": desc[:240],
            }
        )
        category_sample_counts[category] += 1
        if len(evidence_samples) >= 16:
            break

    llm_compact = {
        "service_name": args.service_name,
        "week_lock": summary["week_lock"],
        "kpis": {
            "week8_ticket_count": summary["week8"]["ticket_count"],
            "week9_ticket_count": summary["week9"]["ticket_count"],
            "week9_vs_week8_delta": summary["week9"]["ticket_count"] - summary["week8"]["ticket_count"],
            "week9_resolution_pct": summary["week9"]["resolution"]["resolved_pct"],
            "week9_avg_resolution_hours": summary["week9"]["resolution"]["avg_hours"],
        },
        "top_categories_week9": [{"category": category, "count": count} for category, count in top_week9_categories],
        "top_sites_week9": summary["week9"]["top_sites"][:8],
        "largest_category_deltas_wow": summary["wow_category_deltas"][:8],
        "evidence_samples": evidence_samples,
        "data_quality": summary["data_quality"],
        "date_coverage": {
            "locked_window_coverage_pct": summary["date_coverage"]["locked_window_coverage_pct"],
            "required_trailing_two_week_window": summary["date_coverage"]["required_trailing_two_week_window"],
        },
        "limitations": [
            "Rows are classified with deterministic keyword rules only.",
            "No SLA adherence fields are present in this source extract.",
            WFM_ASSIGNMENT_GROUP_SCOPE_NOTE,
            "Samples are truncated for token efficiency.",
        ],
    }

    cleaned_fields = [
        "service_name",
        "ticket_number",
        "opened_at",
        "resolved_at",
        "opened_date",
        "week_bucket",
        "assignment_group",
        "site",
        "category",
        "rule_hit",
        "is_noise",
        "resolution_hours",
        "description_clean",
    ]

    with cleaned_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=cleaned_fields)
        writer.writeheader()
        for record in raw_records:
            writer.writerow(record)

    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    llm_compact_path.write_text(json.dumps(llm_compact, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "service_name": args.service_name,
                "cleaned_csv": str(cleaned_path),
                "summary_json": str(summary_path),
                "llm_compact_json": str(llm_compact_path),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
