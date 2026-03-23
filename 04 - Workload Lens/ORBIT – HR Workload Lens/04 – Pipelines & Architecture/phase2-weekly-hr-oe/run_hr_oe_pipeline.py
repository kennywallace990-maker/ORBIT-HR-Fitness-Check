from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path


PHASE2_SERVICE_SPECS = [
    {"service_name": "Attendance Inquiry", "tokens": ["attendance", "inquiry"]},
    {"service_name": "CS Time and Attendance", "tokens": ["cs", "time", "attendance"]},
    {"service_name": "FC General Inquiry", "tokens": ["fc", "general", "inquiry"]},
    {"service_name": "Timesheet Inquiry", "tokens": ["timesheet", "inquiry"]},
]


def calendar_week_label(week_start: dt.date) -> str:
    return f"Week {int(week_start.strftime('%U'))}"


def run_step(command: list[str]) -> dict[str, object]:
    completed = subprocess.run(command, capture_output=True, text=True)
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def write_chat_handoff(
    path: Path,
    summary: dict[str, object],
    week8_start: str,
    week8_end: str,
    week9_start: str,
    week9_end: str,
) -> None:
    week8_label = calendar_week_label(dt.date.fromisoformat(week8_start))
    week9_label = calendar_week_label(dt.date.fromisoformat(week9_start))
    outputs = summary.get("outputs", {})
    metrics_path = Path(outputs["metrics"]) if isinstance(outputs, dict) and "metrics" in outputs else None
    key_lines = []
    if metrics_path and metrics_path.exists():
        try:
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            p1w9 = metrics["phase1"]["week9"]
            p2w9 = metrics["phase2"]["week9"]
            cross = metrics["cross_phase"]
            key_lines = [
                f"- Phase I {week9_label} UKG touches: {p1w9['total_actions']}",
                f"- Phase I {week9_label} UKG rework touches: {p1w9['rework_actions']}",
                f"- Phase II {week9_label} ticket count: {p2w9['total_tickets']}",
                f"- Ticket visibility vs all UKG touches: {cross['phase2_ticket_visibility_vs_phase1_all_work_pct']}%",
                f"- Ticket visibility vs UKG rework touches: {cross['phase2_ticket_visibility_vs_phase1_rework_pct']}%",
            ]
        except Exception:
            key_lines = []

    lines = [
        "# Chat Handoff",
        "",
        "## Status",
        f"- Pipeline pass: {summary.get('pass')}",
    ]
    if summary.get("error"):
        lines.append(f"- Error: {summary.get('error')}")
    lines.append(f"- Allow partial Phase I: {summary.get('allow_partial_phase1', False)}")
    phase1_date_check = summary.get("phase1_date_check")
    if isinstance(phase1_date_check, dict):
        lines.append(
            "- Phase I required two-week range covered: "
            f"{phase1_date_check['required_trailing_two_week_window']['range_covered']}"
        )
    lines.extend([
        "",
        "## Week Lock",
        f"- {week8_label}: {week8_start} to {week8_end} (Sunday to Saturday)",
        f"- {week9_label}: {week9_start} to {week9_end} (Sunday to Saturday)",
        "",
        "## Outputs",
        f"- Run summary: {summary.get('run_summary_path', 'n/a')}",
    ])
    if isinstance(outputs, dict):
        for key in ("markdown", "metrics", "math_validation", "quality_validation"):
            if key in outputs:
                lines.append(f"- {key}: {outputs[key]}")
    lines.append("")
    lines.append("## Key Metrics")
    if key_lines:
        lines.extend(key_lines)
    else:
        lines.append("- Metrics not available due to earlier pipeline failure.")
    lines.append("")
    lines.append("## Open Items")
    lines.append("- Confirm final primary dark-work KPI definition for leadership reporting.")
    lines.append("- Confirm SLA source fields for Supplemental Q1 answer automation.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def normalize_name(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def score_filename(file_name: str, tokens: list[str]) -> int:
    normalized = normalize_name(file_name)
    return sum(1 for token in tokens if token in normalized)


def discover_phase2_csvs(phase2_dir: Path) -> list[Path]:
    candidates = sorted(phase2_dir.glob("*.csv"))
    if not candidates:
        raise FileNotFoundError(f"No CSV files found in Phase II directory: {phase2_dir}")
    resolved: list[Path] = []
    used_paths: set[Path] = set()
    for spec in PHASE2_SERVICE_SPECS:
        ranked = sorted(
            candidates,
            key=lambda path: (
                score_filename(path.name, spec["tokens"]) == len(spec["tokens"]),
                score_filename(path.name, spec["tokens"]),
                normalize_name(spec["service_name"]) in normalize_name(path.name),
                path.name.lower(),
            ),
            reverse=True,
        )
        best = next(
            (
                path
                for path in ranked
                if score_filename(path.name, spec["tokens"]) == len(spec["tokens"]) and path.resolve() not in used_paths
            ),
            None,
        )
        if best is None:
            raise FileNotFoundError(
                f"Could not auto-discover Phase II CSV for {spec['service_name']} in {phase2_dir}. "
                f"Expected a CSV filename containing all tokens: {spec['tokens']}"
            )
        resolved.append(best.resolve())
        used_paths.add(best.resolve())
    return resolved


def discover_phase1_csv(phase1_dir: Path) -> Path:
    candidates = sorted(phase1_dir.glob("*.csv"))
    if not candidates:
        raise FileNotFoundError(f"No CSV files found in Phase I directory: {phase1_dir}")
    ranked = sorted(
        candidates,
        key=lambda path: (score_filename(path.name, ["snowflake", "ukg"]), path.name.lower()),
        reverse=True,
    )
    return ranked[0].resolve()


def parse_phase1_date(value: str) -> dt.date | None:
    text = (value or "").strip()
    if not text:
        return None
    text = text.replace("\ufeff", "").replace("\u200f", "").replace("\u200e", "")
    for fmt in ("%m/%d/%Y", "%m/%d/%Y %H:%M:%S", "%m/%d/%Y %H:%M", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
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


def build_date_sequence(start: dt.date, end: dt.date) -> list[dt.date]:
    dates = []
    current = start
    while current <= end:
        dates.append(current)
        current += dt.timedelta(days=1)
    return dates


def latest_completed_saturday(pull_date: dt.date) -> dt.date:
    days_since_saturday = (pull_date.weekday() - 5) % 7
    return pull_date - dt.timedelta(days=days_since_saturday)


def build_default_weeks(pull_date: dt.date) -> tuple[dt.date, dt.date, dt.date, dt.date]:
    week9_end = latest_completed_saturday(pull_date)
    week9_start = week9_end - dt.timedelta(days=6)
    week8_end = week9_start - dt.timedelta(days=1)
    week8_start = week8_end - dt.timedelta(days=6)
    return week8_start, week8_end, week9_start, week9_end


def validate_phase1_csv_dates(
    phase1_csv: Path,
    week8_start: dt.date,
    week8_end: dt.date,
    week9_start: dt.date,
    week9_end: dt.date,
    pull_date: dt.date,
) -> dict[str, object]:
    dates_present: set[dt.date] = set()
    rows = 0
    with phase1_csv.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        reader = csv.DictReader(handle)
        for raw_row in reader:
            rows += 1
            normalized = {normalize_name(key): (value or "").strip() for key, value in raw_row.items() if key is not None}
            raw_date = normalized.get("entity event date") or normalized.get("report week") or ""
            parsed = parse_phase1_date(raw_date)
            if parsed:
                dates_present.add(parsed)

    week8_missing = [date.isoformat() for date in build_date_sequence(week8_start, week8_end) if date not in dates_present]
    week9_missing = [date.isoformat() for date in build_date_sequence(week9_start, week9_end) if date not in dates_present]

    required_week9_end = latest_completed_saturday(pull_date)
    required_week9_start = required_week9_end - dt.timedelta(days=6)
    required_week8_end = required_week9_start - dt.timedelta(days=1)
    required_week8_start = required_week8_end - dt.timedelta(days=6)
    required_dates = build_date_sequence(required_week8_start, required_week9_end)
    required_missing = [date.isoformat() for date in required_dates if date not in dates_present]

    all_dates_sorted = sorted(dates_present)
    return {
        "csv": str(phase1_csv),
        "row_count": rows,
        "min_date": all_dates_sorted[0].isoformat() if all_dates_sorted else None,
        "max_date": all_dates_sorted[-1].isoformat() if all_dates_sorted else None,
        "locked_window_missing_dates": {"week8": week8_missing, "week9": week9_missing},
        "required_trailing_two_week_window": {
            "pull_date": pull_date.isoformat(),
            "required_week8_start": required_week8_start.isoformat(),
            "required_week8_end": required_week8_end.isoformat(),
            "required_week9_start": required_week9_start.isoformat(),
            "required_week9_end": required_week9_end.isoformat(),
            "missing_dates": required_missing,
            "range_covered": len(required_missing) == 0,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run HR Operational Excellence weekly pipeline.")
    parser.add_argument("--phase1-csv")
    parser.add_argument("--phase1-dir", default="Phase I\\Phase I CSV")
    parser.add_argument("--phase2-csv", action="append")
    parser.add_argument("--phase2-dir")
    parser.add_argument("--phase2-bi-dir")
    parser.add_argument("--pull-date", default=dt.date.today().isoformat())
    parser.add_argument("--allow-partial-phase1", action="store_true")
    parser.add_argument("--week8-start")
    parser.add_argument("--week8-end")
    parser.add_argument("--week9-start")
    parser.add_argument("--week9-end")
    parser.add_argument("--out-dir", default="Phase II/output")
    parser.add_argument("--label", default="wk9_2026_02_22_to_2026_02_28")
    args = parser.parse_args()

    pull_date = dt.date.fromisoformat(args.pull_date)
    default_week8_start, default_week8_end, default_week9_start, default_week9_end = build_default_weeks(pull_date)
    week8_start = dt.date.fromisoformat(args.week8_start) if args.week8_start else default_week8_start
    week8_end = dt.date.fromisoformat(args.week8_end) if args.week8_end else default_week8_end
    week9_start = dt.date.fromisoformat(args.week9_start) if args.week9_start else default_week9_start
    week9_end = dt.date.fromisoformat(args.week9_end) if args.week9_end else default_week9_end
    week8_start_str = week8_start.isoformat()
    week8_end_str = week8_end.isoformat()
    week9_start_str = week9_start.isoformat()
    week9_end_str = week9_end.isoformat()

    script_dir = Path(__file__).resolve().parent
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    markdown_path = out_dir / f"hr_oe_answer_pack_{args.label}.md"
    metrics_path = out_dir / f"hr_oe_metrics_{args.label}.json"
    math_path = out_dir / f"hr_oe_math_validation_{args.label}.json"
    quality_path = out_dir / f"hr_oe_quality_validation_{args.label}.json"
    run_summary_path = out_dir / f"hr_oe_pipeline_run_{args.label}.json"
    handoff_path = out_dir / f"hr_oe_chat_handoff_{args.label}.md"

    phase2_input_mode = "service_csvs"
    phase2_source_manifest = None
    try:
        phase1_csv = Path(args.phase1_csv).resolve() if args.phase1_csv else discover_phase1_csv(Path(args.phase1_dir).resolve())
        if not phase1_csv.exists():
            raise FileNotFoundError(f"Phase I CSV not found: {phase1_csv}")
        phase1_date_check = validate_phase1_csv_dates(phase1_csv, week8_start, week8_end, week9_start, week9_end, pull_date)
        if not phase1_date_check["required_trailing_two_week_window"]["range_covered"]:
            if not args.allow_partial_phase1:
                raise ValueError(
                    "Phase I CSV does not cover the required trailing two-week window. "
                    f"Missing dates: {phase1_date_check['required_trailing_two_week_window']['missing_dates']}"
                )
        if args.phase2_bi_dir:
            phase2_input_mode = "bi_weekly_two_report_folder"
            intake_out_dir = out_dir / f"_phase2_bi_inputs_{args.label}"
            intake_cmd = [
                sys.executable,
                str(script_dir / "build_ticket_bi_service_inputs.py"),
                "--bi-weekly-dir",
                str(Path(args.phase2_bi_dir).resolve()),
                "--pull-date",
                pull_date.isoformat(),
                "--week8-start",
                week8_start_str,
                "--week8-end",
                week8_end_str,
                "--week9-start",
                week9_start_str,
                "--week9-end",
                week9_end_str,
                "--out-dir",
                str(intake_out_dir),
            ]
            intake_result = run_step(intake_cmd)
            if intake_result["returncode"] != 0:
                raise ValueError(
                    "Phase II BI intake failed. "
                    f"stderr={intake_result['stderr'] or 'n/a'} "
                    f"stdout={intake_result['stdout'] or 'n/a'}"
                )
            try:
                intake_payload = json.loads(intake_result["stdout"])
            except json.JSONDecodeError as exc:
                raise ValueError(f"Phase II BI intake did not return valid JSON: {exc}") from exc
            phase2_csvs = [Path(item["path"]).resolve() for item in intake_payload.get("service_csvs", [])]
            phase2_source_manifest = intake_payload.get("manifest_json")
            if len(phase2_csvs) != len(PHASE2_SERVICE_SPECS):
                raise FileNotFoundError(
                    "Phase II BI intake did not generate all expected service CSVs."
                )
        elif args.phase2_dir:
            phase2_csvs = discover_phase2_csvs(Path(args.phase2_dir).resolve())
        else:
            if not args.phase2_csv:
                raise FileNotFoundError("No Phase II CSVs supplied. Pass --phase2-dir or one or more --phase2-csv values.")
            phase2_csvs = [Path(path).resolve() for path in args.phase2_csv]
        for phase2_csv in phase2_csvs:
            if not phase2_csv.exists():
                raise FileNotFoundError(f"Phase II CSV not found: {phase2_csv}")
    except Exception as exc:
        summary = {
            "pass": False,
            "failed_step": "input_validation",
            "error": str(exc),
            "allow_partial_phase1": args.allow_partial_phase1,
            "phase2_input_mode": phase2_input_mode,
            "phase2_source_manifest": phase2_source_manifest,
            "phase1_date_check": phase1_date_check if 'phase1_date_check' in locals() else None,
            "outputs": {},
            "run_summary_path": str(run_summary_path),
            "generated_at_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        }
        run_summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        write_chat_handoff(
            handoff_path,
            summary,
            week8_start_str,
            week8_end_str,
            week9_start_str,
            week9_end_str,
        )
        print(json.dumps(summary))
        return 1

    analysis_cmd = [
        sys.executable,
        str(script_dir / "hr_oe_weekly_analysis.py"),
        "--phase1-csv",
        str(phase1_csv),
        "--week8-start",
        week8_start_str,
        "--week8-end",
        week8_end_str,
        "--week9-start",
        week9_start_str,
        "--week9-end",
        week9_end_str,
        "--output-markdown",
        str(markdown_path),
        "--output-metrics",
        str(metrics_path),
    ]
    for phase2 in phase2_csvs:
        analysis_cmd.extend(["--phase2-csv", str(phase2)])

    math_cmd = [
        sys.executable,
        str(script_dir / "hr_oe_math_validator.py"),
        "--phase1-csv",
        str(phase1_csv),
        "--metrics-json",
        str(metrics_path),
        "--output-json",
        str(math_path),
        "--week8-start",
        week8_start_str,
        "--week8-end",
        week8_end_str,
        "--week9-start",
        week9_start_str,
        "--week9-end",
        week9_end_str,
    ]
    for phase2 in phase2_csvs:
        math_cmd.extend(["--phase2-csv", str(phase2)])

    quality_cmd = [
        sys.executable,
        str(script_dir / "hr_oe_quality_validator.py"),
        "--markdown",
        str(markdown_path),
        "--output-json",
        str(quality_path),
        "--week8-start",
        week8_start_str,
        "--week8-end",
        week8_end_str,
        "--week9-start",
        week9_start_str,
        "--week9-end",
        week9_end_str,
    ]

    steps = []
    analysis_result = run_step(analysis_cmd)
    steps.append({"step": "analysis", **analysis_result})
    if analysis_result["returncode"] != 0:
        summary = {
            "pass": False,
            "failed_step": "analysis",
            "steps": steps,
            "phase1_csv": str(phase1_csv),
            "phase2_csvs": [str(path) for path in phase2_csvs],
            "allow_partial_phase1": args.allow_partial_phase1,
            "phase2_input_mode": phase2_input_mode,
            "phase2_source_manifest": phase2_source_manifest,
            "phase1_date_check": phase1_date_check,
            "outputs": {},
            "run_summary_path": str(run_summary_path),
            "generated_at_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        }
        run_summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        write_chat_handoff(
            handoff_path,
            summary,
            week8_start_str,
            week8_end_str,
            week9_start_str,
            week9_end_str,
        )
        print(json.dumps(summary))
        return 1

    math_result = run_step(math_cmd)
    steps.append({"step": "math_validation", **math_result})

    quality_result = run_step(quality_cmd)
    steps.append({"step": "quality_validation", **quality_result})

    passed = math_result["returncode"] == 0 and quality_result["returncode"] == 0
    summary = {
        "pass": passed,
        "steps": steps,
        "phase1_csv": str(phase1_csv),
        "phase2_csvs": [str(path) for path in phase2_csvs],
        "allow_partial_phase1": args.allow_partial_phase1,
        "phase2_input_mode": phase2_input_mode,
        "phase2_source_manifest": phase2_source_manifest,
        "phase1_date_check": phase1_date_check,
        "outputs": {
            "markdown": str(markdown_path),
            "metrics": str(metrics_path),
            "math_validation": str(math_path),
            "quality_validation": str(quality_path),
        },
        "run_summary_path": str(run_summary_path),
        "generated_at_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
    }
    run_summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_chat_handoff(
        handoff_path,
        summary,
        week8_start_str,
        week8_end_str,
        week9_start_str,
        week9_end_str,
    )
    print(json.dumps(summary))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
