# BI Usage

## Which files to import

The BI-ready layer lives in `outputs/bi/`.

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
  Directional Excel vs Python comparison.
- `powerbi_measure_catalog.csv`
  Suggested measure definitions for Power BI.

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
