# Power BI Dashboard Blueprint

## Model setup

Use these relationships:

- `dim_year[year]` -> `fact_annual_metrics[year]`
- `dim_metric[metric]` -> `fact_annual_metrics[metric]`
- `dim_scenario[scenario_id]` -> `fact_annual_metrics[scenario_id]`
- `dim_scenario[scenario_id]` -> `fact_scenario_kpis[scenario_id]`

Keep these tables disconnected unless you need custom modeling:

- `fact_simulation_distribution`
- `fact_tornado_sensitivity`
- `fact_heatmap_price_grade`
- `simulation_summary`
- `simulation_percentiles`
- `benchmark_comparison`

## Global slicers

Use these slicers consistently:

- `dim_scenario[scenario_name]`
- `dim_scenario[scenario_category]`

Use a default page filter that excludes `committee_downside` only when you want cleaner executive pages. Keep it visible on the advanced-risk page.

## Page 1: Executive Planning Overview

Goal: show the planning case in business-facing mining language before introducing advanced valuation outputs.

### Visuals

1. KPI card: `Scenario Revenue`
2. KPI card: `Scenario EBITDA`
3. KPI card: `Scenario Operating Cash Flow`
4. KPI card: `Scenario Avg Throughput`
5. KPI card: `Scenario Avg Unit Opex`
6. KPI card: `Scenario EBITDA Margin Proxy`
7. Matrix
   Rows: `dim_scenario[scenario_name]`
   Values: `Scenario Revenue`, `Scenario EBITDA`, `Scenario Avg Throughput`, `Scenario Avg Unit Opex`
8. Bar chart
   Axis: `dim_scenario[scenario_name]`
   Value: `Scenario Revenue`

## Page 2: Throughput and Production

Goal: give the dashboard a strong mining-performance core.

### Visuals

1. Line chart
   X: `dim_year[year]`
   Y: `Annual Processed Tonnes`
2. Line chart
   X: `dim_year[year]`
   Y: `Annual Copper Fine Production`
3. Column chart
   X: `dim_year[phase]`
   Y: `Annual Processed Tonnes`
4. Small KPI cards
   `Scenario Avg Throughput`
   `Scenario Avg Copper Production`

## Page 3: Grade and Recovery

Goal: show ore quality and metallurgical performance in a clean operating view.

### Visuals

1. Line chart
   X: `dim_year[year]`
   Y: `Annual Head Grade %`
2. Line chart
   X: `dim_year[year]`
   Y: `Annual Recovery %`
3. Combined table or small matrix
   Columns: `year`, `Annual Head Grade %`, `Annual Recovery %`
4. KPI card
   `Scenario EBITDA Margin Proxy`

## Page 4: Cost, Revenue and Cash Generation

Goal: connect operations to management control, cost review, and business performance.

### Visuals

1. Line and clustered column chart
   X: `dim_year[year]`
   Columns: `Annual Revenue`
   Line: `Annual EBITDA`
2. Line chart
   X: `dim_year[year]`
   Y: `Annual Unit Opex`
3. Line chart
   X: `dim_year[year]`
   Y: `Annual Operating Cash Flow`
4. Line chart
   X: `dim_year[year]`
   Y: `Annual Free Cash Flow`
5. Column chart
   X: `dim_year[year]`
   Y: `Annual Capex`

## Page 5: Scenario Planning and Price Exposure

Goal: compare planning cases, price exposure, and operating trade-offs.

### Visuals

1. Scatter chart
   X: `Scenario Capex`
   Y: `Selected Scenario NPV`
   Size: `Scenario Revenue`
   Legend: `dim_scenario[scenario_category]`
   Details: `dim_scenario[scenario_name]`
2. Bar chart
   Axis: `dim_scenario[scenario_name]`
   Value: `NPV Delta vs Base`
3. Table
   Columns: `dim_scenario[scenario_name]`, `Scenario Revenue`, `Scenario EBITDA`, `Scenario Avg Throughput`, `Scenario Avg Unit Opex`, `Selected Scenario NPV`
4. Line chart
   X: `dim_year[year]`
   Y: `Annual Net Price`

## Page 6: Advanced Valuation and Downside Risk

Goal: keep the technical upside of the repository, but as a later analytical layer.

### Visuals

1. KPI card: `Selected Scenario NPV`
2. KPI card: `Selected Scenario IRR`
3. KPI card: `Probability of Loss`
4. KPI card: `VaR 5%`
5. KPI card: `CVaR 5%`
6. Histogram
   Source: `fact_simulation_distribution[npv_usd]`
   Use Power BI bins on `npv_usd`
7. Table
   Source: `simulation_percentiles`
   Show P1, P5, P50, P95, P99
8. Diverging bar chart
   Source: `fact_tornado_sensitivity`
   Axis: `driver_label`
   Value: `impact_vs_base_usd`
9. Matrix heatmap
   Source: `fact_heatmap_price_grade`
   Rows: `price_factor`
   Columns: `grade_factor`
   Values: `npv_usd`

## Page 7: Benchmark and Method Transparency

Goal: show technical honesty and comparability discipline.

### Visuals

1. Table
   Source: `benchmark_comparison`
   Columns: `metric`, `benchmark_value`, `python_value`, `reconciliation_status`, `gap`, `pct_gap`
2. Text box
   Explain that only directly comparable metrics should be gap-read, and that deterministic comparable rows can still carry a material residual gap.

This page matters for credibility. It shows the project is serious enough to separate dashboard storytelling from audit logic.

## Layout principles

- Page 1 should feel executive and business-facing.
- Pages 2 to 5 should feel operational and planning-oriented.
- Page 6 should feel clearly advanced, not like the whole repo depends on it.
- Use the same scenario slicer behavior across pages.
- Keep the benchmark page last.
