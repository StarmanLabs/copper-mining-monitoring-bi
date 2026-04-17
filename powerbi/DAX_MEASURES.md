# Power BI DAX Measures

These measures are designed for the current semantic layer in `outputs/bi/`.

## Scenario summary measures

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

Scenario Payback Year =
CALCULATE(
    MAX(fact_scenario_kpis[value]),
    fact_scenario_kpis[metric] = "payback_year"
)
```

## Annual economics measures

```dax
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

Annual Processed Tonnes =
CALCULATE(
    SUM(fact_annual_metrics[value]),
    fact_annual_metrics[metric] = "expanded_tonnes"
)
```

## Driver measures

```dax
Annual Net Price =
CALCULATE(
    AVERAGE(fact_annual_metrics[value]),
    fact_annual_metrics[metric] = "scenario_net_price_usd_per_lb"
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

- NPV, revenue, EBITDA, free cash flow, capex, VaR, CVaR: Currency, display units in billions or millions.
- Probability of Loss: Percentage with one decimal place.
- Head Grade and Recovery: Percentage with two decimal places.
- Payback Year: Whole number.
