from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path


SERVICE_SPECS = [
    {
        "service_name": "Attendance Inquiry",
        "arg_name": "attendance_csv",
        "tokens": ["attendance", "inquiry"],
        "expected_hr_service_tokens": ["attendance", "inquiry"],
    },
    {
        "service_name": "CS Time and Attendance",
        "arg_name": "cs_time_attendance_csv",
        "tokens": ["cs", "time", "attendance"],
        "expected_hr_service_tokens": ["time", "attendance"],
    },
    {
        "service_name": "FC General Inquiry",
        "arg_name": "fc_general_inquiry_csv",
        "tokens": ["fc", "general", "inquiry"],
        "expected_hr_service_tokens": ["general", "inquiry"],
    },
    {
        "service_name": "Timesheet Inquiry",
        "arg_name": "timesheet_inquiry_csv",
        "tokens": ["timesheet", "inquiry"],
        "expected_hr_service_tokens": ["timesheet", "inquiry"],
    },
]


def run_command(command: list[str]) -> dict[str, object]:
    completed = subprocess.run(command, capture_output=True, text=True)
    parsed_stdout = None
    stdout_text = completed.stdout.strip()
    if stdout_text:
        try:
            parsed_stdout = json.loads(stdout_text)
        except json.JSONDecodeError:
            parsed_stdout = None
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": stdout_text,
        "stderr": completed.stderr.strip(),
        "parsed_stdout": parsed_stdout,
    }


def write_chat_handoff(path: Path, manifest: dict[str, object], rollup: dict[str, object]) -> None:
    lines = [
        "# Ticket Prep Chat Handoff",
        "",
        "## Status",
        f"- Pipeline pass: {manifest.get('pass')}",
        f"- Pull date: {manifest.get('pull_date')}",
        "",
        "## Week Lock",
        f"- Week 8: {manifest['week_lock']['week8_start']} to {manifest['week_lock']['week8_end']}",
        f"- Week 9: {manifest['week_lock']['week9_start']} to {manifest['week_lock']['week9_end']}",
        "",
        "## Services",
    ]
    for service in rollup.get("services", []):
        coverage = service.get("date_coverage", {})
        lines.append(
            f"- {service['service_name']}: Week9={service['week9_ticket_count']}, "
            f"WoW={service['week9_vs_week8_delta']}, "
            f"required_range_covered={coverage.get('required_range_covered')}"
        )
    lines.append("")
    lines.append("## Coverage Warnings")
    warnings = manifest.get("coverage_warnings", [])
    if warnings:
        for warning in warnings:
            lines.append(f"- {warning['service_name']} | {warning['type']}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Output Files")
    lines.append(f"- Manifest: {manifest.get('manifest_path')}")
    lines.append(f"- LLM rollup: {manifest.get('rollup_path')}")
    path.write_text("\n".join(lines), encoding="utf-8")


def normalize_name(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def score_filename(file_name: str, tokens: list[str]) -> int:
    normalized = normalize_name(file_name)
    return sum(1 for token in tokens if token in normalized)


def discover_input_files(phase2_dir: Path) -> dict[str, Path]:
    candidates = sorted(phase2_dir.glob("*.csv"))
    resolved: dict[str, Path] = {}
    for spec in SERVICE_SPECS:
        best_file: Path | None = None
        best_score = -1
        for file_path in candidates:
            score = score_filename(file_path.name, spec["tokens"])
            if score > best_score:
                best_score = score
                best_file = file_path
        if best_file is None or best_score <= 0:
            raise FileNotFoundError(
                f"Could not auto-discover CSV for service '{spec['service_name']}' in {phase2_dir}. "
                f"Expected tokens: {spec['tokens']}"
            )
        resolved[spec["arg_name"]] = best_file.resolve()
    return resolved


def hr_service_matches_expected(summary_data: dict[str, object], expected_tokens: list[str]) -> tuple[bool, str | None]:
    hr_services = summary_data.get("data_quality", {}).get("hr_service_values", {})
    if not hr_services:
        return True, None
    top_service = max(hr_services.items(), key=lambda item: item[1])[0]
    normalized = normalize_name(top_service)
    ok = all(token in normalized for token in expected_tokens)
    return ok, top_service


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ticket prep and classification per EPA CSV without combining datasets.")
    parser.add_argument("--attendance-csv")
    parser.add_argument("--cs-time-attendance-csv")
    parser.add_argument("--timesheet-inquiry-csv")
    parser.add_argument("--fc-general-inquiry-csv")
    parser.add_argument("--phase2-dir", help="Optional folder for auto-discovery of the four CSVs.")
    parser.add_argument("--week8-start", default="2026-02-15")
    parser.add_argument("--week8-end", default="2026-02-21")
    parser.add_argument("--week9-start", default="2026-02-22")
    parser.add_argument("--week9-end", default="2026-02-28")
    parser.add_argument("--pull-date", default=dt.date.today().isoformat())
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--label", default="wk9_sun_sat")
    args = parser.parse_args()

    week8_start = dt.date.fromisoformat(args.week8_start)
    week8_end = dt.date.fromisoformat(args.week8_end)
    week9_start = dt.date.fromisoformat(args.week9_start)
    week9_end = dt.date.fromisoformat(args.week9_end)
    pull_date = dt.date.fromisoformat(args.pull_date)

    out_root = Path(args.out_dir).resolve()
    run_dir = out_root / args.label
    run_dir.mkdir(parents=True, exist_ok=True)
    script_dir = Path(__file__).resolve().parent

    explicit_inputs = {
        "attendance_csv": args.attendance_csv,
        "cs_time_attendance_csv": args.cs_time_attendance_csv,
        "timesheet_inquiry_csv": args.timesheet_inquiry_csv,
        "fc_general_inquiry_csv": args.fc_general_inquiry_csv,
    }
    if args.phase2_dir:
        phase2_dir = Path(args.phase2_dir).resolve()
        service_inputs = discover_input_files(phase2_dir)
    else:
        missing = [key for key, value in explicit_inputs.items() if not value]
        if missing:
            raise SystemExit(
                "Missing required CSV args. Provide all four explicit CSV paths or pass --phase2-dir for auto-discovery. "
                f"Missing: {missing}"
            )
        service_inputs = {key: Path(value).resolve() for key, value in explicit_inputs.items()}

    service_runs: list[dict[str, object]] = []
    prep_script = script_dir / "ticket_dataset_prepare.py"
    for spec in SERVICE_SPECS:
        service_name = spec["service_name"]
        arg_name = spec["arg_name"]
        source_path = service_inputs[arg_name]
        service_dir = run_dir / service_name.lower().replace(" ", "_")
        service_dir.mkdir(parents=True, exist_ok=True)
        command = [
            sys.executable,
            str(prep_script),
            "--input-csv",
            str(source_path),
            "--service-name",
            service_name,
            "--week8-start",
            week8_start.isoformat(),
            "--week8-end",
            week8_end.isoformat(),
            "--week9-start",
            week9_start.isoformat(),
            "--week9-end",
            week9_end.isoformat(),
            "--pull-date",
            pull_date.isoformat(),
            "--out-dir",
            str(service_dir),
        ]
        result = run_command(command)
        service_runs.append(
            {
                "service_name": service_name,
                "input_csv": str(source_path),
                "step_result": result,
            }
        )
        if result["returncode"] != 0:
            break

    overall_pass = all(run["step_result"]["returncode"] == 0 for run in service_runs)
    manifest = {
        "pass": overall_pass,
        "generated_at_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "week_lock": {
            "week8_start": week8_start.isoformat(),
            "week8_end": week8_end.isoformat(),
            "week9_start": week9_start.isoformat(),
            "week9_end": week9_end.isoformat(),
            "definition": "Sunday through Saturday",
        },
        "pull_date": pull_date.isoformat(),
        "run_dir": str(run_dir),
        "services": [],
        "coverage_warnings": [],
    }

    for run in service_runs:
        parsed = run["step_result"]["parsed_stdout"] if run["step_result"]["parsed_stdout"] else {}
        manifest["services"].append(
            {
                "service_name": run["service_name"],
                "input_csv": run["input_csv"],
                "returncode": run["step_result"]["returncode"],
                "stderr": run["step_result"]["stderr"],
                "outputs": parsed,
            }
        )

    # Build a compact non-merged rollup for downstream LLM orchestration.
    rollup_services = []
    coverage_failures = 0
    for service in manifest["services"]:
        outputs = service["outputs"]
        summary_path = outputs.get("summary_json") if isinstance(outputs, dict) else None
        llm_path = outputs.get("llm_compact_json") if isinstance(outputs, dict) else None
        if not summary_path or not llm_path:
            continue
        summary_data = json.loads(Path(summary_path).read_text(encoding="utf-8"))
        llm_data = json.loads(Path(llm_path).read_text(encoding="utf-8"))
        expected_tokens = next(spec["expected_hr_service_tokens"] for spec in SERVICE_SPECS if spec["service_name"] == service["service_name"])
        service_match, top_service = hr_service_matches_expected(summary_data, expected_tokens)
        if not service_match:
            coverage_failures += 1
            manifest["coverage_warnings"].append(
                {
                    "service_name": service["service_name"],
                    "type": "hr_service_mismatch",
                    "message": "Input file Hr Service values do not match the expected service.",
                    "expected_tokens": expected_tokens,
                    "top_hr_service_value": top_service,
                }
            )
        date_coverage = summary_data.get("date_coverage", {})
        required_window = date_coverage.get("required_trailing_two_week_window", {})
        locked_missing = date_coverage.get("locked_window_missing_dates", {})
        week8_missing = locked_missing.get("week8", [])
        week9_missing = locked_missing.get("week9", [])
        range_covered = bool(required_window.get("range_covered", False))
        if not range_covered:
            coverage_failures += 1
            manifest["coverage_warnings"].append(
                {
                    "service_name": service["service_name"],
                    "type": "required_range_not_covered",
                    "message": "Input file does not cover the full required trailing two-week range from pull date.",
                    "required_window": required_window,
                    "min_opened_date": date_coverage.get("min_opened_date"),
                    "max_opened_date": date_coverage.get("max_opened_date"),
                }
            )
        if week8_missing or week9_missing:
            manifest["coverage_warnings"].append(
                {
                    "service_name": service["service_name"],
                    "type": "missing_dates_within_locked_window",
                    "week8_missing_dates": week8_missing,
                    "week9_missing_dates": week9_missing,
                }
            )
        rollup_services.append(
            {
                "service_name": service["service_name"],
                "summary_json": summary_path,
                "llm_compact_json": llm_path,
                "week9_ticket_count": summary_data["week9"]["ticket_count"],
                "week9_vs_week8_delta": llm_data["kpis"]["week9_vs_week8_delta"],
                "top_category_week9": llm_data["top_categories_week9"][0] if llm_data["top_categories_week9"] else None,
                "date_coverage": {
                    "locked_window_coverage_pct": date_coverage.get("locked_window_coverage_pct"),
                    "required_range_covered": range_covered,
                    "required_window_coverage_pct": required_window.get("coverage_pct"),
                    "week8_missing_dates_count": len(week8_missing),
                    "week9_missing_dates_count": len(week9_missing),
                },
                "service_match": service_match,
                "top_hr_service_value": top_service,
            }
        )

    if coverage_failures > 0:
        overall_pass = False
        manifest["pass"] = False

    rollup = {
        "pass": overall_pass,
        "note": "No raw rows combined. Each service stays isolated and is referenced separately.",
        "pull_date": pull_date.isoformat(),
        "services": rollup_services,
    }

    manifest_path = run_dir / "ticket_prep_manifest.json"
    rollup_path = run_dir / "ticket_prep_rollup_for_llm.json"
    handoff_path = run_dir / "ticket_prep_chat_handoff.md"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    rollup_path.write_text(json.dumps(rollup, indent=2), encoding="utf-8")
    manifest["manifest_path"] = str(manifest_path)
    manifest["rollup_path"] = str(rollup_path)
    write_chat_handoff(handoff_path, manifest, rollup)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "pass": overall_pass,
                "manifest_json": str(manifest_path),
                "rollup_json": str(rollup_path),
                "handoff_md": str(handoff_path),
            }
        )
    )
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
