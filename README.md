# Copper Mining Planning and Performance Analytics

This repository turns a copper expansion case plus governed monthly and annual sample tables into reproducible KPI marts for mining planning support, management control, BI, and decision support. Power BI is the first-class handoff path, with Tableau as a secondary consumption option. Valuation, Monte Carlo, and benchmark reconciliation remain in the repository as advanced appendix modules rather than as the main project identity.

This base v1.0 release is scoped as a stable public-safe baseline: monthly monitoring first, Power BI handoff ready, private adaptation practical, and advanced appendix modules kept secondary.

## What This Repository Is

- A mining planning and performance analytics portfolio project
- A reusable analytical core for KPI monitoring and BI consumption
- A stronger fit for economics + data + mining domain adaptation than for mine engineering or geology depth

## What It Is Not

- Not an Excel reconstruction project
- Not a valuation-only showcase
- Not a live plant, ERP, or telemetry integration
- Not a control-room dashboard platform

## Current Core Story

1. Monthly actual-vs-plan monitoring
   Sample/demo monthly datasets feed canonical validation, KPI variance logic, and BI-ready monitoring marts with site, process-area, and cost-center drill support.
2. Work-core reuse layer
   Config-driven source mapping, data quality reporting, KPI exceptions, source-profile templates, and refresh reporting make the monthly layer easier to adapt to real company exports.
3. BI-ready semantic layer
   The main outputs are CSV facts, marts, and dictionaries designed for Power BI or Tableau.
4. Planning and scenario context
   Annual KPI and scenario tables provide supporting planning context around the monthly management story.
5. Advanced appendix
   Valuation, Monte Carlo, tornado, heatmap, and benchmark reconciliation remain available as secondary analytical layers.
## Data Reality

- The current workbook source is `data/raw/Copper_mining_risk_model.xlsm`
- The monthly monitoring layer runs from sample/demo CSV inputs in `data/sample_data/monthly_monitoring/`
- The advanced appendix now runs by default from canonical annual sample/demo CSV inputs in `data/sample_data/annual_appendix/`
- The workbook remains available only as a legacy adapter and benchmark reference path for the appendix
- Monthly outputs are suitable for planning-style monitoring demos and BI prototyping
- Monthly outputs should not be presented as live operating actuals or ERP-connected reports

The honest claim is:

- planning/control/BI-ready architecture: yes
- sample/demo monthly actual-vs-plan monitoring: yes
- live monthly operational monitoring: not yet
- advanced valuation and downside appendix: yes

## What To Open First

If you are reviewing the project on GitHub, start with these files:

1. `README.md`
2. `docs/GETTING_STARTED.md`
3. `RELEASE_V1.md`
4. `powerbi/START_HERE.md`
5. `docs/MONTHLY_MONITORING_LAYER.md`
6. `docs/BI_USAGE.md`
7. `outputs/bi/kpi_monthly_summary.csv`
8. `outputs/bi/fact_monthly_actual_vs_plan.csv`
9. `outputs/bi/monthly_kpi_dictionary.csv`

## Main Output Families

### Monthly monitoring core

- `outputs/bi/dim_site.csv`
- `outputs/bi/dim_month.csv`
- `outputs/bi/kpi_monthly_summary.csv`
- `outputs/bi/fact_monthly_actual_vs_plan.csv`
- `outputs/bi/mart_monthly_executive_overview.csv`
- `outputs/bi/mart_monthly_process_performance.csv`
- `outputs/bi/mart_monthly_cost_margin.csv`
- `outputs/bi/mart_monthly_by_site.csv`
- `outputs/bi/mart_process_driver_summary.csv`
- `outputs/bi/mart_cost_center_summary.csv`
- `outputs/bi/dim_monthly_metric.csv`
- `outputs/bi/dim_process_area.csv`
- `outputs/bi/dim_cost_center.csv`
- `outputs/bi/monthly_kpi_dictionary.csv`
- `outputs/bi/monthly_dataset_catalog.csv`
- `outputs/bi/monthly_field_catalog.csv`

### Monthly work core

- `outputs/bi/source_mapping_audit.csv`
- `outputs/bi/data_quality_report.csv`
- `outputs/bi/kpi_exceptions.csv`
- `outputs/bi/refresh_summary.json`

### Power BI starter kit support

- `outputs/bi/dashboard_page_catalog.csv`
- `outputs/bi/powerbi_table_catalog.csv`
- `outputs/bi/powerbi_query_catalog.csv`
- `outputs/bi/powerbi_relationship_catalog.csv`
- `outputs/bi/powerbi_visual_binding_catalog.csv`
- `outputs/bi/powerbi_measure_catalog.csv`
- `outputs/bi/powerbi_sort_by_catalog.csv`
- `outputs/bi/powerbi_field_visibility_catalog.csv`

### Appendix context

- `outputs/bi/annual_appendix_dataset_catalog.csv`
- `outputs/bi/annual_appendix_field_catalog.csv`
- `outputs/bi/fact_annual_metrics.csv`
- `outputs/bi/fact_scenario_kpis.csv`
- `outputs/bi/appendix_kpi_catalog.csv`
- `outputs/bi/dim_year.csv`
- `outputs/bi/dim_metric.csv`
- `outputs/bi/dim_scenario.csv`

### Advanced appendix

- `outputs/bi/fact_simulation_distribution.csv`
- `outputs/bi/simulation_summary.csv`
- `outputs/bi/simulation_percentiles.csv`
- `outputs/bi/fact_tornado_sensitivity.csv`
- `outputs/bi/fact_heatmap_price_grade.csv`
- `outputs/bi/benchmark_comparison.csv`
- `outputs/bi/benchmark_scope_catalog.csv`
- `outputs/bi/advanced_appendix_assumption_catalog.csv`
- `outputs/bi/advanced_appendix_output_catalog.csv`

## Repository Flow

```text
legacy workbook adapter or future governed source
  -> validation
  -> canonical datasets
  -> monthly monitoring and KPI transforms
  -> BI-facing marts and dictionaries
  -> Power BI / Tableau semantic layer
  -> advanced valuation / risk appendix
```

## Repository Structure

```text
copper_minning_risk_model/
  config/                     Scenario and project configuration
  data/raw/                   Raw workbook input
  data/sample_data/           Public sample/demo monthly and annual appendix inputs
  docs/                       Focused project guidance
  outputs/bi/                 Main BI-ready marts and dictionaries
  powerbi/                    Power BI starter kit plus template and PBIP finalization scaffolds
  scripts/                    Build entrypoints and the unified local runner
  src/copper_risk_model/      Core analytical package
  tests/                      Analytical and pipeline validation
```

## Power BI Starter Kit

Use the tables in `outputs/bi/`.

Start with:

1. `powerbi/START_HERE.md`
2. `powerbi/TEMPLATE_LAYER.md`
3. `powerbi/pbip_tmdl_scaffold/README.md`
4. `powerbi/template_scaffold/README.md`
5. `powerbi/RELATIONSHIP_BLUEPRINT.md`
6. `powerbi/REPORT_BUILD_CHECKLIST.md`
7. `powerbi/PAGE_BUILD_GUIDE.md`
8. `powerbi/SLICER_AND_FILTER_GUIDE.md`
9. `powerbi/VISUAL_BINDING_CATALOG.csv`

Use these supporting assets:

- `powerbi/DASHBOARD_BLUEPRINT.md`
- `powerbi/DAX_MEASURES.md`
- `powerbi/pbip_tmdl_scaffold/`
- `powerbi/template_scaffold/`
- `outputs/bi/powerbi_table_catalog.csv`
- `outputs/bi/powerbi_query_catalog.csv`
- `outputs/bi/powerbi_relationship_catalog.csv`
- `outputs/bi/powerbi_visual_binding_catalog.csv`
- `outputs/bi/powerbi_measure_catalog.csv`
- `outputs/bi/powerbi_sort_by_catalog.csv`
- `outputs/bi/powerbi_field_visibility_catalog.csv`
- `outputs/bi/monthly_kpi_dictionary.csv`
- `powerbi/copper_risk_theme.json`

The monthly Power BI model uses shared `site` and `month` dimensions so the first four pages can be filtered coherently from one core slicer layer, and the PBIP/TMDL-oriented scaffold packages sort-by, hidden-field, relationship, and measure metadata in a more native-feeling continuation structure.

The Power BI scaffolds are now profile-aware at the package level: if a local profile disables the advanced appendix path, the current query catalogs, page manifests, and parameter manifests stay monthly-first and omit appendix assets from the active handoff. When a scaffold is regenerated over an older build in a constrained local environment, previously generated scaffold files outside the current package are marked obsolete in place rather than silently reused.

Recommended page order:

1. Executive Overview
2. Monthly Actual vs Plan
3. Process Performance
4. Cost and Margin
5. Advanced Scenario / Risk Appendix

For Tableau, keep separate subject-area sources instead of forcing every mart into one merged model. The secondary Tableau split is documented in `docs/BI_USAGE.md`.

## Public Demo vs Private Adaptation

Public version:

- keeps the raw workbook only as a legacy adapter / benchmark source
- uses sample/demo monthly CSV inputs
- uses sample/demo annual appendix CSV inputs
- includes `config/source_profiles/public_demo_profile.yaml` for the unified local runner
- avoids private company data and proprietary exports

Private adaptation path:

- replace sample monthly source tables with governed private plan, actual, plant, cost, and market datasets
- map private annual planning, parameter, scenario, and benchmark tables into canonical annual appendix inputs
- preserve canonical monthly schemas so the BI layer does not break
- preserve canonical annual appendix schemas so the secondary appendix remains source-agnostic
- keep workbook logic isolated as benchmark or transition logic
- keep private mappings, source profiles, raw exports, and local dashboard files in ignored local folders only
- use canonical outputs as the handoff boundary into Power BI

## Fastest Starting Paths

For portfolio / public demo review:

1. install dependencies with `python -m pip install -e .[dev]`
2. build the baseline with `python scripts/build_bi_dataset.py`
3. review `outputs/bi/` and `powerbi/START_HERE.md`
4. open `powerbi/pbip_tmdl_scaffold/` for the strongest Power BI continuation path

For private local adaptation:

1. copy `config/source_profiles/templates/example_private_company_profile.yaml` into an ignored local path such as `config/source_profiles/local/my_company_profile.yaml`
2. copy the mapping templates you need into ignored local mapping files
3. point the profile to your local raw export folders and output folders
4. prevalidate with `python scripts/run_local_profile.py --profile config/source_profiles/local/my_company_profile.yaml --validate-only`
5. run `--scope monthly` first, then `--scope all` only when the appendix path is really needed
6. regenerate the Power BI scaffold with the same profile so the output-root queries follow your local folders

## How To Run

Install dependencies:

```bash
python -m pip install -e .[dev]
```

Build BI outputs:

```bash
python scripts/build_bi_dataset.py
```

Run the unified public demo flow from one source profile:

```bash
python scripts/run_local_profile.py --profile config/source_profiles/public_demo_profile.yaml --scope all
```

Run only the monthly layer from one local/private profile:

```bash
python scripts/run_local_profile.py --profile config/source_profiles/local/my_company_profile.yaml --scope monthly
```

Run only the annual appendix continuation from one local/private profile:

```bash
python scripts/run_local_profile.py --profile config/source_profiles/local/my_company_profile.yaml --scope annual_appendix
```

Prevalidate a local/private profile before building outputs:

```bash
python scripts/run_local_profile.py --profile config/source_profiles/local/my_company_profile.yaml --validate-only
```

Regenerate only the Power BI template layer:

```bash
python scripts/build_powerbi_template_layer.py
```

Regenerate the Power BI template layer with output roots aligned to a local source profile:

```bash
python scripts/build_powerbi_template_layer.py --profile config/source_profiles/local/my_company_profile.yaml
```

Regenerate only the PBIP/TMDL-oriented scaffold:

```bash
python scripts/build_powerbi_native_scaffold.py
```

Regenerate the PBIP finalization package with output roots aligned to a local source profile:

```bash
python scripts/build_powerbi_native_scaffold.py --profile config/source_profiles/local/my_company_profile.yaml
```

Build the monthly monitoring layer only:

```bash
python scripts/build_monthly_monitoring_dataset.py
```

Build the monthly refresh support package:

```bash
python scripts/build_refresh_package.py
```

Build the annual appendix work-adaptation package:

```bash
python scripts/build_annual_appendix_work_package.py
```

Build only the advanced appendix from the canonical annual path:

```bash
python scripts/build_advanced_appendix_dataset.py
```

Build the appendix from the legacy workbook adapter and legacy benchmark path:

```bash
python scripts/build_advanced_appendix_dataset.py --input-mode legacy_workbook --benchmark-mode legacy_workbook
```

Run tests:

```bash
python -m pytest -q
```

## Documentation Map

- `RELEASE_V1.md`: concise v1 scope, included workflows, and intentional out-of-scope boundary
- `docs/GETTING_STARTED.md`: shortest public-review path and shortest private-adaptation path
- `docs/MONTHLY_MONITORING_LAYER.md`: monthly canonical schemas, marts, and validation rules
- `docs/WORK_ADAPTATION.md`: source mapping, private adaptation pattern, and public-safe reuse guidance
- `docs/PRIVATE_DEPLOYMENT_PATTERN.md`: what belongs in the public repo vs local/private usage only
- `docs/MONTHLY_REFRESH_RUNBOOK.md`: monthly refresh sequence, validation outputs, and exception interpretation
- `docs/ANNUAL_APPENDIX_WORK_ADAPTATION.md`: annual appendix mapping, validation, and local canonicalization pattern
- `docs/BI_USAGE.md`: Power BI-first handoff guidance with Tableau as a secondary path
- `docs/VALUATION_AND_RISK_APPENDIX.md`: advanced appendix scope, canonical annual inputs, legacy benchmark path, and limits
- `docs/PROJECT_STRUCTURE.md`: folder guide and archive boundaries
- `powerbi/START_HERE.md`: fastest Power BI build entrypoint
- `powerbi/TEMPLATE_LAYER.md`: query-first and PBIP/TMDL-oriented scaffold strategy
- `powerbi/RELATIONSHIP_BLUEPRINT.md`: recommended Power BI model
- `powerbi/REPORT_BUILD_CHECKLIST.md`: ordered build and refresh checklist
- `powerbi/PAGE_BUILD_GUIDE.md`: page-by-page report guidance

## Main Limitations

This repository is stronger as a planning, control, and BI project than as an engineering model.

It does not claim:

- live actual-vs-plan reporting from plant, ERP, or dispatch systems
- engineering-grade mine planning realism
- full workbook parity outside explicit benchmark outputs
- a full fiscal or corporate-finance model
- structural commodity-price forecasting

What it does claim honestly:

> A reproducible mining planning and performance analytics workflow with a sample/demo monthly actual-vs-plan layer, BI-ready KPI marts, scenario context, benchmark transparency, and advanced valuation / downside appendix outputs.

## Disclaimer

This is a public analytical portfolio project based on a hypothetical copper mining expansion case. It is not investment advice and should not substitute for geological, metallurgical, engineering, fiscal, financial, or operating due diligence.

