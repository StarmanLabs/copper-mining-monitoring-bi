# Monthly Refresh Runbook

This runbook describes the public-safe monthly refresh flow for the repository.

## Purpose

Use the refresh package when you want to answer four practical questions quickly:

1. Did the monthly refresh run?
2. What source files were used?
3. What validations passed or failed?
4. What KPI exceptions need management attention?

## Default Command

```bash
python scripts/run_local_profile.py --profile config/source_profiles/public_demo_profile.yaml --scope monthly
```

This uses:

- sample monthly inputs from `data/sample_data/monthly_monitoring/`
- the public-safe mapping config at `config/mappings/public_demo_identity_mapping.yaml`
- the default output folder `outputs/bi/`

Direct package-level fallback:

```bash
python scripts/build_refresh_package.py
```

## Optional Private Adaptation Pattern

A private user can point the same script at a different input directory and a different mapping config:

```bash
python scripts/run_local_profile.py --profile config/source_profiles/local/my_company_profile.yaml --scope monthly
```

That is the intended adaptation path.

## Refresh Sequence

1. confirm the latest source export files are present
2. run the mapping config against those exports
3. validate the mapped canonical monthly datasets
4. rebuild the monthly KPI summary plus the site, process-area, and cost-center marts
5. generate the data-quality, exception, and refresh outputs
6. refresh Power BI only after the work-core outputs look credible

## Output Review Order

Review the outputs in this order:

1. `outputs/bi/refresh_summary.json`
2. `outputs/bi/source_mapping_audit.csv`
3. `outputs/bi/data_quality_report.csv`
4. `outputs/bi/kpi_exceptions.csv`
5. `outputs/bi/kpi_monthly_summary.csv`

That order keeps the workflow practical.

## How To Read The Mapping Audit

Focus on:

- `source_file`
- `status`
- `missing_required_columns_after_mapping`
- `default_columns_applied`
- `unmapped_source_columns`

What good looks like:

- status = `ready_for_validation`
- no missing required columns after mapping
- only expected defaults applied

What should trigger a pause:

- missing required canonical fields
- unexpected unmapped source columns
- a mapping file that no longer matches the export layout

## How To Read The Data Quality Report

Core checks include:

- required columns present
- required values complete
- duplicate keys absent
- period values valid
- period sequence complete
- month fields consistent where derived month fields exist
- numeric ranges valid

Interpretation:

- `pass`: check is clean
- `fail`: the dataset needs investigation before trusting downstream outputs
- `not_applicable`: the check does not apply to that dataset shape

## How To Read The KPI Exceptions

The current business-facing exceptions are intentionally simple:

- major throughput shortfall
- major recovery underperformance
- major production shortfall
- unit cost deterioration

Use this output as a monthly management-control triage layer, not as a root-cause engine.

It tells you where to look first.

It does not replace operating analysis.

## Before Refreshing Power BI

Check:

- `refresh_summary.json` shows a successful refresh
- `data_quality_report.csv` has no failed core checks you would ignore in real work
- `kpi_exceptions.csv` looks business-plausible
- `kpi_monthly_summary.csv` includes the expected latest month
- the new drill marts (`mart_monthly_by_site.csv`, `mart_process_driver_summary.csv`, `mart_cost_center_summary.csv`) reflect the same latest month and site set

Only then move into the Power BI layer.

## Current Limitation

The refresh package is reusable and public-safe, but it is still file-based and batch-oriented.

That is appropriate for the repository's current scope.
