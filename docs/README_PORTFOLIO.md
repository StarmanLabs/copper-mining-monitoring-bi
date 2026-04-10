# Copper Mining Risk Model

Rebuilding a copper mining valuation workbook into a reproducible Python risk engine with BI-ready outputs for Power BI and Tableau.

## Overview

This project started as an Excel and VBA financial model for a hypothetical copper mining expansion. The original workbook already contained a strong economic structure: production assumptions, price paths, operating costs, expansion capex, and Monte Carlo simulation.

The limitation was not the idea. The limitation was the medium.

In spreadsheet form, the model was hard to audit, hard to extend, and difficult to connect to modern reporting workflows. The goal of this repository is to turn that static workbook into a portfolio-grade analytical product with four qualities:

- reproducible economics
- transparent assumptions
- scalable simulation
- dashboard-ready data architecture

## What This Project Does

The repository now supports:

- structured extraction of assumptions and benchmark outputs from the Excel workbook
- deterministic project valuation in Python
- Monte Carlo simulation for downside risk analysis
- scenario comparison across market, operational, and investment stress cases
- tornado sensitivity and price-grade stress heatmaps
- semantic BI exports with dimensions, fact tables, KPI catalogs, and Power BI measure templates

## The Transformation Story

### Stage 1: Excel Prototype

The project began as a workbook built around:

- copper price assumptions
- ore grade decline
- metallurgical recovery
- throughput expansion
- capex scheduling
- project cash flow valuation
- Monte Carlo simulation

### Stage 2: Python Rebuild

The core model was translated into modular Python components:

- workbook extraction
- valuation engine
- stochastic simulation
- scenario analysis
- BI export layer

### Stage 3: BI Product Layer

The project was then elevated from a modeling exercise to a reporting product:

- star-schema style outputs
- scenario dimension
- annual fact tables
- KPI fact tables
- sensitivity fact tables
- simulation distribution tables
- semantic documentation for dashboard development

## Core Output Layer

The export pipeline generates:

- `dim_year.csv`
- `dim_metric.csv`
- `dim_scenario.csv`
- `fact_annual_metrics.csv`
- `fact_scenario_kpis.csv`
- `fact_simulation_distribution.csv`
- `fact_tornado_sensitivity.csv`
- `fact_heatmap_price_grade.csv`
- `dashboard_kpis.csv`
- `benchmark_comparison.csv`
- `powerbi_measure_catalog.csv`

## Portfolio Value

This project demonstrates the ability to:

- translate an opaque Excel model into a reproducible Python system
- preserve economic logic while improving analytical transparency
- move from one-off spreadsheet analysis to scalable reporting architecture
- structure outputs for Power BI or Tableau instead of leaving them trapped in a workbook
- present limitations honestly through benchmark comparison rather than hiding model divergence

## Important Limitation

The current Python engine is a strong analytical product prototype, but it is not yet a perfect financial reconciliation of the original workbook. Benchmark comparison files explicitly show where Python and Excel still diverge.
