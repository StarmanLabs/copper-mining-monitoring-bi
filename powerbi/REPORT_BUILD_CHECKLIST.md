# Report Build Checklist

Use this checklist to build the first working Power BI report from the repository exports.

## 1. Pre-Build

- confirm `python scripts/build_bi_dataset.py` ran successfully
- confirm `powerbi/template_scaffold/` was regenerated successfully
- confirm `powerbi/pbip_tmdl_scaffold/` was regenerated successfully
- confirm the latest files exist in `outputs/bi/`
- confirm you are building the report around the monthly monitoring layer first
- confirm the appendix will stay secondary

## 2. Start From The Scaffold

Use these files first if you are starting from a blank Power BI file:

1. `powerbi/template_scaffold/README.md`
2. `powerbi/template_scaffold/parameters/ProjectRoot.pq`
3. `powerbi/template_scaffold/model/powerbi_query_catalog.csv`
4. `powerbi/template_scaffold/measures/00_all_measures.dax`
5. `powerbi/template_scaffold/report/report_manifest.json`

If you want the more native-feeling continuation path, use these instead:

1. `powerbi/pbip_tmdl_scaffold/README.md`
2. `powerbi/pbip_tmdl_scaffold/DESKTOP_FINALIZATION.md`
3. `powerbi/pbip_tmdl_scaffold/CopperMiningMonitoring.SemanticModel/README.md`
4. `powerbi/pbip_tmdl_scaffold/CopperMiningMonitoring.SemanticModel/TMDLScripts/`
5. `powerbi/pbip_tmdl_scaffold/CopperMiningMonitoring.Report/report_shell_manifest.json`

## 3. Import The Core Tables

Import these first:

1. `dim_site.csv`
2. `dim_month.csv`
3. `dim_monthly_metric.csv`
4. `dim_process_area.csv`
5. `dim_cost_center.csv`
6. `kpi_monthly_summary.csv`
7. `fact_monthly_actual_vs_plan.csv`
8. `mart_monthly_executive_overview.csv`
9. `mart_monthly_process_performance.csv`
10. `mart_monthly_cost_margin.csv`
11. `mart_monthly_by_site.csv`
12. `mart_process_driver_summary.csv`
13. `mart_cost_center_summary.csv`
14. `monthly_kpi_dictionary.csv`
15. `powerbi_measure_catalog.csv`
16. `powerbi_query_catalog.csv`

Optional support:

- `dashboard_page_catalog.csv`
- `powerbi_relationship_catalog.csv`
- `powerbi_sort_by_catalog.csv`
- `powerbi_field_visibility_catalog.csv`
- `powerbi_visual_binding_catalog.csv`

If you are using the scaffold package, import the matching `.pq` files from `powerbi/template_scaffold/queries/` in the same order.

If you are using the PBIP/TMDL-oriented scaffold, import the matching `.pq` files from `powerbi/pbip_tmdl_scaffold/CopperMiningMonitoring.SemanticModel/PowerQuery/queries/`.

## 4. Create The Core Relationships

Create these relationships:

- `dim_site[site_id]` -> every monthly mart and monthly fact table that contains `site_id`
- `dim_month[period]` -> every monthly mart and monthly fact table that contains `period`
- `dim_monthly_metric[metric]` -> `fact_monthly_actual_vs_plan[metric]`
- `dim_process_area[process_area]` -> `mart_process_driver_summary[process_area]`
- `dim_cost_center[cost_center]` -> `mart_cost_center_summary[cost_center]`

Check:

- one-to-many
- single direction
- active
- no mart-to-mart relationships

## 5. Import The Theme

Import:

- `powerbi/copper_risk_theme.json`

## 6. Build Measures

Create measures in this order:

1. Executive Overview cards
2. Monthly Actual vs Plan KPI measures
3. Process Performance support measures
4. Cost and Margin measures
5. Appendix measures only after the core report works

Use:

- `powerbi/template_scaffold/measures/`
- `powerbi/pbip_tmdl_scaffold/CopperMiningMonitoring.SemanticModel/TMDLScripts/02_core_monthly_measures.tmdl`
- `powerbi/DAX_MEASURES.md`
- `outputs/bi/powerbi_measure_catalog.csv`

## 7. Build Pages

Build the pages in this order:

1. Executive Overview
2. Monthly Actual vs Plan
3. Process Performance
4. Cost and Margin
5. Advanced Scenario / Risk Appendix

Use:

- `powerbi/template_scaffold/report/report_manifest.json`
- `powerbi/pbip_tmdl_scaffold/CopperMiningMonitoring.Report/report_shell_manifest.json`
- `powerbi/PAGE_BUILD_GUIDE.md`
- `powerbi/VISUAL_BINDING_CATALOG.csv`

## 8. Add Slicers And Filters

Recommended slicers:

- `dim_site[site_name]`
- `dim_month[month_label]`

Optional detail slicers:

- `dim_process_area[process_area]`
- `dim_cost_center[cost_center]`

Appendix-only slicers:

- `scenario_name`
- `scenario_category`

Use:

- `powerbi/SLICER_AND_FILTER_GUIDE.md`
- `outputs/bi/powerbi_sort_by_catalog.csv`

## 9. Validate The Core Monthly Story

Before adding the appendix, check:

- throughput plan vs actual agrees with `fact_monthly_actual_vs_plan`
- head grade and recovery trends agree with `mart_monthly_process_performance`
- revenue proxy, EBITDA proxy, and cash proxies agree with `mart_monthly_cost_margin`
- overall alert level in cards agrees with `kpi_monthly_summary`
- site contribution visuals agree with `mart_monthly_by_site`
- process-area drill visuals agree with `mart_process_driver_summary`
- cost-center drill visuals agree with `mart_cost_center_summary`

## 10. Add The Appendix

Only after the monthly report works:

- import `dim_year`, `dim_metric`, `dim_scenario`, `fact_annual_metrics`, `fact_scenario_kpis`
- import `simulation_summary`, `simulation_percentiles`, `fact_simulation_distribution`
- import `fact_tornado_sensitivity`, `fact_heatmap_price_grade`, `benchmark_comparison`
- create the appendix relationships from `powerbi/RELATIONSHIP_BLUEPRINT.md`

## 11. Monthly Refresh Sequence

Use this order for refresh logic:

1. rebuild repository outputs
2. refresh the Power BI scaffold queries or reimport if the model is being rebuilt
3. reapply TMDL scripts if the model structure was rebuilt from scratch
4. refresh Power BI core monthly tables
5. validate the four core pages
6. refresh the appendix tables
7. validate the appendix visuals

## 12. Sanity Checks After Refresh

Check these every time:

- latest month exists in `kpi_monthly_summary`
- no duplicate `site_id + period` rows appear in the monthly marts
- no blank KPI cards appear on the Executive Overview page
- variance visuals still return expected metric names and units
- shared `dim_site` and `dim_month` slicers affect all four monthly pages consistently
- site, process-area, and cost-center drill visuals reconcile back to the monthly summary for the selected month
- appendix scenario slicers do not affect the core monthly pages

## 13. Before Publish

Check:

- page order still follows the starter kit order
- appendix remains last
- sample/demo language is preserved
- no visual implies live ERP or plant integration
- cards, labels, and units remain business-readable

If any of those fail, fix the semantics before publishing.
