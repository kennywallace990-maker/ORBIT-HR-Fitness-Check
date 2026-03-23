from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
from collections import Counter
from pathlib import Path
import re

from phase2_scope import is_wfm_assignment_group


def normalize_header(header: str) -> str:
    header = (header or "").replace("\ufeff", "").strip().lower().replace("_", " ")
    header = re.sub(r"\s+", " ", header)
    return header


def parse_date(value: str) -> dt.date | None:
    text = (value or "").strip()
    if not text:
        return None
    text = text.replace("\u200f", "").replace("\u200e", "")
    for fmt in ("%m/%d/%Y", "%m/%d/%Y %H:%M:%S", "%m/%d/%Y %H:%M", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    token = text.split()[0]
    for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(token, fmt).date()
        except ValueError:
            pass
    return None


def parse_datetime(value: str) -> dt.datetime | None:
    text = (value or "").strip()
    if not text:
        return None
    text = text.replace("\u200f", "").replace("\u200e", "")
    for fmt in ("%m/%d/%Y", "%m/%d/%Y %H:%M:%S", "%m/%d/%Y %H:%M", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return dt.datetime.strptime(text, fmt)
        except ValueError:
            pass
    token = text.split()[0]
    for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(token, fmt)
        except ValueError:
            pass
    return None


def safe_hours_delta(opened: dt.datetime | None, resolved: dt.datetime | None) -> float | None:
    if not opened or not resolved:
        return None
    delta = (resolved - opened).total_seconds() / 3600.0
    if delta < 0:
        return None
    return delta


def to_bucket_int(value: str) -> int:
    text = (value or "").strip().lower()
    if text in {"1", "1.0", "true", "t", "y", "yes"}:
        return 1
    try:
        return 1 if float(text) > 0 else 0
    except ValueError:
        return 0


def pick_first(row: dict[str, str], aliases: list[str]) -> str:
    for alias in aliases:
        key = normalize_header(alias)
        if key in row and (row[key] or "").strip():
            return row[key].strip()
    return ""


def load_phase2_records(paths: list[Path]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for path in paths:
        with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
            reader = csv.DictReader(handle)
            for raw_row in reader:
                row = {normalize_header(key): (value or "").strip() for key, value in raw_row.items() if key is not None}
                opened = parse_datetime(pick_first(row, ["Opened At", "Opened", "Created At"]))
                if not opened:
                    continue
                assignment_group = pick_first(row, ["Assignment Group", "AssignmentGroup"])
                if is_wfm_assignment_group(assignment_group):
                    continue
                resolved = parse_datetime(pick_first(row, ["U Resolved", "Resolved At", "Closed At"]))
                service = pick_first(row, ["Hr Service", "Service", "Ticket Type"]) or path.stem
                records.append({"opened_date": opened.date(), "opened": opened, "resolved": resolved, "service": service})
    return records


def load_phase1_records(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        reader = csv.DictReader(handle)
        for raw_row in reader:
            row = {normalize_header(key): (value or "").strip() for key, value in raw_row.items() if key is not None}
            actor_group = pick_first(row, ["OBR_ACTOR_GROUP", "WBR_ACTOR_GROUP", "ACTOR_GROUP"]).upper()
            edit_target = pick_first(row, ["EDIT_TARGET"]).upper()
            if edit_target == "SELF" or actor_group in {"TEAM MEMBER", "OTHER", "AUTOMATION", "WFM"}:
                continue
            event_date = parse_date(pick_first(row, ["ENTITY_EVENT_DATE", "REPORT_WEEK"]))
            if not event_date:
                continue
            rows.append({"event_date": event_date, "bucket_b": to_bucket_int(pick_first(row, ["BUCKET_B"]))})
    return rows


def filter_week(records: list[dict[str, object]], key: str, start: dt.date, end: dt.date) -> list[dict[str, object]]:
    return [record for record in records if start <= record[key] <= end]


def summarize_phase2(records: list[dict[str, object]]) -> dict[str, object]:
    service_counts = Counter()
    resolved_count = 0
    for record in records:
        service_counts[record["service"]] += 1
        if safe_hours_delta(record["opened"], record["resolved"]) is not None:
            resolved_count += 1
    return {
        "total_tickets": len(records),
        "resolved_count": resolved_count,
        "by_service": dict(service_counts),
    }


def summarize_phase1(rows: list[dict[str, object]]) -> dict[str, int]:
    total = len(rows)
    rework = sum(row["bucket_b"] for row in rows)
    return {"total_actions": total, "rework_actions": rework}


def compare(actual, expected, key: str, mismatches: list[dict[str, object]], tolerance: float = 0.0001) -> None:
    if isinstance(expected, float) or isinstance(actual, float):
        if abs(float(actual) - float(expected)) > tolerance:
            mismatches.append({"metric": key, "expected": expected, "actual": actual})
        return
    if actual != expected:
        mismatches.append({"metric": key, "expected": expected, "actual": actual})


def main() -> int:
    parser = argparse.ArgumentParser(description="Independent math validator for HR OE weekly pack.")
    parser.add_argument("--phase1-csv", required=True)
    parser.add_argument("--phase2-csv", action="append", required=True)
    parser.add_argument("--metrics-json", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--week8-start", default="2026-02-15")
    parser.add_argument("--week8-end", default="2026-02-21")
    parser.add_argument("--week9-start", default="2026-02-22")
    parser.add_argument("--week9-end", default="2026-02-28")
    args = parser.parse_args()

    week8_start = dt.date.fromisoformat(args.week8_start)
    week8_end = dt.date.fromisoformat(args.week8_end)
    week9_start = dt.date.fromisoformat(args.week9_start)
    week9_end = dt.date.fromisoformat(args.week9_end)

    phase1_path = Path(args.phase1_csv).resolve()
    phase2_paths = [Path(path).resolve() for path in args.phase2_csv]
    metrics_path = Path(args.metrics_json).resolve()
    output_path = Path(args.output_json).resolve()

    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    phase2_records = load_phase2_records(phase2_paths)
    phase1_rows = load_phase1_records(phase1_path)

    phase2_week8 = summarize_phase2(filter_week(phase2_records, "opened_date", week8_start, week8_end))
    phase2_week9 = summarize_phase2(filter_week(phase2_records, "opened_date", week9_start, week9_end))
    phase1_week8 = summarize_phase1(filter_week(phase1_rows, "event_date", week8_start, week8_end))
    phase1_week9 = summarize_phase1(filter_week(phase1_rows, "event_date", week9_start, week9_end))

    mismatches: list[dict[str, object]] = []
    compare(phase2_week8["total_tickets"], metrics["phase2"]["week8"]["total_tickets"], "phase2.week8.total_tickets", mismatches)
    compare(phase2_week9["total_tickets"], metrics["phase2"]["week9"]["total_tickets"], "phase2.week9.total_tickets", mismatches)
    compare(phase2_week8["resolved_count"], metrics["phase2"]["week8"]["resolved_count"], "phase2.week8.resolved_count", mismatches)
    compare(phase2_week9["resolved_count"], metrics["phase2"]["week9"]["resolved_count"], "phase2.week9.resolved_count", mismatches)
    compare(phase2_week8["by_service"], metrics["phase2"]["week8"]["by_service"], "phase2.week8.by_service", mismatches)
    compare(phase2_week9["by_service"], metrics["phase2"]["week9"]["by_service"], "phase2.week9.by_service", mismatches)
    compare(phase1_week8["total_actions"], metrics["phase1"]["week8"]["total_actions"], "phase1.week8.total_actions", mismatches)
    compare(phase1_week9["total_actions"], metrics["phase1"]["week9"]["total_actions"], "phase1.week9.total_actions", mismatches)
    compare(phase1_week8["rework_actions"], metrics["phase1"]["week8"]["rework_actions"], "phase1.week8.rework_actions", mismatches)
    compare(phase1_week9["rework_actions"], metrics["phase1"]["week9"]["rework_actions"], "phase1.week9.rework_actions", mismatches)

    visibility_all = (phase2_week9["total_tickets"] / phase1_week9["total_actions"] * 100.0) if phase1_week9["total_actions"] else 0.0
    visibility_rework = (phase2_week9["total_tickets"] / phase1_week9["rework_actions"] * 100.0) if phase1_week9["rework_actions"] else 0.0
    compare(round(visibility_all, 4), metrics["cross_phase"]["phase2_ticket_visibility_vs_phase1_all_work_pct"], "cross_phase.visibility_all_pct", mismatches)
    compare(round(visibility_rework, 4), metrics["cross_phase"]["phase2_ticket_visibility_vs_phase1_rework_pct"], "cross_phase.visibility_rework_pct", mismatches)

    result = {
        "pass": len(mismatches) == 0,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "validated_metrics": [
            "phase2 totals",
            "phase2 resolved counts",
            "phase2 by service",
            "phase1 total and rework touches",
            "cross phase visibility percentages",
        ],
        "validated_at_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
