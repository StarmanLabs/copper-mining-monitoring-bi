# Copper Mining Risk Model

Rebuilding a spreadsheet-based copper mining valuation into a reproducible Python analytics engine with deterministic scenario analysis, structured benchmark reconciliation, upgraded stochastic risk modeling, and BI-ready outputs for Power BI or Tableau.

## Project objective

This repository converts an Excel mining valuation workflow into a Python-first analytical pipeline that is easier to audit, test, extend, and present as a portfolio-grade decision-support project.

The goal is not spreadsheet replacement for its own sake. The goal is to make the model:

- more reproducible
- clearer about what is economically being valued
- more explicit about what is and is not comparable to the workbook benchmark
- stronger for downstream BI dashboards and portfolio presentation

## What the engine does

The project currently produces four analytical layers:

1. Deterministic expanded-project valuation in Python
2. Incremental-expansion benchmark reconciliation against the workbook
3. Stochastic downside analysis with annual price shocks and bounded operating uncertainty
4. BI-ready fact and dimension tables plus a self-contained HTML dashboard showcase

## Analytical design

### Deterministic model

The deterministic engine values the expanded operating case in USD using:

- annual copper price deck from the workbook
- annual base throughput, grade, and recovery inputs from the workbook
- explicit payable and treatment/refining adjustments
- explicit cash operating costs
- simplified tax proxy aligned to the workbook cash-flow chain
- explicit year 0 and year 1 capex timing
- explicit working-capital treatment
- explicit discounted free cash flow, NPV, and IRR

The deterministic scenario layer then stresses price, grade, recovery, throughput, opex, capex, and discount rate for BI comparison and dashboard storytelling.

### Benchmark reconciliation

The workbook benchmark is not treated as a generic "Excel truth table".

Instead, the repo now distinguishes between:

- `total_project_expanded_operation`: the main Python valuation used for scenarios and dashboard KPIs
- `incremental_expansion`: the workbook-style benchmark basis used for deterministic reconciliation

The benchmark comparison table in `outputs/bi/benchmark_comparison.csv` explicitly flags:

- units
- currency
- valuation basis
- timing basis
- comparability status
- explanatory notes

`gap` and `pct_gap` are only computed when direct comparison is defensible.

### Stochastic model

The Monte Carlo layer keeps the deterministic model as the base case and upgrades the stochastic structure by:

- simulating annual copper price variation around the workbook price deck
- treating grade uncertainty as a project-level multiplier
- treating recovery uncertainty as bounded yearly variation
- preserving seed reproducibility
- exporting a BI-friendly simulation distribution table

This is intentionally a practical project-risk engine, not a full commodity-process research model.

## Data flow

```text
Excel workbook
  -> structured loader with sheet/cell validation
  -> deterministic model
  -> scenario analysis
  -> Monte Carlo simulation
  -> benchmark reconciliation
  -> BI exports
  -> HTML dashboard showcase
```

## Files to use in Power BI or Tableau

Use the files in `outputs/bi/`.

### Core model tables

- `dim_year.csv`
- `dim_metric.csv`
- `dim_scenario.csv`
- `fact_annual_metrics.csv`
- `fact_scenario_kpis.csv`
- `fact_simulation_distribution.csv`
- `fact_tornado_sensitivity.csv`
- `fact_heatmap_price_grade.csv`

### Support tables

- `simulation_summary.csv`
- `simulation_percentiles.csv`
- `benchmark_comparison.csv`
- `powerbi_measure_catalog.csv`

For Power BI, keep each fact table attached only to the dimensions it actually uses.

For Tableau, it is usually cleaner to work with separate subject-area sources rather than forcing all facts into one denormalized extract.

## Repository structure

```text
copper_minning_risk_model/
  config/                     Project configuration
  data/raw/                   Source Excel workbook
  docs/                       Technical notes and usage guidance
  outputs/bi/                 BI-ready CSV exports
  outputs/dashboard/          Self-contained HTML dashboard output
  powerbi/                    Theme, DAX, and dashboard blueprint assets
  scripts/                    Build entrypoints
  src/copper_risk_model/      Loader, model, simulation, BI export, dashboard code
  tests/                      Analytical and smoke tests
```

## How to run

Install dependencies:

```bash
python -m pip install -e .[dev]
```

Build BI tables:

```bash
python scripts/build_bi_dataset.py
```

Build BI tables plus the HTML dashboard:

```bash
python scripts/build_portfolio_dashboard.py
```

Run tests:

```bash
python -m pytest -q
```

## Technical notes

- Model scope and conventions: `docs/MODEL_NOTES.md`
- BI usage guidance: `docs/BI_USAGE.md`
- Folder guide: `docs/PROJECT_STRUCTURE.md`

## Main limitations

This repository is a serious analytical rebuild, but it is still deliberately simplified.

It does not claim:

- full formula-by-formula Excel parity
- a complete mining fiscal regime
- engineering-grade mine planning realism
- a structural commodity-price forecasting model

What it does claim honestly is:

> This project rebuilds a spreadsheet-based copper mining valuation into a reproducible Python analytical engine with improved scenario design, stronger stochastic risk modeling, explicit benchmark reconciliation, and BI-ready outputs for decision support.

## Disclaimer

This is an analytical portfolio project based on a hypothetical mining expansion case. It is not investment advice and should not substitute for geological, metallurgical, fiscal, financial, or operational due diligence.

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
