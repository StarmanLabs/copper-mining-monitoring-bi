# Valuation And Risk Appendix

This document covers the advanced appendix modules of the repository. These outputs are intentionally secondary to the monthly monitoring and BI story.

## Role In The Repository

The advanced appendix adds technical depth through:

- deterministic scenario comparison
- project-level NPV and IRR
- Monte Carlo downside analysis
- tornado sensitivity
- price-grade stress testing
- benchmark reconciliation

These modules strengthen decision-support credibility, but they are not the main reason the repository exists.

## Appendix Module Boundary

The appendix is packaged as an explicit secondary layer:

- `src/copper_risk_model/annual_appendix_inputs.py`
  Canonical annual appendix contracts, validation, and loader logic
- `src/copper_risk_model/valuation_model.py`
  Deterministic valuation engine
- `src/copper_risk_model/scenario_analysis.py`
  Deterministic scenario and stress helpers
- `src/copper_risk_model/simulation.py`
  Monte Carlo downside helpers
- `src/copper_risk_model/benchmark_reconciliation.py`
  Benchmark transparency and comparability logic
- `src/copper_risk_model/advanced_appendix.py`
  Builder that exports only the appendix outputs and transparency catalogs

The main BI builder can still generate these files, but the appendix also has a dedicated entrypoint:

- `python scripts/build_advanced_appendix_dataset.py`

## Default Input Path

The appendix is no longer workbook-defined by default.

The default path is now:

- canonical annual appendix tables in `data/sample_data/annual_appendix/`
- validated parameter and scenario tables
- benchmark metadata loaded from an explicit benchmark table

Core canonical inputs:

- `annual_appendix_inputs.csv`
  annual price, throughput, grade, recovery, unit-cost, and capex drivers
- `appendix_parameters.csv`
  scalar commercial, fiscal-proxy, ramp, and simulation parameters
- `appendix_scenarios.csv`
  deterministic appendix scenario registry
- `appendix_benchmark_metrics.csv`
  benchmark reference points kept explicit and auditable

This keeps the appendix source-agnostic and easier to adapt privately later.

For local/private adaptation, the intended pre-build step is now:

- `python scripts/build_annual_appendix_work_package.py`

That work package maps and validates private annual exports before the appendix builder consumes canonical annual tables.

## Legacy Workbook Path

The workbook is still supported, but only as:

- a legacy adapter for annual appendix inputs
- a benchmark reference source
- a transitional compatibility path

Recommended default:

```bash
python scripts/build_advanced_appendix_dataset.py
```

Explicit legacy path:

```bash
python scripts/build_advanced_appendix_dataset.py --input-mode legacy_workbook --benchmark-mode legacy_workbook
```

That distinction matters because the workbook should no longer define the architecture of the appendix.

## Current Data Reality

The public appendix now uses repository-governed annual tables, not workbook-native structures, as its main path.

That means:

- deterministic valuation can run from canonical annual tables
- scenario outputs can run from canonical annual tables
- Monte Carlo downside can run from canonical annual tables
- benchmark outputs can still reference the legacy workbook when needed

The appendix should still be described as:

- planning-style scenario and downside support
- benchmark-transparent analytical appendix
- public-safe decision-support layer

It should not be described as:

- a full mine-planning system
- a complete fiscal model
- an asset-grade valuation platform

## Appendix Governance Outputs

Use these files to understand the appendix input contract before touching the model logic:

- `outputs/bi/annual_appendix_dataset_catalog.csv`
  documents the annual appendix source tables
- `outputs/bi/annual_appendix_field_catalog.csv`
  documents field meaning, units, and required flags
- `outputs/bi/advanced_appendix_assumption_catalog.csv`
  makes assumption sources and simplifications explicit
- `outputs/bi/advanced_appendix_output_catalog.csv`
  explains what each appendix output is for and why it remains secondary

## Benchmark Interpretation

`outputs/bi/benchmark_comparison.csv` is an audit table, not a marketing table.

Use it to distinguish:

- canonical appendix outputs
- benchmark-backed comparisons
- direct comparison vs reference-only comparison
- explicit reasons why some comparisons are blocked

Use these companion transparency files as well:

- `outputs/bi/benchmark_scope_catalog.csv`
  explains why a metric is a direct comparison or only a reference point
- `outputs/bi/advanced_appendix_assumption_catalog.csv`
  makes appendix assumptions and simplifications explicit
- `outputs/bi/advanced_appendix_output_catalog.csv`
  explains what each appendix output is for and why it remains secondary
- `outputs/bi/appendix_kpi_catalog.csv`
  documents the KPI semantics used by `fact_scenario_kpis.csv`

## Suggested Review Order

If you are reviewing the appendix after the monthly story, open:

1. `outputs/bi/annual_appendix_dataset_catalog.csv`
2. `outputs/bi/fact_scenario_kpis.csv`
3. `outputs/bi/simulation_summary.csv`
4. `outputs/bi/fact_tornado_sensitivity.csv`
5. `outputs/bi/fact_heatmap_price_grade.csv`
6. `outputs/bi/benchmark_comparison.csv`
7. `outputs/bi/benchmark_scope_catalog.csv`
8. `outputs/bi/advanced_appendix_assumption_catalog.csv`

That order keeps the appendix useful without letting it dominate the repository narrative.

## Main Limitations

The advanced appendix does not claim:

- full workbook parity outside explicit benchmark outputs
- live mine monitoring
- mine-plan optimization
- structural commodity-price forecasting
- a complete fiscal regime
- a full corporate-finance model

The canonical annual path improves architecture and reuse, but it does not change those modeling limits.

## Recommended Use In Presentation

Use the appendix after the monthly monitoring and BI story has already been established.

Good sequence:

1. monthly executive monitoring
2. monthly actual vs plan
3. process and cost review
4. scenario planning context
5. advanced appendix

That sequence keeps the repository aligned with planning, management control, BI, and decision-support roles.
