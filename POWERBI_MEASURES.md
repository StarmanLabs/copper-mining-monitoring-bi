# Power BI Measures

## Suggested measures

```DAX
Base NPV =
CALCULATE(
    MAX(dashboard_kpis[value]),
    dashboard_kpis[metric] = "python_base_npv_usd"
)
```

```DAX
Expected NPV =
CALCULATE(
    MAX(dashboard_kpis[value]),
    dashboard_kpis[metric] = "python_expected_npv_usd"
)
```

```DAX
Probability of Loss =
CALCULATE(
    MAX(dashboard_kpis[value]),
    dashboard_kpis[metric] = "python_probability_of_loss"
)
```

```DAX
Scenario NPV =
CALCULATE(
    SUM(fact_scenario_kpis[value]),
    fact_scenario_kpis[metric] = "base_npv_usd"
)
```

```DAX
Scenario Revenue =
CALCULATE(
    SUM(fact_scenario_kpis[value]),
    fact_scenario_kpis[metric] = "total_revenue_usd"
)
```

```DAX
Worst Tail NPV =
MIN(fact_simulation_distribution[npv_usd])
```

```DAX
Median Simulated NPV =
MEDIAN(fact_simulation_distribution[npv_usd])
```

```DAX
Tornado Impact =
MAX(fact_tornado_sensitivity[impact_vs_base_usd])
```

## Recommended formatting

- currency metrics: `USD #,##0; (USD #,##0)`
- percentages: `0.0%`
- year fields: whole number

## Practical advice

Do not overload the report with too many measures at once. The strongest portfolio version is the one that keeps:

- a sharp executive page
- one scenario comparison page
- one risk page
- one operational/economic trajectory page
