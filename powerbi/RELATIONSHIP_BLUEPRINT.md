# Relationship Blueprint

This file defines the recommended Power BI model for the repository's starter report.

## Modeling Principle

Keep the core monthly story simple, but not disconnected.

Do not force every table into one giant semantic model, and do not connect monthly marts directly to each other.

Use a shared monthly dimension layer so the report can filter all core monthly marts coherently through `site` and `month`.

## Core Starter Kit Model

Create this shared monthly relationship set first:

1. `dim_site[site_id]` -> `kpi_monthly_summary[site_id]`
2. `dim_site[site_id]` -> `fact_monthly_actual_vs_plan[site_id]`
3. `dim_site[site_id]` -> `mart_monthly_executive_overview[site_id]`
4. `dim_site[site_id]` -> `mart_monthly_process_performance[site_id]`
5. `dim_site[site_id]` -> `mart_monthly_cost_margin[site_id]`
6. `dim_site[site_id]` -> `mart_monthly_by_site[site_id]`
7. `dim_site[site_id]` -> `mart_process_driver_summary[site_id]`
8. `dim_site[site_id]` -> `mart_cost_center_summary[site_id]`
9. `dim_month[period]` -> `kpi_monthly_summary[period]`
10. `dim_month[period]` -> `fact_monthly_actual_vs_plan[period]`
11. `dim_month[period]` -> `mart_monthly_executive_overview[period]`
12. `dim_month[period]` -> `mart_monthly_process_performance[period]`
13. `dim_month[period]` -> `mart_monthly_cost_margin[period]`
14. `dim_month[period]` -> `mart_monthly_by_site[period]`
15. `dim_month[period]` -> `mart_process_driver_summary[period]`
16. `dim_month[period]` -> `mart_cost_center_summary[period]`
17. `dim_monthly_metric[metric]` -> `fact_monthly_actual_vs_plan[metric]`

Recommended settings:

- cardinality: one-to-many
- filter direction: single
- active: yes

This is the core monthly semantic model.

It lets one site slicer and one month slicer drive the first four pages cleanly.

## Optional Detail Dimensions

Add these only when you want cleaner drill or reusable detail-page slicers:

1. `dim_process_area[process_area]` -> `mart_process_driver_summary[process_area]`
2. `dim_cost_center[cost_center]` -> `mart_cost_center_summary[cost_center]`

Use the same recommended settings:

- cardinality: one-to-many
- filter direction: single
- active: yes

These dimensions are useful because they avoid page-local slicers built straight from the detail marts.

## Keep These Tables Disconnected

Keep these starter-kit reference tables disconnected:

- `monthly_kpi_dictionary`
- `powerbi_measure_catalog`
- `dashboard_page_catalog`
- `powerbi_visual_binding_catalog`
- `powerbi_query_catalog`
- `powerbi_table_catalog`

Why:

- they are documentation and build-support assets, not report filters
- connecting them adds no business value to the report model

## Appendix Relationships

If you add the appendix visuals, create these relationships:

1. `dim_year[year]` -> `fact_annual_metrics[year]`
2. `dim_metric[metric]` -> `fact_annual_metrics[metric]`
3. `dim_scenario[scenario_id]` -> `fact_annual_metrics[scenario_id]`
4. `dim_scenario[scenario_id]` -> `fact_scenario_kpis[scenario_id]`

Recommended settings:

- cardinality: one-to-many
- filter direction: single
- active: yes

Keep these appendix tables disconnected:

- `simulation_summary`
- `simulation_percentiles`
- `fact_simulation_distribution`
- `fact_tornado_sensitivity`
- `fact_heatmap_price_grade`
- `benchmark_comparison`

## Fact vs Dimension Structure

Core monthly layer:

- dimensions:
  `dim_site`
  `dim_month`
- dimension: `dim_monthly_metric`
- optional detail dimensions:
  `dim_process_area`
  `dim_cost_center`
- fact:
  `fact_monthly_actual_vs_plan`
- wide mart:
  `kpi_monthly_summary`
- subject marts:
  `mart_monthly_executive_overview`
  `mart_monthly_process_performance`
  `mart_monthly_cost_margin`
  `mart_monthly_by_site`
  `mart_process_driver_summary`
  `mart_cost_center_summary`

Appendix layer:

- dimensions:
  `dim_year`
  `dim_metric`
  `dim_scenario`
- facts:
  `fact_annual_metrics`
  `fact_scenario_kpis`
- disconnected appendix support:
  `simulation_summary`
  `simulation_percentiles`
  `fact_simulation_distribution`
  `fact_tornado_sensitivity`
  `fact_heatmap_price_grade`
  `benchmark_comparison`

## Practical Modeling Notes

- Use `dim_site[site_name]` as the main site slicer across the first four pages.
- Use `dim_month[month_label]` as the main month slicer across the first four pages.
- Apply `outputs/bi/powerbi_sort_by_catalog.csv` so site, month, KPI, process-area, and cost-center labels sort correctly.
- Apply `outputs/bi/powerbi_field_visibility_catalog.csv` so repeated keys and technical metadata stay hidden by default.
- Keep relationships single-direction from dimensions to marts or facts.
- Do not create fact-to-fact or mart-to-mart joins inside the monthly model.
- Use `kpi_monthly_summary` for KPI cards and concise status tables.
- Use `fact_monthly_actual_vs_plan` for metric-level variance visuals.
- Use `mart_monthly_process_performance` only for process-driver visuals.
- Use `mart_monthly_cost_margin` only for cost, revenue proxy, EBITDA proxy, and cash proxy visuals.
- Use `mart_monthly_by_site` when the page needs site contribution to the monthly gap.
- Use `mart_process_driver_summary` with `dim_process_area` when the page needs process-area drill and downtime interpretation.
- Use `mart_cost_center_summary` with `dim_cost_center` when the page needs cost-center drill and margin-pressure interpretation.
- Use `fact_scenario_kpis` and the simulation tables only inside the appendix.

## Handoff Rule

If a visual can be built cleanly from one purpose-built mart filtered by shared dimensions, prefer that over extra DAX or extra fact-to-fact joins.

This starter kit is designed to reduce semantic ambiguity, not to maximize modeling cleverness.
