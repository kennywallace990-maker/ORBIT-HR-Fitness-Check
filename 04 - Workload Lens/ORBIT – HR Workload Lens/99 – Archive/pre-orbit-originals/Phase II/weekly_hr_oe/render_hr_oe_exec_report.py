from __future__ import annotations

import argparse
import datetime as dt
import html
import json
from pathlib import Path


def format_signed(value: int) -> str:
    return f"+{value}" if value > 0 else str(value)


def safe_pct(num: float, den: float) -> float:
    if den == 0:
        return 0.0
    return (num / den) * 100.0


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def render_review_markdown(metrics: dict[str, object], source_markdown: str) -> str:
    meta = metrics["meta"]
    week8 = meta["week8"]
    week9 = meta["week9"]
    phase1_coverage = metrics["phase1_coverage"]
    phase1_week8 = metrics["phase1"]["week8"]
    phase1_week9 = metrics["phase1"]["week9"]
    phase2_week8 = metrics["phase2"]["week8"]
    phase2_week9 = metrics["phase2"]["week9"]
    cross_phase = metrics["cross_phase"]
    q2 = metrics["answers"]["q2"]

    week9_tickets = phase2_week9["total_tickets"]
    week8_tickets = phase2_week8["total_tickets"]
    ticket_delta = week9_tickets - week8_tickets
    ticket_delta_pct = safe_pct(ticket_delta, week8_tickets)
    resolved_pct_delta = phase2_week9["resolved_pct"] - phase2_week8["resolved_pct"]
    largest_increase = q2["largest_increases"][0] if q2["largest_increases"] else None

    lines: list[str] = []
    lines.append("# HR Operational Excellence Report")
    lines.append("")
    lines.append("Preview this file in the IDE Markdown preview pane to review and comment.")
    lines.append("")
    lines.append("## Review Header")
    lines.append(f"- Week 8: {week8['start']} to {week8['end']} (Sunday to Saturday)")
    lines.append(f"- Week 9: {week9['start']} to {week9['end']} (Sunday to Saturday)")
    lines.append(f"- Generated UTC: {meta['generated_at_utc']}")
    lines.append("")
    lines.append("## VP Summary")
    lines.append(
        f"Week 9 closed at {week9_tickets} HR Operational Excellence tickets, up {ticket_delta} from Week 8 "
        f"({ticket_delta_pct:.2f}%)."
    )
    lines.append(
        f"Resolved rate moved from {phase2_week8['resolved_pct']:.2f}% to {phase2_week9['resolved_pct']:.2f}% "
        f"({resolved_pct_delta:+.2f} pp)."
    )
    if largest_increase:
        lines.append(
            f"The largest growth driver was {largest_increase['service']} "
            f"({format_signed(largest_increase['delta'])}, {largest_increase['delta_pct']:.2f}%)."
        )
    lines.append(
        f"Ticketed Rework Coverage % was {cross_phase['phase2_ticket_visibility_vs_phase1_rework_pct']:.4f}%, "
        "which should be the primary cross-phase KPI."
    )
    lines.append("")
    lines.append("## Data Caveat")
    if phase1_coverage["missing_dates"]["week8"]:
        lines.append(
            "Phase I Week 8 is retained as directional context only because event-date coverage is incomplete."
        )
        lines.append(
            f"Retained sample: {phase1_week8['total_actions']} UKG touches and "
            f"{phase1_week8['rework_actions']} rework touches."
        )
        lines.append(
            f"Missing Phase I Week 8 dates: {', '.join(phase1_coverage['missing_dates']['week8'])}"
        )
    else:
        lines.append("No Phase I week-lock coverage caveat detected.")
    lines.append("")
    lines.append("## Full Working Report")
    lines.append("")
    lines.append(source_markdown.strip())
    lines.append("")
    lines.append("## Review Notes")
    lines.append("- Add comments directly below the section you want changed.")
    lines.append("- Treat this file as the review surface for tonight's discussion.")
    return "\n".join(lines)


def metric_card(label: str, value: str, sublabel: str) -> str:
    return (
        '<div class="card">'
        f'<div class="card-label">{html.escape(label)}</div>'
        f'<div class="card-value">{html.escape(value)}</div>'
        f'<div class="card-sub">{html.escape(sublabel)}</div>'
        "</div>"
    )


def render_html(metrics: dict[str, object]) -> str:
    meta = metrics["meta"]
    week8 = meta["week8"]
    week9 = meta["week9"]
    phase1_week8 = metrics["phase1"]["week8"]
    phase1_week9 = metrics["phase1"]["week9"]
    phase2_week8 = metrics["phase2"]["week8"]
    phase2_week9 = metrics["phase2"]["week9"]
    phase1_coverage = metrics["phase1_coverage"]
    cross_phase = metrics["cross_phase"]
    q1 = metrics["answers"]["q1"]
    q2 = metrics["answers"]["q2"]
    q3 = metrics["answers"]["q3"]

    week8_tickets = phase2_week8["total_tickets"]
    week9_tickets = phase2_week9["total_tickets"]
    ticket_delta = week9_tickets - week8_tickets
    ticket_delta_pct = safe_pct(ticket_delta, week8_tickets)
    resolved_pct_delta = phase2_week9["resolved_pct"] - phase2_week8["resolved_pct"]

    week9_services = phase2_week9["by_service"]
    attendance_week9 = week9_services.get("Attendance inquiry", 0)
    time_week9 = week9_services.get("CC Time and Attendance", 0) + week9_services.get("CS Time and Attendance", 0)
    timesheet_week9 = week9_services.get("Timesheet Inquiry", 0)
    attendance_time_total = attendance_week9 + time_week9
    attendance_time_share = safe_pct(attendance_time_total, week9_tickets)

    largest_increase = q2["largest_increases"][0] if q2["largest_increases"] else None
    largest_decrease = q2["largest_decreases"][0] if q2["largest_decreases"] else None
    unticketed_rework_proxy_pct = 100.0 - cross_phase["phase2_ticket_visibility_vs_phase1_rework_pct"]

    opportunity_rows = []
    for item in q3["top_service_opportunities"]:
        opportunity_rows.append(
            "<tr>"
            f"<td>{html.escape(item['service'])}</td>"
            f"<td>{item['week9_volume']}</td>"
            f"<td>{html.escape(item['opportunity'])}</td>"
            "</tr>"
        )

    delta_rows = []
    for row in q2["largest_increases"] + q2["largest_decreases"]:
        pct = "n/a" if row["delta_pct"] is None else f"{row['delta_pct']:.2f}%"
        delta_rows.append(
            "<tr>"
            f"<td>{html.escape(row['service'])}</td>"
            f"<td>{row['week8']}</td>"
            f"<td>{row['week9']}</td>"
            f"<td>{format_signed(row['delta'])}</td>"
            f"<td>{html.escape(pct)}</td>"
            "</tr>"
        )

    missing_dates = ", ".join(phase1_coverage["missing_dates"]["week8"]) if phase1_coverage["missing_dates"]["week8"] else "None"
    generated_label = meta["generated_at_utc"].replace("T", " ").replace("+00:00", " UTC")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>HR Operational Excellence Report</title>
  <style>
    :root {{
      --ink: #1e2430;
      --muted: #5d6678;
      --border: #d7dde8;
      --panel: #ffffff;
      --panel-alt: #f4f7fb;
      --accent: #0d5f73;
      --accent-soft: #dff0f4;
      --warn: #7a3e00;
      --warn-bg: #fff3e3;
      --bg: linear-gradient(180deg, #edf4f8 0%, #f8fafc 55%, #ffffff 100%);
      --shadow: 0 12px 30px rgba(26, 42, 68, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Aptos, "Segoe UI", Calibri, sans-serif;
      color: var(--ink);
      background: var(--bg);
    }}
    .wrap {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 32px 24px 48px;
    }}
    .hero {{
      background: linear-gradient(135deg, #143642 0%, #255d6b 55%, #2f7e89 100%);
      color: #fff;
      border-radius: 22px;
      padding: 28px 32px;
      box-shadow: var(--shadow);
      position: relative;
      overflow: hidden;
    }}
    .hero::after {{
      content: "";
      position: absolute;
      right: -80px;
      top: -60px;
      width: 240px;
      height: 240px;
      background: rgba(255,255,255,0.08);
      border-radius: 50%;
    }}
    h1 {{
      margin: 0 0 10px;
      font-family: Georgia, "Times New Roman", serif;
      font-size: 40px;
      line-height: 1.05;
    }}
    .hero p {{
      margin: 6px 0;
      max-width: 860px;
      font-size: 18px;
      line-height: 1.5;
    }}
    .stamp {{
      margin-top: 14px;
      font-size: 13px;
      opacity: 0.9;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 16px;
      margin: 22px 0 26px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 18px 18px 16px;
      box-shadow: var(--shadow);
    }}
    .card-label {{
      color: var(--muted);
      font-size: 12px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    .card-value {{
      margin-top: 8px;
      font-size: 34px;
      font-weight: 700;
      line-height: 1.05;
    }}
    .card-sub {{
      margin-top: 8px;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.45;
    }}
    .section {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 22px 24px;
      box-shadow: var(--shadow);
      margin-top: 18px;
    }}
    .section h2 {{
      margin: 0 0 12px;
      font-family: Georgia, "Times New Roman", serif;
      font-size: 28px;
    }}
    .section h3 {{
      margin: 20px 0 8px;
      font-size: 18px;
    }}
    .section p, .section li {{
      font-size: 16px;
      line-height: 1.6;
    }}
    .callout {{
      background: var(--accent-soft);
      border-left: 5px solid var(--accent);
      padding: 16px 18px;
      border-radius: 14px;
      margin-top: 14px;
    }}
    .warning {{
      background: var(--warn-bg);
      border-left: 5px solid #d07a00;
    }}
    .columns {{
      display: grid;
      grid-template-columns: 1.3fr 1fr;
      gap: 18px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 12px;
      font-size: 15px;
    }}
    th, td {{
      border-bottom: 1px solid var(--border);
      padding: 10px 8px;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }}
    .pill {{
      display: inline-block;
      padding: 6px 10px;
      border-radius: 999px;
      background: #e9f5ea;
      color: #14643a;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }}
    .muted {{
      color: var(--muted);
    }}
    @media (max-width: 900px) {{
      .grid {{ grid-template-columns: 1fr 1fr; }}
      .columns {{ grid-template-columns: 1fr; }}
      h1 {{ font-size: 32px; }}
    }}
    @media (max-width: 620px) {{
      .wrap {{ padding: 20px 14px 32px; }}
      .hero {{ padding: 22px 20px; }}
      .grid {{ grid-template-columns: 1fr; }}
      .section {{ padding: 18px 16px; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <div class="pill">Supplemental Draft</div>
      <h1>HR Operational Excellence</h1>
      <p>Week 9 closed at <strong>{week9_tickets}</strong> tickets, up <strong>{ticket_delta}</strong> from Week 8 ({ticket_delta_pct:.2f}%). Volume growth was concentrated in Time and Attendance while resolution performance weakened.</p>
      <p>Phase I confirms the queue is only a partial view of work: Week 9 recorded <strong>{phase1_week9['total_actions']}</strong> UKG touches and <strong>{phase1_week9['rework_actions']}</strong> rework touches.</p>
      <div class="stamp">Week 8: {week8['start']} to {week8['end']} | Week 9: {week9['start']} to {week9['end']} | Generated {generated_label}</div>
    </section>

    <section class="grid">
      {metric_card("Week 9 Tickets", str(week9_tickets), f"{format_signed(ticket_delta)} vs Week 8 | {ticket_delta_pct:.2f}%")}
      {metric_card("Resolved Rate", f"{phase2_week9['resolved_pct']:.2f}%", f"{resolved_pct_delta:+.2f} pp vs Week 8")}
      {metric_card("Rework Coverage", f"{cross_phase['phase2_ticket_visibility_vs_phase1_rework_pct']:.4f}%", "Recommended primary KPI")}
      {metric_card("Attendance + Time Share", f"{attendance_time_share:.2f}%", f"{attendance_time_total} of {week9_tickets} Week 9 tickets")}
    </section>

    <section class="section">
      <h2>Executive Readout</h2>
      <p>Week 9 ticket demand increased modestly, but the increase was not broad-based. The primary driver was <strong>{html.escape(largest_increase['service']) if largest_increase else 'the top service category'}</strong>{f' at {largest_increase["week9"]} tickets, up {abs(largest_increase["delta"])} ({largest_increase["delta_pct"]:.2f}%) from Week 8' if largest_increase else ''}. The largest offsetting decline came from <strong>{html.escape(largest_decrease['service']) if largest_decrease else 'another service category'}</strong>{f', down {abs(largest_decrease["delta"])} ({largest_decrease["delta_pct"]:.2f}%)' if largest_decrease else ''}.</p>
      <p>The most actionable near-term reduction opportunity remains attendance and timekeeping demand. Attendance Inquiry plus Time and Attendance work accounts for <strong>{attendance_time_total}</strong> of <strong>{week9_tickets}</strong> Week 9 tickets ({attendance_time_share:.2f}%), which makes that flow the best place to use existing self-service, standardized intake, and same-day correction levers.</p>
      <div class="callout">
        <strong>Recommendation:</strong> Use <strong>Ticketed Rework Coverage %</strong> as the primary cross-phase KPI. Week 9 closed at <strong>{cross_phase['phase2_ticket_visibility_vs_phase1_rework_pct']:.4f}%</strong> ticketed rework coverage, leaving an <strong>Unticketed Rework Proxy %</strong> of <strong>{unticketed_rework_proxy_pct:.4f}%</strong>.
      </div>
    </section>

    <section class="section">
      <h2>Direct Answers</h2>
      <div class="columns">
        <div>
          <h3>Q1. SLA commitments and measurements</h3>
          <p>SLA adherence cannot be measured accurately from the current weekly files because the dataset does not include ticket-level SLA targets, SLA clocks, or breach flags.</p>
          <p><strong>Plan:</strong> define the SLA target by HR Service, stamp the target at open, and calculate within-SLA or breach status both on close and for aging backlog.</p>
          <ul>
            <li>SLA policy table by HR Service</li>
            <li>Ticket-level SLA target at open</li>
            <li>Ticket-level within-SLA or breach status</li>
            <li>Lifecycle timestamps if business-hour clocks apply</li>
          </ul>
        </div>
        <div>
          <h3>Q2. Ticket types driving volume change</h3>
          <p>Week 9 volume increased by <strong>{ticket_delta}</strong> tickets ({ticket_delta_pct:.2f}%). Based on the supplied service labels, the increase was concentrated in Time and Attendance demand.</p>
          <h3>Q3. Biggest opportunity to reduce volume</h3>
          <p>The strongest immediate opportunity is to reduce avoidable attendance and timekeeping contacts using the tools and process controls already in place.</p>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Week 8 vs Week 9 Snapshot</h2>
      <table>
        <thead>
          <tr>
            <th>Metric</th>
            <th>Week 8</th>
            <th>Week 9</th>
            <th>Delta</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Phase II total tickets</td>
            <td>{phase2_week8['total_tickets']}</td>
            <td>{phase2_week9['total_tickets']}</td>
            <td>{format_signed(ticket_delta)}</td>
          </tr>
          <tr>
            <td>Phase II resolved tickets</td>
            <td>{phase2_week8['resolved_count']}</td>
            <td>{phase2_week9['resolved_count']}</td>
            <td>{format_signed(phase2_week9['resolved_count'] - phase2_week8['resolved_count'])}</td>
          </tr>
          <tr>
            <td>Phase II resolved percent</td>
            <td>{phase2_week8['resolved_pct']:.2f}%</td>
            <td>{phase2_week9['resolved_pct']:.2f}%</td>
            <td>{resolved_pct_delta:+.2f} pp</td>
          </tr>
          <tr>
            <td>Phase I total UKG touches</td>
            <td>{phase1_week8['total_actions']} (partial prior-week sample)</td>
            <td>{phase1_week9['total_actions']}</td>
            <td>directional only</td>
          </tr>
          <tr>
            <td>Phase I UKG rework touches</td>
            <td>{phase1_week8['rework_actions']} (partial prior-week sample)</td>
            <td>{phase1_week9['rework_actions']}</td>
            <td>directional only</td>
          </tr>
        </tbody>
      </table>
    </section>

    <section class="section">
      <h2>Service Movement</h2>
      <table>
        <thead>
          <tr>
            <th>Service</th>
            <th>Week 8</th>
            <th>Week 9</th>
            <th>Delta</th>
            <th>Delta %</th>
          </tr>
        </thead>
        <tbody>
          {''.join(delta_rows)}
        </tbody>
      </table>
    </section>

    <section class="section">
      <h2>Recommended Actions This Week</h2>
      <ul>
        <li>Stand up ticket-level SLA measurement design before reporting SLA attainment to leadership.</li>
        <li>Target Attendance Inquiry and Time and Attendance demand first because they dominate Week 9 volume.</li>
        <li>Use Ticketed Rework Coverage % as the primary dark-work KPI for cross-phase reporting.</li>
        <li>Keep Phase I Week 8 in the narrative as directional context until EPA refreshes the missing event dates.</li>
      </ul>
      <table>
        <thead>
          <tr>
            <th>Service</th>
            <th>Week 9 Volume</th>
            <th>Immediate Opportunity</th>
          </tr>
        </thead>
        <tbody>
          {''.join(opportunity_rows)}
        </tbody>
      </table>
    </section>

    <section class="section">
      <h2>Data Caveats</h2>
      <div class="callout warning">
        <strong>Phase I Week 8 remains directional.</strong>
        Missing Phase I event dates: {html.escape(missing_dates)}.
        Retained sample: {phase1_week8['total_actions']} UKG touches and {phase1_week8['rework_actions']} rework touches.
      </div>
      <p class="muted">Method note: {html.escape(cross_phase['method_note'])}</p>
      <p class="muted">SLA gap: {html.escape(q1['answer'])}</p>
    </section>
  </div>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Render review markdown and HTML for HR OE report.")
    parser.add_argument("--metrics-json", required=True)
    parser.add_argument("--source-markdown", required=True)
    parser.add_argument("--output-markdown", required=True)
    parser.add_argument("--output-html", required=True)
    args = parser.parse_args()

    metrics_path = Path(args.metrics_json).resolve()
    source_markdown_path = Path(args.source_markdown).resolve()
    output_markdown_path = Path(args.output_markdown).resolve()
    output_html_path = Path(args.output_html).resolve()

    metrics = load_json(metrics_path)
    source_markdown = source_markdown_path.read_text(encoding="utf-8")

    review_markdown = render_review_markdown(metrics, source_markdown)
    html_report = render_html(metrics)

    output_markdown_path.parent.mkdir(parents=True, exist_ok=True)
    output_html_path.parent.mkdir(parents=True, exist_ok=True)
    output_markdown_path.write_text(review_markdown, encoding="utf-8")
    output_html_path.write_text(html_report, encoding="utf-8")

    print(
        json.dumps(
            {
                "output_markdown": str(output_markdown_path),
                "output_html": str(output_html_path),
                "generated_at_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
