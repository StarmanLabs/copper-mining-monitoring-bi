# Skill: valuation-risk-secondary

## Scope

This is a repository-local skill for `copper_minning_risk_model`.

Use it only for this project and for work on valuation, deterministic scenarios, sensitivity analysis, Monte Carlo, and benchmark reconciliation as advanced secondary modules within the broader mining planning and BI platform.

## Current repository context

This repository already contains advanced secondary analytical modules such as:

- deterministic valuation outputs
- scenario analysis
- Monte Carlo downside analysis
- benchmark reconciliation
- price-grade heatmaps
- tornado sensitivity

These modules currently live alongside the business-facing planning and BI layers and should remain technically useful without becoming the public identity of the repository.

## Purpose

Maintain and improve valuation, deterministic scenarios, sensitivity analysis, and Monte Carlo as advanced secondary modules behind the broader mining planning and BI platform.

## When to use

Use this skill when the task involves:
- valuation logic
- scenario analysis
- Monte Carlo
- benchmark reconciliation
- price/grade stress
- tornado sensitivity
- IRR / NPV logic

## Strategic role

These modules are important, but they are not the public identity of the repo.
They should support decision-making without dominating the platform story.

## Required principles

- Keep assumptions explicit.
- Keep limitations explicit.
- Prefer canonical inputs instead of workbook-native structures whenever feasible.
- Preserve benchmark transparency.
- Do not overclaim realism.

## Modeling honesty

Allowed:
- business-facing scenario analysis
- downside framing
- benchmark comparison
- proxy economic interpretation

Not allowed:
- pretending the model is asset-grade without supporting data
- implying forecast certainty
- implying full workbook parity if not validated

## Technical rules

- avoid deprecated numerical APIs
- document assumption changes
- keep scenario and simulation outputs reproducible
- if refactoring, decouple from workbook-specific structures

## Completion checklist

Before finishing:
- confirm role remains secondary in public framing
- confirm modeling assumptions are visible
- confirm benchmark limitations are not hidden
- confirm changes stay specific to this repository and its advanced analytical layer
