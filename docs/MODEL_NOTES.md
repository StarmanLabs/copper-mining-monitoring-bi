# Model Notes

## Purpose

This note documents what the Python model is doing, what the workbook benchmark represents, and where the analytical engine is intentionally simplified.

## 1. Model scope

The repository contains two related but distinct valuation views:

### Expanded project view

This is the main Python valuation used for:

- deterministic scenario comparison
- BI KPI tables
- tornado sensitivity
- price-grade heatmaps
- dashboard storytelling

It represents the expanded operating case as a project-level valuation in USD.

### Incremental expansion view

This is used only for benchmark reconciliation against the workbook.

It represents the incremental free cash flow created by the expansion relative to the pre-expansion operating case.

This distinction matters. The workbook benchmark is not a direct benchmark for the project-level Python NPV used in the dashboard.

## 2. Currency and units

The active Python engine reports monetary outputs in USD.

The workbook benchmark values used in reconciliation are also treated as USD because:

- the workbook operating and price inputs are labeled in USD
- the deterministic VAN/TIR chain in `Expansion_Model` is built from USD operating flows
- no explicit FX conversion layer is applied in the workbook benchmark formulas used here

The reconciliation table still carries explicit unit and currency columns so that future workbook changes cannot silently create false comparability.

## 3. Workbook extraction logic

The Excel loader is intentionally not a generic ingestion framework.

Instead it now uses an explicit extraction map with:

- required sheet validation
- required cell validation
- documented source sheet and source cell tracking
- workbook benchmark metadata

Notable extraction choices:

- raw capex inputs are read from `Market_Data`
- active benchmark capex values are read from `Sensitivity`
- sustaining capex is read from the expansion cash-flow block because that is where it is actually applied

This prevents a common failure mode in spreadsheet migration projects: comparing Python outputs against workbook values that are not actually the workbook values driving the reported benchmark.

## 4. Deterministic cash-flow design

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

## 5. Working-capital treatment

The repository now uses two different working-capital treatments on purpose:

### Expanded project valuation

The project-level valuation uses a standard balance-delta approach with terminal release.

### Incremental benchmark reconciliation

The benchmark-aligned incremental profile follows the workbook convention instead of forcing a cleaner finance textbook convention onto the reconciliation layer.

That choice is intentional. Reconciliation should match the benchmark's economic mechanics before claiming parity.

## 6. Stochastic model

The Monte Carlo engine has been upgraded relative to the earlier one-factor implementation.

### Price

Annual price realizations are now simulated year by year around the workbook price deck using deck-centered lognormal shocks.

This is a deliberate modeling choice:

- the workbook already provides a year-by-year base price deck
- historical volatility is informative for dispersion
- historical drift is not treated as a reliable 15-year structural forecast

That keeps the simulation dynamic without embedding an unjustified long-run bull case.

### Grade

Grade uncertainty is modeled as a project-level multiplier rather than fully independent annual shocks.

This is more defensible with the available data because the workbook and empirical inputs support level uncertainty and long-run depletion logic more clearly than year-specific geological noise.

### Recovery

Recovery uncertainty is modeled as bounded yearly variation around the base recovery path.

This is reasonable because plant performance can vary from year to year even when the broader project remains the same.

## 7. Benchmark interpretation

`outputs/bi/benchmark_comparison.csv` should be read as an audit table, not as a marketing table.

It now distinguishes:

- directly comparable metrics
- reference-only metrics
- explicit reasons for blocked comparison

At the current stage:

- deterministic incremental NPV and IRR are treated as comparable
- Monte Carlo expected NPV, VaR, and CVaR are reference-only because the upgraded stochastic engine is not formula-identical to the workbook Monte Carlo and the valuation basis also differs

## 8. Remaining limitations

The model remains simplified in several important ways:

- it is not a mine-plan model
- it is not a full fiscal model
- it does not estimate a structural commodity-price process
- it does not claim workbook formula parity outside the explicitly reconciled benchmark scope
- scenario definitions remain stylized managerial stresses, not estimated probability-weighted forecasts

Those limitations are deliberate and should be stated plainly in any portfolio presentation.
