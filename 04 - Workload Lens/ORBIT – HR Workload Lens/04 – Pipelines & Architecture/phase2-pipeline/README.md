# ORBIT Workload Lens - Weekly Pipeline

This folder contains the older four-service CSV workflow that was used before BI changed the governed Phase II ticket delivery model.

## Status

This pipeline is now legacy.

The current governed intake for Phase II ticket processing is:

1. a rolling folder that contains the weekly BI `opened last week` and `closed last week` files
2. the BI reconstruction and cleanup flow in `../phase2-weekly-hr-oe/`

Use the current README instead:

- `../phase2-weekly-hr-oe/README.md`

Use the current entrypoints instead:

- `run_ticket_prep_pipeline.py --bi-weekly-dir ...`
- `run_ticket_folder_drop.py --bi-weekly-dir ...`
- `run_hr_oe_pipeline.py --phase2-bi-dir ...`

Keep this folder only for historical reproduction of the older service-specific CSV workflow.
