# AGENTS.md

## Project identity

This repository is a mining planning, performance analytics, and BI portfolio project for an Economics graduate targeting business-facing mining roles.

Primary positioning:
- mining planning support
- management control
- performance analytics
- KPI monitoring
- BI-ready analytical outputs
- decision support

This repository is NOT primarily:
- an Excel reconstruction project
- a pure Monte Carlo / valuation showcase
- a mine-engineering or geology system
- a real-time control room or telemetry system

Valuation, scenario analysis, and Monte Carlo are valuable, but they are secondary advanced modules behind a broader planning-and-monitoring story.

## Business-facing objective

Every substantial change should improve at least one of these:
- planning support
- management control
- actual-vs-plan visibility
- KPI monitoring
- BI semantic clarity
- executive decision support
- portfolio credibility for mining recruiters and analytics managers

If a proposed change is technically interesting but does not improve any of the above, deprioritize it.

## Current strategic direction

The repo is being refactored away from workbook-centric logic toward a source-agnostic mining analytics platform.

Preferred target flow:
source data -> validation -> canonical datasets -> analytical transformations -> KPI marts -> dashboard / BI outputs -> advanced valuation/risk modules

Workbook-based extraction must be treated as:
- legacy adapter
- benchmark layer
- transitional source
not as the platform backbone

## Main priorities

Priority order:
1. monthly actual-vs-plan monitoring layer when actual datasets exist
2. canonical mining datasets and validation
3. KPI marts for BI and executive dashboards
4. documentation and recruiter-facing clarity
5. valuation/risk modules as advanced secondary analytics
6. workbook legacy isolation and benchmark transparency

## Data principles

Prefer monthly business-facing mining datasets first.

Core metrics and entities to prioritize:
- throughput
- head grade
- recovery
- copper production
- unit cost
- revenue proxy
- EBITDA proxy
- operating cash flow proxy
- capex
- working capital
- free cash flow
- actual vs plan variance
- scenario comparison

Always make explicit:
- grain
- units
- key columns
- assumptions
- limitations

Do not hide unit conversions.
Do not leave ambiguous whether a metric is actual, plan, scenario, proxy, or benchmark-derived.

## Modeling principles

Be honest about realism.
Do not overclaim engineering realism, live operations readiness, or full corporate-finance depth.

Allowed:
- planning-style KPI monitoring
- business-facing operational proxies
- scenario comparison
- benchmark reconciliation
- decision-support framing

Not allowed unless explicitly requested:
- pretending sample data is real mine telemetry
- implying the repo is asset-grade
- implying real ERP/plant integration where none exists
- overselling valuation parity with the workbook

## Architecture principles

Prefer:
- modular functions
- typed interfaces where reasonable
- explicit transformation layers
- canonical tables
- small CLI entrypoints
- reproducible outputs
- lightweight, inspectable pipelines

Avoid:
- hidden coupling
- hardcoded workbook cell logic in core modules
- overengineered abstraction
- cloud infra
- orchestration frameworks
- unnecessary framework churn

## Code change rules

When changing code:
- preserve readability
- preserve portfolio clarity
- add docstrings for important new logic
- add or update tests for non-trivial changes
- keep names business-readable
- avoid cleverness that hurts maintainability

If touching core pipeline logic:
- update docs
- update tests
- update assumptions and limitations if needed

## Documentation rules

All major features should be documented in recruiter-readable language.

Documentation should help two audiences:
1. technical reviewer
2. mining hiring manager / BI lead / planning lead

README and docs must consistently present the project as:
a mining planning and performance analytics platform with BI-ready outputs and advanced secondary valuation/risk modules

## Legacy workbook rules

Workbook logic must stay isolated.
Do not expand workbook dependency unless explicitly asked.

If valuation/risk modules are refactored, make them consume canonical inputs instead of workbook-native structures whenever feasible.

Workbook-specific extraction belongs in legacy / adapter-style modules.

## Validation rules

Whenever adding a new dataset or mart:
- define grain
- define required columns
- define optional columns
- define units
- define key logic
- validate missing columns
- validate duplicate keys
- validate period consistency
- validate numeric ranges

## Dashboard rules

Dashboards should first answer:
- Are we on plan?
- Where are the largest deviations?
- What is driving economic performance?
- What needs managerial attention?

Dashboards should not be designed only for visual flair.

Preferred dashboard themes:
- executive overview
- monthly actual vs plan
- cost and margin
- process performance
- scenario planning
- advanced downside / valuation appendix

## PR and change-summary behavior

When summarizing work:
- lead with business value
- state affected modules
- state validations/tests run
- state assumptions or remaining limitations
- avoid exaggerated language

Preferred summary structure:
1. what changed
2. why it matters
3. what was validated
4. what still remains limited

## Required commands before finishing meaningful code changes

Run these unless the task is documentation-only and clearly cannot affect behavior:
- python -m pytest -q
- python scripts/build_bi_dataset.py
- python scripts/build_portfolio_dashboard.py

If a change affects only docs, still run at least the relevant checks if practical, because repo instructions should be validated whenever feasible.

## Final check before submitting changes

Before declaring a task complete, verify:
- the repo still reads as planning/control/BI-oriented
- workbook dependency did not increase accidentally
- new outputs are documented
- tests were run or a limitation was clearly stated
- the change helps the portfolio for mining business-facing roles
