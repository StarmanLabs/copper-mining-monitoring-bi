# AGENTS.md

## Scope

This file applies to everything under `powerbi/`.

## Purpose

Power BI assets should help turn canonical mining datasets into a credible executive monitoring product.

## Rules

- Prioritize business-facing dashboard pages.
- Make measure names readable.
- Separate executive KPI pages from advanced analytical appendix pages.
- Use marts intentionally; do not force unrelated facts into one model.
- Keep a clean semantic layer.
- Document each page's purpose.

## Preferred page order

1. Executive overview
2. Monthly actual vs plan
3. Process performance
4. Cost and margin
5. Scenario planning
6. Advanced downside / valuation appendix

## Avoid

- page designs with no clear business question
- visually flashy but semantically weak measures
- unnecessary complexity in DAX if the mart could solve it upstream
