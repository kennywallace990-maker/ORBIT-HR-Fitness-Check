from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import re
from pathlib import Path


OUTPUT_HEADERS = [
    "REPORT_WEEK",
    "EMPLOYEE_ID",
    "BUILDING_LOCATION",
    "OBR_SITE_GROUP",
    "OBR_ACTOR_GROUP",
    "EDIT_TARGET",
    "ENTITY_EVENT_DATE",
    "ENTITY_TYPE",
    "REVISION_TYPE",
    "PAYCODE_NAME",
    "PAYCODE_CATEGORY",
    "HC_CATEGORY",
    "BUCKET_A",
    "BUCKET_B",
    "BUCKET_G",
    "FRICTION_SCORE",
    "HIGH_RISK_REWORK",
    "HAS_COMMENT",
    "DAILY_MISSED_PUNCHES",
    "WEEKLY_MISSED_PUNCHES",
    "MISSING_PUNCH_FLAG",
    "MISSED_PUNCH_DATES",
    "COMMENT",
    "NOTE_TEXT",
]


def normalize_header(value: str) -> str:
    value = (value or "").replace("\ufeff", "").strip().lower().replace("_", " ")
    return re.sub(r"\s+", " ", value)


def pick_first(row: dict[str, str], aliases: list[str]) -> str:
    for alias in aliases:
        key = normalize_header(alias)
        if key in row and (row[key] or "").strip():
            return row[key].strip()
    return ""


def parse_date(value: str) -> dt.date | None:
    text = (value or "").strip()
    if not text:
        return None
    text = text.replace("\u200f", "").replace("\u200e", "")
    token = text.split()[0]
    for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
        try:
            return dt.datetime.strptime(token, fmt).date()
        except ValueError:
            pass
    return None


def to_report_week(event_date: dt.date) -> dt.date:
    return event_date - dt.timedelta(days=(event_date.weekday() + 1) % 7)


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def stable_employee_key(value: str) -> str:
    text = (value or "").strip()
    if not text:
        return ""
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    return f"emp_{digest}"


def contains_any(text: str, patterns: list[str]) -> bool:
    lowered = (text or "").strip().lower()
    return any(pattern in lowered for pattern in patterns)


def bucket_b(entity_type: str, revision_type: str, paycode_name: str) -> bool:
    entity = (entity_type or "").strip().lower()
    revision = (revision_type or "").strip().lower()
    paycode = (paycode_name or "").strip().lower()
    if entity == "punch":
        return True
    if entity == "historical correction":
        return True
    if revision in {"edit", "delete"} and entity in {"pay code edit", "manager justified time"}:
        return True
    if entity == "manager justified time" and revision == "add":
        if contains_any(paycode, ["late", "early", "ncns", "call off", "unpd"]):
            return True
    return False


def bucket_a(entity_type: str, revision_type: str, paycode_name: str) -> bool:
    entity = (entity_type or "").strip().lower()
    revision = (revision_type or "").strip().lower()
    paycode = (paycode_name or "").strip().lower()
    if entity == "pay code edit" and revision == "add":
        return True
    if entity == "manager justified time" and revision == "add":
        return not contains_any(paycode, ["late", "early", "ncns", "call off", "unpd"])
    return False


def bucket_g(entity_type: str) -> bool:
    entity = (entity_type or "").strip().lower()
    return entity in {
        "exception comment",
        "punch comment",
        "pay code edit comment",
        "historical correction comment",
        "mark as reviewed",
        "manager approval",
    }


def friction_score(entity_type: str, revision_type: str) -> str:
    entity = (entity_type or "").strip().lower()
    revision = (revision_type or "").strip().lower()
    if entity == "historical correction":
        return "5.0"
    if revision in {"edit", "delete"} and entity in {"punch", "pay code edit", "manager justified time"}:
        return "1.0"
    return "0.5"


def high_risk_rework(entity_type: str, revision_type: str, paycode_name: str) -> bool:
    entity = (entity_type or "").strip().lower()
    revision = (revision_type or "").strip().lower()
    paycode = (paycode_name or "").strip().lower()
    if entity == "historical correction":
        return True
    if entity == "punch" and revision in {"add", "edit", "delete"}:
        return True
    if entity == "pay code edit" and revision in {"add", "edit"}:
        return contains_any(paycode, ["pto", "sick", "regular", "overtime"])
    return False


def paycode_category(paycode_name: str) -> str:
    paycode = (paycode_name or "").strip().lower()
    if not paycode:
        return "Manual Punch Correction"
    if "vto" in paycode or "voluntary" in paycode:
        return "Time spent manually coding VTO (Real-time or Pre-VTO)"
    if "weather" in paycode:
        return "Time spent manually coding weather-related event"
    if "late" in paycode:
        return "Making up PTO deficit or adding missed late arrival"
    if "early" in paycode:
        return "Making up PTO deficit or adding missed early departure"
    if "ncns" in paycode:
        return "Manual coding NCNS response"
    if "call off" in paycode:
        return "Manual coding Advance Call Off or NCNS"
    if "sick" in paycode:
        return "Manual coding Sick Time"
    if "leave" in paycode:
        return "Manual coding Intermittent Leave or LOA"
    if "pto paid dur" in paycode or "personal unpd dur" in paycode:
        return "Manual coding for early departure/long lunch to deduct UTO"
    if "pto" in paycode:
        return "Manual coding of Paid Time Off"
    if "meal break" in paycode:
        return "Manual coding to prevent UTO (Meal Break)"
    if "personal" in paycode:
        return "Manual coding of Personal Time"
    return f"Time spent manually coding {paycode_name.strip()}"


def hc_category(paycode_name: str) -> str:
    paycode = (paycode_name or "").strip().lower()
    if contains_any(paycode, ["ncns", "late", "early", "call off"]):
        return "Attendance Enforcement"
    if contains_any(paycode, ["regular", "overtime", "meal", "pto paid"]):
        return "Core Pay & Missing Time"
    if contains_any(paycode, ["personal", "vto", "weather", "unpaid"]):
        return "Schedule & Unpaid True-Ups"
    if contains_any(paycode, ["leave", "fmla", "loa", "bereavement"]):
        return "Leave & Compliance Lag"
    return "Other"


def load_rows(paths: list[Path]) -> tuple[list[dict[str, str]], dict[str, object]]:
    output_rows: list[dict[str, str]] = []
    summary: dict[str, object] = {"inputs": [], "row_count": 0, "date_min": None, "date_max": None}
    min_date: dt.date | None = None
    max_date: dt.date | None = None

    for path in paths:
        input_rows = 0
        kept_rows = 0
        with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
            reader = csv.DictReader(handle)
            for raw_row in reader:
                input_rows += 1
                row = {normalize_header(key): (value or "").strip() for key, value in raw_row.items() if key is not None}
                event_date = parse_date(pick_first(row, ["ENTITY_EVENT_DATE", "PARTITION_DATE", "REPORT_WEEK"]))
                if not event_date:
                    continue

                building_location = pick_first(row, ["BUILDING_LOCATION"])
                site_group = pick_first(row, ["OBR_SITE_GROUP", "WBR_SITE_GROUP"])
                actor_group = pick_first(row, ["OBR_ACTOR_GROUP", "WBR_ACTOR_GROUP", "REVISION_GROUP", "ACTOR_GROUP"])
                revision_type_value = pick_first(row, ["REVISION_TYPE"])
                entity_type_value = pick_first(row, ["ENTITY_TYPE"])
                paycode_name_value = pick_first(row, ["PAYCODE_NAME"])
                comment_value = pick_first(row, ["COMMENT"])
                note_value = pick_first(row, ["NOTE_TEXT", "NOTES_TEXT"])

                output_rows.append(
                    {
                        "REPORT_WEEK": to_report_week(event_date).isoformat(),
                        "EMPLOYEE_ID": stable_employee_key(pick_first(row, ["EMPLOYEE_ID", "PERSON_NUMBER"])),
                        "BUILDING_LOCATION": building_location,
                        "OBR_SITE_GROUP": site_group,
                        "OBR_ACTOR_GROUP": actor_group,
                        "EDIT_TARGET": pick_first(row, ["EDIT_TARGET"]) or "Other",
                        "ENTITY_EVENT_DATE": event_date.isoformat(),
                        "ENTITY_TYPE": entity_type_value,
                        "REVISION_TYPE": revision_type_value,
                        "PAYCODE_NAME": paycode_name_value,
                        "PAYCODE_CATEGORY": paycode_category(paycode_name_value),
                        "HC_CATEGORY": hc_category(paycode_name_value),
                        "BUCKET_A": bool_text(bucket_a(entity_type_value, revision_type_value, paycode_name_value)),
                        "BUCKET_B": bool_text(bucket_b(entity_type_value, revision_type_value, paycode_name_value)),
                        "BUCKET_G": bool_text(bucket_g(entity_type_value)),
                        "FRICTION_SCORE": friction_score(entity_type_value, revision_type_value),
                        "HIGH_RISK_REWORK": bool_text(high_risk_rework(entity_type_value, revision_type_value, paycode_name_value)),
                        "HAS_COMMENT": "1" if comment_value or note_value else "0",
                        "DAILY_MISSED_PUNCHES": "0",
                        "WEEKLY_MISSED_PUNCHES": "0",
                        "MISSING_PUNCH_FLAG": "No",
                        "MISSED_PUNCH_DATES": "",
                        "COMMENT": "",
                        "NOTE_TEXT": "",
                    }
                )
                kept_rows += 1
                min_date = event_date if min_date is None or event_date < min_date else min_date
                max_date = event_date if max_date is None or event_date > max_date else max_date

        summary["inputs"].append(
            {
                "path": str(path),
                "input_rows": input_rows,
                "kept_rows": kept_rows,
            }
        )

    summary["row_count"] = len(output_rows)
    summary["date_min"] = min_date.isoformat() if min_date else None
    summary["date_max"] = max_date.isoformat() if max_date else None
    return output_rows, summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a manual, de-identified Phase I UKG CSV for the weekly pipeline.")
    parser.add_argument("--input", action="append", required=True, help="Raw UKG CSV input path. Pass multiple times for multi-week builds.")
    parser.add_argument("--output", required=True, help="Output CSV path.")
    args = parser.parse_args()

    input_paths = [Path(value).resolve() for value in args.input]
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows, summary = load_rows(input_paths)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_HEADERS)
        writer.writeheader()
        writer.writerows(rows)

    summary["output"] = str(output_path)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
