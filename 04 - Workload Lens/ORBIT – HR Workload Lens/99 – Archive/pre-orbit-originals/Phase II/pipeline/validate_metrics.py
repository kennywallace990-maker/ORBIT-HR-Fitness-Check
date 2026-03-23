"""
Validate key metrics emitted by the weekly Workload Lens report.

Usage:
  python validate_metrics.py
  python validate_metrics.py --week 2026-03-01

The validator recomputes metrics from the source CSVs using the same pipeline
logic as run_weekly.py, then compares those results to the generated classified
ticket export and the HTML report for the requested week label.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime

from run_weekly import (
    CSV_DIR,
    OUTPUT_DIR,
    SELF_SERVICE_POTENTIAL_ASSUMPTION,
    SERVICES,
    assign_weeks,
    classify_all,
    compute_metrics,
    detect_weeks,
    load_csvs,
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--week",
        help="Week label matching the generated files, e.g. 2026-03-01. Defaults to the current detected week.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the validation payload as JSON only.",
    )
    return parser.parse_args()


def classify_source_data():
    tickets, files_loaded = load_csvs(CSV_DIR)
    prior_start, current_start = detect_weeks(tickets)
    assign_weeks(tickets, prior_start, current_start)
    in_scope = [t for t in tickets if t.get("week") in ("prior", "current")]
    classify_all(in_scope)
    metrics = compute_metrics(in_scope, prior_start, current_start)
    return {
        "tickets": in_scope,
        "files_loaded": files_loaded,
        "prior_start": prior_start,
        "current_start": current_start,
        "metrics": metrics,
    }


def build_expected_summary(metrics):
    total = metrics["total_all"]
    ss_total = metrics["class_counts"].get("Self Service Eligible", {}).get("total", 0)
    class_breakdown = {}
    for name, data in metrics["class_counts"].items():
        count = data.get("total", 0)
        class_breakdown[name] = {
            "count": count,
            "pct": round((count / total * 100), 1) if total else 0.0,
        }

    service_breakdown = {}
    for service in SERVICES:
        total_service = sum(metrics["svc_counts"].get(service, {}).values())
        ss_service = metrics["svc_class"].get(service, {}).get("Self Service Eligible", {})
        ss_total_service = ss_service.get("prior", 0) + ss_service.get("current", 0)
        service_breakdown[service] = {
            "total": total_service,
            "self_service_count": ss_total_service,
            "self_service_pct": round((ss_total_service / total_service * 100), 1) if total_service else 0.0,
        }

    return {
        "total_tickets": total,
        "observed_self_service_count": ss_total,
        "observed_self_service_pct": round((ss_total / total * 100), 1) if total else 0.0,
        "assumed_self_service_count": round(total * SELF_SERVICE_POTENTIAL_ASSUMPTION),
        "assumed_self_service_pct": round(SELF_SERVICE_POTENTIAL_ASSUMPTION * 100, 1),
        "classification_breakdown": class_breakdown,
        "service_self_service_breakdown": service_breakdown,
    }


def summarize_classified_csv(csv_path):
    counts = Counter()
    services = defaultdict(lambda: {"total": 0, "ss": 0})
    total = 0
    with open(csv_path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            total += 1
            classification = row["classification"]
            service = row["service"]
            counts[classification] += 1
            services[service]["total"] += 1
            if classification == "Self Service Eligible":
                services[service]["ss"] += 1

    service_summary = {}
    for service in SERVICES:
        total_service = services[service]["total"]
        ss_service = services[service]["ss"]
        service_summary[service] = {
            "total": total_service,
            "self_service_count": ss_service,
            "self_service_pct": round((ss_service / total_service * 100), 1) if total_service else 0.0,
        }

    return {
        "total_tickets": total,
        "classification_breakdown": {
            name: {
                "count": count,
                "pct": round((count / total * 100), 1) if total else 0.0,
            }
            for name, count in counts.items()
        },
        "service_self_service_breakdown": service_summary,
    }


def extract_report_metrics(html_path):
    with open(html_path, encoding="utf-8") as handle:
        html = handle.read()

    observed_match = re.search(r"Observed:\s*([0-9.]+)%", html, re.IGNORECASE)
    assumed_match = re.search(
        r'<div class="label">Self-Service Potential</div><div class="value"[^>]*>([0-9.]+)%</div>',
        html,
        re.IGNORECASE,
    )
    total_match = re.search(r"We classified all\s*([0-9,]+)\s*tickets", html, re.IGNORECASE)
    class_match = re.search(
        r"Self Service Eligible</strong></td><td class=\"r\"><strong>([0-9,]+)</strong></td><td class=\"r\"><strong>([0-9.]+)%</strong></td>",
        html,
        re.IGNORECASE,
    )

    return {
        "total_tickets": int(total_match.group(1).replace(",", "")) if total_match else None,
        "observed_self_service_count": int(class_match.group(1).replace(",", "")) if class_match else None,
        "observed_self_service_pct": float(class_match.group(2)) if class_match else None,
        "assumed_self_service_pct": float(assumed_match.group(1)) if assumed_match else None,
        "kpi_observed_self_service_pct": float(observed_match.group(1)) if observed_match else None,
    }


def compare(expected, classified_csv=None, report_metrics=None):
    mismatches = []

    def check(path, expected_value, actual_value):
        if actual_value != expected_value:
            mismatches.append(
                {"metric": path, "expected": expected_value, "actual": actual_value}
            )

    if classified_csv:
        check("classified_csv.total_tickets", expected["total_tickets"], classified_csv["total_tickets"])
        for name, values in expected["classification_breakdown"].items():
            actual = classified_csv["classification_breakdown"].get(name, {"count": 0, "pct": 0.0})
            check(f"classified_csv.classification_breakdown.{name}.count", values["count"], actual["count"])
            check(f"classified_csv.classification_breakdown.{name}.pct", values["pct"], actual["pct"])

        for service, values in expected["service_self_service_breakdown"].items():
            actual = classified_csv["service_self_service_breakdown"].get(service, {})
            check(f"classified_csv.service_self_service_breakdown.{service}.total", values["total"], actual.get("total"))
            check(
                f"classified_csv.service_self_service_breakdown.{service}.self_service_count",
                values["self_service_count"],
                actual.get("self_service_count"),
            )
            check(
                f"classified_csv.service_self_service_breakdown.{service}.self_service_pct",
                values["self_service_pct"],
                actual.get("self_service_pct"),
            )

    if report_metrics:
        check("report.total_tickets", expected["total_tickets"], report_metrics["total_tickets"])
        check(
            "report.observed_self_service_count",
            expected["observed_self_service_count"],
            report_metrics["observed_self_service_count"],
        )
        check(
            "report.observed_self_service_pct",
            expected["observed_self_service_pct"],
            report_metrics["observed_self_service_pct"],
        )
        check(
            "report.kpi_observed_self_service_pct",
            expected["observed_self_service_pct"],
            report_metrics["kpi_observed_self_service_pct"],
        )
        check(
            "report.assumed_self_service_pct",
            expected["assumed_self_service_pct"],
            report_metrics["assumed_self_service_pct"],
        )

    return mismatches


def main():
    args = parse_args()
    source = classify_source_data()
    metrics = source["metrics"]
    week_label = args.week or source["current_start"].strftime("%Y-%m-%d")

    expected = build_expected_summary(metrics)
    classified_csv_path = os.path.join(OUTPUT_DIR, f"classified_tickets_{week_label}.csv")
    report_path = os.path.join(OUTPUT_DIR, f"workload_lens_insights_{week_label}.html")

    classified_summary = summarize_classified_csv(classified_csv_path) if os.path.exists(classified_csv_path) else None
    report_summary = extract_report_metrics(report_path) if os.path.exists(report_path) else None
    mismatches = compare(expected, classified_summary, report_summary)

    payload = {
        "validated_at": datetime.now().isoformat(timespec="seconds"),
        "week_label": week_label,
        "prior_week": metrics["prior_label"],
        "current_week": metrics["current_label"],
        "files_loaded": source["files_loaded"],
        "expected": expected,
        "classified_csv_path": classified_csv_path if os.path.exists(classified_csv_path) else None,
        "report_path": report_path if os.path.exists(report_path) else None,
        "classified_csv_summary": classified_summary,
        "report_summary": report_summary,
        "pass": len(mismatches) == 0,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
        return

    print("=" * 72)
    print("Workload Lens Metric Validation")
    print("=" * 72)
    print(f"Week label: {week_label}")
    print(f"Prior week:  {metrics['prior_label']}")
    print(f"Current week:{metrics['current_label']}")
    print(f"Pass:        {payload['pass']}")
    print(f"Mismatches:  {payload['mismatch_count']}")
    print("")
    print("Overall self-service")
    print(f"  Observed:  {expected['observed_self_service_count']:,} / {expected['total_tickets']:,} = {expected['observed_self_service_pct']:.1f}%")
    print(f"  Assumed:   {expected['assumed_self_service_count']:,} / {expected['total_tickets']:,} = {expected['assumed_self_service_pct']:.1f}%")
    print("")
    print("Classification breakdown")
    for name, values in sorted(
        expected["classification_breakdown"].items(),
        key=lambda item: item[1]["count"],
        reverse=True,
    ):
        print(f"  {name:<24} {values['count']:>5,}  {values['pct']:>5.1f}%")
    print("")
    print("Service-level self-service rates")
    for service in SERVICES:
        values = expected["service_self_service_breakdown"][service]
        print(f"  {service:<24} {values['self_service_count']:>5,} / {values['total']:>5,} = {values['self_service_pct']:>5.1f}%")

    if mismatches:
        print("")
        print("Mismatches")
        for item in mismatches:
            print(f"  {item['metric']}: expected {item['expected']} actual {item['actual']}")


if __name__ == "__main__":
    main()
