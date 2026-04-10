# Dashboard Build Guide

## Recommended build order

1. Load the CSV files from `outputs/bi/`.
2. Use `dashboard_pages.csv` to define the report structure.
3. Use `kpi_catalog.csv` and `metric_catalog.csv` to standardize labels and units.
4. Build the executive page first.
5. Add the risk distribution page second.
6. Add the annual value-creation page third.
7. Close with the benchmark page.

## Power BI modeling suggestion

- Keep `annual_profile_long.csv` as the main fact table for time-series visuals.
- Use `metric_catalog.csv` as a dimension joined on `metric`.
- Keep `dashboard_kpis.csv` and `simulation_summary.csv` as separate small fact tables.
- Use `simulation_distribution.csv` and `simulation_cdf.csv` only for histogram and tail-risk visuals.

## Tableau modeling suggestion

- Prefer a relationship model, not a heavy join, because the distributions and annual profile have different grains.
- Use `annual_profile_long.csv` for year-level trend visuals.
- Use `simulation_distribution.csv` for histogram bins and scenario scatter plots.
- Use `benchmark_comparison.csv` for validation tiles.

## Minimum viable pages

### Executive View

- KPI cards
- NPV benchmark comparison
- Probability of loss
- VaR and CVaR

### Value Creation

- Revenue by year
- EBITDA by year
- Free cash flow by year
- Discounted FCF by year

### Risk Distribution

- NPV histogram
- CDF line
- Tail percentile markers

### Drivers

- Copper price path
- Head grade path
- Recovery path
- Throughput path

### Benchmark

- Python vs Excel summary comparison
- CDF comparison
- gap explanation note

## Portfolio presentation advice

When you show the dashboard, emphasize that the value is not the chart styling itself. The value is that:

- the model is reproducible
- the assumptions are auditable
- the outputs are structured for BI refresh
- the workbook has been translated into a scalable analytical asset
