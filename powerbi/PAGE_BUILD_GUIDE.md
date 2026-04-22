# Page Build Guide

This guide explains what each page is for and how to assemble it from the exported marts.

Use `powerbi/VISUAL_BINDING_CATALOG.csv` for the exact visual-to-table mapping.

## Shared Filters

Use these shared dimensions across the first four pages:

- `dim_site[site_name]`
- `dim_month[month_label]`

Use these only on the relevant detail pages:

- `dim_process_area[process_area]` on Process Performance
- `dim_cost_center[cost_center]` on Cost and Margin

## Page 1. Executive Overview

Purpose:

- open with the monthly management story
- show current scale, margin proxy, cash proxy, and alert status
- highlight what needs attention now

Main marts:

- `kpi_monthly_summary.csv`
- optionally `mart_monthly_executive_overview.csv`
- `mart_monthly_by_site.csv` for site contribution visuals

Main measures:

- Monthly Throughput Actual
- Monthly Revenue Proxy Actual
- Monthly EBITDA Proxy Actual
- Monthly Operating Cash Flow Proxy Actual
- Monthly Free Cash Flow Proxy Actual
- Monthly Critical Alerts
- Monthly Warning Alerts
- Monthly Overall Alert Level

Key questions answered:

- Are we on plan this month?
- Is the issue operational, economic, or both?
- What should management focus on first?
- Which site is contributing most to the production gap?

## Page 2. Monthly Actual vs Plan

Purpose:

- make plan vs actual explicit
- show absolute and percentage variance
- make the variance story auditable by metric

Main marts:

- `fact_monthly_actual_vs_plan.csv`
- `dim_monthly_metric.csv`
- `mart_monthly_by_site.csv`

Main measures:

- Monthly Plan Throughput
- Monthly Actual Throughput
- Monthly Throughput Variance
- Monthly Head Grade Variance %
- Monthly Recovery Variance %
- Monthly Copper Production Variance %
- Monthly Unit Cost Variance %

Key questions answered:

- Which KPI is under or over plan?
- What is the size of the gap?
- Which months require explanation?
- Which site is contributing most to the monthly production shortfall?

## Page 3. Process Performance

Purpose:

- explain operational slippage through process drivers
- connect production outcomes to grade, recovery, availability, and utilization

Main marts:

- `mart_monthly_process_performance.csv`
- `mart_process_driver_summary.csv`

Main measures:

- Monthly Head Grade Actual
- Monthly Recovery Actual
- Monthly Availability Actual
- Monthly Utilization Actual

Key questions answered:

- Is performance slipping because of ore quality?
- Is metallurgical performance weaker than plan?
- Are availability or utilization limiting production?
- Which process area is concentrating downtime or the production gap?

## Page 4. Cost and Margin

Purpose:

- connect cost pressure to revenue proxy, EBITDA proxy, and cash proxy signals
- show whether the operation is losing or gaining economic support over time

Main marts:

- `mart_monthly_cost_margin.csv`
- optionally `kpi_monthly_summary.csv`
- `mart_cost_center_summary.csv`

Main measures:

- Monthly Unit Cost Actual
- Monthly Operating Cost Actual
- Monthly Revenue Proxy Variance %
- Monthly EBITDA Proxy Variance %

Key questions answered:

- Are costs rising faster than the business can absorb?
- Is revenue support improving or weakening?
- What is happening to the margin and cash story?
- Which cost centers are driving margin pressure?

## Page 5. Advanced Scenario / Risk Appendix

Purpose:

- keep scenario and risk context visible but clearly secondary
- provide additional valuation and downside analysis after the monthly story is understood

Main marts:

- `fact_scenario_kpis.csv`
- `simulation_summary.csv`
- `simulation_percentiles.csv`
- `fact_simulation_distribution.csv`
- `fact_tornado_sensitivity.csv`
- `fact_heatmap_price_grade.csv`
- `benchmark_comparison.csv`

Main measures:

- Selected Scenario NPV
- Selected Scenario IRR
- Scenario Revenue
- Scenario EBITDA
- Scenario Avg Throughput
- Scenario Avg Unit Opex
- Probability of Loss
- VaR 5%
- CVaR 5%

Key questions answered:

- What deterministic scenario context sits behind the case?
- What downside shape appears under simulation?
- Which drivers matter most for valuation sensitivity?
- How close is the Python layer to the benchmark where comparison is valid?

## Build Discipline

- Do not lead the report with the appendix.
- Do not let appendix slicers affect the core monthly pages.
- Do not use appendix visuals to compensate for a weak monthly monitoring story.

If the first four pages are not working cleanly, the report is not ready.
