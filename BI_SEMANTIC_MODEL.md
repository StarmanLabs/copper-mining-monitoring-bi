# BI Semantic Model

## Objective

Provide a clean analytical model for Power BI or Tableau so the project is presented as a decision-support product instead of a loose spreadsheet conversion.

## Core dimensions

### `dim_year.csv`

- `year`
- `calendar_year`
- `phase`
- `year_label`

### `dim_metric.csv`

- `metric`
- `display_name`
- `unit`
- `category`
- `dashboard_page`

### `dim_scenario.csv`

- `scenario_id`
- `scenario_name`
- `scenario_category`
- `description`
- driver multipliers and discount-rate shift

## Core fact tables

### `fact_annual_metrics.csv`

Grain:

- `scenario_id`
- `year`
- `metric`

Use for:

- annual trend charts
- scenario comparison over time
- revenue, EBITDA, capex, and cash flow pages

### `fact_scenario_kpis.csv`

Grain:

- `scenario_id`
- `metric`

Use for:

- scenario comparison cards
- ranking scenarios by NPV
- payback and peak-year analysis

### `fact_simulation_distribution.csv`

Grain:

- `iteration`

Use for:

- histograms
- scatter plots of factors vs NPV
- tail-risk analysis

### `fact_tornado_sensitivity.csv`

Grain:

- `driver`
- `direction`

Use for:

- tornado visual
- ranking of key downside drivers

### `fact_heatmap_price_grade.csv`

Grain:

- `price_factor`
- `grade_factor`

Use for:

- bidimensional stress heatmap
- iso-value contour style charts

## Relationships

- `fact_annual_metrics[year]` -> `dim_year[year]`
- `fact_annual_metrics[metric]` -> `dim_metric[metric]`
- `fact_annual_metrics[scenario_id]` -> `dim_scenario[scenario_id]`
- `fact_scenario_kpis[scenario_id]` -> `dim_scenario[scenario_id]`
- `fact_scenario_kpis[metric]` -> `kpi_catalog[metric]`

## Recommended report pages

1. Executive View
2. Scenario Comparison
3. Value Creation
4. Risk Distribution
5. Drivers
6. Sensitivity
7. Benchmark

## Presentation logic

The report should tell a clear decision story:

1. The project may look attractive in the base case.
2. Stress and simulation show downside asymmetry.
3. Market and operational shocks affect value differently.
4. The Python engine provides a scalable analytical layer for monitoring and BI refresh.
