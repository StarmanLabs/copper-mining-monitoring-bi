# Monthly Monitoring Layer

This is the central business-facing layer of the repository.

It is designed to read like a realistic monthly mining planning and management-control workflow without pretending to be a live mine-system integration.

The layer is now intentionally deeper than a generic KPI demo:

- two synthetic sites instead of one undifferentiated operation
- process-area driver detail for downtime and production-gap explanation
- cost-center detail for unit-cost and margin-pressure interpretation
- site-level contribution logic for production shortfall and cost pressure

## Data Reality

The monthly pipeline still runs from public-safe sample/demo CSV inputs in:

- `data/sample_data/monthly_monitoring/`

Those files are intentionally:

- source-agnostic
- workbook-independent
- safe for public GitHub use
- suitable for BI prototyping and portfolio review

They are not:

- live plant telemetry
- ERP-connected actuals
- historian extracts
- control-room data

## Canonical Monthly Source Datasets

### Summary-grain source datasets

These remain the core monthly inputs used to build the wide KPI summary.

### `plan_monthly`

- Purpose: monthly planning baseline for throughput, grade, recovery, unit cost, commercial assumptions, and cash-burden assumptions
- Grain: one row per `site_id` and `period`
- Required columns:
  `site_id`, `period`, `throughput_tonnes_plan`, `head_grade_pct_plan`, `recovery_pct_plan`, `unit_cost_usd_per_tonne_plan`, `copper_price_usd_per_lb_plan`, `tc_rc_usd_per_lb_plan`, `payable_percent_plan`, `sustaining_capex_usd_plan`, `working_capital_change_usd_plan`
- Optional columns:
  `plan_version`, `commentary`

### `actual_production_monthly`

- Purpose: actual monthly throughput and copper production outcomes
- Grain: one row per `site_id` and `period`
- Required columns:
  `site_id`, `period`, `throughput_tonnes_actual`, `copper_production_tonnes_actual`

### `plant_performance_monthly`

- Purpose: site-level process indicators used to explain production variance
- Grain: one row per `site_id` and `period`
- Required columns:
  `site_id`, `period`, `head_grade_pct_actual`, `recovery_pct_actual`
- Optional columns:
  `availability_pct_actual`, `utilization_pct_actual`, `downtime_hours_actual`
- Interpretation:
  this is management-control process context, not engineering-grade plant instrumentation

### `cost_actuals_monthly`

- Purpose: monthly cost actuals plus sustaining capex and working-capital burden
- Grain: one row per `site_id` and `period`
- Required columns:
  `site_id`, `period`, `mining_cost_usd_actual`, `processing_cost_usd_actual`, `ga_cost_usd_actual`, `sustaining_capex_usd_actual`, `working_capital_change_usd_actual`

### `market_prices_monthly`

- Purpose: monthly market and commercial assumptions used in revenue proxies
- Grain: one row per `site_id` and `period`
- Required columns:
  `site_id`, `period`, `copper_price_usd_per_lb_actual`, `tc_rc_usd_per_lb_actual`, `payable_percent_actual`
- Optional columns:
  `benchmark_price_name`

### Detail-grain source datasets

These detail tables provide the operational-depth layer in the stable baseline.

They do not replace the summary-grain core.

They explain it.

### `process_driver_monthly`

- Purpose: process-area explanation layer for downtime, ore source context, stockpile usage, and production-gap concentration
- Grain: one row per `site_id`, `period`, and `process_area`
- Required columns:
  `site_id`, `period`, `process_area`, `ore_source`, `stockpile_flag`, `ore_mix_pct`, `throughput_tonnes_plan`, `throughput_tonnes_actual`, `copper_production_tonnes_plan`, `copper_production_tonnes_actual`, `availability_pct`, `downtime_hours`
- Typical business use:
  show where the operating gap is concentrating inside the monthly story

### `cost_center_monthly`

- Purpose: cost-center explanation layer for unit-cost and margin-pressure interpretation
- Grain: one row per `site_id`, `period`, and `cost_center`
- Required columns:
  `site_id`, `period`, `cost_center`, `cost_usd_plan`, `cost_usd_actual`
- Typical business use:
  show which cost buckets are creating the monthly cost burden

## Monthly Output Contract

### `kpi_monthly_summary`

- Purpose: wide monthly monitoring output with explicit plan, actual, variance, alert, and operational-context fields
- Grain: one row per `site_id` and `period`
- Main additions in the current baseline:
  `site_name`, `downtime_hours_actual`, `stockpile_feed_pct_actual`, `primary_ore_source`, `primary_process_area`, `site_production_gap_share_pct`, `site_cost_pressure_share_pct`, `top_cost_center`

### `fact_monthly_actual_vs_plan`

- Purpose: long metric-level fact table for explicit KPI variance review
- Grain: one row per `site_id`, `period`, and `metric`

### Monthly subject marts

- `mart_monthly_executive_overview.csv`
  headline monthly management view
- `mart_monthly_process_performance.csv`
  site-level process performance view with added downtime and ore-source context
- `mart_monthly_cost_margin.csv`
  site-level cost and margin view with cost-center context
- `mart_monthly_by_site.csv`
  site contribution view for production gap and cost pressure
- `mart_process_driver_summary.csv`
  process-area drill mart for downtime and production-gap explanation
- `mart_cost_center_summary.csv`
  cost-center drill mart for cost variance and margin-pressure interpretation

## Business Logic In This Layer

The new layer now makes these questions easier to answer:

- Which site is driving the production shortfall?
- Which process area is concentrating downtime?
- Is stockpile feed or ore-source mix part of the operating story?
- Which cost center is driving monthly cost pressure?
- How does site-level underperformance connect back to the Executive Overview?

This is still not root-cause analytics.

It is explicit management-control decomposition.

## Validation Rules

The monthly validation and data-quality layer now checks the new detail datasets too.

Core checks still include:

- missing required columns
- missing required values
- duplicate keys
- invalid period format
- missing monthly periods inside observed key sequences
- invalid numeric types
- impossible rates or percentages
- implausible negative values

The key improvement is that period continuity now respects the real grain:

- `site_id + period` for summary tables
- `site_id + period + process_area` for process-driver detail
- `site_id + period + cost_center` for cost-center detail

## How To Run

Build only the monthly layer:

```bash
python scripts/build_monthly_monitoring_dataset.py
```

Build the full BI layer:

```bash
python scripts/build_bi_dataset.py
```

Build the refresh package:

```bash
python scripts/build_refresh_package.py
```

## Interpretation Boundary

The right public claim is:

> This repository includes a sample/demo monthly actual-vs-plan monitoring layer with site, process-area, and cost-center drill support for planning, management control, KPI monitoring, and Power BI handoff.

The wrong claim is:

> This repository is already connected to a live mine, ERP, plant historian, or telemetry environment.
