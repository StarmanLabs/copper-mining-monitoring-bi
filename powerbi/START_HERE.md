# Power BI Starter Kit

This starter kit is the fastest way to turn the repository's monthly monitoring marts into a usable mining management report.

## Fastest Build Path

If you want the most practical starting point, use the generated scaffold package first:

1. `powerbi/TEMPLATE_LAYER.md`
2. `powerbi/template_scaffold/README.md`
3. `powerbi/template_scaffold/model/powerbi_query_catalog.csv`
4. `powerbi/template_scaffold/measures/00_all_measures.dax`
5. `powerbi/template_scaffold/report/report_manifest.json`

This is the fastest public-safe first-build path in the repository.

## More Native Continuation Path

If you want the more source-control-friendly handoff path, use:

1. `powerbi/TEMPLATE_LAYER.md`
2. `powerbi/pbip_tmdl_scaffold/README.md`
3. `powerbi/pbip_tmdl_scaffold/DESKTOP_FINALIZATION.md`
4. `powerbi/pbip_tmdl_scaffold/CopperMiningMonitoring.SemanticModel/README.md`
5. `powerbi/pbip_tmdl_scaffold/CopperMiningMonitoring.SemanticModel/TMDLScripts/`
6. `powerbi/pbip_tmdl_scaffold/CopperMiningMonitoring.Report/report_shell_manifest.json`

This path is now the repository's strongest honest PBIP finalization package.

It is closer to native PBIP/TMDL continuation, while still being explicit that the final Desktop save step must happen in Power BI Desktop.

If you rebuild the scaffold from a profile that disables the advanced appendix path, the active manifests and page shells stay monthly-first and omit the appendix from the current continuation layer.

## What This Report Is For

Use this report as a business-facing monitoring layer for:

- mining planning support
- management control
- KPI monitoring
- executive review
- BI handoff
- decision support

The main story is monthly actual vs plan.

The appendix keeps scenario, valuation, benchmark, Monte Carlo, tornado, and heatmap outputs available without letting them dominate the report.

The core monthly model uses shared dimensions so site and month filters can travel coherently across the monthly marts.

## What To Import First

Start with the core monthly model:

1. `outputs/bi/dim_site.csv`
2. `outputs/bi/dim_month.csv`
3. `outputs/bi/dim_monthly_metric.csv`
4. `outputs/bi/dim_process_area.csv`
5. `outputs/bi/dim_cost_center.csv`
6. `outputs/bi/kpi_monthly_summary.csv`
7. `outputs/bi/fact_monthly_actual_vs_plan.csv`
8. `outputs/bi/mart_monthly_executive_overview.csv`
9. `outputs/bi/mart_monthly_process_performance.csv`
10. `outputs/bi/mart_monthly_cost_margin.csv`
11. `outputs/bi/mart_monthly_by_site.csv`
12. `outputs/bi/mart_process_driver_summary.csv`
13. `outputs/bi/mart_cost_center_summary.csv`
14. `outputs/bi/monthly_kpi_dictionary.csv`
15. `outputs/bi/powerbi_measure_catalog.csv`
16. `outputs/bi/powerbi_query_catalog.csv`
17. `outputs/bi/powerbi_relationship_catalog.csv`
18. `outputs/bi/powerbi_sort_by_catalog.csv`
19. `outputs/bi/powerbi_field_visibility_catalog.csv`
20. `outputs/bi/powerbi_visual_binding_catalog.csv`

Only after the core report is working should you import the appendix tables:

1. `outputs/bi/dim_year.csv`
2. `outputs/bi/dim_metric.csv`
3. `outputs/bi/dim_scenario.csv`
4. `outputs/bi/fact_annual_metrics.csv`
5. `outputs/bi/fact_scenario_kpis.csv`
6. `outputs/bi/simulation_summary.csv`
7. `outputs/bi/simulation_percentiles.csv`
8. `outputs/bi/fact_simulation_distribution.csv`
9. `outputs/bi/fact_tornado_sensitivity.csv`
10. `outputs/bi/fact_heatmap_price_grade.csv`
11. `outputs/bi/benchmark_comparison.csv`

## Build The Report In This Order

1. Executive Overview
2. Monthly Actual vs Plan
3. Process Performance
4. Cost and Margin
5. Advanced Scenario / Risk Appendix

This order matters.

Pages 1 to 4 are the real product story.

Page 5 is a useful appendix, but it is not the lead narrative for the repository or for a management-facing handoff.

## Shortest Realistic Paths

Public-safe demo baseline:

1. `python scripts/build_bi_dataset.py`
2. `python scripts/build_powerbi_native_scaffold.py`
3. open the package under `powerbi/pbip_tmdl_scaffold/`
4. finalize in Power BI Desktop

If you regenerate over an older scaffold in a constrained local environment, stale scaffold artifacts outside the current package are marked as obsolete in place instead of being silently reused.

Local runner-aware continuation:

1. `python scripts/run_local_profile.py --profile config/source_profiles/local/my_company_profile.yaml --scope all`
2. `python scripts/build_powerbi_native_scaffold.py --profile config/source_profiles/local/my_company_profile.yaml`
3. open the package under `powerbi/pbip_tmdl_scaffold/`
4. update only the output-root parameters that need to follow local runner outputs
5. finalize in Power BI Desktop

## What Each Page Should Answer

- Executive Overview
  Are we on plan, where are the biggest issues, and what needs management attention now?
- Monthly Actual vs Plan
  Which KPI is under or over plan, by how much, and in which month?
- Process Performance
  Which process drivers explain the production outcome?
- Cost and Margin
  How are cost pressure, revenue proxy, EBITDA proxy, and cash proxies moving together?
- Advanced Scenario / Risk Appendix
  What does the scenario and risk context add once the monthly story is already understood?

## Files To Use Alongside This One

- `powerbi/RELATIONSHIP_BLUEPRINT.md`
- `powerbi/TEMPLATE_LAYER.md`
- `powerbi/REPORT_BUILD_CHECKLIST.md`
- `powerbi/PAGE_BUILD_GUIDE.md`
- `powerbi/SLICER_AND_FILTER_GUIDE.md`
- `powerbi/VISUAL_BINDING_CATALOG.csv`
- `powerbi/DAX_MEASURES.md`
- `powerbi/copper_risk_theme.json`

If you are using the PBIP/TMDL-oriented scaffold, also use:

- `powerbi/pbip_tmdl_scaffold/CopperMiningMonitoring.SemanticModel/catalogs/powerbi_sort_by_catalog.csv`
- `powerbi/pbip_tmdl_scaffold/CopperMiningMonitoring.SemanticModel/catalogs/powerbi_field_visibility_catalog.csv`
- `powerbi/pbip_tmdl_scaffold/CopperMiningMonitoring.SemanticModel/TMDLScripts/`

## Public Demo Boundary

This repository is public-safe and sample-data based.

Use language such as:

- sample monthly actual vs plan
- management-control proxy
- BI-ready monitoring layer
- planning and control workflow

Do not present the report as:

- live plant reporting
- ERP-connected reporting
- telemetry integration
- production enterprise BI

## Real Work Adaptation Path

To adapt this starter kit for real work later:

1. preserve the canonical monthly schemas
2. preserve the shared `dim_site` and `dim_month` logic so one filter set can drive the whole monthly model
3. replace the sample monthly source tables with governed plan, actual, plant, cost, and market inputs
4. keep the core Power BI page structure
5. harden refresh checks and publishing controls around the real source systems

That is the intended work-facing use of this starter kit.
