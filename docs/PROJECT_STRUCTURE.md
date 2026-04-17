# Project Structure

## Folder guide

- `config/`
  Project configuration, scenario assumptions, and the path to the source workbook.
- `data/raw/`
  Raw input files. This is the original workbook used by the current pipeline.
- `src/copper_risk_model/`
  Core Python package.
  This is the planning, KPI, scenario, and advanced-risk engine.
- `scripts/`
  Entry points to build outputs.
- `outputs/bi/`
  Final KPI marts and analytical support tables for Power BI and Tableau.
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
- `docs/PORTFOLIO_POSITIONING.md`
  Why the repo fits mining planning, management control, BI, and economics-facing roles.
- `outputs/dashboard/index.html`
  Ready-to-show dashboard artifact.
- `outputs/bi/fact_annual_metrics.csv`
  Main annual mining KPI mart.
- `outputs/bi/fact_scenario_kpis.csv`
  Executive scenario mart.
- `docs/MODEL_NOTES.md`
  Technical note for platform scope, benchmark basis, and limitations.
- `docs/BI_USAGE.md`
  Exact guidance on which files to import into Power BI or Tableau.
- `outputs/bi/benchmark_comparison.csv`
  Audit-style reconciliation output for technical credibility.

## Python package files

- `excel_loader.py`
  Reads the workbook and extracts structured assumptions and benchmarks.
- `model.py`
  Deterministic operating and cash flow model.
- `simulation.py`
  Advanced Monte Carlo engine.
- `scenario_analysis.py`
  Deterministic scenarios plus KPI aggregation, tornado table, and heatmap generation.
- `bi_semantic.py`
  Semantic helpers for KPI catalogs, dashboard page structure, and Power BI measure guidance.
- `bi_export.py`
  Builds the BI-ready KPI marts and advanced analytical tables.
- `dashboard_builder.py`
  Builds the self-contained HTML dashboard showcase.
- `__main__.py`
  Package entrypoint.

## Documentation

- `PORTFOLIO_POSITIONING.md`
  Public positioning note for portfolio use.
- `MODEL_NOTES.md`
  Technical note on platform scope, benchmark scope, stochastic design, and remaining limits.
- `BI_USAGE.md`
  Which exports to use in Power BI or Tableau and how to connect them.

## Build scripts

- `build_bi_dataset.py`
  Generates the BI-ready marts and analytical support tables.
- `build_portfolio_dashboard.py`
  Generates the BI-ready marts and the dashboard showcase.

## Files to leave alone

- `data/raw/Copper_mining_risk_model.xlsm`
  This is the raw workbook input.
- `config/project.yaml`
  If you move the workbook or rename outputs, update this file carefully.
