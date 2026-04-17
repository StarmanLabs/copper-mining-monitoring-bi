# Skill: mining-planning-architect

## Scope

This is a repository-local skill for `copper_minning_risk_model`.

Use it only for this project, its current structure, and its current transition from workbook-seeded analytics toward a more canonical mining planning, performance, and BI platform.

## Purpose

Refactor the repository toward a business-facing mining analytics platform centered on planning, management control, performance analytics, KPI monitoring, BI, and decision support.

## When to use

Use this skill when the task involves:
- repo repositioning
- architecture redesign
- module reorganization
- separating core platform logic from legacy workbook logic
- redefining package boundaries
- changing naming or ownership of modules
- deciding what belongs in monitoring vs valuation/risk

## Current repository context

This skill applies to the current repository state:

- repository root: `copper_minning_risk_model`
- current package namespace: `src/copper_risk_model/`
- current raw source anchor: `data/raw/Copper_mining_risk_model.xlsm`
- current BI delivery layer: `outputs/bi/`, `outputs/dashboard/`, and `powerbi/`
- current documentation layer: `README.md` and `docs/`
- current advanced secondary modules: valuation, deterministic scenarios, benchmark reconciliation, Monte Carlo downside, tornado, and heatmap outputs

The skill should improve this repository specifically. It should not be written or interpreted as a generic mining-platform architecture template.

## Core mindset

The repo should primarily read as:
a mining planning and performance analytics platform

not as:
- an Excel-to-Python migration
- a pure valuation project
- a mine-engineering platform

## Business framing to preserve

The target reviewer is likely to be:
- a mining hiring manager
- a BI lead
- a planning analyst
- a performance or management-control lead
- a business-facing technical reviewer

The candidate profile is:
Economics + data + mining domain adaptation

For this repository, the strongest portfolio story is:

- planning support
- KPI mart design
- BI semantic clarity
- performance and cost monitoring
- scenario planning
- business-facing mining analytics

not:

- mine engineering depth
- geology specialization
- formula-by-formula workbook replication as the main achievement

## Mandatory principles

1. Workbook logic is legacy or benchmark logic.
2. Core logic should prefer canonical datasets.
3. Monitoring and BI should be more prominent than standalone valuation.
4. Valuation, scenarios, and Monte Carlo remain useful but secondary.
5. Architecture should stay practical and portfolio-ready.
6. Do not overengineer.

## Project-specific architecture intent

When using this skill in this repository, prefer to push logic toward clear platform layers such as:

- workbook adapters and legacy extraction
- validation of structured inputs
- canonical tables and transforms
- monitoring and KPI layers
- BI export semantics
- advanced valuation and downside modules
- dashboard-facing outputs

Avoid spreading workbook-native assumptions deeper into:

- BI marts
- dashboard semantics
- scenario summary layers
- future monthly monitoring structures

## Preferred architecture pattern

Aim for modules such as:
- adapters
- ingestion
- validation
- transforms
- monitoring
- bi
- valuation
- risk
- dashboards

## What good output looks like

A good result from this skill:
- makes the repo easier to explain to a mining recruiter
- reduces workbook centrality
- strengthens planning/control/BI relevance
- keeps advanced analytics but demotes them structurally
- improves long-term extensibility

## What to avoid

Avoid:
- rewriting everything without clear gain
- adding cloud infra
- adding orchestration
- inventing enterprise-scale complexity
- pushing engineering realism beyond actual data support
- architecture that is abstract but not useful

## Expected deliverables

Depending on the task, produce some combination of:
- revised repo tree
- migration plan
- ownership map for modules
- rename suggestions
- README outline
- separation of legacy vs core
- explicit implementation phases

## Completion checklist

Before finishing:
- confirm the repo now reads as planning/control/BI-oriented
- confirm workbook dependency did not spread
- confirm docs and architecture tell the same story
- confirm changes improve portfolio positioning
- confirm the output is clearly specific to this repository rather than a generic mining analytics template
