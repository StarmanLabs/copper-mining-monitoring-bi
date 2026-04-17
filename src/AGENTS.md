# AGENTS.md

## Scope

This file applies to everything under `src/`.

## Purpose of code in src

Code under `src/` should serve one of these platform functions:
- ingestion
- validation
- canonical modeling
- KPI transformation
- monitoring
- BI export
- valuation/risk as secondary advanced analytics

## Rules for src

- Keep core logic source-agnostic where possible.
- Avoid placing workbook-specific logic in general-purpose modules.
- Prefer canonical tabular interfaces over sheet/cell-native structures.
- Favor business-readable naming over purely quantitative shorthand.
- Keep functions small and composable.
- Add docstrings for new public functions, important transformations, and non-obvious assumptions.
- Use type hints where they improve clarity.
- Do not introduce unnecessary dependencies.

## Core preference

If a design choice exists between:
A. workbook-tied shortcut
B. canonical reusable interface

prefer B unless the task is explicitly legacy-adapter-only.

## Testing expectations

For non-trivial changes in `src/`, add or update tests.
At minimum validate:
- shape and schema expectations
- key transformations
- KPI calculations
- variance logic
- failure behavior for invalid inputs

## Naming preference

Prefer names like:
- actual_production_monthly
- plan_monthly
- plant_performance_monthly
- cost_actuals_monthly
- kpi_monthly_summary

Avoid vague names like:
- final_data
- merged_table
- clean_output
- calc2
- model_new
