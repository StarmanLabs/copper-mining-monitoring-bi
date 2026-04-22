# Sample Data Guide

This folder contains public sample/demo datasets used to demonstrate the monthly monitoring core and the secondary annual appendix path.

## Purpose

These files exist to:

- keep the monthly monitoring pipeline workbook-independent
- make the repository runnable on public GitHub
- support Power BI or Tableau demos without private company data

## Current Contents

- `monthly_monitoring/plan_monthly.csv`
- `monthly_monitoring/actual_production_monthly.csv`
- `monthly_monitoring/plant_performance_monthly.csv`
- `monthly_monitoring/cost_actuals_monthly.csv`
- `monthly_monitoring/market_prices_monthly.csv`
- `annual_appendix/annual_appendix_inputs.csv`
- `annual_appendix/appendix_parameters.csv`
- `annual_appendix/appendix_scenarios.csv`
- `annual_appendix/appendix_benchmark_metrics.csv`

## Interpretation Rules

- Treat these files as sample/demo data
- Do not present them as live mine, plant, dispatch, assay, or ERP exports
- Keep the monthly grain and field names stable because downstream marts depend on them
- Keep the annual appendix field names stable because the secondary valuation and risk layer now depends on them

## Private Adaptation Path

To adapt this repository for real work later:

- replace these sample tables with governed private source tables
- preserve the canonical schemas where possible
- document any new fields, unit conventions, or source-system assumptions
