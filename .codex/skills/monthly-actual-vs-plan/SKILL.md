# Skill: monthly-actual-vs-plan

## Scope

This is a repository-local skill for `copper_minning_risk_model`.

Use it only for this project and for monthly monitoring layers that are added to this repository as part of its evolution toward a mining planning, management-control, and BI platform.

## Current repository context

This repository does not currently contain a fully implemented live monthly actual-vs-plan layer sourced from plant, ERP, or telemetry systems.

That means this skill should be used to:

- design monthly canonical schemas
- add realistic sample monthly datasets when needed
- build validation and transformation logic
- create BI-ready monthly marts
- prepare the repo for future actual-vs-plan monitoring

It should not be used to imply that the current repository already has live operational integration when it does not.

## Purpose

Build a credible monthly actual-vs-plan monitoring layer for mining planning, management control, performance analytics, and BI.

## When to use

Use this skill when the task involves:
- monthly mining datasets
- plan vs actual logic
- KPI monitoring
- variance calculations
- management-control style marts
- monthly dashboard outputs

## Target business questions

This skill should help answer questions such as:
- Are we on plan this month?
- Which KPI has the largest negative deviation?
- Is throughput weakness offset by grade or recovery?
- Are unit costs worsening?
- How is price exposure affecting revenue or margin proxies?
- Which areas require management attention?

## Canonical datasets to prefer

Prefer defining or using:
- plan_monthly
- actual_production_monthly
- plant_performance_monthly
- cost_actuals_monthly
- market_prices_monthly
- kpi_monthly_summary

## KPI priority list

Prioritize these KPIs:
- throughput
- head_grade
- recovery
- copper_production
- unit_opex
- revenue_proxy
- ebitda_proxy
- operating_cash_flow_proxy
- actual_minus_plan
- pct_variance
- variance flags / alert status

## Validation rules

Every dataset should be checked for:
- required columns
- duplicate keys
- invalid or missing periods
- impossible rates
- invalid negative values where not allowed
- unit ambiguity
- inconsistent grain

## Output rules

Outputs should be BI-friendly and recruiter-readable.
Use clear field names.
Keep marts dashboard-ready.

## Assumption rules

If using sample data:
- keep it realistic
- clearly mark it as sample
- do not imply live plant or ERP integration

## What to avoid

Avoid:
- daily telemetry complexity
- pseudo-real-time framing
- engineering-level process simulation
- overcomplicated KPI hierarchies
- unexplained synthetic fields

## Expected deliverables

Depending on the task:
- canonical monthly schemas
- sample monthly datasets
- validation code
- transformation pipeline
- KPI marts
- monthly dashboard guidance
- tests

## Completion checklist

Before finishing:
- confirm monthly grain is consistent
- confirm actual-vs-plan fields are explicit
- confirm all KPIs have clear units and meaning
- confirm outputs are useful for management control / BI
- confirm the implementation does not overclaim live mine-system integration
