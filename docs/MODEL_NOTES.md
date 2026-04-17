# Model Notes

## Purpose

This note documents what the Python platform is doing, what the workbook benchmark represents, and where the repository is intentionally simplified.

The repository should now be read primarily as a mining planning and performance analytics project with advanced valuation and risk modules, not as a valuation-only rebuild.

## 1. Platform scope

The current repository supports two different analytical layers.

### Primary layer: planning and performance analytics

This is the main portfolio layer used for:

- annual KPI exports
- scenario comparison
- throughput, production, grade, recovery, price, and unit-cost views
- revenue, EBITDA, operating cash flow, and free cash flow proxies
- Power BI and Tableau dashboards

This is the strongest fit for mining planning, BI, management control, and business-analysis roles.

### Secondary layer: advanced valuation and downside analysis

This layer contains:

- project-level NPV and IRR
- deterministic stress scenarios
- Monte Carlo downside outputs
- benchmark reconciliation

These modules deepen the project technically, but they are not the only reason the repository exists.

## 2. Current data reality

The implementation is workbook-seeded.

That means:

- the current source system is an Excel workbook
- the ingestion logic is still workbook-specific
- the downstream analytics are structured as mining KPI marts rather than spreadsheet tables
- the current repo is planning-ready and BI-ready, but not yet a live operating-actuals platform

So the appropriate claim is not "real-time mine monitoring." The appropriate claim is "reproducible mining KPI and scenario analytics built from a workbook seed."

## 3. Currency and units

The active Python engine reports monetary outputs in USD.

The workbook benchmark values used in reconciliation are also treated as USD because:

- the workbook operating and price inputs are labeled in USD
- the deterministic VAN/TIR chain in `Expansion_Model` is built from USD operating flows
- no explicit FX conversion layer is applied in the workbook benchmark formulas used here

The reconciliation table still carries explicit unit and currency columns so that future workbook changes cannot silently create false comparability.

## 4. Workbook extraction logic

The Excel loader is intentionally not a generic ingestion framework.

Instead it uses an explicit extraction map with:

- required sheet validation
- required cell validation
- documented source sheet and source cell tracking
- workbook benchmark metadata

Notable extraction choices:

- raw capex inputs are read from `Market_Data`
- active benchmark capex values are read from `Sensitivity`
- sustaining capex is read from the expansion cash-flow block because that is where it is actually applied

This is important because the portfolio claim is not just "Python can read Excel." The stronger claim is that the migration is auditable and explicit about what data is actually driving the outputs.

## 5. Deterministic cash-flow design

The deterministic engine uses:

- payable copper pricing
- treatment and refining charges
- explicit operating cost per tonne
- explicit working-capital treatment
- explicit year 0 and year 1 capex timing
- discounted free cash flow
- NPV and IRR computed from explicit year-0-aware cash flows

### Tax logic

The model uses a simplified tax proxy aligned to the workbook cash-flow chain.

The workbook input sheet lists royalty and levy parameters, but the benchmark cash-flow chain that drives the reported VAN/TIR only applies the income tax rate inside the operating-flow construction. The Python rebuild therefore keeps those rates visible as extracted assumptions, but does not pretend to implement a fuller fiscal regime without a defensible workbook basis.

## 6. KPI interpretation

The annual and scenario marts are the core business-facing outputs.

### Annual KPI mart

`fact_annual_metrics.csv` is the main monitoring-style export. It contains:

- throughput
- copper production
- price and net price
- head grade
- recovery
- unit opex
- revenue
- EBITDA
- operating cash flow
- capex
- working capital
- free cash flow

### Executive scenario mart

`fact_scenario_kpis.csv` is the management summary layer. It contains:

- total revenue
- total EBITDA
- total opex
- total operating cash flow
- total free cash flow
- average throughput
- average copper production
- average unit opex
- average price, grade, and recovery
- EBITDA margin proxy
- NPV, IRR, and payback

This is the most useful table for business-facing dashboards.

## 7. Working-capital treatment

The repository uses two different working-capital treatments on purpose.

### Expanded project valuation

The project-level valuation uses a standard balance-delta approach with terminal release.

### Incremental benchmark reconciliation

The benchmark-aligned incremental profile follows the workbook convention instead of forcing a cleaner finance-textbook convention onto the reconciliation layer.

That choice is intentional. Reconciliation should match the benchmark's economic mechanics before claiming parity.

## 8. Stochastic model

The Monte Carlo engine has been upgraded relative to the earlier one-factor implementation.

### Price

Annual price realizations are simulated year by year around the workbook price deck using autocorrelated deck-centered lognormal shocks.

This choice is deliberate:

- the workbook already provides a year-by-year base price deck
- historical volatility is informative for dispersion
- historical drift is not treated as a reliable long-horizon structural forecast
- a modest AR(1)-style dependence is used so adjacent years are not unrealistically independent

### Grade

Grade uncertainty is modeled as a project-level multiplier rather than fully independent annual shocks.

### Recovery

Recovery uncertainty is modeled as bounded yearly variation around the base recovery path.

This keeps the stochastic layer useful for downside framing without pretending to be an engineering-grade process model.

## 9. Benchmark interpretation

`outputs/bi/benchmark_comparison.csv` should be read as an audit table, not as a marketing table.

It distinguishes:

- directly comparable metrics
- reference-only metrics
- explicit reasons for blocked comparison

At the current stage:

- deterministic incremental NPV and IRR are treated as directly comparable, but still flagged when the residual gap remains material
- Monte Carlo expected NPV, VaR, and CVaR are reference-only because the upgraded stochastic engine is not formula-identical to the workbook Monte Carlo and the valuation basis also differs

## 10. Remaining limitations

The platform remains simplified in several important ways:

- it is not a mine-plan optimization model
- it is not a live actual-vs-plan system
- it is not a full fiscal model
- it does not estimate a structural commodity-price process
- it does not claim workbook parity outside the explicitly reconciled benchmark scope
- scenario definitions remain stylized managerial stresses, not estimated probability-weighted forecasts
- the deterministic benchmark still shows a material residual gap, which indicates workbook logic not yet fully replicated

Those limitations are deliberate and should be stated plainly in any portfolio presentation.
