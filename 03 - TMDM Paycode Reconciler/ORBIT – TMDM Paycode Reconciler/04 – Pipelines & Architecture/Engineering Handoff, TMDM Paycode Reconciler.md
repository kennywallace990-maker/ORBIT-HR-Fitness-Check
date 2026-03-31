# TMDM Paycode Reconciler — Engineering Handoff

This document contains everything needed to implement the paycode reconciler detection logic. It is the single source of truth for edge case definitions, CASE evaluation order, recommendation text, validation rules, and paycode classification.

**Reference SQL**: `final-training_data_reconciler.sql` (working, validated implementation)

---

## 1. Paycode Classification Table

Every UKG Pro paycode must be classified into one of these categories. Unknown paycodes (not in this table) are ignored — they don't count as work or time-off.

### Work Paycodes (`paycode_type = 'work'`)

These contribute to `worked_hours`.

| pay_code_name | is_pto | is_exempt |
|--------------|--------|-----------|
| Regular | FALSE | FALSE |
| Overtime | FALSE | FALSE |
| Overtime $1.50 | FALSE | FALSE |
| Overtime $2.00 | FALSE | FALSE |
| Overtime $2.50 | FALSE | FALSE |
| Overtime $3.00 | FALSE | FALSE |
| Overtime $5.00 | FALSE | FALSE |
| BT | FALSE | FALSE |
| BT OT | FALSE | FALSE |
| BT $1.50 | FALSE | FALSE |
| BT $2.00 | FALSE | FALSE |
| BT $2.50 | FALSE | FALSE |
| BT $4.00 | FALSE | FALSE |
| BT 7D OT | FALSE | FALSE |
| 7DAYOT | FALSE | FALSE |
| Exempt Punch | FALSE | FALSE |

### Time-Off Paycodes — Non-Exempt (`paycode_type = 'timeoff'`, `is_exempt = FALSE`)

These contribute to `timeoff_applied_hours` and drive the over-application calculation.

| pay_code_name | is_pto | is_exempt | Notes |
|--------------|--------|-----------|-------|
| PTO PAID | TRUE | FALSE | Highest risk — creates pay defects |
| PTO PAID PTO Sick | TRUE | FALSE | |
| Vet Care - PTO PAID | TRUE | FALSE | |
| Customer Service PTO - VTO | TRUE | FALSE | |
| Personal UNPAID | FALSE | FALSE | UTO — attendance risk |
| Personal UNPD Call Off | FALSE | FALSE | RPA-applied |
| Personal UNPD Late arrival | FALSE | FALSE | RPA-applied |
| Personal UNPD Early Departure | FALSE | FALSE | RPA-applied |
| Personal UNPD NCNS | FALSE | FALSE | RPA-applied |
| Voluntary Time Off | FALSE | FALSE | VTO — lowest risk, metrics impact |
| SICK | FALSE | FALSE | |
| Education UNPAID | FALSE | FALSE | |
| Jury Duty | FALSE | FALSE | |
| Unpaid Time Off - Unscheduled | FALSE | FALSE | |

### Time-Off Paycodes — Exempt (`paycode_type = 'timeoff'`, `is_exempt = TRUE`)

These are **excluded from `timeoff_applied_hours`** but still appear in the `paycodes_detail` LISTAGG for context.

| pay_code_name | is_pto | is_exempt | Why Excluded |
|--------------|--------|-----------|--------------|
| LEAVE | FALSE | TRUE | FMLA/LOA — managed by Leave Administration |
| Intermittent Leave PTO | TRUE | TRUE | FMLA-certified intermittent leave |
| Intermittent Leave-Unpaid | FALSE | TRUE | FMLA-certified intermittent leave |
| Bereavement | FALSE | TRUE | Compassionate leave |
| Bereavement - Unpaid | FALSE | TRUE | Compassionate leave |
| Military Leave | FALSE | TRUE | USERRA-protected |

**Implementation rule**: If ALL time-off paycodes on an employee/date are exempt, exclude the row entirely (`has_non_exempt_timeoff = 0`). If ANY non-exempt paycode exists, include the row — exempt paycodes appear in detail but don't inflate the hours.

---

## 2. Over-Application Formula

### Step 1: Determine Effective Scheduled Hours

```sql
effective_scheduled_hours = CASE
    WHEN scheduled_hours = 0 AND original_scheduled_from_history > 0
    THEN original_scheduled_from_history
    ELSE scheduled_hours
END
```

This handles the case where UKG replaced the schedule with a time-off paycode (overwrite detection).

### Step 2: Calculate Over-Applied Hours

```sql
over_applied_raw = GREATEST(0,
    timeoff_applied_hours           -- non-exempt only
    - scheduled_pto                 -- already on the schedule, don't double-count
    - GREATEST(0, effective_scheduled_hours - worked_hours)
)
```

### Step 3: Apply Safeguards

```sql
over_applied_hours = CASE
    WHEN worked_hours >= effective_scheduled_hours
        THEN 0                      -- worked full shift, no over-application
    WHEN over_applied_raw < 0.0334
        THEN 0                      -- de minimis (< 2 min rounding noise)
    ELSE over_applied_raw
END
```

### Step 4: Flagging Threshold

```sql
WHERE over_applied_hours > 0.25     -- only flag >= 15 minutes
  AND has_non_exempt_timeoff = 1    -- at least one non-exempt paycode
  AND timeoff_applied > 0           -- non-exempt hours exist
```

---

## 3. Schedule Version Selection

**This is critical. Getting the sort order wrong was a previous bug that affected 22,125 records.**

| CTE | Table | Sort Order | Why |
|-----|-------|-----------|-----|
| `schedule_original` | `GOLD_V_SCHEDULE_TOTAL` | `ORDER BY load_date_time DESC` | Current schedule (latest version) |
| `shift_hours` | `V_SCHEDULE_SHIFT` | `ORDER BY load_date_time DESC` | Current shift start/end times |
| `schedule_pto` | `GOLD_V_SCHEDULE_TOTAL` | `ORDER BY load_date_time DESC` | Current scheduled PTO |
| `schedule_original_from_history` | `V_SCHEDULE_TRANSACTION` | `ORDER BY load_date_time ASC` | Oldest version — pre-overwrite schedule for restoration |

**Why the history CTE uses ASC**: When UKG overwrites a Regular schedule with a PTO paycode, `scheduled_hours` drops to 0. We need to find what the schedule was *before* the overwrite. The earliest records in `V_SCHEDULE_TRANSACTION` contain the original Regular/Overtime entries.

### Meal Break Deduction

```sql
scheduled_hours = CASE
    WHEN shift_hours IS NOT NULL AND shift_hours >= 6
    THEN shift_hours - 0.5 + spillover_hours      -- gross shift minus 30-min meal break
    ELSE SUM(schedule_total.hours_amount) + spillover_hours
END
```

Shifts >= 6 hours get a 0.5 hr meal break deduction. This is because `V_SCHEDULE_SHIFT` reports gross hours (start to end) but the team member doesn't work during the meal break.

### Overnight Spillover

```sql
spillover_hours = DATEDIFF('minute',
    end_date_time::DATE::TIMESTAMP,
    end_date_time
) / 60.0
WHERE end_date_time::DATE > start_date_time::DATE
```

For shifts that cross midnight (e.g., 11pm–5:30am), the hours after midnight are credited to the next calendar day.

---

## 4. Schedule Anomaly Detection

Evaluated BEFORE root cause classification. Stored in `schedule_anomaly` column.

| Anomaly | Condition | Meaning |
|---------|-----------|---------|
| `TIMEOFF_OVERWROTE_SCHEDULE` | `scheduled_hours = 0 AND original_scheduled_from_history > 0` | UKG replaced the Regular schedule with time-off. Original schedule restored from history. |
| `UNSCHEDULED_DAY_TIMEOFF` | `scheduled_hours = 0 AND original_scheduled_from_history = 0 AND timeoff_applied > 0` | Time-off on a day with no schedule and no history. |
| `OT_DAY_WORKED` | `scheduled_hours = 0 AND worked > 0` | Employee worked on a day with no schedule (OT/extra day). Not flagged. |
| `NULL` | All other cases | Normal schedule exists. |

---

## 5. Root Cause Classification — CASE Order

**ORDER MATTERS.** The CASE statement evaluates top-to-bottom. The first match wins. Changing the order will change classification.

### Root Cause Column

```sql
CASE
    WHEN over_applied_hours BETWEEN 0.45 AND 0.55
        AND effective_scheduled_hours >= 6
        THEN 'Meal Break (30 min) in Time-Off'

    WHEN paycodes_detail LIKE '%NCNS%' AND paycodes_detail LIKE '%Call Off%'
        THEN 'NCNS Not Cleared (RPA Workflow)'

    WHEN ampm_evidence IS NOT NULL
        THEN 'AM/PM Miscoding (Confirmed)'

    WHEN schedule_anomaly = 'TIMEOFF_OVERWROTE_SCHEDULE'
        THEN 'Schedule Overwritten by Time-Off'

    WHEN schedule_anomaly = 'UNSCHEDULED_DAY_TIMEOFF'
        THEN 'Time-Off on Unscheduled Day'

    WHEN over_applied_hours BETWEEN 11 AND 13
        THEN 'AM/PM Miscoding (Likely)'

    WHEN timeoff_applied >= 15 AND over_applied_hours >= 10
        THEN 'AM/PM Miscoding (Possible)'

    WHEN over_applied_hours >= 4
        THEN 'Excess Time-Off Applied'

    WHEN over_applied_hours > 0.25
        THEN 'Minor Over-Application'

    ELSE NULL
END
```

### Recommendation Column

```sql
CASE
    WHEN over_applied_hours BETWEEN 0.45 AND 0.55
        AND effective_scheduled_hours >= 6
        THEN 'No action - meal break (30 min) in UKG time-off'

    WHEN paycodes_detail LIKE '%NCNS%' AND paycodes_detail LIKE '%Call Off%'
        THEN 'Clear NCNS paycode - RPA workflow did not complete cleanup'

    WHEN ampm_evidence IS NOT NULL
        THEN 'Correct PTO end time from PM to AM - ' || ampm_evidence

    WHEN schedule_anomaly = 'TIMEOFF_OVERWROTE_SCHEDULE'
        THEN 'Schedule overwritten (orig ~' || ROUND(original_scheduled_from_history, 2)
             || ' hrs). Reduce time-off by ' || ROUND(over_applied_hours, 2) || ' hrs'

    WHEN schedule_anomaly = 'UNSCHEDULED_DAY_TIMEOFF'
        THEN 'Time-off on unscheduled day - reduce by '
             || ROUND(timeoff_applied, 2) || ' hrs'

    WHEN over_applied_hours BETWEEN 11 AND 13
        THEN 'Verify PTO timestamps for ~12hr error, reduce by '
             || ROUND(over_applied_hours, 2) || ' hrs'

    WHEN timeoff_applied >= 15 AND over_applied_hours >= 10
        THEN 'Review PTO entry for AM/PM error, reduce by '
             || ROUND(over_applied_hours, 2) || ' hrs'

    WHEN over_applied_hours >= 4
        THEN 'Reduce time-off by ' || ROUND(over_applied_hours, 2)
             || ' hrs - HIGH PRIORITY'

    WHEN over_applied_hours > 0.25
        THEN 'Review and reduce time-off by '
             || ROUND(over_applied_hours, 2) || ' hrs'

    ELSE NULL
END
```

---

## 6. Confidence Level

```sql
CASE
    WHEN schedule_group IS NULL
         OR TRIM(schedule_group) = ''
         OR schedule_group = 'Always Available'
        THEN 'LOW - No UKG schedule'

    WHEN schedule_anomaly = 'TIMEOFF_OVERWROTE_SCHEDULE'
        THEN 'MEDIUM - Schedule restored from history'

    ELSE 'HIGH'
END
```

---

## 7. Data Warnings

These are informational flags that surface suspicious data patterns. They do not change the root cause or recommendation — they alert the reviewer to check the record more carefully.

```sql
ARRAY_TO_STRING(ARRAY_COMPACT(ARRAY_CONSTRUCT(

    CASE WHEN worked + timeoff_applied > 24
        THEN 'WARN: worked + time-off exceeds 24 hrs ('
             || ROUND(worked + timeoff_applied, 2) || ')' END,

    CASE WHEN effective_scheduled_hours > 16
        THEN 'WARN: effective schedule > 16 hrs ('
             || ROUND(effective_scheduled_hours, 2) || ')' END,

    CASE WHEN effective_scheduled_hours = 0
         AND schedule_anomaly IS NULL
         AND timeoff_applied > 0
        THEN 'WARN: no schedule found but time-off applied' END,

    CASE WHEN over_applied_hours > timeoff_applied
        THEN 'WARN: over-applied exceeds total time-off (math error)' END,

    CASE WHEN worked > 0 AND timeoff_applied > 0
         AND worked + timeoff_applied > effective_scheduled_hours + 4
        THEN 'WARN: worked + time-off far exceeds schedule - possible double-count' END,

    CASE WHEN over_applied_hours BETWEEN 11 AND 13
         AND effective_scheduled_hours >= 10
        THEN 'WARN: flagged as AM/PM error but employee has 10+ hr schedule'
             || ' - may be legitimate long-shift PTO' END

)), '; ')
```

---

## 8. Validation Status

```sql
CASE
    WHEN worked + timeoff_applied > 24
         OR over_applied_hours > timeoff_applied
        THEN 'SUSPECT'

    WHEN worked > 0 AND timeoff_applied > 0
         AND worked + timeoff_applied > effective_scheduled_hours + 4
        THEN 'REVIEW'

    WHEN over_applied_hours BETWEEN 11 AND 13
         AND effective_scheduled_hours >= 10
        THEN 'REVIEW'

    WHEN schedule_anomaly = 'UNSCHEDULED_DAY_TIMEOFF'
        THEN 'REVIEW'

    ELSE 'CLEAN'
END
```

| Status | Meaning | Action |
|--------|---------|--------|
| `SUSPECT` | Data quality issue — mathematically impossible or inconsistent | Investigate before acting on recommendation |
| `REVIEW` | Unusual pattern — could be legitimate, could be an error | Human review recommended before correction |
| `CLEAN` | Standard defect — recommendation can be acted on directly | Proceed with correction |

---

## 9. AM/PM Verification (Transaction-Level)

This CTE queries `GOLD_V_TIMECARD_TRANSACTION` for direct evidence of AM/PM miscoding.

```sql
ampm_evidence = MAX(CASE
    WHEN pay_code LIKE '%PTO%'
         AND duration_in_hours >= 12
         AND HOUR(end_date_time) BETWEEN 12 AND 20
    THEN 'CONFIRMED: End time ' || TO_CHAR(end_date_time, 'HH12:MI AM')
         || ' should be AM (PTO coded 12+ hrs)'
    ELSE NULL
END)
```

**Logic**: If a PTO entry has duration >= 12 hours AND the end time is in the afternoon (12pm–8pm), it's almost certainly an AM/PM error — someone entered 5:00 PM when they meant 5:00 AM.

---

## 10. Output Columns

The final SELECT produces these columns in this order:

| Column | Source | Description |
|--------|--------|-------------|
| Business Unit | `building_list.cohort` | FC or Rx |
| Building | `ukg_import.site_code` | 4-char building code |
| Employee ID | `employees.employee_id` | UKG person_number |
| Employee Full Name | `employees.employee_full_name` | Last, First |
| Schedule Group Name | `employees.schedule_group` | UKG schedule group |
| Reports To | `employees.reports_to` | Supervisor |
| Date | `partition_date` | Flagged date |
| Hours Scheduled | `effective_scheduled_hours` | Net scheduled (after meal break, overwrite restoration) |
| Hours Worked | `worked` | From UKG timecard (or UKG import for training data) |
| Time-Off Applied | `timeoff_applied` | Non-exempt hours only |
| Over-Applied Hrs | `over_applied_hours` | The defect — how much time-off exceeds the gap |
| Paycodes (name: HH:MM) | `paycodes_detail` | All paycodes incl. exempt, formatted as name: HH:MM |
| Recommendation | CASE logic (Section 5) | Action text for HR |
| Root Cause | CASE logic (Section 5) | Category label |
| Schedule Anomaly | `schedule_anomaly` | NULL, TIMEOFF_OVERWROTE_SCHEDULE, UNSCHEDULED_DAY_TIMEOFF, OT_DAY_WORKED |
| Confidence | CASE logic (Section 6) | HIGH, MEDIUM, LOW |
| Data Warnings | ARRAY logic (Section 7) | Semicolon-delimited warning strings |
| Validation Status | CASE logic (Section 8) | CLEAN, REVIEW, SUSPECT |

### Sort Order

```sql
ORDER BY
    CASE WHEN ampm_evidence IS NOT NULL THEN 0 ELSE 1 END,  -- AM/PM confirmed first
    over_applied_hours DESC,                                  -- worst defects next
    employee_full_name,
    partition_date
```

---

## 11. Data Sources & Join Keys

| CTE | Table | Join Key | Filter |
|-----|-------|----------|--------|
| `ukg_import` | `PAYCODE_RECONCILER_TRAINING_DATA` | — | `PAY_CODE_COMBINED_INDICATOR = FALSE` |
| `employees` | `GOLD_V_PEOPLE` | `person_number = EMPLOYEE_ID::VARCHAR` | Not terminated, not deleted, not Exempt schedule |
| `shift_hours` | `V_SCHEDULE_SHIFT` | `person_id + partition_date` | `NOT deleted` |
| `schedule_original` | `GOLD_V_SCHEDULE_TOTAL` | `person_id + partition_date` | `combined_pay_code_swt = FALSE`, pay_code IN (Regular, Overtime) |
| `schedule_original_from_history` | `V_SCHEDULE_TRANSACTION` | `person_id + partition_date` | `combined_pay_code_swt = FALSE`, `NOT deleted`, pay_code IN (Regular, Overtime, Exempt Punch) |
| `schedule_pto` | `GOLD_V_SCHEDULE_TOTAL` | `person_id + partition_date + pay_code` | Joined to `paycode_types` where `paycode_type = 'timeoff'` |
| `ampm_verification` | `GOLD_V_TIMECARD_TRANSACTION` | `person_id + partition_date` | PTO paycodes only, `NOT deleted` |
| `overnight_spillover` | `V_SCHEDULE_SHIFT` | `person_id + partition_date` | Shifts crossing midnight |

### Important: `combined_pay_code_swt`

UKG stores both individual paycodes and combined/rollup paycodes. Always filter `combined_pay_code_swt = FALSE` to get individual entries. Combined entries double-count hours.

### Important: Date Range Padding

Schedule CTEs use `partition_date BETWEEN date_range - 1 AND end_date`. The -1 day padding captures overnight shifts that start the day before the range. The overnight spillover CTE uses -2 days for the same reason.

---

## 12. Known Edge Cases to Test

When validating a new implementation, test these specific scenarios:

| Test Case | What to Check | Expected Behavior |
|-----------|---------------|-------------------|
| Employee works full shift + has PTO | `worked >= effective_scheduled` | `over_applied = 0` (zeroed out) |
| Meal break on 6+ hr shift with early departure | `over_applied BETWEEN 0.45 AND 0.55` | Root cause = "Meal Break" |
| Meal break on < 6 hr shift | `effective_scheduled < 6` | Root cause = "Minor" (not meal break) |
| PTO + RPA late arrival stacked | Multiple paycodes on same date | Both appear in paycodes_detail, combined hours drive over_applied |
| Schedule overwritten by PTO | `scheduled_hours = 0`, history has Regular | `schedule_anomaly = TIMEOFF_OVERWROTE_SCHEDULE`, restored hours used |
| Exempt-only day (LEAVE only) | `has_non_exempt_timeoff = 0` | Row excluded from output |
| Mixed exempt + non-exempt | LEAVE + PTO PAID on same date | Row included, LEAVE in detail but not in hours sum |
| AM/PM PTO entry (13+ hrs) | `GOLD_V_TIMECARD_TRANSACTION` has end_time in PM | `ampm_evidence` populated, root cause = "AM/PM Confirmed" |
| Overnight shift (11pm–5:30am) | `end_date > start_date` | Spillover hours credited to next day |
| De minimis (1 minute over) | `over_applied < 0.0334` | Zeroed out, not flagged |
| NCNS + Call Off combo | Both paycodes present | Root cause = "NCNS Not Cleared" |
| SUSPECT: worked + timeoff > 24 | Impossible day | Validation = "SUSPECT", data warning generated |

---

## 13. File Reference

| File | What It Is |
|------|-----------|
| `final-training_data_reconciler.sql` | Latest validated SQL — use as reference implementation |
| `training_data_reconciler.sql` | Earlier version (may not have all edge cases) |
| `TMDM Paycode Reconciler.sql` | Production reconciler (uses Snowflake timecard tables, has deleted-row logic) |
| `TMDM Edge Cases & Audit Reference.md` | Business-facing edge case catalog |
| `TMDM Validation & SPC Methodology.md` | Validation report with SPC analysis and root cause insights |

---

*Last updated: March 2026*
*ORBIT AI for HR | Enterprise People Analytics*
