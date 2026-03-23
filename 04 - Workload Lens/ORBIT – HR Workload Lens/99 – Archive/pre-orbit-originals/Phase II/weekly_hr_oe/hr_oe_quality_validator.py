from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import re


def contains_all(text: str, required_snippets: list[str]) -> list[str]:
    missing = []
    for snippet in required_snippets:
        if snippet not in text:
            missing.append(snippet)
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(description="Writing quality validator for HR OE weekly pack.")
    parser.add_argument("--markdown", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--week8-start", default="2026-02-15")
    parser.add_argument("--week8-end", default="2026-02-21")
    parser.add_argument("--week9-start", default="2026-02-22")
    parser.add_argument("--week9-end", default="2026-02-28")
    args = parser.parse_args()

    md_path = Path(args.markdown).resolve()
    output_path = Path(args.output_json).resolve()
    text = md_path.read_text(encoding="utf-8")

    required_headings = [
        "# HR Operational Excellence Answer Pack",
        "## Week Lock",
        "## Inputs Used",
        "## Week 8 vs Week 9 Snapshot",
        "## HR Operational Excellence Answers",
        "### Q1",
        "### Q2",
        "### Q3",
        "## Cross Phase Coverage Proxy",
        "## Data Gaps",
    ]
    missing_headings = contains_all(text, required_headings)

    week_lock_required = [
        f"Week 8: {args.week8_start} to {args.week8_end} (Sunday to Saturday)",
        f"Week 9: {args.week9_start} to {args.week9_end} (Sunday to Saturday)",
    ]
    missing_week_lock = contains_all(text, week_lock_required)

    prohibited_markers = ["TODO", "FIXME", "<fill", "??"]
    found_prohibited = [marker for marker in prohibited_markers if marker in text]

    question_sentence_checks = {
        "Q1": "What is our plan to establish accurate SLA commitments and measurements?",
        "Q2": "Which ticket types account for the volume change?",
        "Q3": "What is the biggest remaining opportunity, using existing process and technology, to reduce volume?",
    }
    missing_questions = [qid for qid, sentence in question_sentence_checks.items() if sentence not in text]

    has_table_pattern = bool(re.search(r"\| Metric \| Week 8 \| Week 9 \| Delta \|", text))
    long_lines = [idx + 1 for idx, line in enumerate(text.splitlines()) if len(line) > 260]

    errors: list[str] = []
    warnings: list[str] = []

    if missing_headings:
        errors.append(f"Missing required headings: {missing_headings}")
    if missing_week_lock:
        errors.append(f"Missing explicit week lock statements: {missing_week_lock}")
    if missing_questions:
        errors.append(f"Missing required question prompts: {missing_questions}")
    if found_prohibited:
        errors.append(f"Found prohibited placeholders: {found_prohibited}")
    if not has_table_pattern:
        errors.append("Missing required Week 8 vs Week 9 snapshot table.")
    if long_lines:
        warnings.append(f"Found long lines over 260 characters at lines: {long_lines[:20]}")

    passed = len(errors) == 0
    result = {
        "pass": passed,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "validated_at_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
