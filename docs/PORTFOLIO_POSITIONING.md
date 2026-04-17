# Portfolio Positioning

## Recommended public title

Recommended portfolio title:

**Copper Mining Planning and Performance Analytics**

Alternative public titles:

- Copper Mining BI and Decision Support Platform
- Mining Planning, KPI, and Risk Analytics
- Copper Mining Performance Monitoring and Scenario Planning

The current repository and package names can remain unchanged for continuity. The public-facing title should emphasize planning, control, BI, and decision support rather than only valuation.

## Core positioning statement

This repository is best positioned as a mining analytics platform for:

- planning support
- management control
- performance monitoring
- cost and margin review
- business intelligence
- finance or business analysis support in mining

The advanced valuation and Monte Carlo layers should be presented as secondary modules that deepen the platform, not as the platform's identity.

## Why this fits an economics graduate

This framing is stronger for an economics profile because it highlights:

- KPI design
- cost structure interpretation
- price exposure analysis
- revenue and cash-generation proxies
- dashboarding and BI communication
- scenario planning for management decisions
- explicit treatment of uncertainty and downside

It does **not** require pretending to be a mine engineer, planner, or geologist. It shows mining domain adaptation through metrics, structure, and decision use.

## Current data reality

The current implementation is workbook-seeded, not source-universal in the ingestion layer.

That means the honest framing is:

- the source today is an Excel workbook
- the downstream analytical model is organized around mining KPI entities rather than workbook tabs
- the BI layer is reusable and source-extensible
- true live actual-vs-plan monitoring would require additional source tables from plant, lab, planning, dispatch, or ERP systems

This distinction should be stated clearly in interviews and in the README.

## Module priority

The recommended module hierarchy is:

1. **Mining KPI layer**
   Throughput, copper production, grade, recovery, price, unit cost, revenue, EBITDA, operating cash flow, capex, and free cash flow.
2. **Executive BI marts**
   Scenario summary outputs, annual KPI outputs, and dimension tables designed for Power BI or Tableau.
3. **Scenario planning layer**
   Reference case, market cases, operating stress, capex stress, and committee downside.
4. **Advanced valuation and downside layer**
   NPV, IRR, Monte Carlo, tornado, and heatmap outputs.
5. **Benchmark transparency layer**
   Explicit reconciliation versus workbook benchmarks, with comparability rules and blocked-gap logic.

This order is important. It determines what the repository appears to be.

## Recommended KPI layer

The core KPI layer should revolve around metrics useful for business-facing mining functions.

### Current KPIs already supported by the repository

- processed tonnes
- copper production
- copper price and net realized price
- head grade
- recovery
- unit opex
- total opex
- revenue
- EBITDA
- operating cash flow
- free cash flow
- capex
- working capital deltas
- scenario margin proxy
- scenario payback / NPV / IRR

### Recommended KPI framing in dashboards

- throughput trend
- production trend
- grade trend
- recovery trend
- unit cost trend
- revenue exposure to copper price
- EBITDA and operating cash flow proxies
- free cash flow and capex profile
- scenario spread versus the reference planning case
- downside and tail-risk overlays for advanced pages

### Important honesty rule

Do not label the current data as true `actual vs plan` unless actual operational data is added.

With the current repository, the correct labels are:

- planning profile
- reference case
- scenario case
- stress case
- benchmark reference

## Recommended canonical dataset design

The portfolio should be described as aiming toward a source-extensible mining data model with canonical subject areas.

### Current populated subject areas

- annual operating profile
- metallurgical profile
- commercial and pricing profile
- cost and cash profile
- scenario catalog
- advanced risk distribution
- benchmark reference

### Recommended next subject areas for a fuller platform

- period operating actuals
- period operating plan
- metallurgical actuals from lab or plant reporting
- cost actuals from ERP or management accounting
- budget or forecast tables
- shipment / payable / commercial settlement tables

That roadmap helps the repository read like a platform, even while the current source remains workbook-based.

## Recommended dashboard page structure

Recommended Power BI or Tableau page order:

1. **Executive Planning Overview**
   Revenue, EBITDA, operating cash flow, average throughput, average unit opex, margin proxy, selected scenario summary.
2. **Throughput and Production**
   Processed tonnes, copper production, project phase, ramp-up profile.
3. **Grade and Recovery**
   Head grade trend, recovery trend, metallurgical quality view.
4. **Cost, Revenue and Cash Generation**
   Unit cost, opex, revenue, EBITDA, operating cash flow, capex, free cash flow.
5. **Scenario Planning and Price Exposure**
   Scenario comparison, commodity price sensitivity, scenario deltas, planning trade-offs.
6. **Advanced Valuation and Downside Risk**
   NPV, IRR, Monte Carlo, tail-risk percentiles, tornado, price-grade heatmap.
7. **Benchmark and Method Transparency**
   Workbook reconciliation and explicit comparability notes.

This sequence makes the repo feel useful to administrative mining areas first and technically deeper second.

## How to describe the project in an interview

Recommended short description:

> I built a Python-based mining analytics workflow that turns workbook inputs into reproducible KPI marts for planning, performance review, scenario analysis, and BI dashboards. The project also includes valuation, Monte Carlo, and benchmark reconciliation modules, but the main value is a reusable decision-support layer for mining business functions.

Recommended role fit language:

- planning analyst support
- management control support
- mining BI analyst
- cost and performance analytics
- business analysis for mining operations or corporate teams

## What would move the project one level higher

The clearest next upgrade would be adding true period actuals and plan data side by side.

That would unlock:

- real production vs plan dashboards
- actual vs budget cost monitoring
- variance decomposition by throughput, grade, recovery, and price
- monthly management-control use cases
- stronger credibility for administrative mining functions

Until then, the project should be presented as planning-ready and BI-ready, not as a full live-monitoring platform.
