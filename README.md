# Copper Mining Risk Model

Rebuilding a spreadsheet-based copper mining valuation into a reproducible Python analytics engine with deterministic scenario analysis, structured benchmark reconciliation, upgraded stochastic risk modeling, and BI-ready outputs for Power BI or Tableau.

## Portfolio snapshot

- Domain: mining economics, project valuation, and downside risk analysis
- Starting point: spreadsheet-based copper expansion model
- Rebuild target: auditable Python valuation and risk engine
- Delivery layer: BI-ready CSV tables plus a self-contained HTML dashboard
- Main value: scenario comparison, benchmark transparency, and dashboard-ready decision support

## Project objective

This repository converts an Excel mining valuation workflow into a Python-first analytical pipeline that is easier to audit, test, extend, and present as a portfolio-grade decision-support project.

The goal is not spreadsheet replacement for its own sake. The goal is to make the model:

- more reproducible
- clearer about what is economically being valued
- more explicit about what is and is not comparable to the workbook benchmark
- stronger for downstream BI dashboards and portfolio presentation

## What the engine does

The project currently produces four analytical layers:

1. Deterministic expanded-project valuation in Python
2. Incremental-expansion benchmark reconciliation against the workbook
3. Stochastic downside analysis with annual price shocks and bounded operating uncertainty
4. BI-ready fact and dimension tables plus a self-contained HTML dashboard showcase

## What To Open First

If you are reviewing the repository on GitHub, start here:

1. `README.md`
   High-level project framing, scope, outputs, and limitations.
2. `docs/MODEL_NOTES.md`
   Technical note on valuation basis, benchmark logic, and model limits.
3. `outputs/dashboard/index.html`
   Portfolio-facing dashboard showcase generated from the BI exports.
4. `outputs/bi/benchmark_comparison.csv`
   Audit-style reconciliation table showing what is directly comparable and what is not.
5. `powerbi/DASHBOARD_BLUEPRINT.md`
   Page-by-page guide to rebuild the dashboard in Power BI.

## Analytical design

### Deterministic model

The deterministic engine values the expanded operating case in USD using:

- annual copper price deck from the workbook
- annual base throughput, grade, and recovery inputs from the workbook
- explicit payable and treatment/refining adjustments
- explicit cash operating costs
- simplified tax proxy aligned to the workbook cash-flow chain
- explicit year 0 and year 1 capex timing
- explicit working-capital treatment
- explicit discounted free cash flow, NPV, and IRR

The deterministic scenario layer then stresses price, grade, recovery, throughput, opex, capex, and discount rate for BI comparison and dashboard storytelling.

### Benchmark reconciliation

The workbook benchmark is not treated as a generic "Excel truth table".

Instead, the repo now distinguishes between:

- `total_project_expanded_operation`: the main Python valuation used for scenarios and dashboard KPIs
- `incremental_expansion`: the workbook-style benchmark basis used for deterministic reconciliation

The benchmark comparison table in `outputs/bi/benchmark_comparison.csv` explicitly flags:

- units
- currency
- valuation basis
- timing basis
- comparability status
- explanatory notes

`gap` and `pct_gap` are only computed when direct comparison is defensible, and directly comparable rows are still flagged when the remaining residual gap is material.

### Stochastic model

The Monte Carlo layer keeps the deterministic model as the base case and upgrades the stochastic structure by:

- simulating annual copper price variation around the workbook price deck with autocorrelated lognormal shocks
- treating grade uncertainty as a project-level multiplier
- treating recovery uncertainty as bounded yearly variation
- preserving seed reproducibility
- exporting a BI-friendly simulation distribution table

This is intentionally a practical project-risk engine, not a full commodity-process research model.

## Data flow

```text
Excel workbook
  -> structured loader with sheet/cell validation
  -> deterministic model
  -> scenario analysis
  -> Monte Carlo simulation
  -> benchmark reconciliation
  -> BI exports
  -> HTML dashboard showcase
```

## Files to use in Power BI or Tableau

Use the files in `outputs/bi/`.

### Minimum file set by dashboard page

- Executive scenario dashboard:
  `fact_scenario_kpis.csv`, `dim_scenario.csv`
- Annual operating and cash flow trends:
  `fact_annual_metrics.csv`, `dim_year.csv`, `dim_metric.csv`, `dim_scenario.csv`
- Monte Carlo risk page:
  `fact_simulation_distribution.csv`, `simulation_summary.csv`, `simulation_percentiles.csv`
- Sensitivity and stress page:
  `fact_tornado_sensitivity.csv`, `fact_heatmap_price_grade.csv`
- Benchmark credibility page:
  `benchmark_comparison.csv`

### Core model tables

- `dim_year.csv`
- `dim_metric.csv`
- `dim_scenario.csv`
- `fact_annual_metrics.csv`
- `fact_scenario_kpis.csv`
- `fact_simulation_distribution.csv`
- `fact_tornado_sensitivity.csv`
- `fact_heatmap_price_grade.csv`

### Support tables

- `simulation_summary.csv`
- `simulation_percentiles.csv`
- `benchmark_comparison.csv`
- `powerbi_measure_catalog.csv`

For Power BI, keep each fact table attached only to the dimensions it actually uses.

For Tableau, it is usually cleaner to work with separate subject-area sources rather than forcing all facts into one denormalized extract.

### Exact recommendation for Power BI

Import these first:

- `outputs/bi/dim_year.csv`
- `outputs/bi/dim_metric.csv`
- `outputs/bi/dim_scenario.csv`
- `outputs/bi/fact_annual_metrics.csv`
- `outputs/bi/fact_scenario_kpis.csv`
- `outputs/bi/fact_simulation_distribution.csv`
- `outputs/bi/fact_tornado_sensitivity.csv`
- `outputs/bi/fact_heatmap_price_grade.csv`
- `outputs/bi/simulation_summary.csv`
- `outputs/bi/simulation_percentiles.csv`
- `outputs/bi/benchmark_comparison.csv`

Then use:

- `powerbi/DAX_MEASURES.md`
- `powerbi/DASHBOARD_BLUEPRINT.md`
- `powerbi/dashboard_visual_map.csv`
- `powerbi/copper_risk_theme.json`

### Exact recommendation for Tableau

Use separate data sources instead of one big model:

- Scenario source:
  `fact_scenario_kpis.csv`, `dim_scenario.csv`
- Annual profile source:
  `fact_annual_metrics.csv`, `dim_year.csv`, `dim_metric.csv`, `dim_scenario.csv`
- Monte Carlo source:
  `fact_simulation_distribution.csv`, `simulation_summary.csv`, `simulation_percentiles.csv`
- Sensitivity source:
  `fact_tornado_sensitivity.csv`
- Heatmap source:
  `fact_heatmap_price_grade.csv`
- Benchmark source:
  `benchmark_comparison.csv`

## Repository structure

```text
copper_minning_risk_model/
  config/                     Project configuration
  data/raw/                   Source Excel workbook
  docs/                       Technical notes and usage guidance
  outputs/bi/                 BI-ready CSV exports
  outputs/dashboard/          Self-contained HTML dashboard output
  powerbi/                    Theme, DAX, and dashboard blueprint assets
  scripts/                    Build entrypoints
  src/copper_risk_model/      Loader, model, simulation, BI export, dashboard code
  tests/                      Analytical and smoke tests
```

## How to run

Install dependencies:

```bash
python -m pip install -e .[dev]
```

Build BI tables:

```bash
python scripts/build_bi_dataset.py
```

Build BI tables plus the HTML dashboard:

```bash
python scripts/build_portfolio_dashboard.py
```

Run tests:

```bash
python -m pytest -q
```

## Technical notes

- Model scope and conventions: `docs/MODEL_NOTES.md`
- BI usage guidance: `docs/BI_USAGE.md`
- Folder guide: `docs/PROJECT_STRUCTURE.md`
- Power BI page design: `powerbi/DASHBOARD_BLUEPRINT.md`
- Power BI measure set: `powerbi/DAX_MEASURES.md`

## Main limitations

This repository is a serious analytical rebuild, but it is still deliberately simplified.

It does not claim:

- full formula-by-formula Excel parity
- a complete mining fiscal regime
- engineering-grade mine planning realism
- a structural commodity-price forecasting model
- tight deterministic reconciliation to every workbook line item

What it does claim honestly is:

> This project rebuilds a spreadsheet-based copper mining valuation into a reproducible Python analytical engine with improved scenario design, stronger stochastic risk modeling, explicit benchmark reconciliation, and BI-ready outputs for decision support.

## Disclaimer

This is an analytical portfolio project based on a hypothetical mining expansion case. It is not investment advice and should not substitute for geological, metallurgical, fiscal, financial, or operational due diligence.

