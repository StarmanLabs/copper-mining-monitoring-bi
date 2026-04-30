# Power BI Dashboard

## Purpose

This dashboard is the business-facing presentation layer for the repository's monthly mining monitoring workflow.

It is designed to show a reproducible path from Python-generated monitoring marts into a public-safe Power BI dashboard focused on:

- monthly actual-vs-plan control
- KPI alerting and management attention
- process-driver explanation
- cost and margin pressure review
- scenario and risk context as a secondary appendix

The dashboard is a portfolio artifact and a practical handoff pattern.

It should not be described as a fully automated Power BI product generated end to end by code alone.

## Dashboard Scope

The locally finished dashboard contains five pages:

1. Executive Overview
2. Monthly Actual vs Plan
3. Process Performance
4. Cost & Margin
5. Scenario / Risk Appendix

Pages 1 to 4 are the main product story.

Page 5 is intentionally secondary.

## Data Sources Used From `outputs/bi`

### Monthly core

- `dim_site.csv`
- `dim_month.csv`
- `dim_monthly_metric.csv`
- `dim_process_area.csv`
- `dim_cost_center.csv`
- `kpi_monthly_summary.csv`
- `fact_monthly_actual_vs_plan.csv`
- `mart_monthly_executive_overview.csv`
- `mart_monthly_process_performance.csv`
- `mart_monthly_cost_margin.csv`
- `mart_monthly_by_site.csv`
- `mart_process_driver_summary.csv`
- `mart_cost_center_summary.csv`
- `monthly_kpi_dictionary.csv`

### Power BI semantic support

- `powerbi_measure_catalog.csv`
- `powerbi_query_catalog.csv`
- `powerbi_relationship_catalog.csv`
- `powerbi_sort_by_catalog.csv`
- `powerbi_field_visibility_catalog.csv`
- `powerbi_visual_binding_catalog.csv`
- `dashboard_page_catalog.csv`

### Secondary appendix

- `dim_year.csv`
- `dim_metric.csv`
- `dim_scenario.csv`
- `fact_annual_metrics.csv`
- `fact_scenario_kpis.csv`
- `simulation_summary.csv`
- `simulation_percentiles.csv`
- `fact_simulation_distribution.csv`
- `fact_tornado_sensitivity.csv`
- `fact_heatmap_price_grade.csv`
- `benchmark_comparison.csv`

## Page-By-Page Explanation

### 1. Executive Overview

Purpose:

- provide the fastest management readout of monthly operating and economic performance

![Executive Overview](../assets/powerbi/executive_overview.png)

Main questions answered:

- Are we on plan this month?
- Which KPI is driving the alert state?
- How are throughput, production, revenue proxy, EBITDA proxy, and cash proxies moving together?

Typical tables used:

- `mart_monthly_executive_overview.csv`
- `kpi_monthly_summary.csv`

Interpretation note:

- revenue, EBITDA, operating cash flow, and free cash flow are planning/control proxies, not audited financial statements

### 2. Monthly Actual vs Plan

Purpose:

- show explicit plan, actual, variance, and variance percent across the core KPI set

![Monthly Actual vs Plan](../assets/powerbi/monthly_actual_vs_plan.png)

Main questions answered:

- Which KPI is off plan?
- By how much?
- Which months and sites concentrate the largest deviations?

Typical tables used:

- `fact_monthly_actual_vs_plan.csv`
- `dim_monthly_metric.csv`

Interpretation note:

- this page is the monthly management-control center of the repository

### 3. Process Performance

Purpose:

- connect production outcomes back to grade, recovery, utilization, availability, downtime, and process-area drivers

![Process Performance](../assets/powerbi/process_performance.png)

Main questions answered:

- Is the production gap process-driven?
- Which process area is concentrating downtime?
- How do grade and recovery explain the monthly production result?

Typical tables used:

- `mart_monthly_process_performance.csv`
- `mart_process_driver_summary.csv`

Interpretation note:

- this is management-control process context, not engineering-grade root-cause analytics

### 4. Cost & Margin

Purpose:

- show the interaction between price, net realized price proxy, operating cost, revenue proxy, EBITDA proxy, and cash pressure

![Cost & Margin](../assets/powerbi/cost_margin.png)

Main questions answered:

- Is the monthly issue primarily price, cost, or a production-driven margin squeeze?
- Which cost center is driving cost pressure?
- How do working capital and sustaining capex affect the monthly cash proxy?

Typical tables used:

- `mart_monthly_cost_margin.csv`
- `mart_cost_center_summary.csv`
- `kpi_monthly_summary.csv`

Interpretation note:

- financial fields should be labeled as planning/control proxies, not as statutory accounting outputs

### 5. Scenario / Risk Appendix

Purpose:

- provide optional planning context after the monthly story is already understood

![Scenario / Risk Appendix](../assets/powerbi/scenario_risk_appendix.png)

Main questions answered:

- How sensitive is the case to price, grade, recovery, or cost assumptions?
- What do the simulation percentiles and scenario outputs suggest about downside and dispersion?

Typical tables used:

- `fact_scenario_kpis.csv`
- `simulation_summary.csv`
- `simulation_percentiles.csv`
- `fact_tornado_sensitivity.csv`
- `fact_heatmap_price_grade.csv`
- `benchmark_comparison.csv`

Interpretation note:

- this page is useful, but it is not the main identity of the repository

## Public-Safe Disclaimer

This dashboard is built from public-safe sample/demo outputs stored under `outputs/bi/`.

It does not contain:

- private company data
- ERP-connected reporting
- live telemetry
- private local profiles
- local mapping files

## Limitations

- the final Power BI canvas was manually finalized in Desktop
- the repository automates the Python datasets, semantic catalogs, and starter scaffolds, but not the finished PBIX canvas itself
- financial fields are planning/control proxies rather than audited financial statements
- the monthly layer is realistic for monitoring and BI prototyping, not a live operating reporting stack
- the scenario/risk appendix is secondary and should not be presented as the core product story

## Reproduce The BI-Ready Datasets

Install dependencies:

```bash
python -m pip install -e .[dev]
```

Build the public-safe baseline:

```bash
python scripts/build_bi_dataset.py
```

Run the public demo profile end to end:

```bash
python scripts/run_local_profile.py --profile config/source_profiles/public_demo_profile.yaml --scope all
```

Run tests:

```bash
python -m pytest -q
```

## Open Or Continue The Power BI Dashboard

Recommended honest workflow:

1. regenerate `outputs/bi/`
2. review `powerbi/START_HERE.md`
3. use `powerbi/pbip_tmdl_scaffold/` as the strongest public-safe continuation package
4. finish or continue the PBIX manually in Power BI Desktop
5. save the local PBIX outside the public repo or in an ignored local path unless you intentionally decide to version a binary artifact

What is automated by the repo:

- monthly and appendix dataset generation
- BI-ready CSV marts
- semantic catalogs
- PBIP/TMDL-oriented scaffold files

What remains manual in Power BI Desktop:

- final canvas layout
- final visual formatting
- screenshot capture
- any PBIX save/export action
