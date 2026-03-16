from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import statistics
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

from phase2_scope import WFM_ASSIGNMENT_GROUP_SCOPE_NOTE, is_wfm_assignment_group


DATE_FORMATS = (
    "%m/%d/%Y",
    "%m/%d/%Y %H:%M:%S",
    "%m/%d/%Y %H:%M",
    "%Y-%m-%d",
    "%Y-%m-%d %H:%M:%S",
)


def normalize_header(header: str) -> str:
    header = (header or "").replace("\ufeff", "").strip().lower()
    header = re.sub(r"\s+", " ", header)
    return header


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
        first_token = text.split()[0]
        for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
            try:
                return dt.datetime.strptime(first_token, fmt)
            except ValueError:
                pass
    return None


def parse_date(value: str) -> dt.date | None:
    parsed = parse_datetime(value)
    return parsed.date() if parsed else None


def parse_boolish_to_int(value: str) -> int:
    text = (value or "").strip().lower()
    if not text:
        return 0
    if text in {"y", "yes", "true", "t"}:
        return 1
    try:
        return 1 if float(text) > 0 else 0
    except ValueError:
        return 0


def safe_pct(num: float, den: float) -> float:
    if den == 0:
        return 0.0
    return (num / den) * 100.0


def safe_hours_delta(opened: dt.datetime | None, resolved: dt.datetime | None) -> float | None:
    if not opened or not resolved:
        return None
    delta = (resolved - opened).total_seconds() / 3600.0
    if delta < 0:
        return None
    return delta


def pick_first(row: dict[str, str], aliases: Iterable[str]) -> str:
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
    if "HR " in upper:
        first_token = upper.split()[0]
        if first_token:
            return first_token
    return "CENTRALIZED"


def format_count(counter: Counter) -> list[dict[str, int]]:
    return [
        {"name": name, "count": count}
        for name, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    ]


def resolution_summary(hours: list[float], total_tickets: int) -> dict[str, float]:
    if not hours:
        return {
            "resolved_count": 0,
            "resolved_pct": 0.0,
            "avg_hours": 0.0,
            "median_hours": 0.0,
            "p90_hours": 0.0,
            "over_72h_count": 0,
            "over_168h_count": 0,
        }
    sorted_hours = sorted(hours)
    idx_90 = min(len(sorted_hours) - 1, int(math.ceil(len(sorted_hours) * 0.9)) - 1)
    return {
        "resolved_count": len(sorted_hours),
        "resolved_pct": safe_pct(len(sorted_hours), total_tickets),
        "avg_hours": round(statistics.mean(sorted_hours), 2),
        "median_hours": round(statistics.median(sorted_hours), 2),
        "p90_hours": round(sorted_hours[idx_90], 2),
        "over_72h_count": sum(1 for h in sorted_hours if h > 72),
        "over_168h_count": sum(1 for h in sorted_hours if h > 168),
    }


def parse_phase2_csv(path: Path) -> tuple[list[dict[str, object]], set[str], dict[str, object]]:
    records: list[dict[str, object]] = []
    observed_columns: set[str] = set()
    excluded_assignment_groups: Counter[str] = Counter()
    excluded_wfm_rows = 0
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            normalized = {normalize_header(key): (value or "").strip() for key, value in row.items() if key is not None}
            observed_columns.update(normalized.keys())
            opened_raw = pick_first(normalized, ["Opened At", "Opened", "Created At"])
            opened_at = parse_datetime(opened_raw)
            if not opened_at:
                continue
            resolved_at = parse_datetime(pick_first(normalized, ["U Resolved", "Resolved At", "Closed At"]))
            hr_service = pick_first(normalized, ["Hr Service", "Service", "Ticket Type"])
            number = pick_first(normalized, ["Number", "Ticket Number", "Case Number"])
            assignment_group = pick_first(normalized, ["Assignment Group", "AssignmentGroup"])
            if is_wfm_assignment_group(assignment_group):
                excluded_wfm_rows += 1
                excluded_assignment_groups[assignment_group or "UNKNOWN"] += 1
                continue
            description = pick_first(normalized, ["Description1", "Description", "Short Description"])
            records.append(
                {
                    "opened_at": opened_at,
                    "opened_date": opened_at.date(),
                    "resolved_at": resolved_at,
                    "hr_service": hr_service if hr_service else path.stem,
                    "number": number if number else f"{path.stem}:{len(records)+1}",
                    "assignment_group": assignment_group,
                    "description": description,
                    "site": extract_site(assignment_group),
                    "source_file": str(path),
                }
            )
    return (
        records,
        observed_columns,
        {
            "source_file": str(path),
            "excluded_wfm_rows": excluded_wfm_rows,
            "excluded_assignment_groups": dict(excluded_assignment_groups),
        },
    )


def parse_phase1_csv(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            normalized = {normalize_header(key): (value or "").strip() for key, value in row.items() if key is not None}
            actor_group = pick_first(normalized, ["OBR_ACTOR_GROUP", "WBR_ACTOR_GROUP", "ACTOR_GROUP"]).upper()
            edit_target = pick_first(normalized, ["EDIT_TARGET"]).upper()
            if edit_target == "SELF" or actor_group in {"TEAM MEMBER", "OTHER", "AUTOMATION", "WFM"}:
                continue
            event_date_raw = pick_first(normalized, ["ENTITY_EVENT_DATE", "REPORT_WEEK"])
            event_date = parse_date(event_date_raw)
            if not event_date:
                continue
            rows.append(
                {
                    "event_date": event_date,
                    "site": pick_first(normalized, ["BUILDING_LOCATION"]) or "UNKNOWN",
                    "site_group": pick_first(normalized, ["OBR_SITE_GROUP"]) or "UNKNOWN",
                    "bucket_b": parse_boolish_to_int(pick_first(normalized, ["BUCKET_B"])),
                }
            )
    return rows


def slice_records_by_week(records: list[dict[str, object]], week_start: dt.date, week_end: dt.date, date_key: str) -> list[dict[str, object]]:
    return [record for record in records if week_start <= record[date_key] <= week_end]


def summarize_phase2_week(records: list[dict[str, object]]) -> dict[str, object]:
    by_service = Counter()
    by_site = Counter()
    hours: list[float] = []
    for record in records:
        by_service[record["hr_service"]] += 1
        by_site[record["site"]] += 1
        delta = safe_hours_delta(record["opened_at"], record["resolved_at"])
        if delta is not None:
            hours.append(delta)
    summary = {
        "total_tickets": len(records),
        "by_service": dict(by_service),
        "by_site": dict(by_site),
    }
    summary.update(resolution_summary(hours, len(records)))
    return summary


def summarize_phase1_week(rows: list[dict[str, object]]) -> dict[str, object]:
    by_site_actions = Counter()
    by_site_rework = Counter()
    total_actions = 0
    rework_actions = 0
    for row in rows:
        total_actions += 1
        by_site_actions[row["site"]] += 1
        if row["bucket_b"] == 1:
            rework_actions += 1
            by_site_rework[row["site"]] += 1
    return {
        "total_actions": total_actions,
        "rework_actions": rework_actions,
        "defect_rate_pct": round(safe_pct(rework_actions, total_actions), 2),
        "by_site_actions": dict(by_site_actions),
        "by_site_rework": dict(by_site_rework),
    }


def build_date_sequence(start: dt.date, end: dt.date) -> list[dt.date]:
    dates = []
    current = start
    while current <= end:
        dates.append(current)
        current += dt.timedelta(days=1)
    return dates


def summarize_phase1_coverage(
    rows: list[dict[str, object]],
    week8_start: dt.date,
    week8_end: dt.date,
    week9_start: dt.date,
    week9_end: dt.date,
) -> dict[str, object]:
    dates_present = {row["event_date"] for row in rows}
    week8_missing = [date.isoformat() for date in build_date_sequence(week8_start, week8_end) if date not in dates_present]
    week9_missing = [date.isoformat() for date in build_date_sequence(week9_start, week9_end) if date not in dates_present]
    all_dates = sorted(dates_present)
    return {
        "min_event_date": all_dates[0].isoformat() if all_dates else None,
        "max_event_date": all_dates[-1].isoformat() if all_dates else None,
        "missing_dates": {"week8": week8_missing, "week9": week9_missing},
        "week8_comparable": len(week8_missing) == 0,
        "week9_comparable": len(week9_missing) == 0,
    }


def compute_cross_phase(phase1_week9: dict[str, object], phase2_week9: dict[str, object]) -> dict[str, object]:
    total_phase1 = phase1_week9["total_actions"]
    rework_phase1 = phase1_week9["rework_actions"]
    total_phase2 = phase2_week9["total_tickets"]
    return {
        "phase2_ticket_visibility_vs_phase1_all_work_pct": round(safe_pct(total_phase2, total_phase1), 4),
        "phase2_ticket_visibility_vs_phase1_rework_pct": round(safe_pct(total_phase2, rework_phase1), 4),
        "non_ticket_work_proxy_count": max(total_phase1 - total_phase2, 0),
        "non_ticket_rework_proxy_count": max(rework_phase1 - total_phase2, 0),
        "method_note": "Proxy only. Ticket count and UKG touch count are different units and are not one-to-one linked.",
    }


def format_signed_int(value: int) -> str:
    return f"+{value}" if value > 0 else str(value)


def build_hr_operational_excellence_answers(
    week8_phase2: dict[str, object],
    week9_phase2: dict[str, object],
    observed_phase2_columns: set[str],
) -> dict[str, object]:
    week8_by_service = Counter(week8_phase2["by_service"])
    week9_by_service = Counter(week9_phase2["by_service"])
    all_services = set(week8_by_service.keys()) | set(week9_by_service.keys())
    deltas = []
    for service in all_services:
        wk8 = week8_by_service.get(service, 0)
        wk9 = week9_by_service.get(service, 0)
        deltas.append(
            {
                "service": service,
                "week8": wk8,
                "week9": wk9,
                "delta": wk9 - wk8,
                "delta_pct": round(safe_pct(wk9 - wk8, wk8), 2) if wk8 else None,
            }
        )
    deltas.sort(key=lambda item: (abs(item["delta"]), item["service"]), reverse=True)
    decreases = [item for item in deltas if item["delta"] < 0]
    increases = [item for item in deltas if item["delta"] > 0]

    has_sla_columns = any("sla" in col for col in observed_phase2_columns)
    q1 = {
        "question": "What is our plan to establish accurate SLA commitments and measurements?",
        "status": "data_gap",
        "answer": (
            "The current CSV inputs do not include SLA target definitions, SLA clocks, or breach flags, "
            "so adherence accuracy cannot be validated from this dataset alone."
        ),
        "required_data": [
            "SLA policy table by HR Service",
            "Ticket level SLA target at open time",
            "Ticket level within_SLA or breach indicator",
            "Timestamp-level lifecycle events if business-hour clocks are used",
        ],
        "has_sla_columns_in_input": has_sla_columns,
    }

    q2 = {
        "question": "Which ticket types account for the volume change?",
        "status": "answered",
        "answer": (
            "Week over week change is driven by the services with the largest absolute deltas between Week 8 and Week 9."
        ),
        "largest_decreases": decreases[:5],
        "largest_increases": increases[:5],
    }

    top_services = sorted(week9_by_service.items(), key=lambda item: (-item[1], item[0]))[:3]
    opportunity_map = {
        "attendance": "Drive one standardized call off intake path through UKG self service and enforce manager adoption.",
        "time and attendance": "Expand manager and TM self service for corrections before HR queueing.",
        "timesheet": "Increase missed punch self service and same day approval to reduce delayed inquiries.",
        "general inquiry": "Use guided intake and triage macros to route recurring requests to self service paths.",
        "leave": "Standardize required intake documents at first touch to reduce follow up loops.",
    }

    opportunities = []
    for service, volume in top_services:
        service_lower = service.lower()
        mapped = None
        for key, recommendation in opportunity_map.items():
            if key in service_lower:
                mapped = recommendation
                break
        if not mapped:
            mapped = "Create a service specific deflection playbook based on top repeating request patterns."
        opportunities.append(
            {
                "service": service,
                "week9_volume": volume,
                "opportunity": mapped,
                "type": "inference",
            }
        )

    q3 = {
        "question": "What is the biggest remaining opportunity, using existing process and technology, to reduce volume?",
        "status": "answered_with_inference",
        "answer": (
            "The biggest immediate opportunity is concentrated in the highest volume services in Week 9, "
            "where standardized self service and intake routing can reduce avoidable ticket creation."
        ),
        "top_service_opportunities": opportunities,
    }

    return {"q1": q1, "q2": q2, "q3": q3, "service_deltas": deltas}


def render_markdown(
    week8_start: dt.date,
    week8_end: dt.date,
    week9_start: dt.date,
    week9_end: dt.date,
    phase2_files: list[str],
    phase1_file: str,
    phase2_week8: dict[str, object],
    phase2_week9: dict[str, object],
    phase1_week8: dict[str, object],
    phase1_week9: dict[str, object],
    phase1_coverage: dict[str, object],
    cross_phase: dict[str, object],
    answers: dict[str, object],
) -> str:
    q1 = answers["q1"]
    q2 = answers["q2"]
    q3 = answers["q3"]
    week8_tickets = phase2_week8["total_tickets"]
    week9_tickets = phase2_week9["total_tickets"]
    ticket_delta = week9_tickets - week8_tickets
    ticket_delta_pct = safe_pct(ticket_delta, week8_tickets) if week8_tickets else 0.0
    resolved_pct_delta = round(phase2_week9["resolved_pct"] - phase2_week8["resolved_pct"], 2)

    week9_services = Counter(phase2_week9["by_service"])
    attendance_week9 = week9_services.get("Attendance inquiry", 0)
    cc_time_week9 = week9_services.get("CC Time and Attendance", 0) + week9_services.get("CS Time and Attendance", 0)
    timesheet_week9 = week9_services.get("Timesheet Inquiry", 0)
    attendance_time_total = attendance_week9 + cc_time_week9
    attendance_time_share = safe_pct(attendance_time_total, week9_tickets)

    largest_increase = q2["largest_increases"][0] if q2["largest_increases"] else None
    largest_decrease = q2["largest_decreases"][0] if q2["largest_decreases"] else None
    unticketed_rework_proxy_pct = round(100.0 - cross_phase["phase2_ticket_visibility_vs_phase1_rework_pct"], 4)

    lines: list[str] = []
    lines.append("# HR Operational Excellence Answer Pack")
    lines.append("")
    lines.append("## Week Lock")
    lines.append(f"- Week 8: {week8_start.isoformat()} to {week8_end.isoformat()} (Sunday to Saturday)")
    lines.append(f"- Week 9: {week9_start.isoformat()} to {week9_end.isoformat()} (Sunday to Saturday)")
    lines.append("")
    lines.append("## Inputs Used")
    lines.append(f"- Phase I CSV: `{phase1_file}`")
    lines.append("- Phase II CSVs:")
    for file_path in phase2_files:
        lines.append(f"  - `{file_path}`")
    lines.append("")
    lines.append("## Source Caveats")
    if phase1_coverage["missing_dates"]["week8"] or phase1_coverage["missing_dates"]["week9"]:
        lines.append(
            "Phase I prior-week data is retained in this report, but the Week 8 event-date coverage is incomplete. "
            "Use the prior-week Phase I values as directional signal rather than full-week equivalent."
        )
        lines.append("")
        lines.append(f"- Phase I min event date: {phase1_coverage['min_event_date']}")
        lines.append(f"- Phase I max event date: {phase1_coverage['max_event_date']}")
        lines.append(f"- Phase I Week 8 missing dates: {', '.join(phase1_coverage['missing_dates']['week8']) if phase1_coverage['missing_dates']['week8'] else 'None'}")
        lines.append(f"- Phase I Week 9 missing dates: {', '.join(phase1_coverage['missing_dates']['week9']) if phase1_coverage['missing_dates']['week9'] else 'None'}")
        lines.append(
            f"- Retained Phase I Week 8 sample: {phase1_week8['total_actions']} UKG touches and "
            f"{phase1_week8['rework_actions']} rework touches from the available rows."
        )
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Supplemental Response Draft")
    lines.append("")
    lines.append(
        f"Week 9 HR Operational Excellence ticket demand closed at {week9_tickets}, up {ticket_delta} from Week 8 "
        f"({ticket_delta_pct:.2f}%). Resolution performance weakened at the same time, with resolved rate moving "
        f"from {phase2_week8['resolved_pct']:.2f}% in Week 8 to {phase2_week9['resolved_pct']:.2f}% in Week 9 "
        f"({resolved_pct_delta:+.2f} pp)."
    )
    lines.append("")
    if largest_increase:
        increase_pct = "n/a" if largest_increase["delta_pct"] is None else f"{largest_increase['delta_pct']:.2f}%"
        lines.append(
            f"Based on the supplied ticket service labels, the net increase was driven primarily by "
            f"{largest_increase['service']} ({format_signed_int(largest_increase['delta'])} tickets, {increase_pct})."
        )
    if largest_decrease:
        decrease_pct = "n/a" if largest_decrease["delta_pct"] is None else f"{largest_decrease['delta_pct']:.2f}%"
        lines.append(
            f"The largest offsetting decline came from {largest_decrease['service']} "
            f"({format_signed_int(largest_decrease['delta'])} tickets, {decrease_pct})."
        )
    lines.append("")
    lines.append(
        f"Phase I shows {phase1_week9['total_actions']} UKG touches and {phase1_week9['rework_actions']} rework "
        f"touches in Week 9. Against that workload, the Phase II ticket stream covers "
        f"{cross_phase['phase2_ticket_visibility_vs_phase1_all_work_pct']:.4f}% of all UKG touches and "
        f"{cross_phase['phase2_ticket_visibility_vs_phase1_rework_pct']:.4f}% of UKG rework touches."
    )
    lines.append("")
    lines.append(
        "This supports using rework coverage as the primary cross-phase KPI, "
        "while treating the all-work view as secondary context."
    )
    lines.append("")
    lines.append(
        f"The most actionable near-term reduction opportunity remains attendance and timekeeping demand."
    )
    lines.append("")
    lines.append(
        f"Attendance Inquiry plus Time and Attendance work accounts for {attendance_time_total} of {week9_tickets} "
        f"Week 9 tickets ({attendance_time_share:.2f}%). Standardizing intake, self-service usage, and same-day correction "
        f"should produce the highest immediate impact."
    )
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"- Week 9 tickets: {week9_tickets} ({format_signed_int(ticket_delta)} WoW, {ticket_delta_pct:.2f}%).")
    lines.append(
        f"- Week 9 resolved rate: {phase2_week9['resolved_pct']:.2f}% ({resolved_pct_delta:+.2f} pp vs Week 8)."
    )
    if largest_increase:
        increase_pct = "n/a" if largest_increase["delta_pct"] is None else f"{largest_increase['delta_pct']:.2f}%"
        lines.append(
            f"- Largest growth driver: {largest_increase['service']} ({format_signed_int(largest_increase['delta'])}, {increase_pct})."
        )
    if largest_decrease:
        decrease_pct = "n/a" if largest_decrease["delta_pct"] is None else f"{largest_decrease['delta_pct']:.2f}%"
        lines.append(
            f"- Largest offsetting decline: {largest_decrease['service']} ({format_signed_int(largest_decrease['delta'])}, {decrease_pct})."
        )
    lines.append(
        f"- Primary cross-phase KPI recommendation: Ticketed Rework Coverage % = "
        f"{cross_phase['phase2_ticket_visibility_vs_phase1_rework_pct']:.4f}%."
    )
    lines.append(
        f"- Unticketed Rework Proxy % = {unticketed_rework_proxy_pct:.4f}% "
        f"({cross_phase['non_ticket_rework_proxy_count']} rework touches beyond the ticket count proxy)."
    )
    lines.append("")
    lines.append("## Week 8 vs Week 9 Snapshot")
    lines.append("")
    lines.append("| Metric | Week 8 | Week 9 | Delta |")
    lines.append("|---|---:|---:|---:|")
    lines.append(
        f"| Phase II total tickets | {phase2_week8['total_tickets']} | {phase2_week9['total_tickets']} | {format_signed_int(phase2_week9['total_tickets'] - phase2_week8['total_tickets'])} |"
    )
    lines.append(
        f"| Phase II resolved tickets | {phase2_week8['resolved_count']} | {phase2_week9['resolved_count']} | {format_signed_int(phase2_week9['resolved_count'] - phase2_week8['resolved_count'])} |"
    )
    lines.append(
        f"| Phase II resolved percent | {phase2_week8['resolved_pct']:.2f}% | {phase2_week9['resolved_pct']:.2f}% | {format_signed_int(round(phase2_week9['resolved_pct'] - phase2_week8['resolved_pct'], 2))} pp |"
    )
    if phase1_coverage["week8_comparable"] and phase1_coverage["week9_comparable"]:
        lines.append(
            f"| Phase I total UKG touches | {phase1_week8['total_actions']} | {phase1_week9['total_actions']} | {format_signed_int(phase1_week9['total_actions'] - phase1_week8['total_actions'])} |"
        )
        lines.append(
            f"| Phase I UKG rework touches | {phase1_week8['rework_actions']} | {phase1_week9['rework_actions']} | {format_signed_int(phase1_week9['rework_actions'] - phase1_week8['rework_actions'])} |"
        )
    else:
        lines.append(
            f"| Phase I total UKG touches | {phase1_week8['total_actions']} (partial prior-week sample) | {phase1_week9['total_actions']} | directional only |"
        )
        lines.append(
            f"| Phase I UKG rework touches | {phase1_week8['rework_actions']} (partial prior-week sample) | {phase1_week9['rework_actions']} | directional only |"
        )
    lines.append("")
    lines.append("## HR Operational Excellence Answers")
    lines.append("")
    lines.append("### Q1")
    lines.append(q1["question"])
    lines.append("")
    lines.append(
        "Direct answer: SLA adherence cannot be measured accurately from the current weekly files because the input set "
        "does not contain ticket-level SLA targets, SLA clocks, or breach flags."
    )
    lines.append("")
    lines.append(
        "Recommended plan: define the SLA commitment by HR Service, stamp the target on each ticket at open, "
        "calculate within-SLA or breach status on close and on aging backlog, and only then publish SLA attainment "
        "as an enterprise metric."
    )
    lines.append("")
    lines.append("Required data to answer this fully:")
    for needed in q1["required_data"]:
        lines.append(f"- {needed}")
    lines.append("")
    lines.append("### Q2")
    lines.append(q2["question"])
    lines.append("")
    lines.append(
        f"Direct answer: Week 9 volume increased by {ticket_delta} tickets ({ticket_delta_pct:.2f}%). "
        "Based on the supplied service labels, the increase was concentrated in Time and Attendance demand rather than "
        "broad-based growth across all services."
    )
    lines.append("")
    if largest_increase:
        increase_pct = "n/a" if largest_increase["delta_pct"] is None else f"{largest_increase['delta_pct']:.2f}%"
        lines.append(
            f"The primary growth driver was {largest_increase['service']} at {largest_increase['week9']} tickets, "
            f"up {abs(largest_increase['delta'])} ({increase_pct}) from Week 8."
        )
    if largest_decrease:
        decrease_pct = "n/a" if largest_decrease["delta_pct"] is None else f"{largest_decrease['delta_pct']:.2f}%"
        lines.append(
            f"The largest offset came from {largest_decrease['service']}, down {abs(largest_decrease['delta'])} "
            f"({decrease_pct}) from Week 8."
        )
    lines.append("")
    lines.append("Largest decreases:")
    if q2["largest_decreases"]:
        lines.append("| Service | Week 8 | Week 9 | Delta | Delta % |")
        lines.append("|---|---:|---:|---:|---:|")
        for row in q2["largest_decreases"]:
            pct = "n/a" if row["delta_pct"] is None else f"{row['delta_pct']:.2f}%"
            lines.append(
                f"| {row['service']} | {row['week8']} | {row['week9']} | {format_signed_int(row['delta'])} | {pct} |"
            )
    else:
        lines.append("- None")
    lines.append("")
    lines.append("Largest increases:")
    if q2["largest_increases"]:
        lines.append("| Service | Week 8 | Week 9 | Delta | Delta % |")
        lines.append("|---|---:|---:|---:|---:|")
        for row in q2["largest_increases"]:
            pct = "n/a" if row["delta_pct"] is None else f"{row['delta_pct']:.2f}%"
            lines.append(
                f"| {row['service']} | {row['week8']} | {row['week9']} | {format_signed_int(row['delta'])} | {pct} |"
            )
    else:
        lines.append("- None")
    lines.append("")
    lines.append("### Q3")
    lines.append(q3["question"])
    lines.append("")
    lines.append(
        f"Direct answer: the biggest near-term opportunity is to reduce avoidable attendance and timekeeping contacts "
        f"with existing tools and process controls. Those demand types represent {attendance_time_total} of {week9_tickets} "
        f"Week 9 tickets ({attendance_time_share:.2f}%)."
    )
    lines.append("")
    lines.append(
        "Immediate focus should be one standardized intake path, stronger manager adoption of self-service and approvals, "
        "and same-day correction before work converts into inquiries or rework."
    )
    lines.append("")
    lines.append("| Service | Week 9 Volume | Opportunity | Source Type |")
    lines.append("|---|---:|---|---|")
    for item in q3["top_service_opportunities"]:
        lines.append(
            f"| {item['service']} | {item['week9_volume']} | {item['opportunity']} | {item['type']} |"
        )
    lines.append("")
    lines.append("## HR Operational Excellence Focus")
    lines.append("")
    lines.append("Use this section as the direct Supplemental response for the weekly HR Operational Excellence discussion.")
    lines.append("")
    lines.append("### Narrative")
    lines.append(
        f"Week 9 ticket demand increased modestly, but the increase was concentrated in Time and Attendance work. "
        f"At the same time, closure performance fell from {phase2_week8['resolved_pct']:.2f}% to "
        f"{phase2_week9['resolved_pct']:.2f}%, indicating more work remained open at week close."
    )
    lines.append("")
    lines.append(
        f"Phase I reinforces that the ticket queue is only a partial view of workload. "
        f"Week 9 recorded {phase1_week9['total_actions']} UKG touches and {phase1_week9['rework_actions']} rework touches, "
        f"compared with {week9_tickets} tickets."
    )
    lines.append("")
    lines.append(
        "The rework-based coverage view is the better primary KPI because it aligns more closely "
        "to effort that likely required investigation or correction."
    )
    lines.append("")
    lines.append("### Recommended Actions This Week")
    lines.append("- Stand up ticket-level SLA measurement design before reporting SLA attainment to leadership.")
    lines.append("- Target CC Time and Attendance and Attendance Inquiry first because they dominate Week 9 demand.")
    lines.append("- Use Ticketed Rework Coverage % as the primary dark-work KPI for cross-phase reporting.")
    lines.append("- Keep Phase I Week 8 in the narrative as directional context until EPA refreshes the missing event dates.")
    lines.append("")
    lines.append("## Cross Phase Coverage Proxy")
    lines.append(
        "Ticket to touch mapping is not one to one. The following values are directional coverage proxies to estimate dark work."
    )
    lines.append("")
    lines.append("| Metric | Week 9 Value |")
    lines.append("|---|---:|")
    lines.append(
        f"| Ticketed Rework Coverage % (recommended primary KPI) | {cross_phase['phase2_ticket_visibility_vs_phase1_rework_pct']:.4f}% |"
    )
    lines.append(
        f"| Unticketed Rework Proxy % | {unticketed_rework_proxy_pct:.4f}% |"
    )
    lines.append(
        f"| Phase II ticket visibility vs all Phase I work | {cross_phase['phase2_ticket_visibility_vs_phase1_all_work_pct']:.4f}% |"
    )
    lines.append(
        f"| Phase II ticket visibility vs Phase I rework | {cross_phase['phase2_ticket_visibility_vs_phase1_rework_pct']:.4f}% |"
    )
    lines.append(
        f"| Non ticket work proxy count | {cross_phase['non_ticket_work_proxy_count']} |"
    )
    lines.append(
        f"| Non ticket rework proxy count | {cross_phase['non_ticket_rework_proxy_count']} |"
    )
    lines.append("")
    lines.append("## Data Gaps")
    lines.append("- SLA adherence commitments and breach logic cannot be validated from current CSV columns.")
    lines.append("- Proxy coverage cannot identify true ticket linkage without a shared ticket identifier in UKG touch records.")
    lines.append(f"- {WFM_ASSIGNMENT_GROUP_SCOPE_NOTE}")
    if phase1_coverage["missing_dates"]["week8"] or phase1_coverage["missing_dates"]["week9"]:
        lines.append("- Phase I event-date coverage is incomplete, so Phase I WoW comparisons are provisional.")
    lines.append("")
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build HR Operational Excellence weekly answer pack.")
    parser.add_argument("--phase1-csv", required=True, help="Phase I UKG touches CSV path")
    parser.add_argument("--phase2-csv", action="append", required=True, help="Phase II ticket CSV path. Pass multiple times.")
    parser.add_argument("--week8-start", default="2026-02-15")
    parser.add_argument("--week8-end", default="2026-02-21")
    parser.add_argument("--week9-start", default="2026-02-22")
    parser.add_argument("--week9-end", default="2026-02-28")
    parser.add_argument("--output-markdown", required=True)
    parser.add_argument("--output-metrics", required=True)
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()

    week8_start = dt.date.fromisoformat(args.week8_start)
    week8_end = dt.date.fromisoformat(args.week8_end)
    week9_start = dt.date.fromisoformat(args.week9_start)
    week9_end = dt.date.fromisoformat(args.week9_end)

    phase1_path = Path(args.phase1_csv).resolve()
    phase2_paths = [Path(path).resolve() for path in args.phase2_csv]
    markdown_path = Path(args.output_markdown).resolve()
    metrics_path = Path(args.output_metrics).resolve()

    phase2_records: list[dict[str, object]] = []
    observed_phase2_columns: set[str] = set()
    phase2_scope_filters: list[dict[str, object]] = []
    for path in phase2_paths:
        parsed_records, observed_columns, scope_filter = parse_phase2_csv(path)
        phase2_records.extend(parsed_records)
        observed_phase2_columns.update(observed_columns)
        phase2_scope_filters.append(scope_filter)

    phase1_rows = parse_phase1_csv(phase1_path)

    phase2_week8_rows = slice_records_by_week(phase2_records, week8_start, week8_end, "opened_date")
    phase2_week9_rows = slice_records_by_week(phase2_records, week9_start, week9_end, "opened_date")
    phase1_week8_rows = slice_records_by_week(phase1_rows, week8_start, week8_end, "event_date")
    phase1_week9_rows = slice_records_by_week(phase1_rows, week9_start, week9_end, "event_date")

    phase2_week8 = summarize_phase2_week(phase2_week8_rows)
    phase2_week9 = summarize_phase2_week(phase2_week9_rows)
    phase1_week8 = summarize_phase1_week(phase1_week8_rows)
    phase1_week9 = summarize_phase1_week(phase1_week9_rows)
    phase1_coverage = summarize_phase1_coverage(phase1_rows, week8_start, week8_end, week9_start, week9_end)
    cross_phase = compute_cross_phase(phase1_week9, phase2_week9)
    answers = build_hr_operational_excellence_answers(phase2_week8, phase2_week9, observed_phase2_columns)

    metrics = {
        "meta": {
            "generated_at_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
            "week8": {"start": week8_start.isoformat(), "end": week8_end.isoformat()},
            "week9": {"start": week9_start.isoformat(), "end": week9_end.isoformat()},
            "phase1_csv": str(phase1_path),
            "phase2_csvs": [str(path) for path in phase2_paths],
            "phase2_scope_filters": phase2_scope_filters,
        },
        "phase2": {"week8": phase2_week8, "week9": phase2_week9},
        "phase1": {"week8": phase1_week8, "week9": phase1_week9},
        "phase1_coverage": phase1_coverage,
        "cross_phase": cross_phase,
        "answers": answers,
        "observed_phase2_columns": sorted(observed_phase2_columns),
    }

    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(
        render_markdown(
            week8_start=week8_start,
            week8_end=week8_end,
            week9_start=week9_start,
            week9_end=week9_end,
            phase2_files=[str(path) for path in phase2_paths],
            phase1_file=str(phase1_path),
            phase2_week8=phase2_week8,
            phase2_week9=phase2_week9,
            phase1_week8=phase1_week8,
            phase1_week9=phase1_week9,
            phase1_coverage=phase1_coverage,
            cross_phase=cross_phase,
            answers=answers,
        ),
        encoding="utf-8",
    )
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(json.dumps({"markdown_path": str(markdown_path), "metrics_path": str(metrics_path)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
