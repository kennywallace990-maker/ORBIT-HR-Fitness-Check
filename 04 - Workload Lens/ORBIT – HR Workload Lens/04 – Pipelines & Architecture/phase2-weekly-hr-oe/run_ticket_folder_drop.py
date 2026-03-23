from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path


def latest_completed_saturday(pull_date: dt.date) -> dt.date:
    days_since_saturday = (pull_date.weekday() - 5) % 7
    return pull_date - dt.timedelta(days=days_since_saturday)


def build_default_weeks(pull_date: dt.date) -> tuple[dt.date, dt.date, dt.date, dt.date]:
    week9_end = latest_completed_saturday(pull_date)
    week9_start = week9_end - dt.timedelta(days=6)
    week8_end = week9_start - dt.timedelta(days=1)
    week8_start = week8_end - dt.timedelta(days=6)
    return week8_start, week8_end, week9_start, week9_end


def run_command(command: list[str]) -> dict[str, object]:
    completed = subprocess.run(command, capture_output=True, text=True)
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Folder-drop runner for weekly BI opened/closed ticket reports."
    )
    parser.add_argument("--bi-weekly-dir", required=True)
    parser.add_argument("--pull-date", default=dt.date.today().isoformat())
    parser.add_argument("--week8-start")
    parser.add_argument("--week8-end")
    parser.add_argument("--week9-start")
    parser.add_argument("--week9-end")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--label")
    parser.add_argument("--state-file")
    args = parser.parse_args()

    pull_date = dt.date.fromisoformat(args.pull_date)
    default_week8_start, default_week8_end, default_week9_start, default_week9_end = build_default_weeks(pull_date)
    week8_start = dt.date.fromisoformat(args.week8_start) if args.week8_start else default_week8_start
    week8_end = dt.date.fromisoformat(args.week8_end) if args.week8_end else default_week8_end
    week9_start = dt.date.fromisoformat(args.week9_start) if args.week9_start else default_week9_start
    week9_end = dt.date.fromisoformat(args.week9_end) if args.week9_end else default_week9_end

    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    state_file = Path(args.state_file).resolve() if args.state_file else out_dir / "ticket_folder_drop_state.json"
    label = args.label or f"ticket_bi_drop_{week9_start.isoformat()}_to_{week9_end.isoformat()}"
    run_key = f"{label}|{pull_date.isoformat()}"

    if state_file.exists():
        try:
            existing_state = json.loads(state_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing_state = {}
        if existing_state.get("last_successful_run_key") == run_key:
            payload = {
                "pass": True,
                "skipped": True,
                "reason": "already_processed",
                "run_key": run_key,
                "state_file": str(state_file),
            }
            print(json.dumps(payload))
            return 0

    script_dir = Path(__file__).resolve().parent
    command = [
        sys.executable,
        str(script_dir / "run_ticket_prep_pipeline.py"),
        "--bi-weekly-dir",
        str(Path(args.bi_weekly_dir).resolve()),
        "--pull-date",
        pull_date.isoformat(),
        "--week8-start",
        week8_start.isoformat(),
        "--week8-end",
        week8_end.isoformat(),
        "--week9-start",
        week9_start.isoformat(),
        "--week9-end",
        week9_end.isoformat(),
        "--out-dir",
        str(out_dir),
        "--label",
        label,
    ]
    result = run_command(command)

    payload: dict[str, object]
    try:
        payload = json.loads(result["stdout"]) if result["stdout"] else {}
    except json.JSONDecodeError:
        payload = {}

    if result["returncode"] == 0:
        state = {
            "last_successful_run_key": run_key,
            "last_successful_pull_date": pull_date.isoformat(),
            "last_successful_label": label,
            "last_successful_completed_at_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        }
        state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")

    final_payload = {
        "pass": result["returncode"] == 0,
        "run_key": run_key,
        "state_file": str(state_file),
        "command": command,
        "stdout_json": payload if payload else None,
        "stderr": result["stderr"] or None,
    }
    print(json.dumps(final_payload))
    return result["returncode"]


if __name__ == "__main__":
    raise SystemExit(main())
