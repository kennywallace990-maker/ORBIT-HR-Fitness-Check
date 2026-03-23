# ORBIT Workload Lens — Weekly Pipeline

## How to Run

### 1. Drop your files

Place this week's ServiceNow CSV exports into:

```
Phase II/Phase II CSVs/
```

**Required CSVs** (naming is flexible — the script reads the `Hr Service` column to identify them):

- Attendance Inquiry `*.csv`
- CC Time and Attendance `*.csv` (or "CS Time and Attendance")
- FC General Inquiry `*.csv`
- Timesheet Inquiry `*.csv`

**Optional:** Drop the EPA OBR PDF into the same folder for validation context.

### 2. Run the pipeline

```powershell
cd "04 - Workload Lens\Phase II\pipeline"
python run_weekly.py
```

### 3. Get your report

The pipeline outputs two files to `Phase II/output/`:

- `workload_lens_insights_YYYY-MM-DD.html` — The full insights & recommendations report
- `classified_tickets_YYYY-MM-DD.csv` — Every ticket with its classification, sub-category, and self-service channel

Open the HTML in any browser. It's ready to share.

### 4. Validate the metrics

To confirm the report math against the generated outputs:

```powershell
cd "04 - Workload Lens\Phase II\pipeline"
python validate_metrics.py --week 2026-03-01
```

The validator recomputes the metrics from source CSVs using the same logic as `run_weekly.py`, then compares those numbers to:

- `output/classified_tickets_YYYY-MM-DD.csv`
- `output/workload_lens_insights_YYYY-MM-DD.html`

Use `python validate_metrics.py --json` if you want a machine-readable payload.

## What the Pipeline Does

1. **Auto-detects CSVs** in the `Phase II CSVs/` folder and loads all tickets
2. **Auto-detects the two most recent weeks** from the date data (no manual week config needed)
3. **Classifies every ticket** into Self Service Eligible, Process Required, Defect, or Unclear using rule-based pattern matching on Description1 and Contact Type
4. **Extracts OBR PDF text** (if present) for validation
5. **Generates the HTML report** with executive summary, 4 focus areas, site breakdowns, and recommendations
6. **Exports classified data** as a CSV for further analysis

## Weekly Workflow

Each week:

1. Export the 4 ServiceNow CSVs for the latest 2-week window
2. Download the EPA OBR PDF
3. Drop both into `Phase II CSVs/`
4. Run `python run_weekly.py`
5. Share the HTML report

## File Structure

```
Phase II/
├── Phase II CSVs/         ← Drop CSVs and PDF here
│   ├── Attendance Inquiry *.csv
│   ├── CC Time and Attendance *.csv
│   ├── FC General Inquiry *.csv
│   ├── Timesheet Inquiry *.csv
│   └── Week XX OBR.pdf   (optional)
├── pipeline/
│   ├── run_weekly.py      ← Main script
│   ├── classifier.py      ← Classification rules (editable)
│   └── README.md          ← This file
└── output/
    ├── workload_lens_insights_*.html
    └── classified_tickets_*.csv
```

## Tuning the Classifier

The classification rules live in `classifier.py`. Each rule has:

- **Sub-category name** (e.g., "Call out / absence report (UKG app available)")
- **Classification** (Self Service Eligible, Process Required, or Defect)
- **Regex patterns** matched against Description1
- **Contact type filter** (optional — e.g., only match Phone)

Rules are evaluated top-down, first match wins. To add or adjust rules, edit the `RULES` list in `classifier.py`.

## Requirements

- Python 3.10+
- `pdfplumber` (for OBR PDF extraction — optional)
- No other external dependencies (uses csv, re, collections from stdlib)

## Future State

Once ServiceNow data lands in Snowflake, this CSV pipeline will be replaced by a direct query. The classifier rules and report template will carry forward.
