# BI Usage

The repository's main BI handoff path is now the Power BI Starter Kit under `powerbi/`.

Use Tableau only as a secondary consumption path after the Power BI handoff is understood.

## Start Here

Open these files in this order:

1. `powerbi/START_HERE.md`
2. `powerbi/TEMPLATE_LAYER.md`
3. `powerbi/pbip_tmdl_scaffold/README.md`
4. `powerbi/template_scaffold/README.md`
5. `powerbi/RELATIONSHIP_BLUEPRINT.md`
6. `powerbi/REPORT_BUILD_CHECKLIST.md`
7. `powerbi/PAGE_BUILD_GUIDE.md`
8. `powerbi/SLICER_AND_FILTER_GUIDE.md`
9. `powerbi/VISUAL_BINDING_CATALOG.csv`

Then use these generated support files from `outputs/bi/`:

- `dashboard_page_catalog.csv`
- `powerbi_table_catalog.csv`
- `powerbi_query_catalog.csv`
- `powerbi_relationship_catalog.csv`
- `powerbi_visual_binding_catalog.csv`
- `powerbi_measure_catalog.csv`
- `powerbi_sort_by_catalog.csv`
- `powerbi_field_visibility_catalog.csv`
- `monthly_kpi_dictionary.csv`

The scaffold package under `powerbi/template_scaffold/` is still the fastest public-safe route from repository marts to a first working Power BI file.

The PBIP/TMDL-oriented scaffold under `powerbi/pbip_tmdl_scaffold/` is now the closer-to-native route when the user wants a more source-control-friendly continuation path.

The monthly semantic model now uses shared dimensions so the first four pages can be filtered through one site slicer and one month slicer instead of page-local fields.

For local/private adaptation, keep Power BI connected to canonical monthly or canonical annual appendix outputs only.

Do not point Power BI directly at private raw exports.

## Interpretation Boundary

The repository contains two BI-facing families:

- a core monthly actual-vs-plan monitoring layer
- a secondary appendix with scenario, valuation, benchmark, and downside outputs

The appendix now runs from canonical annual appendix tables by default, while the workbook remains only a legacy adapter or benchmark source.

The correct public claim is:

- sample monthly actual-vs-plan monitoring: yes
- BI-ready handoff package: yes
- live mine-system reporting: no

## Power BI Consumption Rule

If you are starting from zero, use:

- `powerbi/template_scaffold/parameters/ProjectRoot.pq`
- `powerbi/template_scaffold/queries/`
- `powerbi/template_scaffold/measures/`
- `powerbi/template_scaffold/report/report_manifest.json`

If you want the more native-feeling path, use:

- `powerbi/pbip_tmdl_scaffold/CopperMiningMonitoring.SemanticModel/PowerQuery/`
- `powerbi/pbip_tmdl_scaffold/CopperMiningMonitoring.SemanticModel/TMDLScripts/`
- `powerbi/pbip_tmdl_scaffold/CopperMiningMonitoring.Report/report_shell_manifest.json`

Build the report around the monthly pages first:

1. Executive Overview
2. Monthly Actual vs Plan
3. Process Performance
4. Cost and Margin

Only then add:

5. Advanced Scenario / Risk Appendix

That is the intended business-facing narrative.

## Core Monthly Table Roles

- `dim_site.csv`
  Shared site dimension for the monthly monitoring model.
- `dim_month.csv`
  Shared month dimension for consistent monthly filtering and sort behavior.
- `dim_process_area.csv`
  Optional shared dimension for process-driver drill visuals.
- `dim_cost_center.csv`
  Optional shared dimension for cost-pressure drill visuals.
- `kpi_monthly_summary.csv`
  Wide monthly monitoring table for cards, alerts, and concise management tables.
- `fact_monthly_actual_vs_plan.csv`
  Long fact table for explicit KPI variance review.
- `mart_monthly_executive_overview.csv`
  Narrow executive mart for headline monthly review.
- `mart_monthly_process_performance.csv`
  Site-level process mart for grade, recovery, availability, utilization, downtime, and ore-source context.
- `mart_monthly_cost_margin.csv`
  Cost, revenue proxy, EBITDA proxy, cash proxy, and top cost-center context mart.
- `mart_monthly_by_site.csv`
  Site contribution mart for production-gap concentration and cost-pressure concentration.
- `mart_process_driver_summary.csv`
  Process-area drill mart for downtime, ore mix, stockpile context, and production-gap share.
- `mart_cost_center_summary.csv`
  Cost-center drill mart for cost variance and margin-pressure share.
- `dim_monthly_metric.csv`
  KPI dimension for the monthly variance fact table.
- `monthly_kpi_dictionary.csv`
  Business dictionary for monthly KPI meaning, units, proxy status, and page usage.

Use `dim_site` and `dim_month` as the default slicer layer for the monthly model.

## Appendix Table Roles

- `annual_appendix_dataset_catalog.csv`
  Read-only dataset contract for the canonical annual appendix path.
- `annual_appendix_field_catalog.csv`
  Read-only field dictionary for the canonical annual appendix path.
- `fact_scenario_kpis.csv`
  Deterministic scenario KPI summary.
- `appendix_kpi_catalog.csv`
  Read-only KPI dictionary for the deterministic appendix metrics.
- `fact_annual_metrics.csv`
  Annual trend context for the appendix.
- `simulation_summary.csv`
  Summary risk metrics such as Probability of Loss, VaR, and CVaR.
- `fact_simulation_distribution.csv`
  Monte Carlo distribution rows for the histogram.
- `fact_tornado_sensitivity.csv`
  Sensitivity ranking table.
- `fact_heatmap_price_grade.csv`
  Joint stress-test grid.
- `benchmark_comparison.csv`
  Benchmark transparency table.
- `benchmark_scope_catalog.csv`
  Read-only explanation of which benchmark comparisons are direct and which are reference-only.
- `advanced_appendix_assumption_catalog.csv`
  Read-only appendix assumption register.
- `advanced_appendix_output_catalog.csv`
  Read-only guide to when each appendix output should be used.

## Tableau Note

Tableau remains viable, but it should consume the same subject-area marts rather than one merged extract.

If you adapt the repo for Tableau:

- keep the monthly subject marts separate
- keep the appendix tables separate
- preserve the same report narrative order as the Power BI starter kit

## Private Adaptation Path

For real work adaptation later:

1. replace the sample monthly inputs with governed private sources
2. preserve the canonical monthly schemas
3. preserve the page structure, KPI semantics, and detail-grain drill marts where private data supports them
4. map annual private appendix sources into canonical annual appendix tables before rebuilding the appendix
5. keep `.pbix`, `.pbit`, `.twb`, and `.twbx` files in ignored local folders only
6. tighten refresh controls and validation around the real source systems
