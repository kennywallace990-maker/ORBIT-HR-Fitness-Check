# Chewy Codex Brand Package v2

This package reorganizes the saved Master Brand Guidelines export so it follows the same top-level order shown in Bynder.

Recommended setup:
- place `AGENTS.md` at the repo root
- place the rest of this folder in `/brand`
- use `chewy_masterbrand_ordered.md` as the first reference file for manual review
- use `chewy_masterbrand_ordered.json` for structured lookups in tools or scripts

Notes:
- The ordered files are cleaned from the saved HTML export and may still contain some extraction noise.
- The `raw` folder preserves the earlier raw extraction for comparison.
- The saved export did not appear to include a distinct Video page, so that section is called out as missing.


Color update:
- The ordered markdown and JSON now include exact approved Chewy color values from the 2026 Chewy Brand Toolkit PDF, including HEX, RGB, CMYK, and PMS where available.
- These values should be treated as the source of truth for implementation and should not be approximated.
