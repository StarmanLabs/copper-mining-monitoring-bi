# Annual Appendix Work Adaptation

This document explains the local/private adaptation pattern for the annual appendix layer.

The purpose is to let a private user transform annual planning, budget, commercial, or benchmark exports into canonical appendix inputs without changing core appendix code.

## Why This Layer Exists

The advanced appendix now runs from canonical annual inputs by default.

That creates a clear private adaptation path:

private annual exports  
-> mapping and validation  
-> canonical appendix tables  
-> appendix build  
-> local review or BI appendix page

This keeps the workbook in a secondary legacy/benchmark role.

## Canonical Annual Appendix Targets

The annual work-adaptation package produces these canonical tables:

- `annual_appendix_inputs.csv`
  Grain: one row per project year
  Purpose: core annual price, throughput, grade, recovery, unit-cost, and capex drivers
- `appendix_parameters.csv`
  Grain: one row per parameter name
  Purpose: scalar commercial, fiscal-proxy, ramp, and simulation parameters
- `appendix_scenarios.csv`
  Grain: one row per scenario
  Purpose: deterministic appendix scenario registry
- `appendix_benchmark_metrics.csv`
  Grain: one row per benchmark metric
  Purpose: benchmark transparency input for appendix comparisons

These tables are not a full mine-planning or finance system.

They are the minimum clean annual contract needed to run the appendix credibly.

## Mapping Templates

Use:

- `config/mappings/public_demo_annual_appendix_identity_mapping.yaml`
  public demo identity mapping
- `config/mappings/templates/example_company_annual_appendix_mapping.yaml`
  private adaptation template

The template supports:

- source file names
- source dataset labels
- column mapping into canonical fields
- default values
- simple value multipliers
- year normalization

That is intentionally the limit of the public-safe mapping layer.

## Default Public Demo Command

```bash
python scripts/run_local_profile.py --profile config/source_profiles/public_demo_profile.yaml --scope annual_appendix
```

This uses:

- sample annual inputs from `data/sample_data/annual_appendix/`
- the public-safe identity mapping
- the default output folder `outputs/bi/`

Direct package-level fallback:

```bash
python scripts/build_annual_appendix_work_package.py
```

## Private Local Command

```bash
python scripts/run_local_profile.py --profile config/source_profiles/local/my_company_profile.yaml --scope annual_appendix
```

That command is the intended local/private pattern. The runner will first canonicalize annual inputs and then, if the profile enables it, continue into the secondary advanced appendix build.

## Work Package Outputs

The annual work-adaptation package exports:

- `annual_appendix_dataset_catalog.csv`
- `annual_appendix_field_catalog.csv`
- `annual_appendix_inputs.csv`
- `appendix_parameters.csv`
- `appendix_scenarios.csv`
- `appendix_benchmark_metrics.csv`
- `annual_appendix_source_mapping_audit.csv`
- `annual_appendix_data_quality_report.csv`
- `annual_appendix_refresh_summary.json`

### Intended use of each output

- `annual_appendix_source_mapping_audit.csv`
  Shows which annual source files were used and whether they mapped cleanly.
- `annual_appendix_data_quality_report.csv`
  Shows required-column, missing-value, duplicate-key, year-sequence, numeric-range, and canonical-contract checks.
- `annual_appendix_refresh_summary.json`
  Provides a concise annual refresh readout.
- canonical CSVs
  Form the handoff boundary for the appendix builder.

## Output Review Order

Review these in order:

1. `annual_appendix_refresh_summary.json`
2. `annual_appendix_source_mapping_audit.csv`
3. `annual_appendix_data_quality_report.csv`
4. `annual_appendix_inputs.csv`
5. `appendix_parameters.csv`
6. `appendix_scenarios.csv`
7. `appendix_benchmark_metrics.csv`

Only then run the appendix report build.

## Appendix Build From Local Canonical Outputs

After the work package looks clean, rebuild the appendix from the local canonical annual folder:

```bash
python scripts/build_advanced_appendix_dataset.py --data-dir outputs/private/annual_appendix_canonical --benchmark-mode canonical --output-dir outputs/private/annual_appendix_report
```

That keeps the appendix builder connected to canonical tables rather than to raw private exports.

## What This Layer Does Not Claim

It does not claim:

- a full long-range mine-planning system
- a complete corporate-finance model
- confidential planning parity
- asset-grade scenario design

It is a practical annual adaptation layer for:

- scenario framing
- downside discussion
- benchmark transparency
- local continuation of the appendix

## Relationship To The Monthly Core

The monthly monitoring layer remains the main product story.

The annual appendix work-adaptation layer is useful when a private user wants to keep the appendix alive locally without dragging private raw exports directly into the public repo or into Power BI.
