# Daily People Pulse Pipeline — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python pipeline that reads UKG data, computes all six report sections, calls the Anthropic API for AI insights, renders a print-ready HTML report, and saves it for Phoenix to convert to PDF.

**Architecture:** Multi-stage CLI pipeline following the ORBIT standard: one Python file per stage, `main() -> int` entry points, argparse config, standard library only (except Anthropic API called directly via `urllib.request`). An orchestrator `run_dpp_pipeline.py` executes stages in order. The HTML template is a Jinja2-style f-string rendered in Python (no template engine dependency).

**Tech Stack:** Python 3.9+, standard library (`argparse`, `csv`, `json`, `datetime`, `pathlib`, `collections`, `urllib.request`), Anthropic API via HTTP (no SDK), HTML/CSS output (from POC template in `05 – Application & UX/DPP_POC_Mock.html`).

**Spec:** `docs/superpowers/specs/2026-03-23-daily-people-pulse-poc-design.md`

---

## File Map

All files live under:
`01 - Daily People Pulse/ORBIT – Daily People Pulse/04 – Pipelines & Architecture/dpp-pipeline/`

| File | Responsibility |
|------|---------------|
| `dpp_scope.py` | Report mode logic, department registry, date window calculations, thresholds |
| `dpp_ukg_reader.py` | Reads and normalizes UKG CSV input into a list of typed dicts |
| `sections/dpp_attendance.py` | Computes Section 01 attendance metrics per dept/shift |
| `sections/dpp_ncns.py` | Identifies Section 02 NCNS records, calculates day numbers |
| `sections/dpp_unscheduled.py` | Identifies Section 03 unscheduled-but-worked (≥10 min, prior day) |
| `sections/dpp_paycode.py` | Identifies Section 04 paycode mismatches (WTD or prior week) |
| `sections/dpp_time_off.py` | Computes Section 05 upcoming time off per dept |
| `sections/dpp_overtime.py` | Computes Section 06 60+ hour watch with CRITICAL/WATCH precedence |
| `dpp_insights.py` | Calls Anthropic API to generate AI insight text per dept section |
| `dpp_html_renderer.py` | Assembles all section data into the final HTML string |
| `run_dpp_pipeline.py` | Orchestrator: runs all stages, handles errors, writes output HTML |
| `tests/test_dpp_scope.py` | Tests for date window and report mode logic |
| `tests/test_dpp_attendance.py` | Tests for attendance computation |
| `tests/test_dpp_ncns.py` | Tests for NCNS detection and day numbering |
| `tests/test_dpp_sections.py` | Tests for unscheduled, paycode, time off, overtime sections |

---

## Chunk 1: Scope Module & Date Logic

### Task 1: Create `dpp_scope.py`

**Files:**
- Create: `04 – Pipelines & Architecture/dpp-pipeline/dpp_scope.py`
- Create: `04 – Pipelines & Architecture/dpp-pipeline/tests/test_dpp_scope.py`

This is the foundation everything else depends on. Get this right before any other stage.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_dpp_scope.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from datetime import date
from dpp_scope import get_report_mode, get_date_windows, DEPT_REGISTRY, ATTENDANCE_THRESHOLDS

def test_wtd_mode_on_wednesday():
    d = date(2026, 3, 19)  # Wednesday
    assert get_report_mode(d) == "WTD"

def test_prior_week_mode_on_sunday():
    d = date(2026, 3, 15)  # Sunday
    assert get_report_mode(d) == "PRIOR_WEEK"

def test_prior_week_mode_on_monday():
    d = date(2026, 3, 16)  # Monday
    assert get_report_mode(d) == "PRIOR_WEEK"

def test_wtd_window_wednesday():
    d = date(2026, 3, 19)
    windows = get_date_windows(d)
    assert windows["wtd_start"] == date(2026, 3, 15)   # Sunday
    assert windows["wtd_end"]   == date(2026, 3, 18)   # Tuesday (prior day)
    assert windows["prior_day"] == date(2026, 3, 18)

def test_prior_week_window_sunday():
    d = date(2026, 3, 15)  # Sunday
    windows = get_date_windows(d)
    assert windows["prior_week_start"] == date(2026, 3, 8)   # prior Sunday
    assert windows["prior_week_end"]   == date(2026, 3, 14)  # prior Saturday
    assert windows["prior_day"]        == date(2026, 3, 14)  # Saturday

def test_dept_registry_has_required_depts():
    codes = {d["code"] for d in DEPT_REGISTRY.values()}
    assert 2300 in codes  # Outbound
    assert 3300 in codes  # Pharmacy

def test_attendance_threshold():
    assert ATTENDANCE_THRESHOLDS["green_min"] == 0.85
    assert ATTENDANCE_THRESHOLDS["amber_min"] == 0.80
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd "c:/Users/kwallace12/OneDrive - Chewy.com, LLC/Desktop/ORBIT Products/01 - Daily People Pulse/ORBIT – Daily People Pulse/04 – Pipelines & Architecture/dpp-pipeline"
python -m pytest tests/test_dpp_scope.py -v 2>&1
```

Expected: `ModuleNotFoundError: No module named 'dpp_scope'`

- [ ] **Step 3: Implement `dpp_scope.py`**

```python
# dpp_scope.py
"""
DPP Scope — report mode logic, department registry, date windows, thresholds.
All dates are datetime.date objects. No external dependencies.
"""
from datetime import date, timedelta

# ── Report mode ──────────────────────────────────────────────────────────────

def get_report_mode(report_date: date) -> str:
    """Return 'WTD' (Tue–Sat) or 'PRIOR_WEEK' (Sun–Mon)."""
    return "PRIOR_WEEK" if report_date.weekday() in (6, 0) else "WTD"

# ── Date windows ─────────────────────────────────────────────────────────────

def get_date_windows(report_date: date) -> dict:
    """
    Return the relevant date windows for the report_date.

    WTD mode (Tue–Sat):
      wtd_start   = most recent Sunday
      wtd_end     = prior_day (day before report_date)
      prior_day   = report_date - 1

    PRIOR_WEEK mode (Sun–Mon):
      prior_week_start = Sunday of the week before last
      prior_week_end   = Saturday of the prior week
      prior_day        = report_date - 1  (Saturday on Sunday, Sunday on Monday)
    """
    prior_day = report_date - timedelta(days=1)
    mode = get_report_mode(report_date)

    if mode == "WTD":
        days_since_sunday = report_date.weekday() + 1  # Mon=0 in weekday(); +1 → Mon=1, Tue=2, ..., Sat=6 days since prior Sunday
        wtd_start = report_date - timedelta(days=days_since_sunday)
        return {
            "mode": "WTD",
            "wtd_start": wtd_start,
            "wtd_end": prior_day,
            "prior_day": prior_day,
        }
    else:  # PRIOR_WEEK
        # Find the Sunday of the *prior* week
        days_back_to_last_sunday = report_date.weekday() + 1
        if report_date.weekday() == 6:  # today is Sunday
            days_back_to_last_sunday = 7
        prior_week_start = report_date - timedelta(days=days_back_to_last_sunday)
        prior_week_end = prior_week_start + timedelta(days=6)
        return {
            "mode": "PRIOR_WEEK",
            "prior_week_start": prior_week_start,
            "prior_week_end": prior_week_end,
            "prior_day": prior_day,
        }

# ── Department registry ───────────────────────────────────────────────────────
# key = canonical name used in report output
# code = UKG dept code (None = TBD, confirm with product owner)
# has_night = whether this dept runs a night shift (may vary by site — overrideable)

DEPT_REGISTRY = {
    "Outbound":          {"code": 2300, "label": "Outbound Technicians",   "has_night": True},
    "Inbound":           {"code": 2100, "label": "Inbound Technicians",    "has_night": True},
    "Replenishment":     {"code": 2200, "label": "Replenishment",          "has_night": False},
    "Inventory Control": {"code": 2400, "label": "Inventory Control",      "has_night": False},
    "Pharmacy":          {"code": 3300, "label": "Pharmacy",               "has_night": True},
    "Vet Tech I":        {"code": None, "label": "Vet Services – Tech I",  "has_night": False},
    "Vet Tech II":       {"code": None, "label": "Vet Services – Tech II", "has_night": False},
}

# ── Attendance thresholds ─────────────────────────────────────────────────────

ATTENDANCE_THRESHOLDS = {
    "green_min":  0.85,   # >= 85% → green
    "amber_min":  0.80,   # >= 80% and < 85% → amber
    # < amber_min → red
}

def attendance_color_class(rate: float) -> str:
    """Return CSS class name for attendance rate."""
    if rate >= ATTENDANCE_THRESHOLDS["green_min"]:
        return "good"
    if rate >= ATTENDANCE_THRESHOLDS["amber_min"]:
        return "warn"
    return "bad"

# ── NCNS day-number recommendation text ──────────────────────────────────────

NCNS_REC = {
    1: "Validate NCNS on timesheet \u2192 Initiate NCNS Comm Day 1",
    2: "NCNS Comm Day 2 sent \u2192 monitor for Day 3 threshold. "
       "If absent again, initiate Term Review Ticket within 36 hrs of Day 3 comm",
    3: "Day 3 threshold reached \u2192 Send Term Review Ticket to Site HR within 36 hrs of this comm",
}
NCNS_REC_DEFAULT = "Day {n} \u2192 Send Term Review Ticket to Site HR within 36 hrs of this comm"

def ncns_recommendation(day_number: int) -> str:
    return NCNS_REC.get(day_number, NCNS_REC_DEFAULT.format(n=day_number))

# ── OT thresholds ─────────────────────────────────────────────────────────────

OT_CRITICAL_HOURS = 60.0   # WTD worked >= this → CRITICAL
OT_WATCH_HOURS    = 58.0   # WTD worked >= this (and projected > 60) → WATCH
OT_WATCH_PROJECTED = 60.0  # (WTD worked + remaining scheduled) > this → WATCH
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_dpp_scope.py -v 2>&1
```

Expected: All 7 tests PASS

- [ ] **Step 5: Commit**

```bash
git add "ORBIT – Daily People Pulse/04 – Pipelines & Architecture/dpp-pipeline/dpp_scope.py"
git add "ORBIT – Daily People Pulse/04 – Pipelines & Architecture/dpp-pipeline/tests/test_dpp_scope.py"
git commit -m "feat(dpp): add scope module — report mode, date windows, dept registry, thresholds"
```

---

## Chunk 2: UKG Data Reader

### Task 2: Create `dpp_ukg_reader.py`

**Files:**
- Create: `04 – Pipelines & Architecture/dpp-pipeline/dpp_ukg_reader.py`
- Append tests to: `tests/test_dpp_scope.py` (or create `tests/test_dpp_reader.py`)

The reader normalizes UKG CSV rows into a consistent `UKGRecord` dict. All downstream section modules consume this format — getting it right here saves pain everywhere else.

**Expected UKG CSV columns** (confirm against actual UKG API output; adjust field names in `FIELD_MAP` if they differ):

| CSV Column | Normalized Key | Type |
|---|---|---|
| Employee ID | `eid` | str |
| Employee Name | `tm_name` | str (Last, First) |
| Dept Code | `dept_code` | int |
| Schedule Group | `schedule_group` | str |
| Reports To | `reports_to` | str |
| Date | `date` | `datetime.date` |
| Scheduled Hours | `scheduled_hours` | float (decimal hours) |
| Worked Hours | `worked_hours` | float |
| Paycode | `paycode` | str |
| Shift | `shift` | str ("Day" or "Night") |
| Hours Type | `hours_type` | str ("Regular", "OT", etc.) |

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_dpp_reader.py
import sys, os, csv, io
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from datetime import date
from dpp_ukg_reader import parse_hours, normalize_row, load_ukg_csv

def test_parse_hours_hhmm():
    assert parse_hours("10:00") == 10.0
    assert parse_hours("10:30") == 10.5
    assert parse_hours("00:15") == 0.25

def test_parse_hours_decimal():
    assert parse_hours("10.5") == 10.5

def test_parse_hours_empty():
    assert parse_hours("") == 0.0
    assert parse_hours(None) == 0.0

def test_normalize_row_basic():
    raw = {
        "Employee ID": "12034",
        "Employee Name": "Alvarez, Maria",
        "Dept Code": "2300",
        "Schedule Group": "F06-SDF4-SMTW-0600-1630-A",
        "Reports To": "Harden, TJ",
        "Date": "03/17/2026",
        "Scheduled Hours": "10:00",
        "Worked Hours": "00:00",
        "Paycode": "NCNS",
        "Shift": "Day",
        "Hours Type": "Regular",
    }
    rec = normalize_row(raw)
    assert rec["eid"] == "12034"
    assert rec["tm_name"] == "Alvarez, Maria"
    assert rec["dept_code"] == 2300
    assert rec["date"] == date(2026, 3, 17)
    assert rec["scheduled_hours"] == 10.0
    assert rec["worked_hours"] == 0.0

def test_load_ukg_csv_from_string():
    data = (
        "Employee ID,Employee Name,Dept Code,Schedule Group,Reports To,"
        "Date,Scheduled Hours,Worked Hours,Paycode,Shift,Hours Type\n"
        "12034,\"Alvarez, Maria\",2300,F06-SDF4-SMTW-0600-1630-A,\"Harden, TJ\","
        "03/17/2026,10:00,00:00,NCNS,Day,Regular\n"
    )
    path = "/tmp/test_ukg.csv"
    with open(path, "w", encoding="utf-8-sig") as f:
        f.write(data)
    records = load_ukg_csv(path, site_filter=None)
    assert len(records) == 1
    assert records[0]["eid"] == "12034"
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest tests/test_dpp_reader.py -v 2>&1
```

Expected: `ModuleNotFoundError: No module named 'dpp_ukg_reader'`

- [ ] **Step 3: Implement `dpp_ukg_reader.py`**

```python
# dpp_ukg_reader.py
"""
UKG Data Reader — normalizes UKG CSV rows into UKGRecord dicts.
Field names in FIELD_MAP should match your actual UKG API CSV output.
Adjust keys here if column names differ; no other file needs to change.
"""
import csv
from datetime import datetime, date
from pathlib import Path

# ── Field name mapping (CSV column → normalized key) ─────────────────────────
# Update these if your UKG export uses different column names.
FIELD_MAP = {
    "Employee ID":      "eid",
    "Employee Name":    "tm_name",
    "Dept Code":        "dept_code",
    "Schedule Group":   "schedule_group",
    "Reports To":       "reports_to",
    "Date":             "date",
    "Scheduled Hours":  "scheduled_hours",
    "Worked Hours":     "worked_hours",
    "Paycode":          "paycode",
    "Shift":            "shift",
    "Hours Type":       "hours_type",
}

DATE_FORMATS = ["%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y"]

def parse_hours(value) -> float:
    """Parse 'HH:MM' or decimal string to float hours. Returns 0.0 on empty/None."""
    if not value:
        return 0.0
    value = str(value).strip()
    if ":" in value:
        parts = value.split(":")
        try:
            return int(parts[0]) + int(parts[1]) / 60
        except (ValueError, IndexError):
            return 0.0
    try:
        return float(value)
    except ValueError:
        return 0.0

def parse_date(value: str) -> date:
    """Parse date string using multiple formats. Raises ValueError if none match."""
    value = str(value).strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {value!r}")

def normalize_row(raw: dict) -> dict:
    """
    Convert a raw CSV row (using FIELD_MAP keys) into a normalized UKGRecord dict.
    Unknown columns are preserved under their original key for debugging.
    """
    rec = {}
    for csv_key, norm_key in FIELD_MAP.items():
        val = raw.get(csv_key, "")
        if norm_key in ("scheduled_hours", "worked_hours"):
            rec[norm_key] = parse_hours(val)
        elif norm_key == "dept_code":
            try:
                rec[norm_key] = int(str(val).strip()) if val else 0
            except ValueError:
                rec[norm_key] = 0
        elif norm_key == "date":
            try:
                rec[norm_key] = parse_date(val)
            except ValueError:
                rec[norm_key] = None
        else:
            rec[norm_key] = str(val).strip()
    return rec

def load_ukg_csv(path: str, site_filter: str | None = None) -> list[dict]:
    """
    Read a UKG CSV file and return a list of normalized UKGRecord dicts.
    site_filter: if provided, only include rows where 'site' matches (case-insensitive).
    Rows with unparseable dates are skipped with a warning.
    """
    records = []
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"UKG input file not found: {path}")

    with open(p, encoding="utf-8-sig", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        for i, raw in enumerate(reader, start=2):
            rec = normalize_row(raw)
            if rec.get("date") is None:
                print(f"  [warn] Row {i}: unparseable date — skipped")
                continue
            if site_filter and rec.get("site", "").upper() != site_filter.upper():
                continue
            records.append(rec)

    return records
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_dpp_reader.py -v 2>&1
```

Expected: All 5 tests PASS

- [ ] **Step 5: Commit**

```bash
git add "ORBIT – Daily People Pulse/04 – Pipelines & Architecture/dpp-pipeline/dpp_ukg_reader.py"
git add "ORBIT – Daily People Pulse/04 – Pipelines & Architecture/dpp-pipeline/tests/test_dpp_reader.py"
git commit -m "feat(dpp): add UKG CSV reader with hour/date normalization"
```

---

## Chunk 3: Section 01 — Attendance & Section 02 — NCNS

### Task 3: `sections/dpp_attendance.py`

**Files:**
- Create: `04 – Pipelines & Architecture/dpp-pipeline/sections/__init__.py` (empty)
- Create: `04 – Pipelines & Architecture/dpp-pipeline/sections/dpp_attendance.py`
- Create: `04 – Pipelines & Architecture/dpp-pipeline/tests/test_dpp_attendance.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_dpp_attendance.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from datetime import date
from sections.dpp_attendance import compute_attendance

RECORDS = [
    # Dept 2300, Day, worked
    {"dept_code": 2300, "shift": "Day",  "date": date(2026,3,18),
     "scheduled_hours": 10.0, "worked_hours": 7.8,  "paycode": ""},
    {"dept_code": 2300, "shift": "Day",  "date": date(2026,3,18),
     "scheduled_hours": 10.0, "worked_hours": 10.0, "paycode": ""},
    # Dept 2300, Night, partial absence
    {"dept_code": 2300, "shift": "Night","date": date(2026,3,18),
     "scheduled_hours": 10.0, "worked_hours": 10.0, "paycode": ""},
    # Outbound WTD second day
    {"dept_code": 2300, "shift": "Day",  "date": date(2026,3,15),
     "scheduled_hours": 10.0, "worked_hours": 10.0, "paycode": ""},
]

WTD_DATES  = [date(2026,3,15), date(2026,3,16), date(2026,3,17), date(2026,3,18)]
PRIOR_DATE = date(2026,3,18)

def test_prior_day_day_attendance():
    result = compute_attendance(RECORDS, WTD_DATES, PRIOR_DATE)
    dept = result[2300]
    # Prior day Day: 17.8 worked / 20.0 scheduled
    assert abs(dept["prior_day"]["Day"]["pct"] - 17.8 / 20.0) < 0.001

def test_prior_day_night_attendance():
    result = compute_attendance(RECORDS, WTD_DATES, PRIOR_DATE)
    dept = result[2300]
    assert dept["prior_day"]["Night"]["worked_hours"] == 10.0

def test_wtd_day_attendance():
    result = compute_attendance(RECORDS, WTD_DATES, PRIOR_DATE)
    dept = result[2300]
    # WTD Day: 27.8 worked / 30.0 scheduled
    assert abs(dept["wtd"]["Day"]["pct"] - 27.8 / 30.0) < 0.001

def test_missing_dept_not_in_result():
    result = compute_attendance(RECORDS, WTD_DATES, PRIOR_DATE)
    assert 3300 not in result  # no Pharmacy records
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest tests/test_dpp_attendance.py -v 2>&1
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement `sections/dpp_attendance.py`**

```python
# sections/dpp_attendance.py
"""
Section 01 — Attendance Summary.
Computes per-dept, per-shift attendance for WTD window and Prior Day.
Returns a dict keyed by dept_code.
"""
from datetime import date
from collections import defaultdict

def _empty_shift_bucket():
    return {"scheduled_hours": 0.0, "worked_hours": 0.0,
            "early_departures": 0, "early_departure_hours": 0.0,
            "full_missed": 0,       "full_missed_hours": 0.0,
            "late_arrivals": 0,     "late_arrival_hours": 0.0}

def _pct(worked, scheduled):
    return worked / scheduled if scheduled > 0 else 0.0

def _add_to_bucket(bucket, rec):
    bucket["scheduled_hours"] += rec["scheduled_hours"]
    bucket["worked_hours"]    += rec["worked_hours"]
    paycode = (rec.get("paycode") or "").upper()
    diff = rec["scheduled_hours"] - rec["worked_hours"]
    if paycode in ("EARLY DEPARTURE", "EARLY DEP", "EARLY_DEPARTURE"):
        bucket["early_departures"]      += 1
        bucket["early_departure_hours"] += diff
    elif rec["worked_hours"] == 0.0 and rec["scheduled_hours"] > 0:
        bucket["full_missed"]       += 1
        bucket["full_missed_hours"] += rec["scheduled_hours"]
    elif paycode in ("LATE ARRIVAL", "LATE_ARRIVAL"):
        bucket["late_arrivals"]      += 1
        bucket["late_arrival_hours"] += abs(diff)

def _finalize_bucket(bucket):
    bucket["pct"] = _pct(bucket["worked_hours"], bucket["scheduled_hours"])
    return bucket

def compute_attendance(
    records: list[dict],
    wtd_dates: list[date],
    prior_day: date,
) -> dict:
    """
    Returns:
      { dept_code: {
          "wtd":       { "Day": bucket, "Night": bucket },
          "prior_day": { "Day": bucket, "Night": bucket },
        }
      }
    Only depts with at least one record are included.
    """
    wtd_set = set(wtd_dates)

    # dept_code → period ("wtd"|"prior_day") → shift → bucket
    data = defaultdict(lambda: {
        "wtd":       {"Day": _empty_shift_bucket(), "Night": _empty_shift_bucket()},
        "prior_day": {"Day": _empty_shift_bucket(), "Night": _empty_shift_bucket()},
    })

    for rec in records:
        dc   = rec.get("dept_code")
        d    = rec.get("date")
        shift = rec.get("shift", "Day")
        if dc is None or d is None:
            continue
        if d in wtd_set:
            _add_to_bucket(data[dc]["wtd"][shift], rec)
        if d == prior_day:
            _add_to_bucket(data[dc]["prior_day"][shift], rec)

    # finalize
    result = {}
    for dc, periods in data.items():
        result[dc] = {}
        for period, shifts in periods.items():
            result[dc][period] = {s: _finalize_bucket(b) for s, b in shifts.items()}

    return result
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_dpp_attendance.py -v 2>&1
```

Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add "ORBIT – Daily People Pulse/04 – Pipelines & Architecture/dpp-pipeline/sections/__init__.py"
git add "ORBIT – Daily People Pulse/04 – Pipelines & Architecture/dpp-pipeline/sections/dpp_attendance.py"
git add "ORBIT – Daily People Pulse/04 – Pipelines & Architecture/dpp-pipeline/tests/test_dpp_attendance.py"
git commit -m "feat(dpp): add Section 01 attendance computation"
```

---

### Task 4: `sections/dpp_ncns.py`

**Files:**
- Create: `04 – Pipelines & Architecture/dpp-pipeline/sections/dpp_ncns.py`
- Create: `04 – Pipelines & Architecture/dpp-pipeline/tests/test_dpp_ncns.py`

NCNS records are those with a confirmed NCNS paycode and zero worked hours. Day number = consecutive calendar days with NCNS paycode in the scope window; any gap (approved leave or worked shift) resets the count.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_dpp_ncns.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from datetime import date
from sections.dpp_ncns import is_ncns_paycode, compute_ncns, compute_day_number

def test_ncns_paycode_detection():
    assert is_ncns_paycode("NCNS") is True
    assert is_ncns_paycode("No Call No Show") is True
    assert is_ncns_paycode("PTO PAID") is False
    assert is_ncns_paycode("") is False

def test_compute_ncns_filters_out_approved_leave():
    records = [
        {"eid": "1", "tm_name": "A, B", "dept_code": 2300,
         "schedule_group": "X", "reports_to": "Y",
         "date": date(2026,3,17), "scheduled_hours": 10.0,
         "worked_hours": 0.0, "paycode": "NCNS", "shift": "Day"},
        {"eid": "2", "tm_name": "C, D", "dept_code": 2300,
         "schedule_group": "X", "reports_to": "Y",
         "date": date(2026,3,17), "scheduled_hours": 10.0,
         "worked_hours": 0.0, "paycode": "PTO PAID", "shift": "Day"},
    ]
    scope_dates = [date(2026,3,15), date(2026,3,16), date(2026,3,17), date(2026,3,18)]
    result = compute_ncns(records, scope_dates)
    assert len(result) == 1
    assert result[0]["eid"] == "1"

def test_day_number_consecutive():
    all_records = [
        {"eid": "1", "date": date(2026,3,17), "paycode": "NCNS", "worked_hours": 0.0},
        {"eid": "1", "date": date(2026,3,18), "paycode": "NCNS", "worked_hours": 0.0},
    ]
    assert compute_day_number("1", date(2026,3,17), all_records) == 1
    assert compute_day_number("1", date(2026,3,18), all_records) == 2

def test_day_number_resets_on_gap():
    all_records = [
        {"eid": "1", "date": date(2026,3,16), "paycode": "NCNS",    "worked_hours": 0.0},
        {"eid": "1", "date": date(2026,3,17), "paycode": "PTO PAID","worked_hours": 0.0},
        {"eid": "1", "date": date(2026,3,18), "paycode": "NCNS",    "worked_hours": 0.0},
    ]
    assert compute_day_number("1", date(2026,3,18), all_records) == 1  # reset by gap

def test_ncns_sorted_by_name_then_date_desc():
    records = [
        {"eid": "1", "tm_name": "Smith, John", "dept_code": 2300,
         "schedule_group": "X", "reports_to": "Y",
         "date": date(2026,3,17), "scheduled_hours": 10.0,
         "worked_hours": 0.0, "paycode": "NCNS", "shift": "Day"},
        {"eid": "1", "tm_name": "Smith, John", "dept_code": 2300,
         "schedule_group": "X", "reports_to": "Y",
         "date": date(2026,3,18), "scheduled_hours": 10.0,
         "worked_hours": 0.0, "paycode": "NCNS", "shift": "Day"},
        {"eid": "2", "tm_name": "Adams, Mary", "dept_code": 2300,
         "schedule_group": "X", "reports_to": "Y",
         "date": date(2026,3,18), "scheduled_hours": 10.0,
         "worked_hours": 0.0, "paycode": "NCNS", "shift": "Day"},
    ]
    scope_dates = [date(2026,3,15), date(2026,3,16), date(2026,3,17), date(2026,3,18)]
    result = compute_ncns(records, scope_dates)
    names = [r["tm_name"] for r in result]
    assert names[0] == "Adams, Mary"         # A before S
    assert names[1] == "Smith, John"          # Smith 3/18 before 3/17 (desc date)
    assert result[1]["date"] == date(2026,3,18)
    assert result[2]["date"] == date(2026,3,17)
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest tests/test_dpp_ncns.py -v 2>&1
```

- [ ] **Step 3: Implement `sections/dpp_ncns.py`**

```python
# sections/dpp_ncns.py
"""
Section 02 — No Call No Show (NCNS).
Only records with NCNS paycodes and zero worked hours are included.
"""
from datetime import date, timedelta
from dpp_scope import ncns_recommendation

NCNS_PAYCODES = {"NCNS", "NO CALL NO SHOW", "NO_CALL_NO_SHOW"}

def is_ncns_paycode(paycode: str) -> bool:
    return paycode.strip().upper() in NCNS_PAYCODES

def compute_day_number(eid: str, target_date: date, all_records: list[dict]) -> int:
    """
    Walk backwards from target_date. Count consecutive NCNS days for this EID.
    Any day with a non-NCNS record (worked shift or approved leave) breaks the streak.
    """
    eid_dates = {
        r["date"]: r for r in all_records
        if r.get("eid") == eid and r.get("date") is not None
    }
    count = 1
    check = target_date - timedelta(days=1)
    while True:
        if check not in eid_dates:
            break  # no record → gap → stop
        prev = eid_dates[check]
        if is_ncns_paycode(prev.get("paycode", "")) and prev.get("worked_hours", 1) == 0.0:
            count += 1
            check -= timedelta(days=1)
        else:
            break  # worked or approved leave → reset
    return count

def compute_ncns(records: list[dict], scope_dates: list[date]) -> list[dict]:
    """
    Return NCNS rows sorted by TM Name (A–Z), then Date descending.
    Each row includes a `day_number` and `recommendation` field.
    """
    scope_set = set(scope_dates)
    ncns_rows = [
        r for r in records
        if r.get("date") in scope_set
        and is_ncns_paycode(r.get("paycode", ""))
        and r.get("worked_hours", 0.0) == 0.0
    ]

    enriched = []
    for r in ncns_rows:
        day_n = compute_day_number(r["eid"], r["date"], records)
        enriched.append({**r, "day_number": day_n,
                         "recommendation": ncns_recommendation(day_n)})

    return sorted(enriched, key=lambda x: (x["tm_name"], -x["date"].toordinal()))
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_dpp_ncns.py -v 2>&1
```

Expected: All 5 tests PASS

- [ ] **Step 5: Commit**

```bash
git add "ORBIT – Daily People Pulse/04 – Pipelines & Architecture/dpp-pipeline/sections/dpp_ncns.py"
git add "ORBIT – Daily People Pulse/04 – Pipelines & Architecture/dpp-pipeline/tests/test_dpp_ncns.py"
git commit -m "feat(dpp): add Section 02 NCNS detection and day-number logic"
```

---

## Chunk 4: Sections 03–04 — Unscheduled Work & Paycode Reconciler

### Task 5: `sections/dpp_unscheduled.py`

**Files:**
- Create: `04 – Pipelines & Architecture/dpp-pipeline/sections/dpp_unscheduled.py`

Threshold: worked_hours − scheduled_hours ≥ (10/60). Prior day only. No VET paycode on record.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_dpp_sections.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from datetime import date
from sections.dpp_unscheduled import compute_unscheduled

PRIOR = date(2026, 3, 18)

def _rec(eid, scheduled, worked, paycode="", dept=2300):
    return {"eid": eid, "tm_name": f"TM {eid}", "dept_code": dept,
            "schedule_group": "X", "reports_to": "Y",
            "date": PRIOR, "scheduled_hours": scheduled,
            "worked_hours": worked, "paycode": paycode, "shift": "Day"}

def test_over_threshold_included():
    records = [_rec("1", 10.0, 10.5)]   # +30 min → over threshold
    result = compute_unscheduled(records, PRIOR)
    assert len(result) == 1
    assert abs(result[0]["over_hours"] - 0.5) < 0.001

def test_under_threshold_excluded():
    records = [_rec("2", 10.0, 10.08)]  # +5 min → below 10-min threshold
    result = compute_unscheduled(records, PRIOR)
    assert len(result) == 0

def test_vet_approved_excluded():
    records = [_rec("3", 10.0, 10.5, paycode="VET")]
    result = compute_unscheduled(records, PRIOR)
    assert len(result) == 0

def test_wrong_date_excluded():
    rec = _rec("4", 10.0, 10.5)
    rec["date"] = date(2026, 3, 17)   # not prior day
    result = compute_unscheduled([rec], PRIOR)
    assert len(result) == 0
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest tests/test_dpp_sections.py -v 2>&1
```

- [ ] **Step 3: Implement**

```python
# sections/dpp_unscheduled.py
"""Section 03 — Unscheduled but Worked (10+ min over, prior day, no VET)."""
from datetime import date

UNSCHEDULED_THRESHOLD_HOURS = 10 / 60  # 10 minutes
VET_PAYCODES = {"VET", "VOLUNTARY EXTENDED TIME"}

def compute_unscheduled(records: list[dict], prior_day: date) -> list[dict]:
    """Return rows sorted by TM Name where worked > scheduled + threshold, no VET."""
    result = []
    for r in records:
        if r.get("date") != prior_day:
            continue
        if r.get("paycode", "").upper() in VET_PAYCODES:
            continue
        over = r.get("worked_hours", 0.0) - r.get("scheduled_hours", 0.0)
        if over < UNSCHEDULED_THRESHOLD_HOURS:
            continue
        result.append({**r, "over_hours": over})
    return sorted(result, key=lambda x: x["tm_name"])
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_dpp_sections.py::test_over_threshold_included \
  tests/test_dpp_sections.py::test_under_threshold_excluded \
  tests/test_dpp_sections.py::test_vet_approved_excluded \
  tests/test_dpp_sections.py::test_wrong_date_excluded -v 2>&1
```

Expected: All 4 PASS

- [ ] **Step 5: Commit**

```bash
git add "ORBIT – Daily People Pulse/04 – Pipelines & Architecture/dpp-pipeline/sections/dpp_unscheduled.py"
git add "ORBIT – Daily People Pulse/04 – Pipelines & Architecture/dpp-pipeline/tests/test_dpp_sections.py"
git commit -m "feat(dpp): add Section 03 unscheduled-but-worked module"
```

---

### Task 6: `sections/dpp_paycode.py`

**Files:**
- Create: `04 – Pipelines & Architecture/dpp-pipeline/sections/dpp_paycode.py`

Identifies rows where total time-off paycodes applied don't match scheduled hours.

- [ ] **Step 1: Add failing tests to `test_dpp_sections.py`**

```python
from sections.dpp_paycode import compute_paycode_mismatches

SCOPE = [date(2026,3,15), date(2026,3,16), date(2026,3,17), date(2026,3,18)]

def test_over_applied_detected():
    records = [{"eid": "1", "tm_name": "A, B", "dept_code": 2300,
                "schedule_group": "X", "reports_to": "Y",
                "date": date(2026,3,17), "scheduled_hours": 10.0,
                "worked_hours": 0.0, "paycode": "PTO PAID",
                "paycode_hours": 10.5, "shift": "Day"}]
    result = compute_paycode_mismatches(records, SCOPE)
    assert len(result) == 1
    assert result[0]["mismatch_type"] == "over"

def test_under_applied_detected():
    records = [{"eid": "2", "tm_name": "C, D", "dept_code": 2300,
                "schedule_group": "X", "reports_to": "Y",
                "date": date(2026,3,17), "scheduled_hours": 10.0,
                "worked_hours": 0.0, "paycode": "Personal Unpaid Call Off",
                "paycode_hours": 7.0, "shift": "Day"}]
    result = compute_paycode_mismatches(records, SCOPE)
    assert len(result) == 1
    assert result[0]["mismatch_type"] == "under"

def test_matching_paycode_excluded():
    records = [{"eid": "3", "tm_name": "E, F", "dept_code": 2300,
                "schedule_group": "X", "reports_to": "Y",
                "date": date(2026,3,17), "scheduled_hours": 10.0,
                "worked_hours": 0.0, "paycode": "PTO PAID",
                "paycode_hours": 10.0, "shift": "Day"}]
    result = compute_paycode_mismatches(records, SCOPE)
    assert len(result) == 0
```

- [ ] **Step 2: Run to verify failure**

- [ ] **Step 3: Implement `sections/dpp_paycode.py`**

```python
# sections/dpp_paycode.py
"""Section 04 — Paycode Reconciler. Detects over/under-applied time-off paycodes."""
from datetime import date

LEAVE_PAYCODES = {"PTO PAID", "UTO", "PERSONAL UNPAID CALL OFF",
                  "SICK", "BEREAVEMENT", "JURY DUTY"}
MISMATCH_TOLERANCE = 0.0  # no tolerance — any delta flagged

def _is_leave_paycode(paycode: str) -> bool:
    return paycode.strip().upper() in LEAVE_PAYCODES

def _action_text(mismatch_type: str, delta_hours: float) -> str:
    delta_hhmm = _decimal_to_hhmm(abs(delta_hours))
    if mismatch_type == "over":
        return f"Over-applied by {delta_hhmm} \u2014 review & correct paycode entry"
    return (f"Under-applied by {delta_hhmm} \u2014 paycode does not cover full "
            "scheduled shift; review for missing paycode or NCNS designation")

def _decimal_to_hhmm(h: float) -> str:
    hours = int(h)
    minutes = round((h - hours) * 60)
    return f"{hours:02d}:{minutes:02d}"

def compute_paycode_mismatches(records: list[dict], scope_dates: list[date]) -> list[dict]:
    """
    Expects each record to have a `paycode_hours` field (hours the paycode covers).
    Returns rows sorted by TM Name (A–Z), then Date descending.
    """
    scope_set = set(scope_dates)
    result = []
    for r in records:
        if r.get("date") not in scope_set:
            continue
        if not _is_leave_paycode(r.get("paycode", "")):
            continue
        sched = r.get("scheduled_hours", 0.0)
        applied = r.get("paycode_hours", 0.0)
        delta = applied - sched
        if abs(delta) <= MISMATCH_TOLERANCE:
            continue
        mtype = "over" if delta > 0 else "under"
        result.append({**r, "mismatch_type": mtype, "delta_hours": delta,
                       "action": _action_text(mtype, delta)})
    return sorted(result, key=lambda x: (x["tm_name"], -x["date"].toordinal()))
```

- [ ] **Step 4: Run all section tests so far**

```bash
python -m pytest tests/test_dpp_sections.py -v 2>&1
```

Expected: All 7 tests PASS

- [ ] **Step 5: Commit**

```bash
git add "ORBIT – Daily People Pulse/04 – Pipelines & Architecture/dpp-pipeline/sections/dpp_paycode.py"
git add "ORBIT – Daily People Pulse/04 – Pipelines & Architecture/dpp-pipeline/tests/test_dpp_sections.py"
git commit -m "feat(dpp): add Section 04 paycode reconciler"
```

---

## Chunk 5: Sections 05–06 — Time Off & Overtime

### Task 7: `sections/dpp_time_off.py`

**Files:**
- Create: `04 – Pipelines & Architecture/dpp-pipeline/sections/dpp_time_off.py`

Scope: next 7 calendar days from report date. Groups by dept, sorts by date ascending.

- [ ] **Step 1: Add failing tests**

```python
# append to tests/test_dpp_sections.py
from sections.dpp_time_off import compute_time_off
from datetime import date

def test_time_off_within_window():
    report_date = date(2026, 3, 19)
    records = [
        {"eid": "1", "tm_name": "A, B", "dept_code": 2300,
         "reports_to": "Y", "date": date(2026, 3, 20),
         "paycode": "PTO PAID", "paycode_hours": 10.0, "scheduled_hours": 10.0,
         "worked_hours": 0.0, "shift": "Day", "schedule_group": "X"},
        {"eid": "1", "tm_name": "A, B", "dept_code": 2300,
         "reports_to": "Y", "date": date(2026, 3, 21),
         "paycode": "PTO PAID", "paycode_hours": 10.0, "scheduled_hours": 10.0,
         "worked_hours": 0.0, "shift": "Day", "schedule_group": "X"},
    ]
    result = compute_time_off(records, report_date)
    assert 2300 in result
    assert result[2300][0]["tm_name"] == "A, B"
    # Multi-day blocks collapsed into one row
    assert len(result[2300]) == 1
    assert result[2300][0]["total_hours"] == 20.0

def test_time_off_outside_window_excluded():
    report_date = date(2026, 3, 19)
    records = [
        {"eid": "1", "tm_name": "A, B", "dept_code": 2300,
         "reports_to": "Y", "date": date(2026, 3, 27),  # outside 7-day window
         "paycode": "PTO PAID", "paycode_hours": 10.0, "scheduled_hours": 10.0,
         "worked_hours": 0.0, "shift": "Day", "schedule_group": "X"},
    ]
    result = compute_time_off(records, report_date)
    assert 2300 not in result
```

- [ ] **Step 2: Run to verify failure**

- [ ] **Step 3: Implement `sections/dpp_time_off.py`**

```python
# sections/dpp_time_off.py
"""Section 05 — Upcoming Time Off. Next 7 days, grouped by dept, sorted by date ascending."""
from datetime import date, timedelta
from collections import defaultdict

LEAVE_PAYCODES = {"PTO PAID", "UTO", "PERSONAL UNPAID CALL OFF",
                  "SICK", "BEREAVEMENT", "JURY DUTY"}

def compute_time_off(records: list[dict], report_date: date) -> dict:
    """
    Returns { dept_code: [ time_off_row, ... ] } sorted by date ascending.
    Multi-day consecutive absences for the same TM are collapsed into one row.
    """
    window_start = report_date
    window_end   = report_date + timedelta(days=6)

    # Collect leave records in window
    leave = defaultdict(lambda: defaultdict(list))  # dept → eid → [rec]
    for r in records:
        d = r.get("date")
        if d is None or not (window_start <= d <= window_end):
            continue
        if r.get("paycode", "").upper().strip() not in LEAVE_PAYCODES:
            continue
        leave[r["dept_code"]][r["eid"]].append(r)

    result = {}
    for dept_code, by_eid in leave.items():
        rows = []
        for eid, recs in by_eid.items():
            recs_sorted = sorted(recs, key=lambda x: x["date"])
            total_pto = sum(r.get("paycode_hours", 0.0)
                           for r in recs_sorted
                           if "PTO" in r.get("paycode","").upper())
            total_uto = sum(r.get("paycode_hours", 0.0)
                           for r in recs_sorted
                           if "UTO" in r.get("paycode","").upper())
            dates_str = ", ".join(r["date"].strftime("%m/%d") for r in recs_sorted)
            rows.append({
                "eid":        eid,
                "tm_name":    recs_sorted[0]["tm_name"],
                "reports_to": recs_sorted[0].get("reports_to", ""),
                "dates_str":  dates_str,
                "dates":      [r["date"] for r in recs_sorted],
                "pto_hours":  total_pto,
                "uto_hours":  total_uto,
                "total_hours": total_pto + total_uto,
            })
        rows.sort(key=lambda x: min(x["dates"]))  # earliest date first
        result[dept_code] = rows

    return result
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_dpp_sections.py -v 2>&1
```

---

### Task 8: `sections/dpp_overtime.py`

**Files:**
- Create: `04 – Pipelines & Architecture/dpp-pipeline/sections/dpp_overtime.py`

CRITICAL/WATCH with explicit precedence: CRITICAL if WTD worked ≥ 60; WATCH (only if not CRITICAL) if WTD ≥ 58 or projected > 60.

- [ ] **Step 1: Add failing tests**

```python
from sections.dpp_overtime import compute_overtime, classify_risk

def test_critical_classification():
    level, rec = classify_risk(61.0, 0.0)
    assert level == "CRITICAL"

def test_watch_classification_by_wtd():
    level, rec = classify_risk(58.5, 5.0)   # WTD >= 58, projected 63.5
    assert level == "WATCH"

def test_watch_classification_by_projection():
    level, rec = classify_risk(55.0, 7.0)   # WTD < 58, projected 62 > 60
    assert level == "WATCH"

def test_no_risk():
    level, rec = classify_risk(40.0, 15.0)  # projected 55 — fine
    assert level is None

def test_critical_takes_precedence_over_watch():
    # 60+ WTD: meets both CRITICAL (>=60) and WATCH (>=58) — must be CRITICAL
    level, rec = classify_risk(60.0, 10.0)
    assert level == "CRITICAL"
```

- [ ] **Step 2: Run to verify failure**

- [ ] **Step 3: Implement `sections/dpp_overtime.py`**

```python
# sections/dpp_overtime.py
"""Section 06 — 60+ Hour Watch. CRITICAL/WATCH with explicit precedence."""
from dpp_scope import OT_CRITICAL_HOURS, OT_WATCH_HOURS, OT_WATCH_PROJECTED

CRITICAL_REC = ("Immediate manager intervention \u2014 adjust remaining schedule to "
                "prevent/address exceedance; review and document business justification per SOP")
WATCH_REC    = ("Monitor closely; do not approve additional OT; review upcoming schedule "
                "and cap remaining hours below 60")

def classify_risk(wtd_worked: float, remaining_scheduled: float) -> tuple:
    """
    Returns (risk_level, recommendation) where risk_level is 'CRITICAL', 'WATCH', or None.
    CRITICAL takes precedence: evaluated first.
    """
    if wtd_worked >= OT_CRITICAL_HOURS:
        return ("CRITICAL", CRITICAL_REC)
    projected = wtd_worked + remaining_scheduled
    if wtd_worked >= OT_WATCH_HOURS or projected > OT_WATCH_PROJECTED:
        return ("WATCH", WATCH_REC)
    return (None, "")

def compute_overtime(records: list[dict], wtd_dates: list) -> list[dict]:
    """
    Aggregate WTD worked hours per EID, find remaining scheduled hours,
    classify risk, return only CRITICAL and WATCH rows sorted by risk (CRITICAL first).
    """
    from collections import defaultdict
    wtd_set = set(wtd_dates)

    wtd_worked     = defaultdict(float)
    remaining_sched = defaultdict(float)
    meta           = {}  # eid → latest record for name/dept/etc.

    for r in records:
        eid = r.get("eid")
        if not eid:
            continue
        if r.get("date") in wtd_set:
            wtd_worked[eid] += r.get("worked_hours", 0.0)
        else:
            remaining_sched[eid] += r.get("scheduled_hours", 0.0)
        meta[eid] = r  # overwrite — last seen is fine for name/dept

    result = []
    for eid, wtd in wtd_worked.items():
        rem = remaining_sched.get(eid, 0.0)
        level, rec = classify_risk(wtd, rem)
        if level is None:
            continue
        m = meta[eid]
        result.append({
            "eid":                eid,
            "tm_name":            m.get("tm_name", ""),
            "dept_code":          m.get("dept_code"),
            "schedule_group":     m.get("schedule_group", ""),
            "reports_to":         m.get("reports_to", ""),
            "wtd_worked":         wtd,
            "remaining_scheduled": rem,
            "projected_total":    wtd + rem,
            "risk_level":         level,
            "recommendation":     rec,
        })

    # CRITICAL first, then WATCH; within each level sort by projected total desc
    order = {"CRITICAL": 0, "WATCH": 1}
    return sorted(result, key=lambda x: (order[x["risk_level"]], -x["projected_total"]))
```

- [ ] **Step 4: Run all section tests**

```bash
python -m pytest tests/ -v 2>&1
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add "ORBIT – Daily People Pulse/04 – Pipelines & Architecture/dpp-pipeline/sections/dpp_time_off.py"
git add "ORBIT – Daily People Pulse/04 – Pipelines & Architecture/dpp-pipeline/sections/dpp_overtime.py"
git commit -m "feat(dpp): add Section 05 time off and Section 06 overtime watch"
```

---

## Chunk 6: AI Insights

### Task 9: `dpp_insights.py`

**Files:**
- Create: `04 – Pipelines & Architecture/dpp-pipeline/dpp_insights.py`

Calls the Anthropic API via `urllib.request` (no SDK). Takes computed section data and a plain-text data summary, returns insight strings per dept/section. Falls back to a stub string on API error.

**Before implementing:** Confirm the `ANTHROPIC_API_KEY` environment variable is set in your Phoenix/local environment. The pipeline reads it from `os.environ`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_dpp_insights.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from unittest.mock import patch, MagicMock
from dpp_insights import build_attendance_prompt, build_time_off_prompt, FALLBACK_INSIGHT

def test_attendance_prompt_contains_dept_name():
    prompt = build_attendance_prompt("Outbound Technicians", {
        "wtd": {"Day": {"pct": 0.823, "scheduled_hours": 904.5, "worked_hours": 744.3},
                "Night": {"pct": 0.785, "scheduled_hours": 740.0, "worked_hours": 581.0}},
        "prior_day": {"Day": {"pct": 0.782, "scheduled_hours": 399.0, "worked_hours": 312.0,
                              "full_missed": 7, "full_missed_hours": 70.0,
                              "early_departures": 4, "early_departure_hours": 8.5,
                              "late_arrivals": 2, "late_arrival_hours": 0.5},
                      "Night": {"pct": 0.814, "scheduled_hours": 253.0, "worked_hours": 206.0,
                                "full_missed": 3, "full_missed_hours": 30.0,
                                "early_departures": 2, "early_departure_hours": 3.0,
                                "late_arrivals": 1, "late_arrival_hours": 0.25}},
    })
    assert "Outbound Technicians" in prompt
    assert "82.3%" in prompt or "82" in prompt

def test_fallback_insight_is_string():
    assert isinstance(FALLBACK_INSIGHT, str)
    assert len(FALLBACK_INSIGHT) > 0
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest tests/test_dpp_insights.py -v 2>&1
```

- [ ] **Step 3: Implement `dpp_insights.py`**

```python
# dpp_insights.py
"""
AI Insights — calls Anthropic API to generate narrative insight text.
Uses urllib.request only (no SDK). Reads ANTHROPIC_API_KEY from environment.
Falls back to FALLBACK_INSIGHT on any API error.
"""
import json
import os
import urllib.request
import urllib.error
from datetime import date

FALLBACK_INSIGHT = "Insufficient data to generate an insight for this department this period."
API_URL = "https://api.anthropic.com/v1/messages"
MODEL   = "claude-haiku-4-5-20251001"    # verified: Haiku 4.5 model ID as of 2026-03-23
MAX_TOKENS = 300

# ── Prompt builders ───────────────────────────────────────────────────────────

def _pct_str(pct: float) -> str:
    return f"{pct * 100:.1f}%"

def _hhmm(decimal_hours: float) -> str:
    h = int(decimal_hours)
    m = round((decimal_hours - h) * 60)
    return f"{h:02d}:{m:02d}"

def build_attendance_prompt(dept_name: str, data: dict) -> str:
    wtd = data.get("wtd", {})
    pd  = data.get("prior_day", {})

    lines = [
        f"Department: {dept_name}",
        f"WTD Day attendance: {_pct_str(wtd.get('Day',{}).get('pct',0))} "
        f"({_hhmm(wtd.get('Day',{}).get('worked_hours',0))} of "
        f"{_hhmm(wtd.get('Day',{}).get('scheduled_hours',0))} hrs)",
        f"WTD Night attendance: {_pct_str(wtd.get('Night',{}).get('pct',0))} "
        f"({_hhmm(wtd.get('Night',{}).get('worked_hours',0))} of "
        f"{_hhmm(wtd.get('Night',{}).get('scheduled_hours',0))} hrs)",
        "",
        "Prior Day:",
        f"  Day: {_pct_str(pd.get('Day',{}).get('pct',0))} — "
        f"{pd.get('Day',{}).get('full_missed',0)} full missed shifts "
        f"({_hhmm(pd.get('Day',{}).get('full_missed_hours',0))} hrs), "
        f"{pd.get('Day',{}).get('early_departures',0)} early departures "
        f"({_hhmm(pd.get('Day',{}).get('early_departure_hours',0))} hrs), "
        f"{pd.get('Day',{}).get('late_arrivals',0)} late arrivals",
        f"  Night: {_pct_str(pd.get('Night',{}).get('pct',0))} — "
        f"{pd.get('Night',{}).get('full_missed',0)} full missed shifts "
        f"({_hhmm(pd.get('Night',{}).get('full_missed_hours',0))} hrs), "
        f"{pd.get('Night',{}).get('early_departures',0)} early departures "
        f"({_hhmm(pd.get('Night',{}).get('early_departure_hours',0))} hrs)",
    ]

    return (
        "You are generating a brief AI Insight for an HR daily report. "
        "RULES: (1) Do NOT re-state the numbers in the data above — they already appear in the report. "
        "(2) Interpret trends, identify risks, and recommend one specific action. "
        "(3) Do NOT make disciplinary recommendations or speculate about protected characteristics. "
        "(4) Write in plain, professional English. Maximum 4 sentences. "
        "(5) If there is nothing meaningful to say, respond with exactly: "
        f"'{FALLBACK_INSIGHT}'\n\nDATA:\n" + "\n".join(lines)
    )

def build_time_off_prompt(dept_name: str, rows: list[dict], dept_attendance_pct: float) -> str:
    if not rows:
        return ""
    summary_lines = [
        f"  {r['tm_name']}: {r['dates_str']} — "
        f"PTO {_hhmm(r['pto_hours'])} / UTO {_hhmm(r['uto_hours'])} "
        f"/ Total {_hhmm(r['total_hours'])}"
        for r in rows
    ]
    return (
        "You are generating a brief AI Insight about upcoming time off for an HR daily report. "
        "RULES: (1) Do NOT re-state the dates or hours — they already appear in the table. "
        "(2) Identify coverage risks, flag any patterns (multi-day absences, same-day overlap), "
        "and recommend one specific action. "
        "(3) Do NOT make disciplinary recommendations or speculate about protected characteristics. "
        "(4) Write in plain, professional English. Maximum 3 sentences. "
        "(5) If there is nothing meaningful to say, respond with exactly: "
        f"'{FALLBACK_INSIGHT}'\n\n"
        f"Department: {dept_name}\n"
        f"WTD attendance: {_pct_str(dept_attendance_pct)}\n"
        "Upcoming Time Off:\n" + "\n".join(summary_lines)
    )

# ── API caller ────────────────────────────────────────────────────────────────

def call_anthropic(prompt: str) -> str:
    """
    Call the Anthropic Messages API and return the text content.
    Returns FALLBACK_INSIGHT on any error.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("  [warn] ANTHROPIC_API_KEY not set — using fallback insight")
        return FALLBACK_INSIGHT

    payload = json.dumps({
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "x-api-key":         api_key,
            "anthropic-version": "2023-06-01",
            "content-type":      "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body["content"][0]["text"].strip()
    except (urllib.error.URLError, KeyError, json.JSONDecodeError) as exc:
        print(f"  [warn] Anthropic API error: {exc} — using fallback insight")
        return FALLBACK_INSIGHT

# ── Public interface ──────────────────────────────────────────────────────────

def generate_attendance_insight(dept_name: str, data: dict) -> str:
    prompt = build_attendance_prompt(dept_name, data)
    return call_anthropic(prompt)

def generate_time_off_insight(dept_name: str, rows: list[dict],
                               dept_attendance_pct: float) -> str:
    if not rows:
        return FALLBACK_INSIGHT
    prompt = build_time_off_prompt(dept_name, rows, dept_attendance_pct)
    return call_anthropic(prompt)
```

- [ ] **Step 4: Run tests (no API key required — tests mock or test prompt shape only)**

```bash
python -m pytest tests/test_dpp_insights.py -v 2>&1
```

Expected: Both tests PASS

- [ ] **Step 5: Commit**

```bash
git add "ORBIT – Daily People Pulse/04 – Pipelines & Architecture/dpp-pipeline/dpp_insights.py"
git add "ORBIT – Daily People Pulse/04 – Pipelines & Architecture/dpp-pipeline/tests/test_dpp_insights.py"
git commit -m "feat(dpp): add AI insights module with Anthropic API caller and fallback"
```

---

## Chunk 7: HTML Renderer & Orchestrator

### Task 10: `dpp_html_renderer.py`

**Files:**
- Create: `04 – Pipelines & Architecture/dpp-pipeline/dpp_html_renderer.py`

Takes all section data dicts and insight strings, returns a complete HTML string.
The CSS and structure matches the POC (`05 – Application & UX/DPP_POC_Mock.html`).
This is the longest file — keep rendering logic isolated here so no other module touches HTML.

**Implementation note:** The HTML string is assembled via Python f-strings and helper functions — one function per section. Do not use Jinja2 or any template engine. This keeps the zero-external-deps constraint.

- [ ] **Step 1: Write a smoke test**

```python
# tests/test_dpp_renderer.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from datetime import date
from dpp_html_renderer import render_report

def _minimal_data():
    from datetime import date
    return {
        "site":        "SDF4",
        "report_date": date(2026, 3, 19),
        "windows":     {"mode": "WTD", "wtd_start": date(2026,3,15),
                        "wtd_end": date(2026,3,18), "prior_day": date(2026,3,18)},
        "attendance":  {},
        "ncns":        [],
        "unscheduled": [],
        "paycode":     [],
        "time_off":    {},
        "overtime":    [],
        "insights":    {"attendance": {}, "time_off": {}},
        "dept_registry": {},
    }

def test_render_returns_html_string():
    html = render_report(_minimal_data())
    assert isinstance(html, str)
    assert "<!DOCTYPE html>" in html
    assert "Daily People Pulse" in html
    assert "SDF4" in html

def test_render_has_all_section_ids():
    html = render_report(_minimal_data())
    for section_id in ["section-01", "section-02", "section-03",
                       "section-04", "section-05", "section-06", "summary"]:
        assert section_id in html, f"Missing section: {section_id}"
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest tests/test_dpp_renderer.py -v 2>&1
```

- [ ] **Step 3: Implement `dpp_html_renderer.py`**

The renderer assembles the same CSS block from `DPP_POC_Mock.html` as a Python constant, then builds each section with helper functions that return HTML strings. Refer to the POC for exact CSS class names — they are already defined and validated.

```python
# dpp_html_renderer.py
"""
HTML Renderer — assembles all section data into the final DPP report HTML string.
Reference: 05 – Application & UX/DPP_POC_Mock.html for CSS and structure.
No external dependencies — pure f-string assembly.
"""
from datetime import date, datetime
from dpp_scope import attendance_color_class, DEPT_REGISTRY

# ── helpers ───────────────────────────────────────────────────────────────────

def _hhmm(decimal_hours: float) -> str:
    h = int(decimal_hours)
    m = round((decimal_hours - h) * 60)
    return f"{h:02d}:{m:02d}"

def _pct(rate: float) -> str:
    return f"{rate * 100:.1f}%"

def _esc(s: str) -> str:
    """Minimal HTML escaping."""
    return (str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))

def _date_label(d: date) -> str:
    return d.strftime("%m/%d/%Y") if d else ""

# ── CSS loader ────────────────────────────────────────────────────────────────
# CSS is read from the POC HTML file at render time (not import time) so that
# a missing file raises at run-time with a clear error, not on import.

def _load_css() -> str:
    """Extract CSS from POC HTML (single source of truth). Called once per render."""
    from pathlib import Path
    poc_path = (
        Path(__file__).parent
        / "../../../05 \u2013 Application & UX/DPP_POC_Mock.html"
    )
    raw = poc_path.read_text(encoding="utf-8")
    return raw.split("<style>")[1].split("</style>")[0]

# ── Section renderers ─────────────────────────────────────────────────────────

def _render_att_bucket(bucket: dict, shift: str, has_night: bool) -> str:
    if shift == "Night" and not has_night:
        return ""
    cls = attendance_color_class(bucket.get("pct", 0))
    sched = bucket.get("scheduled_hours", 0)
    worked = bucket.get("worked_hours", 0)
    return f"""
      <div class="att-shift">
        <div class="shift-label">{_esc(shift)}</div>
        <div class="att-pct {cls}">{_pct(bucket.get('pct', 0))}</div>
        <div class="att-fraction">{_hhmm(worked)} of {_hhmm(sched)} hrs worked/sched</div>
      </div>"""

def _render_loss_bullets(bucket: dict) -> str:
    items = []
    if bucket.get("full_missed", 0):
        items.append(f"<li>{bucket['full_missed']} full missed shift"
                     f"{'s' if bucket['full_missed'] != 1 else ''} "
                     f"({_hhmm(bucket.get('full_missed_hours', 0))} hrs)</li>")
    if bucket.get("early_departures", 0):
        items.append(f"<li>{bucket['early_departures']} Early Departure"
                     f"{'s' if bucket['early_departures'] != 1 else ''} "
                     f"({_hhmm(bucket.get('early_departure_hours', 0))} hrs)</li>")
    if bucket.get("late_arrivals", 0):
        items.append(f"<li>{bucket['late_arrivals']} Late Arrival"
                     f"{'s' if bucket['late_arrivals'] != 1 else ''} "
                     f"({_hhmm(bucket.get('late_arrival_hours', 0))} hrs)</li>")
    if not items:
        return ""
    return "<ul class='att-bullets'>" + "".join(items) + "</ul>"

def _render_attendance_dept(dept_key: str, dept_info: dict,
                             att_data: dict, prior_day: date,
                             wtd_start: date, wtd_end: date,
                             insight: str) -> str:
    has_night = dept_info.get("has_night", True)
    code_badge = (f"<span class='dept-code'>{dept_info['code']}</span>"
                  if dept_info.get("code") else "")
    night_note = ("<span class='dept-note'>Day shift only at this site</span>"
                  if not has_night else "")
    no_night_card = ("<div class='no-night' style='margin-top:8px;'>"
                     "Night shift not active at this site for this department.</div>"
                     if not has_night else "")

    wtd = att_data.get("wtd", {})
    pd  = att_data.get("prior_day", {})

    wtd_day   = wtd.get("Day",   {"pct": 0, "scheduled_hours": 0, "worked_hours": 0})
    wtd_night = wtd.get("Night", {"pct": 0, "scheduled_hours": 0, "worked_hours": 0})
    pd_day    = pd.get("Day",    {"pct": 0, "scheduled_hours": 0, "worked_hours": 0})
    pd_night  = pd.get("Night",  {"pct": 0, "scheduled_hours": 0, "worked_hours": 0})

    pd_label  = (f"{prior_day.strftime('%A, %B ')}{prior_day.day}"
                 if prior_day else "Prior Day")
    wtd_label = (f"Sun {wtd_start.month}/{wtd_start.day} \u2013 "
                 f"{wtd_end.strftime('%a ')}{wtd_end.month}/{wtd_end.day}"
                 ) if wtd_start else ""

    insight_html = (f"<div class='insight-box'><div class='ib-label'>AI Insight</div>"
                    f"<p>{_esc(insight)}</p></div>") if insight else ""

    pd_night_section = ""
    if has_night:
        pd_night_section = f"""
        <div class='att-divider'></div>
        <div class='att-break-label'>Hours Lost — Night</div>
        {_render_loss_bullets(pd_night)}"""

    return f"""
  <div class='dept-section no-break'>
    <div class='dept-hdr'>{_esc(dept_info['label'])} {code_badge} {night_note}</div>
    <div class='att-grid'>
      <div class='att-card'>
        <div class='att-period'>Week to Date &middot; {wtd_label}</div>
        <div class='att-shifts'>
          {_render_att_bucket(wtd_day, 'Day', True)}
          {_render_att_bucket(wtd_night, 'Night', has_night)}
        </div>
        {no_night_card}
      </div>
      <div class='att-card'>
        <div class='att-period'>Prior Day &middot; {pd_label}</div>
        <div class='att-shifts'>
          {_render_att_bucket(pd_day, 'Day', True)}
          {_render_att_bucket(pd_night, 'Night', has_night)}
        </div>
        <div class='att-divider'></div>
        <div class='att-break-label'>Hours Lost &mdash; Day</div>
        {_render_loss_bullets(pd_day)}
        {pd_night_section}
      </div>
    </div>
    {insight_html}
  </div>"""

def _render_ncns_table(rows: list[dict]) -> str:
    if not rows:
        return "<p style='font-size:.8rem;color:var(--tm);font-style:italic;'>No NCNS records in this period.</p>"
    trs = "".join(f"""
      <tr>
        <td class='eid'>{_esc(r['eid'])}</td>
        <td class='name'>{_esc(r['tm_name'])}</td>
        <td class='dept'>{_esc(r.get('dept_label',''))}</td>
        <td>{_esc(r.get('schedule_group',''))}</td>
        <td>{_esc(r.get('reports_to',''))}</td>
        <td>{r['date'].strftime('%m/%d') if r.get('date') else ''}</td>
        <td class='rec'><strong>Day {r.get('day_number',1)}:</strong> {_esc(r.get('recommendation',''))}</td>
      </tr>""" for r in rows)
    return f"""<table><thead><tr>
      <th>EID</th><th>TM Name</th><th>Department</th><th>Schedule Group</th>
      <th>Reports To</th><th>Date</th><th>Recommended Action</th>
    </tr></thead><tbody>{trs}</tbody></table>"""

def _render_unscheduled_table(rows: list[dict]) -> str:
    if not rows:
        return "<p style='font-size:.8rem;color:var(--tm);font-style:italic;'>No unscheduled work identified for this period.</p>"
    trs = "".join(f"""
      <tr>
        <td class='eid'>{_esc(r['eid'])}</td>
        <td class='name'>{_esc(r['tm_name'])}</td>
        <td class='dept'>{_esc(r.get('dept_label',''))}</td>
        <td>{_esc(r.get('schedule_group',''))}</td>
        <td>{_esc(r.get('reports_to',''))}</td>
        <td class='num'>{_hhmm(r.get('scheduled_hours',0))}</td>
        <td class='num'>{_hhmm(r.get('worked_hours',0))}</td>
        <td class='over'>+{_hhmm(r.get('over_hours',0))}</td>
      </tr>""" for r in rows)
    return f"""<table><thead><tr>
      <th>EID</th><th>TM Name</th><th>Department</th><th>Schedule Group</th>
      <th>Reports To</th><th style='text-align:right'>Scheduled</th>
      <th style='text-align:right'>Worked</th><th style='text-align:right'>Over</th>
    </tr></thead><tbody>{trs}</tbody></table>"""

def _render_paycode_table(rows: list[dict]) -> str:
    if not rows:
        return "<p style='font-size:.8rem;color:var(--tm);font-style:italic;'>No paycode mismatches in this period.</p>"
    trs = "".join(f"""
      <tr>
        <td class='eid'>{_esc(r['eid'])}</td>
        <td class='name'>{_esc(r['tm_name'])}</td>
        <td class='dept'>{_esc(r.get('dept_label',''))}</td>
        <td>{_esc(r.get('schedule_group',''))}</td>
        <td>{_esc(r.get('reports_to',''))}</td>
        <td>{r['date'].strftime('%m/%d') if r.get('date') else ''}</td>
        <td class='num'>{_hhmm(r.get('scheduled_hours',0))}</td>
        <td class='num'>{_hhmm(r.get('paycode_hours',0))}</td>
        <td>{_esc(r.get('paycode',''))}</td>
        <td class='rec'>{_esc(r.get('action',''))}</td>
      </tr>""" for r in rows)
    return f"""<table><thead><tr>
      <th>EID</th><th>TM Name</th><th>Department</th><th>Schedule Group</th>
      <th>Reports To</th><th>Date</th>
      <th style='text-align:right'>Scheduled</th><th style='text-align:right'>Applied</th>
      <th>Paycodes</th><th>Action</th>
    </tr></thead><tbody>{trs}</tbody></table>"""

def _render_time_off_dept(dept_info: dict, rows: list[dict], insight: str) -> str:
    dept_label = _esc(dept_info.get("label", ""))
    code_badge = (f"<span class='dept-code'>{dept_info['code']}</span>"
                  if dept_info.get("code") else "")
    if not rows:
        empty = "<p style='font-size:.8rem;color:var(--tm);font-style:italic;padding:10px 0'>No planned time off this week for this department.</p>"
    else:
        trs = "".join(f"""
          <tr>
            <td class='eid'>{_esc(r['eid'])}</td>
            <td class='name'>{_esc(r['tm_name'])}</td>
            <td>{_esc(r.get('reports_to',''))}</td>
            <td>{_esc(r.get('dates_str',''))}</td>
            <td class='num'>{_hhmm(r.get('pto_hours',0))}</td>
            <td class='num'>{_hhmm(r.get('uto_hours',0))}</td>
            <td class='num'>{_hhmm(r.get('total_hours',0))}</td>
          </tr>""" for r in rows)
        empty = f"""<table><thead><tr>
          <th>EID</th><th>TM Name</th><th>Reports To</th><th>Date(s)</th>
          <th style='text-align:right'>PTO</th><th style='text-align:right'>UTO</th>
          <th style='text-align:right'>Total</th>
        </tr></thead><tbody>{trs}</tbody></table>"""

    insight_html = (f"<div class='insight-box'><div class='ib-label'>AI Insight</div>"
                    f"<p>{_esc(insight)}</p></div>") if insight else ""
    return f"""
  <div class='dept-section no-break'>
    <div class='dept-hdr'>{dept_label} {code_badge}</div>
    {empty}
    {insight_html}
  </div>"""

def _render_overtime_table(rows: list[dict]) -> str:
    if not rows:
        return "<p style='font-size:.8rem;color:var(--tm);font-style:italic;'>No TMs at risk of 60+ hours this week.</p>"
    trs = ""
    for r in rows:
        lvl = r.get("risk_level", "WATCH")
        badge = (f"<span class='risk-red'>\U0001f534 CRITICAL</span>"
                 if lvl == "CRITICAL"
                 else f"<span class='risk-yellow'>\U0001f7e1 WATCH</span>")
        proj_color = "var(--red)" if lvl == "CRITICAL" else "var(--yellow)"
        trs += f"""
      <tr>
        <td class='eid'>{_esc(r['eid'])}</td>
        <td class='name'>{_esc(r['tm_name'])}</td>
        <td class='dept'>{_esc(r.get('dept_label',''))}</td>
        <td>{_esc(r.get('schedule_group',''))}</td>
        <td>{_esc(r.get('reports_to',''))}</td>
        <td class='num'>{_hhmm(r.get('wtd_worked',0))}</td>
        <td class='num'>{_hhmm(r.get('remaining_scheduled',0))}</td>
        <td class='num' style='font-weight:700;color:{proj_color}'>{_hhmm(r.get('projected_total',0))}</td>
        <td>{badge}</td>
        <td class='rec'>{_esc(r.get('recommendation',''))}</td>
      </tr>"""
    return f"""<table><thead><tr>
      <th>EID</th><th>TM Name</th><th>Department</th><th>Schedule Group</th>
      <th>Reports To</th><th style='text-align:right'>WTD Worked</th>
      <th style='text-align:right'>Remaining Sched</th>
      <th style='text-align:right'>Projected Total</th>
      <th>Risk</th><th>Recommendation</th>
    </tr></thead><tbody>{trs}</tbody></table>"""

def _render_summary(data: dict) -> str:
    ncns_count = len(data.get("ncns", []))
    ot_critical = sum(1 for r in data.get("overtime", []) if r.get("risk_level") == "CRITICAL")
    trs = f"""
      <tr><td>Attendance</td><td>Review AI Insights above for departments below 85% threshold</td>
          <td>Flag to Operations Manager; review headcount before shift start</td></tr>
      <tr><td>NCNS</td><td>{ncns_count} NCNS instance{'s' if ncns_count != 1 else ''} in scope window</td>
          <td>TDMs to complete Day 1/2/3 comm workflows per protocol</td></tr>
      <tr><td>Unscheduled Work</td>
          <td>{len(data.get('unscheduled',[]))} TM{'s' if len(data.get('unscheduled',[])) != 1 else ''} worked 10+ min beyond schedule on prior day</td>
          <td>Local HR to review timecards; confirm VET approval or adjust schedule; document per SOP</td></tr>
      <tr><td>Paycode Errors</td>
          <td>{len(data.get('paycode',[]))} paycode mismatch{'es' if len(data.get('paycode',[])) != 1 else ''} in scope window</td>
          <td>Review and correct timecards before pay period close</td></tr>
      <tr><td>Time Off Coverage</td>
          <td>See Section 05 for upcoming PTO/UTO by department (next 7 days)</td>
          <td>Labor-plan by shift before absences occur; flag gaps to Ops Manager</td></tr>
      <tr><td>Overtime Risk</td>
          <td>{ot_critical} TM{'s' if ot_critical != 1 else ''} projected at or above 60 hours</td>
          <td>Immediate schedule adjustment required for CRITICAL TMs</td></tr>"""
    return f"""<table class='summary-table'><thead><tr>
      <th>Category</th><th>Finding</th><th>Recommended Action</th>
    </tr></thead><tbody>{trs}</tbody></table>"""

# ── Main renderer ─────────────────────────────────────────────────────────────

def render_report(data: dict) -> str:
    site        = _esc(data.get("site", ""))
    report_date = data.get("report_date")
    windows     = data.get("windows", {})
    mode        = windows.get("mode", "WTD")
    prior_day   = windows.get("prior_day")
    wtd_start   = windows.get("wtd_start") or windows.get("prior_week_start")
    wtd_end     = windows.get("wtd_end") or windows.get("prior_week_end")
    att_data    = data.get("attendance", {})
    insights    = data.get("insights", {})
    dept_reg    = data.get("dept_registry", DEPT_REGISTRY)

    date_str    = (f"{report_date.strftime('%A, %B ')}{report_date.day}"
                   f"{report_date.strftime(', %Y')}") if report_date else ""
    mode_label  = "Week-to-Date Report" if mode == "WTD" else "Prior Week Report"
    ncns_count  = len(data.get("ncns", []))
    ot_critical = sum(1 for r in data.get("overtime", []) if r.get("risk_level") == "CRITICAL")
    gen_ts      = datetime.now().strftime("%m/%d/%Y at %I:%M %p")

    # Attendance sections
    att_sections_html = ""
    for dk, dinfo in dept_reg.items():
        dc = dinfo.get("code")
        dept_att = att_data.get(dc, {})
        att_insight = insights.get("attendance", {}).get(dk, "")
        att_sections_html += _render_attendance_dept(
            dk, dinfo, dept_att, prior_day, wtd_start, wtd_end, att_insight)

    # Time off sections
    time_off_html = ""
    for dk, dinfo in dept_reg.items():
        dc = dinfo.get("code")
        to_rows   = data.get("time_off", {}).get(dc, [])
        to_insight = insights.get("time_off", {}).get(dk, "")
        time_off_html += _render_time_off_dept(dinfo, to_rows, to_insight)

    # Add dept_label to NCNS/unscheduled/paycode rows for display
    code_to_label = {dinfo["code"]: dinfo["label"] for dinfo in dept_reg.values()
                     if dinfo.get("code")}
    def _label(rows):
        return [{**r, "dept_label": code_to_label.get(r.get("dept_code"), "")}
                for r in rows]

    mode_prefix = "WTD" if mode == "WTD" else "Prior Week"
    scope_label = (
        f"{mode_prefix} &mdash; "
        f"{wtd_start.strftime('%A, %B ')}{wtd_start.day} through "
        f"{wtd_end.strftime('%A, %B ')}{wtd_end.day}"
        if wtd_start and wtd_end else ""
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Daily People Pulse \u2014 {site} \u2014 {date_str}</title>
<style>{_load_css()}</style>
</head>
<body>

<header class="hero">
  <div class="hero-badge">Chewy Confidential &middot; Internal Use Only</div>
  <h1>Daily People Pulse</h1>
  <p class="sub">{site} &middot; {date_str} &middot; {mode_label}</p>
  <p class="hero-desc">A daily operational snapshot for HR Partners, surfacing attendance patterns,
  timecard exceptions, time-off coverage gaps, and overtime risk. Data is sourced directly from
  UKG &mdash; not PUMA &mdash; to ensure real-time accuracy.</p>
  <div class="stats">
    <div class="stat"><span class="n">{site}</span><span class="l">Location</span></div>
    <div class="stat"><span class="n">{len(dept_reg)}</span><span class="l">Departments</span></div>
    <div class="stat"><span class="n">{mode}</span><span class="l">Report Mode</span></div>
    <div class="stat"><span class="n">{ncns_count}</span><span class="l">NCNS Flags</span></div>
    <div class="stat"><span class="n">{ot_critical}</span><span class="l">OT Critical</span></div>
  </div>
  <div class="hero-meta">
    <span>Generated: {gen_ts} ET</span>
    <span>Data source: UKG API</span>
  </div>
</header>

<div class="how-to-read no-break-before section" style="border-top:none;padding-top:0;">
  <h3>How to Read This Report</h3>
  <p><strong>Report mode varies by day of week.</strong> Tuesday through Saturday: WTD metrics
  (Sunday through prior day) plus Prior Day detail. Sunday and Monday: Prior Week and Prior Day
  only (no WTD).</p>
  <p><strong>All hours are UKG hours, not PUMA.</strong> Attendance = hours worked &divide;
  hours scheduled. Below 85% warrants manager attention.</p>
</div>

<div class="section" id="section-01">
  <div class="sec-hdr">
    <span class="sec-num">Section 01</span>
    <span class="sec-title">Attendance Summary</span>
  </div>
  <p class="sec-desc">Attendance = <strong>hours worked &divide; hours scheduled (UKG)</strong>.
  WTD figures reflect {scope_label}. Prior Day figures reflect the day immediately before this report.
  Day and Night shifts are reported separately where applicable.</p>
  {att_sections_html}
</div>

<div class="section" id="section-02">
  <div class="sec-hdr">
    <span class="sec-num">Section 02</span>
    <span class="sec-title">No Call No Show (NCNS)</span>
  </div>
  <p class="sec-desc"><strong>What this is:</strong> Team Members with a confirmed NCNS paycode
  in UKG. Pre-approved PTO, UTO, and any other approved leave excludes a TM from this section.
  <br><strong>TMDM Workflow:</strong> Validate NCNS on timesheet &rarr; NCNS Comm Day 1/2/3 &rarr;
  Term Review Ticket to Site HR within 36 hrs of Day 3 comm.</p>
  <div class="scope-note">&nbsp;Scope: {scope_label}</div>
  {_render_ncns_table(_label(data.get("ncns", [])))}
</div>

<div class="section" id="section-03">
  <div class="sec-hdr">
    <span class="sec-num">Section 03</span>
    <span class="sec-title">Unscheduled but Worked</span>
  </div>
  <p class="sec-desc"><strong>What this is:</strong> Team Members who worked 10 or more minutes
  beyond their scheduled hours on <strong>{f"{prior_day.strftime('%A, %B ')}{prior_day.day}{prior_day.strftime(', %Y')}" if prior_day else 'the prior day'}</strong>,
  with no approved VET on record.<br>
  <strong>Recommendation for all entries:</strong> Local HR to review timecard &rarr; confirm
  VET/approval or adjust schedule; document per SOP.</p>
  {_render_unscheduled_table(_label(data.get("unscheduled", [])))}
</div>

<div class="section" id="section-04">
  <div class="sec-hdr">
    <span class="sec-num">Section 04</span>
    <span class="sec-title">Paycode Reconciler</span>
  </div>
  <p class="sec-desc"><strong>What this is:</strong> Team Members where time-off paycodes applied
  in UKG do not align with scheduled hours. Mismatches can cause payroll errors if not corrected
  before the pay period closes. Sorted by TM Name, then date (most recent first).</p>
  <div class="scope-note">&nbsp;Scope: {scope_label}</div>
  {_render_paycode_table(_label(data.get("paycode", [])))}
</div>

<div class="section" id="section-05">
  <div class="sec-hdr">
    <span class="sec-num">Section 05</span>
    <span class="sec-title">Upcoming Time Off</span>
  </div>
  <p class="sec-desc"><strong>What this is:</strong> PTO and UTO scheduled in UKG for the next
  7 days, organized by department. Use this section to labor plan by shift and date before
  absences occur. Sorted by date, earliest first.</p>
  {time_off_html}
</div>

<div class="section" id="section-06">
  <div class="sec-hdr">
    <span class="sec-num">Section 06</span>
    <span class="sec-title">60+ Hour Watch</span>
  </div>
  <p class="sec-desc"><strong>What this is:</strong> Team Members whose hours are projected to
  exceed 60 this week.&nbsp;
  <span class="risk-red" style="font-size:.75rem;margin-right:6px;">\U0001f534 CRITICAL</span>
  WTD worked &ge; 60 hrs.&nbsp;
  <span class="risk-yellow" style="font-size:.75rem;">\U0001f7e1 WATCH</span>
  WTD &ge; 58 hrs or projected total &gt; 60 hrs.</p>
  <div class="scope-note">&nbsp;WTD Worked: {scope_label}</div>
  {_render_overtime_table(_label(data.get("overtime", [])))}
</div>

<div class="section" id="summary">
  <div class="sec-hdr">
    <span class="sec-num">Summary</span>
    <span class="sec-title">HR Findings &mdash; Action Required Today</span>
  </div>
  {_render_summary(data)}
</div>

<div class="footer">
  Daily People Pulse &middot; {site} &middot; {date_str} &middot;
  Data source: UKG API &middot; Chewy Confidential &mdash; Internal Use Only<br>
  Generated by ORBIT &middot; Daily People Pulse &middot; An ORBIT Product
</div>

</body>
</html>"""
```

- [ ] **Step 4: Run smoke tests**

```bash
python -m pytest tests/test_dpp_renderer.py -v 2>&1
```

Expected: Both tests PASS

- [ ] **Step 5: Commit**

```bash
git add "ORBIT – Daily People Pulse/04 – Pipelines & Architecture/dpp-pipeline/dpp_html_renderer.py"
git add "ORBIT – Daily People Pulse/04 – Pipelines & Architecture/dpp-pipeline/tests/test_dpp_renderer.py"
git commit -m "feat(dpp): add HTML renderer — assembles all section data into print-ready report"
```

---

### Task 11: `run_dpp_pipeline.py` — Orchestrator

**Files:**
- Create: `04 – Pipelines & Architecture/dpp-pipeline/run_dpp_pipeline.py`

Ties everything together. Reads UKG CSV, runs all section computors, calls insight generator, renders HTML, writes output file.

- [ ] **Step 1: Implement orchestrator (no separate test — integration tested manually)**

```python
# run_dpp_pipeline.py
"""
Daily People Pulse — Pipeline Orchestrator
Usage:
  python run_dpp_pipeline.py --input <ukg_csv_path> --site SDF4 \
      --date 2026-03-19 --output <output_dir>

Exits 0 on success, 1 on error.
"""
import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

from dpp_scope         import (get_report_mode, get_date_windows,
                                DEPT_REGISTRY, attendance_color_class)
from dpp_ukg_reader    import load_ukg_csv
from dpp_insights      import generate_attendance_insight, generate_time_off_insight
from dpp_html_renderer import render_report

from sections.dpp_attendance import compute_attendance
from sections.dpp_ncns       import compute_ncns
from sections.dpp_unscheduled import compute_unscheduled
from sections.dpp_paycode    import compute_paycode_mismatches
from sections.dpp_time_off   import compute_time_off
from sections.dpp_overtime   import compute_overtime


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Daily People Pulse pipeline")
    p.add_argument("--input",  required=True, help="Path to UKG CSV file")
    p.add_argument("--site",   required=True, help="Site code (e.g. SDF4)")
    p.add_argument("--date",   required=True, help="Report date YYYY-MM-DD")
    p.add_argument("--output", required=True, help="Output directory for HTML file")
    p.add_argument("--no-insights", action="store_true",
                   help="Skip AI insight generation (useful for testing)")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    # 1. Parse date
    try:
        report_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    except ValueError:
        print(f"[error] Invalid date format: {args.date!r} — expected YYYY-MM-DD")
        return 1

    # 2. Compute date windows
    windows = get_date_windows(report_date)
    mode    = windows["mode"]
    prior_day = windows["prior_day"]

    if mode == "WTD":
        scope_start, scope_end = windows["wtd_start"], windows["wtd_end"]
    else:
        scope_start, scope_end = windows["prior_week_start"], windows["prior_week_end"]

    from datetime import timedelta
    scope_dates = [scope_start + timedelta(days=i)
                   for i in range((scope_end - scope_start).days + 1)]

    print(f"[dpp] Site: {args.site}  Date: {report_date}  Mode: {mode}")
    print(f"[dpp] Scope: {scope_start} – {scope_end}  Prior Day: {prior_day}")

    # 3. Load UKG data
    print(f"[dpp] Loading UKG data from {args.input}")
    try:
        records = load_ukg_csv(args.input, site_filter=args.site)
    except FileNotFoundError as exc:
        print(f"[error] {exc}")
        return 1
    print(f"[dpp] Loaded {len(records)} records")

    # 4. Run all section computors
    print("[dpp] Computing sections...")
    att_data   = compute_attendance(records, scope_dates, prior_day)
    ncns_rows  = compute_ncns(records, scope_dates)
    unsched    = compute_unscheduled(records, prior_day)
    paycode    = compute_paycode_mismatches(records, scope_dates)
    time_off   = compute_time_off(records, report_date)

    # Overtime uses current week's worked dates, not scope_dates.
    # In PRIOR_WEEK mode scope_dates = prior full week, which would corrupt the
    # remaining-scheduled bucket (current-week Mon hours would appear as "remaining").
    if mode == "WTD":
        ot_wtd_dates = scope_dates
    elif report_date.weekday() == 6:  # Sunday: current week just started, 0 WTD hours
        ot_wtd_dates = []
    else:  # Monday: current week started yesterday (Sunday = prior_day)
        ot_wtd_dates = [prior_day]
    overtime   = compute_overtime(records, ot_wtd_dates)

    print(f"  NCNS: {len(ncns_rows)}  Unscheduled: {len(unsched)}"
          f"  Paycode: {len(paycode)}  OT flags: {len(overtime)}")

    # 5. Generate AI insights
    insights = {"attendance": {}, "time_off": {}}
    if not args.no_insights:
        print("[dpp] Generating AI insights...")
        for dk, dinfo in DEPT_REGISTRY.items():
            dc = dinfo.get("code")
            dept_att = att_data.get(dc, {})
            insights["attendance"][dk] = generate_attendance_insight(
                dinfo["label"], dept_att)
            to_rows = time_off.get(dc, [])
            wtd_pct = (dept_att.get("wtd", {}).get("Day", {}).get("pct", 0.0)
                       + dept_att.get("wtd", {}).get("Night", {}).get("pct", 0.0)) / 2
            insights["time_off"][dk] = generate_time_off_insight(
                dinfo["label"], to_rows, wtd_pct)
    else:
        print("[dpp] Skipping AI insights (--no-insights flag set)")

    # 6. Render HTML
    print("[dpp] Rendering HTML...")
    report_data = {
        "site":         args.site,
        "report_date":  report_date,
        "windows":      windows,
        "attendance":   att_data,
        "ncns":         ncns_rows,
        "unscheduled":  unsched,
        "paycode":      paycode,
        "time_off":     time_off,
        "overtime":     overtime,
        "insights":     insights,
        "dept_registry": DEPT_REGISTRY,
    }
    html = render_report(report_data)

    # 7. Write output
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"DPP_{args.site}_{report_date.strftime('%Y-%m-%d')}.html"
    out_file.write_text(html, encoding="utf-8")
    print(f"[dpp] Report written to: {out_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Smoke-test the full pipeline with mock data**

Use `--no-insights` to avoid needing the Anthropic API key during testing.

```bash
cd "c:/Users/kwallace12/OneDrive - Chewy.com, LLC/Desktop/ORBIT Products/01 - Daily People Pulse/ORBIT – Daily People Pulse/04 – Pipelines & Architecture/dpp-pipeline"

python run_dpp_pipeline.py \
  --input "path/to/sample_ukg.csv" \
  --site SDF4 \
  --date 2026-03-19 \
  --output "./output" \
  --no-insights
```

Expected: `[dpp] Report written to: ./output/DPP_SDF4_2026-03-19.html`

Open the output HTML in Chrome and verify it renders correctly. Print → Save as PDF to verify PDF fidelity.

- [ ] **Step 3: Full pipeline test with real API key**

```bash
set ANTHROPIC_API_KEY=<your-key>
python run_dpp_pipeline.py \
  --input "path/to/sample_ukg.csv" \
  --site SDF4 \
  --date 2026-03-19 \
  --output "./output"
```

Verify AI insight boxes are populated with real text.

- [ ] **Step 4: Run full test suite**

```bash
python -m pytest tests/ -v 2>&1
```

Expected: All tests PASS, zero failures

- [ ] **Step 5: Final commit**

```bash
git add "ORBIT – Daily People Pulse/04 – Pipelines & Architecture/dpp-pipeline/run_dpp_pipeline.py"
git add "ORBIT – Daily People Pulse/04 – Pipelines & Architecture/dpp-pipeline/"
git commit -m "feat(dpp): add pipeline orchestrator — end-to-end UKG CSV to HTML report"
```

---

## Integration Checklist

Before handing off to Phoenix:

- [ ] Confirm UKG CSV column names match `FIELD_MAP` in `dpp_ukg_reader.py`
- [ ] Confirm Vet Services Tech I / Tech II dept codes with product owner and update `DEPT_REGISTRY` in `dpp_scope.py`
- [ ] Set `ANTHROPIC_API_KEY` in Phoenix environment
- [ ] Run a full pipeline test against a real UKG CSV export for SDF4
- [ ] Open the generated HTML in Chrome → Print → Save as PDF; verify all sections render correctly, no table row splits across pages
- [ ] Confirm Phoenix Chrome headless PDF render matches the Chrome browser print preview
- [ ] Designate AI insight reviewer for pilot phase (see Open Question 5 in spec)
