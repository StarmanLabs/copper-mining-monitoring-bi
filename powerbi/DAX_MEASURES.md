# Power BI DAX Measures

These measures are designed for the current semantic layer in `outputs/bi/`.

The recommended report order is:

1. planning and performance
2. throughput and production
3. grade and recovery
4. cost, revenue, and cash generation
5. scenario planning and price exposure
6. advanced valuation and downside

## Executive planning measures

```dax
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

Scenario Operating Cash Flow =
CALCULATE(
    MAX(fact_scenario_kpis[value]),
    fact_scenario_kpis[metric] = "total_operating_cash_flow_usd"
)

Scenario Free Cash Flow =
CALCULATE(
    MAX(fact_scenario_kpis[value]),
    fact_scenario_kpis[metric] = "total_free_cash_flow_usd"
)

Scenario Capex =
CALCULATE(
    MAX(fact_scenario_kpis[value]),
    fact_scenario_kpis[metric] = "total_capex_usd"
)

Scenario Avg Throughput =
CALCULATE(
    MAX(fact_scenario_kpis[value]),
    fact_scenario_kpis[metric] = "average_processed_tonnes"
)

Scenario Avg Copper Production =
CALCULATE(
    MAX(fact_scenario_kpis[value]),
    fact_scenario_kpis[metric] = "average_copper_fine_lb"
)

Scenario Avg Unit Opex =
CALCULATE(
    MAX(fact_scenario_kpis[value]),
    fact_scenario_kpis[metric] = "average_unit_opex_usd_per_tonne"
)

Scenario EBITDA Margin Proxy =
CALCULATE(
    MAX(fact_scenario_kpis[value]),
    fact_scenario_kpis[metric] = "ebitda_margin_proxy"
)
```

## Annual KPI measures

```dax
Annual Processed Tonnes =
CALCULATE(
    SUM(fact_annual_metrics[value]),
    fact_annual_metrics[metric] = "expanded_tonnes"
)

Annual Copper Fine Production =
CALCULATE(
    SUM(fact_annual_metrics[value]),
    fact_annual_metrics[metric] = "copper_fine_lb"
)

Annual Head Grade % =
CALCULATE(
    AVERAGE(fact_annual_metrics[value]),
    fact_annual_metrics[metric] = "scenario_grade"
) * 100

Annual Recovery % =
CALCULATE(
    AVERAGE(fact_annual_metrics[value]),
    fact_annual_metrics[metric] = "scenario_recovery"
) * 100

Annual Net Price =
CALCULATE(
    AVERAGE(fact_annual_metrics[value]),
    fact_annual_metrics[metric] = "scenario_net_price_usd_per_lb"
)

Annual Unit Opex =
CALCULATE(
    AVERAGE(fact_annual_metrics[value]),
    fact_annual_metrics[metric] = "unit_opex_usd_per_tonne"
)

Annual Revenue =
CALCULATE(
    SUM(fact_annual_metrics[value]),
    fact_annual_metrics[metric] = "revenue_usd"
)

Annual EBITDA =
CALCULATE(
    SUM(fact_annual_metrics[value]),
    fact_annual_metrics[metric] = "ebitda_usd"
)

Annual Operating Cash Flow =
CALCULATE(
    SUM(fact_annual_metrics[value]),
    fact_annual_metrics[metric] = "operating_cash_flow_usd"
)

Annual Free Cash Flow =
CALCULATE(
    SUM(fact_annual_metrics[value]),
    fact_annual_metrics[metric] = "free_cash_flow_usd"
)

Annual Capex =
CALCULATE(
    SUM(fact_annual_metrics[value]),
    fact_annual_metrics[metric] = "capex_usd"
)
```

## Scenario planning and advanced valuation measures

```dax
Selected Scenario NPV =
CALCULATE(
    MAX(fact_scenario_kpis[value]),
    fact_scenario_kpis[metric] = "scenario_npv_usd"
)

Base Case NPV =
CALCULATE(
    MAX(fact_scenario_kpis[value]),
    fact_scenario_kpis[metric] = "scenario_npv_usd",
    dim_scenario[scenario_id] = "base"
)

Committee Downside NPV =
CALCULATE(
    MAX(fact_scenario_kpis[value]),
    fact_scenario_kpis[metric] = "scenario_npv_usd",
    dim_scenario[scenario_id] = "committee_downside"
)

NPV Delta vs Base =
[Selected Scenario NPV] - [Base Case NPV]

Selected Scenario IRR =
CALCULATE(
    MAX(fact_scenario_kpis[value]),
    fact_scenario_kpis[metric] = "scenario_irr"
)

Scenario Payback Year =
CALCULATE(
    MAX(fact_scenario_kpis[value]),
    fact_scenario_kpis[metric] = "payback_year"
)
```

## Monte Carlo and downside measures

```dax
Expected NPV =
CALCULATE(
    MAX(simulation_summary[value]),
    simulation_summary[metric] = "expected_npv_usd"
)

Median NPV =
CALCULATE(
    MAX(simulation_summary[value]),
    simulation_summary[metric] = "median_npv_usd"
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

## Sensitivity measure

```dax
Tornado Impact =
MAX(fact_tornado_sensitivity[impact_vs_base_usd])
```

## Suggested formatting

- Revenue, EBITDA, operating cash flow, free cash flow, capex, NPV, VaR, CVaR: Currency with millions or billions display units.
- Throughput and copper production: Whole number with compact display units.
- Unit opex and net price: Decimal with 2 decimals.
- Head grade, recovery, and EBITDA margin proxy: Percentage with 1-2 decimals.
- Payback year: Whole number.
