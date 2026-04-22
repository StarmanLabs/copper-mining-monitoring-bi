# Power BI DAX Measures

This file is a curated starting set for the Power BI Starter Kit.

The full generated inventory lives in:

- `outputs/bi/powerbi_measure_catalog.csv`

The executable measure bundles live in:

- `powerbi/template_scaffold/measures/`
- `powerbi/pbip_tmdl_scaffold/CopperMiningMonitoring.SemanticModel/TMDLScripts/02_core_monthly_measures.tmdl`
- `powerbi/pbip_tmdl_scaffold/CopperMiningMonitoring.SemanticModel/TMDLScripts/03_advanced_appendix_measures.tmdl`

Use these measures first.

## Executive Overview

```dax
Monthly Throughput Actual =
SUM(kpi_monthly_summary[throughput_tonnes_actual])

Monthly Revenue Proxy Actual =
SUM(kpi_monthly_summary[revenue_proxy_usd_actual])

Monthly EBITDA Proxy Actual =
SUM(kpi_monthly_summary[ebitda_proxy_usd_actual])

Monthly Operating Cash Flow Proxy Actual =
SUM(kpi_monthly_summary[operating_cash_flow_proxy_usd_actual])

Monthly Free Cash Flow Proxy Actual =
SUM(kpi_monthly_summary[free_cash_flow_proxy_usd_actual])

Monthly Critical Alerts =
SUM(kpi_monthly_summary[critical_alert_count])

Monthly Warning Alerts =
SUM(kpi_monthly_summary[warning_alert_count])

Monthly Overall Alert Level =
VAR CriticalAlerts = SUM(kpi_monthly_summary[critical_alert_count])
VAR WarningAlerts = SUM(kpi_monthly_summary[warning_alert_count])
RETURN
    IF(CriticalAlerts > 0, "critical", IF(WarningAlerts > 0, "warning", "on_track"))

Site Production Gap Contribution % =
MAX(mart_monthly_by_site[site_production_gap_share_pct])
```

## Monthly Actual vs Plan

```dax
Monthly Plan Throughput =
CALCULATE(
    MAX(fact_monthly_actual_vs_plan[plan_value]),
    fact_monthly_actual_vs_plan[metric] = "throughput_tonnes"
)

Monthly Actual Throughput =
CALCULATE(
    MAX(fact_monthly_actual_vs_plan[actual_value]),
    fact_monthly_actual_vs_plan[metric] = "throughput_tonnes"
)

Monthly Throughput Variance =
CALCULATE(
    MAX(fact_monthly_actual_vs_plan[variance_value]),
    fact_monthly_actual_vs_plan[metric] = "throughput_tonnes"
)

Monthly Head Grade Variance % =
MAX(kpi_monthly_summary[head_grade_pct_variance_pct])

Monthly Recovery Variance % =
MAX(kpi_monthly_summary[recovery_pct_variance_pct])

Monthly Copper Production Variance % =
MAX(kpi_monthly_summary[copper_production_tonnes_variance_pct])

Monthly Unit Cost Variance % =
MAX(kpi_monthly_summary[unit_cost_usd_per_tonne_variance_pct])
```

## Process Performance

```dax
Monthly Head Grade Actual =
CALCULATE(
    MAX(fact_monthly_actual_vs_plan[actual_value]),
    fact_monthly_actual_vs_plan[metric] = "head_grade_pct"
)

Monthly Recovery Actual =
CALCULATE(
    MAX(fact_monthly_actual_vs_plan[actual_value]),
    fact_monthly_actual_vs_plan[metric] = "recovery_pct"
)

Monthly Availability Actual =
MAX(mart_monthly_process_performance[availability_pct_actual])

Monthly Utilization Actual =
MAX(mart_monthly_process_performance[utilization_pct_actual])

Monthly Downtime Hours =
SUM(kpi_monthly_summary[downtime_hours_actual])

Process Area Production Gap Share % =
MAX(mart_process_driver_summary[process_area_production_gap_share_pct])
```

## Cost And Margin

```dax
Monthly Unit Cost Actual =
DIVIDE(
    SUM(kpi_monthly_summary[operating_cost_usd_actual]),
    SUM(kpi_monthly_summary[throughput_tonnes_actual])
)

Monthly Operating Cost Actual =
SUM(kpi_monthly_summary[operating_cost_usd_actual])

Monthly Revenue Proxy Variance % =
MAX(kpi_monthly_summary[revenue_proxy_usd_variance_pct])

Monthly EBITDA Proxy Variance % =
MAX(kpi_monthly_summary[ebitda_proxy_usd_variance_pct])

Cost Center Variance =
SUM(mart_cost_center_summary[cost_variance_usd])

Cost Center Margin Pressure Share % =
MAX(mart_cost_center_summary[cost_center_margin_pressure_share_pct])
```

## Advanced Scenario / Risk Appendix

```dax
Selected Scenario NPV =
CALCULATE(
    MAX(fact_scenario_kpis[value]),
    fact_scenario_kpis[metric] = "scenario_npv_usd"
)

Selected Scenario IRR =
CALCULATE(
    MAX(fact_scenario_kpis[value]),
    fact_scenario_kpis[metric] = "scenario_irr"
)

Scenario Revenue =
CALCULATE(
    MAX(fact_scenario_kpis[value]),
    fact_scenario_kpis[metric] = "total_revenue_usd"
)

Scenario EBITDA =
CALCULATE(
    MAX(fact_scenario_kpis[value]),
    fact_scenario_kpis[metric] = "total_ebitda_usd"
)

Probability of Loss =
CALCULATE(
    MAX(simulation_summary[value]),
    simulation_summary[metric] = "probability_of_loss"
)

VaR 5% =
CALCULATE(
    MAX(simulation_summary[value]),
    simulation_summary[metric] = "var_usd"
)

CVaR 5% =
CALCULATE(
    MAX(simulation_summary[value]),
    simulation_summary[metric] = "cvar_usd"
)
```

## Formatting Guidance

- Revenue, EBITDA, cash flow, capex, NPV, VaR, and CVaR:
  Currency with millions or billions display units
- Throughput and copper production:
  Whole number with compact display units
- Unit cost and net price:
  Decimal with two decimals
- Grade, recovery, and margin metrics:
  Percentage with one or two decimals

## Usage Note

The monthly card measures assume a single selected month or a clearly constrained monthly page context.

Because the public demo now includes multiple synthetic sites, prefer a single selected `dim_site[site_name]` and `dim_month[month_label]` on KPI-card pages unless the measure is explicitly additive.

That is the intended operating mode of the starter kit.
