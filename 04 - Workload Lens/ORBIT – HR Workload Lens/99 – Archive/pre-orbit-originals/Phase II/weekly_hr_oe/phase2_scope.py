from __future__ import annotations

import re


TM_SELF_SERVICE_CAPABILITIES = [
    "Clock in / clock out at a timeclock or via the app.",
    "View current timecard for the pay period.",
    "Edit or submit a missed punch or forgot-to-punch request.",
    "Submit timecard corrections or edits for manager approval.",
    "View punch history and punch detail, including location, device, and timestamps.",
    "Confirm or acknowledge punches when the device or app prompts.",
    "View published schedule and future shifts.",
    "View time off balances and accruals.",
    "View status of submitted requests such as timecard edits and PTO.",
    "Get notifications of approvals, denials, or required actions.",
    "Complete simple approval tasks in app when approver rights are enabled.",
]


WFM_ASSIGNMENT_GROUP_SCOPE_NOTE = (
    "Phase II ticket extracts do not include a dedicated resolver field, so WFM-owned tickets are "
    "excluded by assignment-group proxy. Any row assigned to Real Time Analyst or WFM queues is treated "
    "as non-HR workload and removed from HR reporting."
)


def normalize_scope_text(value: str) -> str:
    text = (value or "").strip().lower()
    return re.sub(r"\s+", " ", text)


def is_wfm_assignment_group(assignment_group: str) -> bool:
    normalized = normalize_scope_text(assignment_group)
    if not normalized:
        return False
    return any(
        marker in normalized
        for marker in (
            "real time analyst",
            "wfm",
            "workforce management",
            "nice operations",
            "scheduling team",
        )
    )
