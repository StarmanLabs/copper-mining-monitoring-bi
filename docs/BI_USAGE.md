# BI Usage

## Which files to import

The BI-ready layer lives in `outputs/bi/`.

## If you are building the dashboard now

### Power BI import order

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

### Tableau source split

Use separate Tableau sources instead of one merged extract:

- Executive and scenario comparison:
  `fact_scenario_kpis.csv` + `dim_scenario.csv`
- Annual operating profile:
  `fact_annual_metrics.csv` + `dim_year.csv` + `dim_metric.csv` + `dim_scenario.csv`
- Monte Carlo risk:
  `fact_simulation_distribution.csv` + `simulation_summary.csv` + `simulation_percentiles.csv`
- Sensitivity:
  `fact_tornado_sensitivity.csv`
- Heatmap:
  `fact_heatmap_price_grade.csv`
- Benchmark page:
  `benchmark_comparison.csv`

### Dimensions

- `dim_year.csv`
  Project year dimension.
- `dim_metric.csv`
  Metric dictionary used by the annual fact table.
- `dim_scenario.csv`
  Scenario dictionary with names and categories.

### Fact tables

- `fact_annual_metrics.csv`
  Main annual table by `year`, `scenario_id`, and `metric`.
  Use this for line charts, area charts, and yearly monitoring.
- `fact_scenario_kpis.csv`
  Scenario-level KPI table.
  Use this for KPI cards, bar comparisons, and executive summaries.
- `fact_simulation_distribution.csv`
  Monte Carlo NPV distribution.
  Use this for histograms, CDFs, percentile markers, and downside analysis.
  The table now also carries path summary fields such as average price, terminal price, price-path dispersion, grade factor, and recovery variation.
- `fact_tornado_sensitivity.csv`
  Tornado sensitivity impacts versus the base case.
  Use this for ranked driver charts.
- `fact_heatmap_price_grade.csv`
  Price-grade stress grid.
  Use this for a matrix or heatmap.

### Support tables

- `simulation_summary.csv`
  Summary statistics from the Monte Carlo engine.
- `simulation_percentiles.csv`
  Percentile cutoffs for the NPV distribution.
- `benchmark_comparison.csv`
  Audit-style benchmark reconciliation table with explicit comparability flags, basis metadata, notes, and status labels such as `reference_only`, `close_match`, or `material_gap`.
- `powerbi_measure_catalog.csv`
  Suggested measure definitions for Power BI.

## Power BI assets in the repository

Use the files in `powerbi/` together with the CSV layer:

- `powerbi/copper_risk_theme.json`
  Visual theme.
- `powerbi/DAX_MEASURES.md`
  Copy-ready measure set.
- `powerbi/DASHBOARD_BLUEPRINT.md`
  Page-by-page report design.
- `powerbi/dashboard_visual_map.csv`
  Structured visual inventory.

## Power BI recommendation

Use a star-style model:

- `dim_year` -> `fact_annual_metrics`
- `dim_metric` -> `fact_annual_metrics`
- `dim_scenario` -> `fact_annual_metrics`
- `dim_scenario` -> `fact_scenario_kpis`

Leave the simulation, tornado, and heatmap tables as separate facts connected only where needed. Do not force everything into one denormalized table.

## Tableau recommendation

Use separate data sources by page or visual family:

- Trends: `fact_annual_metrics.csv`
- Scenario comparison: `fact_scenario_kpis.csv`
- Simulation pages: `fact_simulation_distribution.csv`
- Sensitivity pages: `fact_tornado_sensitivity.csv`
- Heatmap pages: `fact_heatmap_price_grade.csv`

This is simpler and safer than trying to stitch all facts together into one giant source.

## First dashboard pages

1. Executive overview
   Use `fact_scenario_kpis.csv` and `dim_scenario.csv`.
2. Annual operating and cash flow profile
   Use `fact_annual_metrics.csv`.
3. Monte Carlo downside
   Use `fact_simulation_distribution.csv`, `simulation_summary.csv`, and `simulation_percentiles.csv`.
4. Sensitivity and stress
   Use `fact_tornado_sensitivity.csv` and `fact_heatmap_price_grade.csv`.

For the detailed Power BI build sequence, use `powerbi/DASHBOARD_BLUEPRINT.md`.
