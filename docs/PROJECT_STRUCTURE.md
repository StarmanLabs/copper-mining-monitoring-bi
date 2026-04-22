# Project Structure

## Folder Guide

- `config/`
  Project configuration, source-mapping templates, source-profile templates, scenario assumptions, and the workbook path.
- `data/raw/`
  Raw workbook input.
- `data/sample_data/`
  Sample/demo monthly monitoring inputs plus canonical annual appendix inputs used by the workbook-independent platform paths.
- `src/copper_risk_model/`
  Core analytical package: validation, canonical monthly monitoring, BI export, scenarios, simulation, and secondary risk modules.
- `scripts/`
  Build entrypoints for BI exports, work-adaptation packages, Power BI scaffolds, and the unified local runner.
- `outputs/bi/`
  Main BI-ready marts, dictionaries, and semantic catalogs for Power BI and Tableau.
- `powerbi/`
  Power BI starter kit, theme, page blueprint, template scaffold, PBIP finalization package, and visual bindings.
- `tests/`
  Analytical, schema, and smoke tests.
- `.github/workflows/`
  CI pipeline.

## Best Entry Points

- `README.md`
  Public-facing overview and repo positioning.
- `docs/GETTING_STARTED.md`
  Shortest path for public portfolio review and shortest path for local private adaptation.
- `RELEASE_V1.md`
  Concise stable-base release marker, scope summary, and out-of-scope boundary.
- `docs/MONTHLY_MONITORING_LAYER.md`
  Canonical monthly schemas, validation rules, marts, and limitations.
- `docs/BI_USAGE.md`
  Power BI-first handoff guidance with Tableau as a secondary path.
- `docs/WORK_ADAPTATION.md`
  Public-safe mapping, data quality, and private adaptation guidance.
- `docs/PRIVATE_DEPLOYMENT_PATTERN.md`
  Public/private boundary, do-not-commit guidance, and local folder pattern.
- `docs/MONTHLY_REFRESH_RUNBOOK.md`
  Monthly refresh sequence and work-core output interpretation.
- `docs/ANNUAL_APPENDIX_WORK_ADAPTATION.md`
  Annual appendix mapping, validation, and local canonicalization guidance.
- `powerbi/START_HERE.md`
  Fastest Power BI starter-kit entrypoint.
- `powerbi/REPORT_BUILD_CHECKLIST.md`
  Ordered build, refresh, and validation checklist for the report.
- `docs/VALUATION_AND_RISK_APPENDIX.md`
  Advanced appendix scope, benchmark basis, and limits.
- `outputs/bi/dashboard_page_catalog.csv`
  Semantic page map for the BI story.
- `outputs/bi/powerbi_relationship_catalog.csv`
  Recommended Power BI relationships.
- `outputs/bi/powerbi_visual_binding_catalog.csv`
  Visual-by-visual report binding catalog.
- `outputs/bi/monthly_kpi_dictionary.csv`
  Monthly KPI meaning, units, proxy status, and page usage.
- `outputs/bi/kpi_monthly_summary.csv`
  Main monthly actual-vs-plan monitoring mart.
- `outputs/bi/fact_monthly_actual_vs_plan.csv`
  Long monthly variance fact table.
- `outputs/bi/source_mapping_audit.csv`
  Mapping audit showing which source files fed the monthly refresh.
- `outputs/bi/data_quality_report.csv`
  Data-quality checks for monthly source datasets and the KPI summary.
- `outputs/bi/kpi_exceptions.csv`
  Business-facing monthly KPI exception triage output.
- `outputs/bi/refresh_summary.json`
  Concise refresh status summary for work-core review.
- `outputs/bi/benchmark_comparison.csv`
  Audit-style reconciliation table.
- `outputs/bi/benchmark_scope_catalog.csv`
  Explanation of direct-vs-reference-only benchmark comparability.
- `outputs/bi/annual_appendix_dataset_catalog.csv`
  Dataset-level contract for the canonical annual appendix input path.
- `outputs/bi/annual_appendix_field_catalog.csv`
  Field-level contract for the canonical annual appendix input path.
- `outputs/bi/advanced_appendix_assumption_catalog.csv`
  Public-safe assumption register for the appendix.
- `outputs/bi/advanced_appendix_output_catalog.csv`
  Guide to what each appendix output answers and why it remains secondary.

## Build Scripts

- `build_bi_dataset.py`
  Generates the BI-ready marts and semantic catalogs.
- `build_monthly_monitoring_dataset.py`
  Generates the monthly monitoring layer without requiring the workbook.
- `build_refresh_package.py`
  Generates the monthly refresh support package, including mapping audit, data quality, and KPI exceptions.
- `build_annual_appendix_work_package.py`
  Generates the annual appendix work-adaptation package, including canonical annual inputs, mapping audit, and data quality outputs.
- `build_advanced_appendix_dataset.py`
  Generates only the advanced valuation, downside, and benchmark appendix layer, defaulting to the canonical annual input path.
- `build_powerbi_template_layer.py`
  Generates the query-first Power BI finalization scaffold.
- `build_powerbi_native_scaffold.py`
  Generates the PBIP/TMDL-oriented Power BI finalization scaffold.
- `run_local_profile.py`
  Runs monthly work-core, annual appendix adaptation, or both from one source profile.

## Files to Leave Alone

- `data/raw/Copper_mining_risk_model.xlsm`
  Raw workbook input.
- `config/project.yaml`
  Project paths and scenario configuration.
