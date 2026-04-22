# Work Adaptation

This repository includes a public-safe work adaptation pattern for two reusable layers:

- monthly monitoring
- annual appendix inputs

The goal is not to mimic a private enterprise stack.

The goal is to make the repository easier to adapt locally when a user later has real company exports from planning, plant, cost-control, commercial, budget, or market-deck workflows.

## What The Work Adaptation Layer Adds

- config-driven mapping templates
- source-profile templates for local/private usage
- mapping audit outputs
- data quality outputs
- repeatable local build commands

These additions remain behind the same repo story:

- monthly monitoring first
- Power BI first
- advanced appendix second

## Public-Safe Boundary

The repository still does not include:

- company data
- private connectors
- internal file paths
- ERP credentials
- local dashboard binaries
- organization-specific source logic

Public-safe examples are included only as templates:

- `config/mappings/public_demo_identity_mapping.yaml`
- `config/mappings/public_demo_annual_appendix_identity_mapping.yaml`
- `config/mappings/templates/`
- `config/source_profiles/templates/`

## Local/Private Pattern

The intended local pattern is:

1. keep raw exports outside Git or in ignored local folders only
2. copy mapping templates into ignored local config folders
3. map private exports into canonical monthly or annual appendix tables
4. validate those canonical tables locally
5. point Power BI or the appendix builder to canonical outputs, not to private raw exports

That separation matters because the canonical outputs are the reusable handoff boundary.

## Recommended Local-Only Folders

These locations are now part of the intended local pattern and are ignored by Git:

- `data/private/`
- `config/source_profiles/local/`
- `config/mappings/local/`
- `outputs/private/`
- `powerbi/local/`

Binary local dashboard files are also ignored:

- `*.pbix`
- `*.pbit`
- `*.twb`
- `*.twbx`

## Monthly Monitoring Adaptation

Use these files first:

1. `config/mappings/templates/example_company_mapping.yaml`
2. `config/source_profiles/templates/example_private_company_profile.yaml`
3. `docs/MONTHLY_REFRESH_RUNBOOK.md`

Core monthly target datasets remain:

- `plan_monthly`
- `actual_production_monthly`
- `plant_performance_monthly`
- `cost_actuals_monthly`
- `market_prices_monthly`
- `process_driver_monthly`
- `cost_center_monthly`

If private users can map their exports into those schemas, the monthly BI layer usually remains stable.

## Annual Appendix Adaptation

Use these files:

1. `config/mappings/templates/example_company_annual_appendix_mapping.yaml`
2. `config/source_profiles/templates/example_private_company_profile.yaml`
3. `docs/ANNUAL_APPENDIX_WORK_ADAPTATION.md`

Canonical annual appendix targets remain:

- `annual_appendix_inputs.csv`
- `appendix_parameters.csv`
- `appendix_scenarios.csv`
- `appendix_benchmark_metrics.csv`

Those canonical tables are the intended input boundary for:

- `python scripts/build_advanced_appendix_dataset.py`

## Shortest Practical Local Flow

Preferred path from one source profile:

```bash
python scripts/run_local_profile.py --profile config/source_profiles/local/my_company_profile.yaml --scope all
```

Monthly only:

```bash
python scripts/run_local_profile.py --profile config/source_profiles/local/my_company_profile.yaml --scope monthly
```

Annual appendix only:

```bash
python scripts/run_local_profile.py --profile config/source_profiles/local/my_company_profile.yaml --scope annual_appendix
```

Profile validation before running anything:

```bash
python scripts/run_local_profile.py --profile config/source_profiles/local/my_company_profile.yaml --validate-only
```

Low-level monthly entrypoint if you want to run that package directly:

```bash
python scripts/build_refresh_package.py --data-dir data/private/monthly_exports --mapping-config config/mappings/local/monthly_private_mapping.yaml --output-dir outputs/private/monthly_work_core
```

Low-level annual appendix canonicalization entrypoint:

```bash
python scripts/build_annual_appendix_work_package.py --data-dir data/private/annual_appendix_exports --mapping-config config/mappings/local/annual_appendix_private_mapping.yaml --output-dir outputs/private/annual_appendix_canonical
```

Low-level appendix rebuild from local canonical annual outputs:

```bash
python scripts/build_advanced_appendix_dataset.py --data-dir outputs/private/annual_appendix_canonical --benchmark-mode canonical --output-dir outputs/private/annual_appendix_report
```

## Power BI Boundary

Power BI should consume:

- public-safe outputs under `outputs/bi/`
- or ignored local canonical outputs under `outputs/private/`

Power BI should not connect directly to:

- private raw exports
- local budget extracts
- local scenario workbooks

That keeps the BI layer cleaner and easier to migrate between public demo and local/private work.

## Recommended Review Order In Local Work

1. mapping audit
2. data quality report
3. canonical outputs
4. KPI or appendix outputs
5. Power BI refresh

If the mapped canonical layer is weak, the BI layer will not be trustworthy.

## Related Docs

- `docs/PRIVATE_DEPLOYMENT_PATTERN.md`
- `docs/MONTHLY_REFRESH_RUNBOOK.md`
- `docs/ANNUAL_APPENDIX_WORK_ADAPTATION.md`
- `docs/VALUATION_AND_RISK_APPENDIX.md`
