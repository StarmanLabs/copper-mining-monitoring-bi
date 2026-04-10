# Copper Mining Risk Model

Rebuilding a copper mining valuation workbook into a reproducible Python risk engine with BI-ready outputs for Power BI and Tableau.

This repository now goes beyond the original Excel and VBA prototype. It includes a modular Python valuation engine, Monte Carlo risk simulation, deterministic scenarios, sensitivity exports, and a semantic BI layer designed for dashboarding.

GitHub-facing portfolio documentation:

- `docs/README_PORTFOLIO.md`
- `docs/GITHUB_CASE_STUDY.md`
- `docs/GITHUB_PORTFOLIO_COPY.md`
- `docs/LINKEDIN_PORTFOLIO_COPY.md`
- `PORTFOLIO_OVERVIEW.md`
- `BI_SEMANTIC_MODEL.md`
- `POWERBI_MEASURES.md`

Canonical public README for GitHub:

- `docs/README_PORTFOLIO.md`

The legacy workbook summary is preserved below for reference.

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
