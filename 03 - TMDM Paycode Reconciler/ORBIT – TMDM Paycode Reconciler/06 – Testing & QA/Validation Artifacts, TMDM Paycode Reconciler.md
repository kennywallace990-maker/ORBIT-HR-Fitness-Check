# Validation Artifacts, TMDM Paycode Reconciler

This folder now contains supporting validation materials in addition to the core QA documents.

These artifacts are not the product itself. They document the Snowflake-based analysis performed on data pulled from UKG and used to finalize the reconciler logic, edge-case handling, and validation approach.

## Included Artifacts

- `TMDM Validation & SPC Methodology.md`  
  Narrative methodology report with findings, root-cause analysis, and SPC validation notes.
- `test-data/final-training_data_reconciler_2026-03-31-1355.csv`  
  Final validated sample output snapshot used as reference data for logic validation.

## Snapshot Summary for the Final Training Output

- Row count: `1,480`
- Column count: `18`
- Root cause mix:
  - `Minor Over-Application`: `937`
  - `Meal Break (30 min) in Time-Off`: `525`
  - `Excess Time-Off Applied`: `16`
  - `AM/PM Miscoding (Likely)`: `1`
  - `AM/PM Miscoding (Possible)`: `1`
- Validation status mix:
  - `CLEAN`: `1,454`
  - `REVIEW`: `25`
  - `SUSPECT`: `1`

## Usage

- Use these files as the traceable evidence base for QA, logic reviews, and future regression checks.
- Do not treat this dataset as the production output contract; it is a validated sample/training artifact.
