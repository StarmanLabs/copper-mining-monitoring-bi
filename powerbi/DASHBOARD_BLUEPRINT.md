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

Use a default page filter that excludes `committee_downside` only when you want cleaner charts for executive pages. Keep it visible on the stress page.

## Page 1: Executive Summary

Goal: show value creation, deterministic downside, and Monte Carlo risk in one screen.

### Visuals

1. KPI card: `Selected Scenario NPV`
2. KPI card: `Base Case NPV`
3. KPI card: `Committee Downside NPV`
4. KPI card: `Probability of Loss`
5. KPI card: `VaR 5%`
6. KPI card: `CVaR 5%`
7. Clustered bar chart
   Axis: `dim_scenario[scenario_name]`
   Value: `Selected Scenario NPV`
   Purpose: compare deterministic scenario NPVs
8. Matrix
   Rows: `dim_scenario[scenario_name]`
   Values: `Scenario Revenue`, `Scenario EBITDA`, `Scenario Free Cash Flow`, `Scenario Capex`
   Purpose: show which scenarios create or destroy operating value

## Page 2: Scenario Comparison

Goal: compare scenario economics and investment outcomes.

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
   Columns: `dim_scenario[scenario_name]`, `Selected Scenario NPV`, `Scenario EBITDA`, `Scenario Free Cash Flow`, `Scenario Payback Year`
4. KPI card: `Scenario Payback Year`

## Page 3: Annual Economics

Goal: show how value is built year by year.

### Visuals

1. Line and clustered column chart
   X: `dim_year[year]`
   Columns: `Annual Revenue`
   Line: `Annual EBITDA`
2. Line chart
   X: `dim_year[year]`
   Y: `Annual Free Cash Flow`
3. Column chart
   X: `dim_year[year]`
   Y: `Annual Capex`
4. Area or line chart
   X: `dim_year[year]`
   Y: `Annual Processed Tonnes`

Use a page-level filter or slicer on `dim_scenario[scenario_name]` so the user can toggle the annual profile by scenario.

## Page 4: Market and Operating Drivers

Goal: explain why the project improves or deteriorates under each scenario.

### Visuals

1. Line chart
   X: `dim_year[year]`
   Y: `Annual Net Price`
2. Line chart
   X: `dim_year[year]`
   Y: `Annual Head Grade %`
3. Line chart
   X: `dim_year[year]`
   Y: `Annual Recovery %`
4. Small KPI cards
   `Scenario Revenue`
   `Scenario EBITDA`
   `Selected Scenario NPV`

Use aligned y-axes and matching colors from the custom theme.

## Page 5: Monte Carlo Risk

Goal: show the downside distribution and central risk statistics.

### Visuals

1. KPI card: `Expected NPV`
2. KPI card: `Median NPV`
3. KPI card: `Probability of Loss`
4. KPI card: `VaR 5%`
5. KPI card: `CVaR 5%`
6. Histogram
   Source: `fact_simulation_distribution[npv_usd]`
   Use Power BI bins on `npv_usd`
   Values: count of rows
7. Table or card strip
   Source: `simulation_percentiles`
   Show P1, P5, P50, P95, P99

If you want a cleaner histogram, create bins in Power BI rather than pre-aggregating them in Python.

## Page 6: Sensitivity and Stress

Goal: isolate the main decision levers.

### Visuals

1. Diverging bar chart
   Source: `fact_tornado_sensitivity`
   Axis: `driver_label`
   Value: `impact_vs_base_usd`
   Legend: `direction`
2. Matrix heatmap
   Source: `fact_heatmap_price_grade`
   Rows: `price_factor`
   Columns: `grade_factor`
   Values: `npv_usd`
   Use conditional formatting on background color
3. KPI card: `Committee Downside NPV`

## Page 7: Reconciliation and Credibility

Goal: show that the migration is honest and still under active refinement.

### Visuals

1. Table
   Source: `benchmark_comparison`
   Columns: `metric`, `excel_value`, `python_value`, `gap`, `pct_gap_vs_excel`
2. Text box
   Explain that workbook benchmarks are still legacy PEN values while the rebuild is reported in USD.

This page is important for credibility in a portfolio or interview setting. It shows transparency rather than pretending a perfect replication.

## Layout principles

- Page 1 should feel executive and sparse.
- Pages 3 to 6 should feel analytical and operational.
- Use the same scenario slicer behavior across pages.
- Use `committee_downside` explicitly on the stress page even if you hide it elsewhere.
- Keep the benchmark page as the last page.
