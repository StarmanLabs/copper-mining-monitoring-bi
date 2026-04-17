# Skill: mining-bi-semantic-layer

## Scope

This is a repository-local skill for `copper_minning_risk_model`.

Use it only for this project and for work that improves the BI-facing semantic layer built from this repository's canonical datasets, KPI marts, dimensions, and dashboard assets.

## Current repository context

This repository already contains a BI delivery layer centered on:

- `outputs/bi/`
- `outputs/dashboard/`
- `powerbi/`
- the semantic helpers inside `src/copper_risk_model/`

The current semantic layer already supports:

- annual mining KPI exports
- executive scenario KPI marts
- advanced downside and sensitivity tables
- Power BI guidance and dashboard blueprint assets

This skill should improve that layer for this repository specifically. It should not be written or interpreted as a generic BI framework skill.

## Purpose

Create business-facing facts, dimensions, KPI dictionaries, and dashboard-ready semantic layers for mining analytics.

## When to use

Use this skill when the task involves:
- Power BI marts
- Tableau-ready exports
- KPI dictionaries
- measure catalogs
- dashboard data modeling
- business-facing semantic cleanup

## Core philosophy

A dashboard is only as good as the semantic layer beneath it.

This skill should produce marts that make it easy to answer:
- what happened
- versus what plan
- why it matters economically
- what management should look at next

## Preferred mart split

Prefer separate subject-area marts such as:
- executive KPI mart
- monthly actual-vs-plan mart
- process performance mart
- cost and margin mart
- scenario planning mart
- advanced risk appendix mart

For the current repository state, preserve a clean separation between:

- business-facing executive and monitoring marts
- scenario planning marts
- advanced valuation and downside marts
- benchmark transparency outputs

## Required metadata mindset

For each mart or dimension, define:
- grain
- keys
- metric meaning
- units
- intended dashboard page
- major limitations

## Naming rules

Prefer business-readable names.
Examples:
- fact_monthly_kpis
- fact_actual_vs_plan
- dim_period
- dim_metric
- dim_scenario
- fact_scenario_kpis

## What to avoid

Avoid:
- one giant denormalized table if it hurts clarity
- cryptic measure names
- marts that only make sense to the model author
- advanced analytical tables mixed into executive pages without framing

## Expected deliverables

Depending on the task:
- mart design
- dimension design
- KPI dictionary
- page mapping
- measure catalog
- dashboard blueprint updates

## Completion checklist

Before finishing:
- confirm executive pages can be built cleanly
- confirm advanced analytics remain separable
- confirm marts are aligned with planning/control use cases
- confirm the semantic layer is specific to this repository and its BI outputs
