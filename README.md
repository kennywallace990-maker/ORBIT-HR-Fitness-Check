# ORBIT HR Fitness Check

**HR Fitness Check** gives Fulfillment Center HR Operations Teams an objective, repeatable, and evidence-backed quarterly assessment of Standard Work. The quarter ends with clear strengths, opportunities, and action plans rather than a manual workbook exercise.

Powered by **ORBIT**, Chewy's AI-powered HR operating layer, HR Fitness Check automates the collection, analysis, and visualization of Standard Work compliance data across your network.

---

## What is HR Fitness Check?

HR Fitness Check is a quarterly assessment tool that evaluates how well your HR operations team executes Standard Work across all fulfillment centers. It provides:

- **Objective Evidence**: Data-driven assessments based on automated metrics and manual validation
- **Repeatable Process**: Standardized evaluation framework that runs consistently each quarter
- **Actionable Insights**: Clear identification of strengths, opportunities, and specific action items
- **Network Visibility**: Site-level, region-level, and network-wide rollup views

### Key Features

- **Site Assessment View**: Detailed workbook baseline counts, Quality Index preview, strengths, opportunities, lineage flags, and line-item evidence
- **Region Rollups**: Aggregated views for 1G, 2G, Rx, and network averages
- **Manual Input Queue**: Simulates physical inspection or hybrid validation ratings while preserving data lineage
- **Catalog Workbench**: Stable Standard Work IDs, source families, automation status, aliases, and reconciliation risks
- **Readiness Board**: Governance and launch-scope decision tracking

---

## Getting Started

### Prerequisites

- Python 3.8+
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Access to source workbooks (see below)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/kennywallace990-maker/ORBIT-HR-Fitness-Check.git
cd ORBIT-HR-Fitness-Check
```

2. Install Python dependencies (if regenerating data):
```bash
pip install openpyxl pandas
```

### Quick Start

#### View the Prototype

Open the POC interface in your browser:

```
./poc/index.html
```

This displays the static Phoenix-style ORBIT workspace with pre-loaded Q3 assessment data.

#### Regenerate Data

To update the assessment with new workbook data:

1. Place your source workbooks in `C:\Users\kwallace12\Downloads\`:
   - `2025 Q3 HR Fitness Check.xlsx`
   - `2025 Q3 SW Quality Index.xlsx`
   - `2025 Q3 Fitness Assessment (based on NEW metrics).xlsx`

2. Run the extraction script from the project root:
```powershell
python .\poc\scripts\extract_workbook_data.py
```

3. Refresh `./poc/index.html` in your browser to see updated data

---

## Project Structure

```
ORBIT-HR-Fitness-Check/
|-- poc/                          # Proof of Concept - Static ORBIT workspace
|   |-- index.html                # Main entry point
|   |-- app.js                    # Core application logic
|   |-- styles.css                # Styling
|   |-- README.md                 # POC-specific documentation
|   |-- assets/                   # Images, icons, logos
|   |-- data/                     # Generated assessment data
|   `-- scripts/
|       `-- extract_workbook_data.py  # Data extraction from Excel workbooks
|-- docs/                         # Discovery PRD and checklist disposition
|-- knowledge-base/               # Source discovery and ingestion planning
|-- outputs/                      # Generated grounding partner workbook
|-- output/                       # Generated POC outputs and reports
|-- LICENSE                       # License information
`-- README.md                     # This file
```

---

## Data Flow

```
Source Workbooks (Excel)
    ->
extract_workbook_data.py
    ->
data.json (Generated assessment data)
    ->
app.js (Client-side processing)
    ->
Browser UI (Phoenix-style ORBIT workspace)
```

### Data Sources

The assessment pulls from three primary workbooks:

1. **HR Fitness Check Workbook**: Baseline counts and manual assessments
2. **SW Quality Index**: Canonical quality metrics for Standard Work items
3. **Fitness Assessment**: NEW metrics-based evaluation framework

---

## Features & Views

### Site Assessment
Drill into individual fulfillment center performance with:
- Workbook baseline counts
- Quality Index preview
- Strengths and opportunities
- Lineage flags for data provenance
- Line-item evidence supporting each assessment

### Region Views
Aggregate performance across:
- 1G (Single-generation) sites
- 2G (Two-generation) sites
- Rx (Specialty) sites
- Network totals and averages

### Manual Input Queue
Manage hybrid validation workflows:
- Queue items for physical inspection or manual review
- Preserve data lineage (track `manual_input` source)
- Simulate validation ratings before committing to assessment

### Catalog Workbench
Maintain Standard Work governance:
- Stable Standard Work IDs and aliases
- Source family classification
- Automation status tracking
- Reconciliation risk identification

### Readiness Board
Track assessment governance:
- Launch scope decisions
- Stakeholder sign-off status
- Dependency tracking
- Timeline management

---

## Configuration

### Updating Source Paths

Edit the paths in `poc/scripts/extract_workbook_data.py` to point to your workbook locations:

```python
WORKBOOK_PATHS = {
    'fitness_check': r'C:\Users\kwallace12\Downloads\2025 Q3 HR Fitness Check.xlsx',
    'quality_index': r'C:\Users\kwallace12\Downloads\2025 Q3 SW Quality Index.xlsx',
    'fitness_assessment': r'C:\Users\kwallace12\Downloads\2025 Q3 Fitness Assessment (based on NEW metrics).xlsx',
}
```

### Customizing Site Groups

Modify site groupings in the data extraction script or directly in the generated `data.json`:

```json
{
  "site_groups": {
    "1G": ["HOU1", "PHX1", ...],
    "2G": ["DEN1", "ATL1", ...],
    "Rx": ["RXC1", ...],
    "TOTAL AVGs": [...]
  }
}
```

---

## Development

### Running Locally

The POC is a static HTML/CSS/JavaScript application with no build step required. Simply open `poc/index.html` in your browser.

For development with live reload, use a local HTTP server:

```bash
# Python 3
python -m http.server 8000

# Then visit http://localhost:8000/poc/index.html
```

### Modifying the UI

- **Layout & Components**: Edit `poc/app.js` (view rendering logic)
- **Styling**: Update `poc/styles.css`
- **Data**: Regenerate via `extract_workbook_data.py` or edit `poc/data/data.json` directly

### Adding New Views

1. Add a new navigation item in `app.js`:
```javascript
{ id: "myview", label: "My View", icon: "V" }
```

2. Implement the render function:
```javascript
function renderMyView() {
  // Return HTML for your view
}
```

3. Add a case in the main render switch statement

---

## Data Lineage & Governance

HR Fitness Check tracks the provenance of every assessment metric:

- **`workbook`**: Data sourced from manual workbook entry
- **`quality_index`**: Derived from canonical SW Quality Index
- **`manual_input`**: Result of physical inspection or hybrid validation
- **`computed`**: Calculated from other metrics (e.g., rollups, averages)

This lineage is visible in the UI and preserved through all transformations.

---

## Discovery Knowledge Base

The current discovery package is in the root documentation and knowledge-base folders:

- `docs/HR-Fitness-Check-PRD.md`
- `docs/Reviewed-Checklist-Disposition.md`
- `knowledge-base/README.md`
- `knowledge-base/source-inventory.md`
- `knowledge-base/voc-pulse-action-roadmap.md`
- `knowledge-base/ingestion-backlog.md`
- `knowledge-base/snowflake-discovery-playbook.md`
- `knowledge-base/snowflake-discovery-results.md`
- `knowledge-base/research-log.md`

The VOC Pulse action roadmap is action-loop and recommendation-library context. It should not be treated as direct Fitness Check scoring input unless a specific approved metric, source field, and rule are added to the catalog.

---

## Troubleshooting

### Data Not Updating

1. Verify source workbook paths in `extract_workbook_data.py`
2. Check that workbooks are closed (not locked by Excel)
3. Run the extraction script and check for error messages
4. Refresh the browser (Ctrl+Shift+R for hard refresh)

### Missing Sites or Metrics

1. Confirm source workbooks contain the expected data
2. Check site IDs match between workbooks
3. Verify Standard Work item IDs are consistent
4. Review the generated `data.json` for completeness

### Browser Compatibility

- Chrome/Chromium: Full support
- Firefox: Full support
- Safari: Full support
- Edge: Full support
- IE11: Not supported

---

## Contributing

To contribute improvements or fixes:

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes and test locally
3. Commit with clear messages: `git commit -m "Add feature description"`
4. Push to your fork and submit a pull request

---

## Support & Documentation

For more information, see:

- **Product Requirements**: `01 - PRD, HR Fitness Check.md`
- **Data Dictionary**: `03 - Data Dictionary, HR Fitness Check.md`
- **Technical Design**: `04 - Technical Design Doc, HR Fitness Check.md`
- **Test Plan**: `06 - Test Plan, HR Fitness Check.md`
- **Runbook**: `07 - Runbook, HR Fitness Check.md`

---

## License

This project is licensed under the terms specified in the LICENSE file.

---

## Questions?

Contact the ORBIT product team or refer to the comprehensive documentation in the `99 - Program Docs/` directory.

---

**Last Updated**: June 2026  
**Version**: 1.0 POC
