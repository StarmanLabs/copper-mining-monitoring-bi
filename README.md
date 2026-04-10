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
- deterministic scenario comparison across market, operational, and investment stress cases
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

## Repository Structure

```text
copper_minning_risk_model/
  config/
    project.yaml
  docs/
    README_PORTFOLIO.md
    GITHUB_CASE_STUDY.md
    GITHUB_PORTFOLIO_COPY.md
    LINKEDIN_PORTFOLIO_COPY.md
    GITHUB_SETUP_CHECKLIST.md
  outputs/
    bi/
  scripts/
    build_bi_dataset.py
  src/
    copper_risk_model/
      excel_loader.py
      model.py
      simulation.py
      scenario_analysis.py
      bi_semantic.py
      bi_export.py
  tests/
    test_pipeline_smoke.py
  .github/
    workflows/
      ci.yml
  BI_SEMANTIC_MODEL.md
  DASHBOARD_BUILD_GUIDE.md
  PORTAFOLIO_BI_BLUEPRINT.md
  PORTFOLIO_OVERVIEW.md
  POWERBI_MEASURES.md
  Copper_mining_risk_model.xlsm
  technical_paper.pdf
  README.md
```

## Core Data Sources

The model uses:

- World Bank copper price history
- Cerro Verde operating data for ore grade and recovery calibration
- project-level assumptions embedded in the original workbook for costs, fiscal structure, WACC, and capex

## Output Layer

Running the pipeline generates BI-ready exports in `outputs/bi/`, including:

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

This is no longer just a model output folder. It is the beginning of a semantic layer for dashboarding.

## Validation

The repository includes a smoke test that verifies the end-to-end BI build pipeline.

Run:

```bash
python -m pytest -q
```

## How to Run

Install dependencies:

```bash
python -m pip install -e .[dev]
```

Generate BI outputs:

```bash
python scripts/build_bi_dataset.py
```

## Documentation

Portfolio and GitHub-facing documentation:

- `docs/README_PORTFOLIO.md`
- `docs/GITHUB_CASE_STUDY.md`
- `docs/GITHUB_PORTFOLIO_COPY.md`
- `docs/LINKEDIN_PORTFOLIO_COPY.md`
- `docs/GITHUB_SETUP_CHECKLIST.md`
- `PORTFOLIO_OVERVIEW.md`
- `PORTAFOLIO_BI_BLUEPRINT.md`
- `DASHBOARD_BUILD_GUIDE.md`
- `BI_SEMANTIC_MODEL.md`
- `POWERBI_MEASURES.md`

## Portfolio Value

This project demonstrates the ability to:

- translate an opaque Excel model into a reproducible Python system
- preserve economic logic while improving analytical transparency
- move from one-off spreadsheet analysis to scalable reporting architecture
- structure outputs for Power BI or Tableau instead of leaving them trapped in a workbook
- present limitations honestly through benchmark comparison rather than hiding model divergence

## Important Limitation

The current Python engine is a strong analytical product prototype, but it is not yet a perfect financial reconciliation of the original workbook. Benchmark comparison files explicitly show where Python and Excel still diverge.

That limitation is kept visible on purpose. For a serious portfolio project, methodological honesty is more valuable than pretending false precision.

## Disclaimer

This is an analytical and educational project based on a hypothetical mining expansion case. It is not an investment recommendation and should not replace technical, geological, fiscal, or financial due diligence.

<!-- Legacy workbook-oriented summary retained below for archive.

---

# Project Overview

Mining investments are highly exposed to uncertainty due to commodity price volatility and geological variability.

This project evaluates the economic viability of a copper mining project over a **15-year horizon**, incorporating uncertainty in key operational and market variables.

The model estimates the **Net Present Value (NPV)** of the project and quantifies financial risk using **Monte Carlo simulation**.

All monetary results are expressed in **Peruvian Soles (S/)**.

---

# Objective

The objective of this project is to evaluate the economic viability of a copper mining investment under uncertainty.

The model analyzes how variability in key factors — copper prices, ore grade, and metallurgical recovery — affects project profitability.

Using Monte Carlo simulation, the project estimates the probability distribution of the project's NPV and quantifies downside risk using metrics such as **Value at Risk (VaR)** and **Conditional Value at Risk (CVaR)**.

---

# Key Results

Monte Carlo simulation (10,000 scenarios) produced the following results:

| Metric | Value |
|------|------|
| Base NPV | **S/ 179,410,192** |
| Expected NPV | **S/ 351,269,556** |
| Probability of Loss | **41.61%** |
| VaR (5%) | **− S/ 1,311,282,054** |
| CVaR (5%) | **− S/ 1,599,912,510** |

---
# Key Insights

The simulation highlights several important economic insights about mining project risk.

- **Commodity price volatility is the dominant risk driver.**  
Changes in copper prices have the largest impact on project profitability compared to operational variables.

- **Operational uncertainty also contributes to financial risk.**  
Variability in ore grade and metallurgical recovery can significantly affect production output and revenues.

- **The project exhibits asymmetric risk.**  
While the expected NPV is positive, the probability of loss remains significant, illustrating the importance of risk-adjusted evaluation in mining investments.

- **Monte Carlo simulation provides a more realistic evaluation framework.**  
Traditional deterministic models may underestimate project risk, while probabilistic simulations reveal the full distribution of potential outcomes.

# Data Sources

The model incorporates empirical data from real mining operations and market sources.

### Copper Prices

Source:

World Bank – Commodity Price Data (The Pink Sheet)

Historical data:

2005 – 2025

Prices are expressed in **USD/lb** and used to estimate statistical parameters for price dynamics.

---

### Mining Operational Data

Source:

Freeport-McMoRan Inc. – Form 10-K Annual Reports

Mine used for calibration:

Cerro Verde (Peru)

Variables used:

- Ore grade (%)
- Metallurgical recovery (%)

Period:

2014 – 2024

These data are used to calibrate geological and operational assumptions.

---

### Production Scale

Source:

Memorias del Ministerio de Energía y Minas (MINEM)

Used to estimate realistic production levels based on large-scale Peruvian copper operations.

---

# Methodology

The project integrates financial modeling with stochastic simulation.

### Price Modeling

Copper prices are modeled using **logarithmic returns**:

RET = ln(Pt / Pt-1)

Estimated parameters:

μ (drift) ≈ 0.05  
σ (volatility) ≈ 0.22

Future price paths are simulated using a **Geometric Brownian Motion (GBM)** process.

---

### Operational Modeling

Ore grade follows a declining trend estimated from historical data:

Grade_t = α + βt

This reflects natural ore depletion over time.

Metallurgical recovery is modeled using historical averages from Cerro Verde operations.

Production starts at **150 million tons per year** and declines approximately **1.5% annually**, reflecting depletion dynamics.

A potential expansion scenario is modeled using a **logistic growth function** to simulate production ramp-up.

---

# Monte Carlo Simulation

A Monte Carlo simulation with **10,000 iterations** was implemented to capture uncertainty in key variables.

Random variables include:

- Copper price  
- Ore grade  
- Metallurgical recovery  

Distribution assumptions:

- Copper price → lognormal process (GBM)
- Ore grade → truncated lognormal distribution
- Recovery rate → truncated normal distribution

For each simulation, the full project cash flow is recalculated and a new **NPV** is obtained.

---

# Risk Metrics

Monte Carlo results are used to compute:

- Expected NPV  
- Standard deviation of NPV  
- Probability of loss  
- Value at Risk (VaR)  
- Conditional Value at Risk (CVaR)

These metrics allow a quantitative assessment of downside risk in the investment.

---

# Dashboard

An interactive Excel dashboard summarizes the results of the simulation and highlights key economic insights.

The dashboard includes:

- NPV distribution histogram  
- Cumulative distribution function (CDF)  
- Probability of value destruction  
- Risk drivers analysis  
- Risk-return comparison  
- Bidimensional sensitivity heatmap (price vs ore grade)

Example:

![Dashboard](images/dashboard.png)

---

# Project Structure

```
mining-project-risk-analysis

model/
   mining_project_model.xlsx

images/
   dashboard.png
   npv_distribution.png
   cdf.png
   sensitivity_heatmap.png

documentation/
   technical_note.pdf

README.md
```
---

# Tools Used

- Microsoft Excel
- VBA
- Financial Modeling
- Monte Carlo Simulation
- Data Visualization

---

# Disclaimer

This model represents a hypothetical mining expansion scenario developed for analytical and educational purposes.

---

# Author

Alejandro Mino  
Economics | Energy & Infrastructure | Economic Risk Analysis
-->
