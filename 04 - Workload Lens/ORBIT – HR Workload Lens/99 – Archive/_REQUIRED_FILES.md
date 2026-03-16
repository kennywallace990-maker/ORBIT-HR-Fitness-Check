# 99 - Archive

## Structure
- `Phase-I-Raw-Data/` -- Phase I raw CSV exports from Snowflake/UKG
- `Phase-II-Raw-Data/` -- Phase II raw CSV exports from ServiceNow + OBR PDF
- `Self-Service-Review-Versions/` -- Timestamped self-service review Excel iterations
- `Pipeline-Smoke-Tests/` -- Pipeline run smoke test JSON outputs

## Notes
- Quarterly subfolders (e.g., 2026-Q1) should be created as content ages
- Large CSV files (25MB+ hr_dataset) kept in original `test-data/` location to avoid OneDrive bloat