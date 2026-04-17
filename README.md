# Copper Mining Planning and Performance Analytics

Workbook-seeded mining inputs are transformed into reproducible KPI marts for planning, performance monitoring, scenario comparison, dashboarding, and decision support. Valuation, scenario analysis, and Monte Carlo remain in the repository, but they now sit as advanced analytical modules behind a broader mining BI and management-control story.

## Portfolio snapshot

- Domain: mining planning support, performance analytics, cost review, and BI
- Starting point: a spreadsheet-based copper expansion case
- Current implementation: workbook-seeded, Python-first analytical pipeline
- Delivery layer: BI-ready CSV marts plus a self-contained HTML dashboard showcase
- Advanced module set: scenario valuation, benchmark reconciliation, and Monte Carlo downside analysis
- Best fit: economics + data roles in planning, management control, business analysis, and mining BI

## Project positioning

This repository should be read first as a mining analytics platform for business-facing functions, not as a pure valuation rebuild.

The core story is:

- convert mining inputs into canonical KPI layers
- monitor throughput, grade, recovery, cost, and cash-generation proxies
- compare planning cases and commodity-price exposure
- feed Power BI or Tableau with reusable subject-area marts
- preserve valuation and risk analysis as advanced decision-support modules

The workbook origin still matters, but it is no longer the portfolio identity. The repo is organized around mining KPIs and downstream BI consumption rather than around spreadsheet tabs.

## Primary use cases

The platform is most relevant for mining teams working in:

- planning support
- management control
- business intelligence
- performance monitoring
- cost and margin review
- finance or business analysis support

It is intentionally credible for an economics graduate with mining domain adaptation. It does not pretend to be a mine-engineering or geology system.

## What the platform currently does

The repository currently produces four practical analytical layers:

1. Planning and performance KPI marts
   Throughput, production, price, grade, recovery, unit opex, revenue, EBITDA, operating cash flow, capex, working capital, and free cash flow are exported in BI-friendly structures.
2. Scenario planning and decision-support views
   Deterministic scenario tables compare reference, market, operating, capital, and downside cases for management discussion.
3. Advanced valuation and risk modules
   NPV, IRR, Monte Carlo downside, tornado sensitivity, and price-grade stress remain available as secondary analytical layers.
4. Benchmark and transparency layer
   Workbook reconciliation is kept as an audit-oriented module so comparability is explicit rather than implied.

## Data reality and scope

This is a source-extensible portfolio project, but the current implementation is still workbook-seeded.

That distinction matters:

- the current source is `data/raw/Copper_mining_risk_model.xlsm`
- the downstream analytics layer is organized around mining business entities and KPI marts, not around workbook sheets
- the current exports are suitable for planning-style dashboards and scenario monitoring
- the current repo does **not** yet contain true plant actuals, dispatch data, lab assay feeds, or ERP cost actuals

So the honest interpretation is:

- planning and monitoring-ready architecture: yes
- live actual-vs-plan operational monitoring: not yet
- advanced valuation and risk decision support: yes

## What To Open First

If you are reviewing the repository on GitHub, start here:

1. `README.md`
   Public-facing framing, use cases, outputs, and limitations.
2. `docs/PORTFOLIO_POSITIONING.md`
   Positioning note that explains why the repo fits mining planning, control, BI, and economics-facing roles.
3. `outputs/dashboard/index.html`
   Portfolio dashboard showcase built from the BI exports.
4. `outputs/bi/fact_annual_metrics.csv`
   The main annual mining KPI mart used for Power BI or Tableau.
5. `outputs/bi/fact_scenario_kpis.csv`
   Executive scenario mart with revenue, EBITDA, throughput, unit-cost, margin-proxy, and valuation summary fields.
6. `powerbi/DASHBOARD_BLUEPRINT.md`
   Page-by-page guide to rebuild the project as a professional BI dashboard.

## Canonical BI marts

The repository is most useful when read through the output marts in `outputs/bi/`.

### Core business-facing marts

- `fact_annual_metrics.csv`
  Main annual KPI mart for throughput, production, grade, recovery, pricing, unit cost, revenue, EBITDA, operating cash flow, capex, and free cash flow.
- `fact_scenario_kpis.csv`
  Executive scenario mart with total revenue, EBITDA, opex, operating cash flow, free cash flow, average throughput, average copper production, average unit opex, margin proxy, and selected valuation KPIs.
- `dim_year.csv`
  Calendar and project-phase dimension.
- `dim_metric.csv`
  Metric dictionary with category, unit, and suggested dashboard page.
- `dim_scenario.csv`
  Scenario catalog for deterministic planning cases.

### Advanced analytical marts

- `fact_simulation_distribution.csv`
  Monte Carlo distribution table for advanced downside analysis.
- `simulation_summary.csv`
  Monte Carlo summary statistics.
- `simulation_percentiles.csv`
  Percentile table for tail-risk readouts.
- `fact_tornado_sensitivity.csv`
  Driver ranking for advanced sensitivity analysis.
- `fact_heatmap_price_grade.csv`
  Price-grade stress grid.
- `benchmark_comparison.csv`
  Audit-style reconciliation table with explicit comparability fields.

## Files to use in Power BI or Tableau

Use the files in `outputs/bi/`.

### Recommended Power BI import order

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

### Recommended Tableau source split

Do not force everything into one giant model. Use separate subject-area sources:

- Executive planning source:
  `fact_scenario_kpis.csv`, `dim_scenario.csv`
- Annual KPI source:
  `fact_annual_metrics.csv`, `dim_year.csv`, `dim_metric.csv`, `dim_scenario.csv`
- Advanced downside source:
  `fact_simulation_distribution.csv`, `simulation_summary.csv`, `simulation_percentiles.csv`
- Sensitivity source:
  `fact_tornado_sensitivity.csv`
- Heatmap source:
  `fact_heatmap_price_grade.csv`
- Benchmark source:
  `benchmark_comparison.csv`

## Data flow

```text
Workbook input
  -> validated extraction layer
  -> annual mining KPI profile
  -> scenario planning outputs
  -> advanced valuation and risk modules
  -> benchmark transparency layer
  -> BI-ready marts
  -> HTML dashboard showcase
```

## Repository structure

```text
copper_minning_risk_model/
  config/                     Project configuration
  data/raw/                   Source workbook input
  docs/                       Positioning, model notes, and BI guidance
  outputs/bi/                 BI-ready KPI marts and support tables
  outputs/dashboard/          Self-contained HTML dashboard output
  powerbi/                    Theme, DAX, and dashboard blueprint assets
  scripts/                    Build entrypoints
  src/copper_risk_model/      Loader, KPI logic, scenarios, simulation, BI export, dashboard code
  tests/                      Analytical and smoke tests
```

The Python package namespace remains `copper_risk_model` for continuity, but the public framing is intentionally broader than valuation alone.

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

- Portfolio positioning: `docs/PORTFOLIO_POSITIONING.md`
- Platform scope and advanced module notes: `docs/MODEL_NOTES.md`
- BI usage guidance: `docs/BI_USAGE.md`
- Folder guide: `docs/PROJECT_STRUCTURE.md`
- Power BI page design: `powerbi/DASHBOARD_BLUEPRINT.md`
- Power BI measure set: `powerbi/DAX_MEASURES.md`

## Main limitations

This repository is stronger as a planning and BI portfolio project than as an engineering model, and it should be presented that way.

It does not claim:

- live operational actual-vs-plan monitoring from plant or ERP systems
- engineering-grade mine planning realism
- a full fiscal or corporate-finance model
- full formula-by-formula workbook parity
- structural commodity-price forecasting
- a mining-operations control room system fed by production telemetry

What it does claim honestly is:

> This project turns a workbook-seeded copper expansion case into a reproducible mining planning and performance analytics platform with KPI marts, scenario planning, benchmark transparency, advanced valuation and downside modules, and BI-ready outputs for decision support.

## Disclaimer

This is an analytical portfolio project based on a hypothetical copper mining expansion case. It is not investment advice and should not substitute for geological, metallurgical, engineering, fiscal, financial, or operating due diligence.

