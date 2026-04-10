# Portfolio Overview

## Project positioning

This repository is not presented as a generic Monte Carlo exercise.

It is positioned as a mining economics and risk analytics product that:

- reconstructs a copper project valuation model from Excel
- makes assumptions explicit
- generates deterministic and probabilistic outputs
- structures data for BI consumption
- supports executive storytelling around value creation and downside risk

## What makes it portfolio-grade

### 1. Economic logic

The project is grounded in mining economics rather than generic data-science framing.

Core drivers:

- copper price
- ore grade
- metallurgical recovery
- throughput
- capex burden
- discount rate

### 2. Reproducibility

The workbook logic is translated into Python modules so the model can be audited, extended, and refreshed.

### 3. BI readiness

The output layer is no longer a loose export. It now includes:

- dimensions
- fact tables
- KPI catalog
- dashboard page model
- Power BI measure suggestions

### 4. Decision orientation

The dashboard logic is designed to answer:

- is the project creating value?
- how fragile is the downside?
- what are the dominant risk drivers?
- how do scenarios compare?

## Recommended portfolio narrative

When presenting the project, the strongest framing is:

1. The original asset existed as an Excel valuation workbook.
2. I rebuilt it into a reproducible analytical engine in Python.
3. I structured outputs into a semantic model for Power BI/Tableau.
4. I extended the model with scenario comparison, tornado sensitivity, and stress heatmaps.
5. I kept benchmark gaps explicit instead of hiding model divergence.

## Most important files

- `src/copper_risk_model/`
- `outputs/bi/`
- `PORTAFOLIO_BI_BLUEPRINT.md`
- `DASHBOARD_BUILD_GUIDE.md`
- `BI_SEMANTIC_MODEL.md`
- `POWERBI_MEASURES.md`

## Honest limitation

The current Python engine is a strong analytical product prototype, but it is not yet a perfect financial reconciliation of the original workbook.

That limitation should be stated openly because it increases credibility rather than weakening it.
