# BI Usage

## Which files to import

The BI-ready layer lives in `outputs/bi/`.

This repository is now best read as a mining planning and performance analytics project, so the first BI pages should emphasize KPI monitoring and scenario planning. Valuation and Monte Carlo should appear later as advanced modules.

## Current interpretation rule

The current exports are workbook-seeded planning outputs.

That means:

- they are valid for planning-style dashboards, scenario comparison, and KPI storytelling
- they are **not** live operating actuals
- they should **not** be labeled as true `actual vs plan` until actual operating data is added

Use labels such as:

- reference case
- planning case
- operating stress case
- market case
- downside case

## Power BI import order

1. `dim_year.csv`
2. `dim_metric.csv`
3. `dim_scenario.csv`
4. `fact_annual_metrics.csv`
5. `fact_scenario_kpis.csv`
6. `fact_simulation_distribution.csv`
7. `fact_tornado_sensitivity.csv`
8. `fact_heatmap_price_grade.csv`
9. `simulation_summary.csv`
10. `simulation_percentiles.csv`
11. `benchmark_comparison.csv`

Then use these repository assets:

- `powerbi/copper_risk_theme.json`
- `powerbi/DAX_MEASURES.md`
- `powerbi/DASHBOARD_BLUEPRINT.md`
- `powerbi/dashboard_visual_map.csv`

## Tableau source split

Use separate Tableau sources instead of one merged extract:

- Executive planning source:
  `fact_scenario_kpis.csv` + `dim_scenario.csv`
- Annual KPI source:
  `fact_annual_metrics.csv` + `dim_year.csv` + `dim_metric.csv` + `dim_scenario.csv`
- Advanced downside source:
  `fact_simulation_distribution.csv` + `simulation_summary.csv` + `simulation_percentiles.csv`
- Sensitivity source:
  `fact_tornado_sensitivity.csv`
- Heatmap source:
  `fact_heatmap_price_grade.csv`
- Benchmark source:
  `benchmark_comparison.csv`

## What each table is for

### Dimensions

- `dim_year.csv`
  Project year dimension with calendar year and project phase.
- `dim_metric.csv`
  Metric dictionary used by the annual KPI mart.
- `dim_scenario.csv`
  Scenario dictionary with names, categories, and stress multipliers.

### Main marts

- `fact_annual_metrics.csv`
  Main annual mining KPI mart by `year`, `scenario_id`, and `metric`.
  Use it for throughput, production, grade, recovery, unit cost, revenue, EBITDA, operating cash flow, capex, and free cash flow trends.
- `fact_scenario_kpis.csv`
  Executive scenario mart.
  Use it for KPI cards and comparison views covering revenue, EBITDA, opex, operating cash flow, free cash flow, throughput, copper production, unit opex, margin proxy, and selected valuation outputs.

### Advanced analytical marts

- `fact_simulation_distribution.csv`
  Monte Carlo NPV distribution with path summary fields.
  Use it only on advanced valuation and downside pages.
- `fact_tornado_sensitivity.csv`
  Tornado sensitivity impacts versus the base case.
- `fact_heatmap_price_grade.csv`
  Price-grade stress grid.

### Support tables

- `simulation_summary.csv`
  Summary statistics from the Monte Carlo engine.
- `simulation_percentiles.csv`
  Percentile cutoffs for the NPV distribution.
- `benchmark_comparison.csv`
  Audit-style benchmark table with explicit comparability flags, basis metadata, and reconciliation notes.
- `powerbi_measure_catalog.csv`
  Suggested Power BI measure inventory generated from the Python semantic layer.

## Recommended dashboard sequence

1. Executive Planning Overview
   Use `fact_scenario_kpis.csv` and `dim_scenario.csv`.
2. Throughput and Production
   Use `fact_annual_metrics.csv`, `dim_year.csv`, and `dim_metric.csv`.
3. Grade and Recovery
   Use `fact_annual_metrics.csv`, `dim_year.csv`, and `dim_metric.csv`.
4. Cost, Revenue and Cash Generation
   Use `fact_annual_metrics.csv`, `dim_year.csv`, and `dim_metric.csv`.
5. Scenario Planning and Price Exposure
   Use `fact_scenario_kpis.csv`, `dim_scenario.csv`, and selected annual pricing metrics.
6. Advanced Valuation and Downside Risk
   Use `fact_simulation_distribution.csv`, `simulation_summary.csv`, `simulation_percentiles.csv`, `fact_tornado_sensitivity.csv`, and `fact_heatmap_price_grade.csv`.
7. Benchmark and Method Transparency
   Use `benchmark_comparison.csv`.

## Power BI recommendation

Use a star-style model:

- `dim_year` -> `fact_annual_metrics`
- `dim_metric` -> `fact_annual_metrics`
- `dim_scenario` -> `fact_annual_metrics`
- `dim_scenario` -> `fact_scenario_kpis`

Keep the simulation, tornado, heatmap, and benchmark tables disconnected unless you have a specific modeling reason to connect them. Do not force everything into one denormalized table.

## Tableau recommendation

Use separate data sources by page or visual family:

- Planning and KPI trends: `fact_annual_metrics.csv`
- Executive scenario comparison: `fact_scenario_kpis.csv`
- Advanced downside pages: `fact_simulation_distribution.csv`
- Sensitivity pages: `fact_tornado_sensitivity.csv`
- Heatmap pages: `fact_heatmap_price_grade.csv`
- Benchmark page: `benchmark_comparison.csv`

This is simpler and safer than trying to stitch all facts together into one giant source.

## Next extension for a fuller mining BI platform

If you later add true operating actuals, the clean next step is:

- keep the current planning/scenario marts intact
- add actual period tables separately
- build explicit variance views on top of plan and actuals

Do not overwrite the current reference-case outputs and call them actuals.

For the detailed Power BI build sequence, use `powerbi/DASHBOARD_BLUEPRINT.md`.
