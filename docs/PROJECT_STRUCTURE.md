# Project Structure

## Folder guide

- `config/`
  Project configuration, scenario assumptions, and the path to the source workbook.
- `data/raw/`
  Raw input files. This is the original workbook used by the Python pipeline.
- `src/copper_risk_model/`
  Core Python package.
  This is the analytical engine.
- `scripts/`
  Entry points to build outputs.
- `outputs/bi/`
  Final CSVs for Power BI and Tableau.
- `outputs/dashboard/`
  HTML showcase built from the BI exports.
- `powerbi/`
  Theme and Power BI-specific assets.
- `tests/`
  Analytical and smoke tests for model logic, simulation, reconciliation, and export integrity.
- `.github/workflows/`
  CI pipeline for GitHub Actions.

## Best entry points on GitHub

- `README.md`
  Public-facing overview of the portfolio project.
- `docs/MODEL_NOTES.md`
  Technical note for model scope, benchmark basis, and limitations.
- `docs/BI_USAGE.md`
  Exact guidance on which files to import into Power BI or Tableau.
- `outputs/dashboard/index.html`
  Ready-to-show dashboard artifact.
- `outputs/bi/`
  Portfolio-ready CSV outputs for BI consumption.

## Python package files

- `excel_loader.py`
  Reads the workbook and extracts structured assumptions and benchmarks.
- `model.py`
  Deterministic operating and cash flow model.
- `simulation.py`
  Monte Carlo engine.
- `scenario_analysis.py`
  Deterministic scenarios, tornado table, and heatmap generation.
- `bi_semantic.py`
  Semantic helpers for metrics and Power BI measure guidance.
- `bi_export.py`
  Builds the BI-ready CSV layer.
- `dashboard_builder.py`
  Builds the self-contained HTML dashboard showcase.
- `__main__.py`
  Package entrypoint.

## Documentation

- `MODEL_NOTES.md`
  Technical note on valuation basis, benchmark scope, stochastic design, and remaining limits.
- `BI_USAGE.md`
  Which exports to use in Power BI or Tableau and how to connect them.

## Build scripts

- `build_bi_dataset.py`
  Generates the BI-ready CSVs.
- `build_portfolio_dashboard.py`
  Generates the BI-ready CSVs and the dashboard showcase.

## Files to leave alone

- `data/raw/Copper_mining_risk_model.xlsm`
  This is the raw workbook input.
- `config/project.yaml`
  If you move the workbook or rename outputs, update this file carefully.
