# ORBIT Products - Chewy Brand Compliance Guide

All ORBIT product reports and UX artifacts must follow the Chewy Masterbrand Guidelines.
Full guidelines are in this folder: `chewy_masterbrand_ordered.md` and `chewy_masterbrand_ordered.json`.

---

## Quick Reference: Approved Color Palette

### Core Colors (use everywhere)
| Name | HEX | Usage |
|------|-----|-------|
| Chewy Blue | `#1C49C2` | Primary brand color, CTAs, links, headers, gradients |
| Royal Blue | `#001A70` | Dark headers, table headers, --ink text, section borders |
| Sky Blue | `#DFEAFF` | Light backgrounds, badges, hover states, callout fills |
| White | `#FFFFFF` | Surfaces, panels, card backgrounds |

### Accent Colors (Chewy-owned channels only, never pair two)
| Name | HEX | Usage |
|------|-----|-------|
| Magenta | `#E83B91` | Strategic emphasis only |
| Orange | `#FF7A2F` | Strategic emphasis only |
| Emerald | `#00CC75` | Strategic emphasis only |
| Key Lime | `#D4FDAA` | Strategic emphasis only |
| Bluey | `#A8B8F7` | Light accent, mid-tone blue fills |

### Functional/Status Colors (retained for data UX)
| Purpose | HEX | Notes |
|---------|-----|-------|
| Success/Green | `#14643a` or `#2E7D32` | Positive indicators |
| Error/Red | `#9b2c2c` or `#C62828` | Critical/alert indicators |
| Warning/Amber | `#7a3e00` or `#E65100` | Caution indicators |

> Functional status colors are standard UX patterns and are acceptable in data-driven reports.
> They must not be used as brand identity colors.

---

## Typography

| Priority | Font | Usage |
|----------|------|-------|
| 1 | **Gordita** (Regular, Bold) | Brand typeface for all external and internal materials |
| 2 | **Roboto** (fallback) | Internal-only fallback when Gordita is unavailable |
| 3 | system-ui, sans-serif | Final fallback for environments without web fonts |

**CSS font stack:**
```css
font-family: 'Gordita', 'Roboto', system-ui, sans-serif;
```

### Rules
- Use regular weight for majority of text
- Bold sparingly and intentionally
- Never use accent colors for text
- Never use all-caps for emphasis
- Never angle text
- Sentence case for headlines, subcopy, and CTAs

---

## CSS Variable Template

Copy this into any new ORBIT report's `:root`:

```css
:root {
  --blue: #1C49C2;       /* Chewy Blue */
  --dark: #001A70;        /* Royal Blue */
  --light: #DFEAFF;       /* Sky Blue */
  --surface: #FFFFFF;
  --bg: #F7F9FC;
  --t1: #1A1A2E;          /* Primary text */
  --t2: #4A4A6A;          /* Secondary text */
  --tm: #8888A8;          /* Muted text */
  --border: #E2E8F0;
  --r: 10px;              /* Border radius */
  /* Functional status colors */
  --green: #2E7D32;
  --green-bg: #E8F5E9;
  --red: #C62828;
  --red-bg: #FFEBEE;
  --amber: #E65100;
  --amber-bg: #FFF8E1;
}
```

---

## Gradient Template

```css
background: linear-gradient(135deg, var(--dark), var(--blue) 60%, #2D5BD2);
```

---

## Products Updated (2026-03-24)

| Product | Files Updated | Status |
|---------|--------------|--------|
| 01 - Daily People Pulse | DPP_POC_Mock.html, design spec | Compliant |
| 04 - Workload Lens | Report_Template_Executive.html, _Integrated.html, _Variance.html, _Insights.html | Compliant |
| 04 - Workload Lens (WBR) | OBR_Week9, hr_oe_report_for_vp_wk9, hr_oe_exec_review_wk9, _wk10, workload_lens_insights | Compliant |
| 05 - ECHO Intelligence | 2025_VOC_Pulse_Report.html, _Rx_Network.html | Compliant |

---

## What Changed

### Colors
- `#0046BE` → `#1C49C2` (Chewy Blue)
- `#002E7D` → `#001A70` (Royal Blue)
- `#E8F0FE` → `#DFEAFF` (Sky Blue)
- `#1565C0` → `#1C49C2` (gradient endpoint)
- `#0d5f73` (teal) → `#1C49C2` (Chewy Blue)
- `#5b21b6` (purple) → `#001A70` (Royal Blue)

### Fonts
- Inter → Gordita/Roboto
- Georgia/Times New Roman → Gordita/Roboto
- Aptos/Segoe UI/Calibri → Gordita/Roboto

---

## Rules to Follow for New Reports

1. Use exact approved color values. Do not approximate brand colors.
2. Never pair two accent colors in the same design.
3. Do not use accent colors in CTA buttons.
4. Keep shapes soft with rounded corners (10-12px border-radius).
5. Sentence case everywhere - no all-caps for emphasis.
6. Gordita is the only approved brand typeface; Roboto is the internal fallback.
7. Reference `99 - Program Docs/brand/chewy_masterbrand_ordered.md` for full guidelines.
