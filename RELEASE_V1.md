# Base Release v1.0.0

This file marks the stable base release of the repository.

The intent of v1 is not to introduce more architecture. The intent is to freeze a clean public-safe baseline that is easy to review, rerun, adapt locally, and extend later without changing the repository's identity.

## What v1 Includes

- monthly actual-vs-plan monitoring as the main business story
- shared dimensions and BI-ready monthly marts
- monthly work-core adaptation with mapping audit, data quality, KPI exceptions, and refresh summary outputs
- annual appendix adaptation that builds canonical annual tables before the advanced appendix
- advanced appendix outputs kept as a secondary analytical layer
- Power BI starter-kit assets plus a PBIP/TMDL-oriented finalization package
- a manually finalized local Power BI dashboard story with five pages:
  - Executive Overview
  - Monthly Actual vs Plan
  - Process Performance
  - Cost & Margin
  - Scenario / Risk Appendix
- a unified local runner driven by source profiles
- public/private adaptation templates and ignored local-only patterns

## What v1 Intentionally Does Not Claim

- live plant, ERP, historian, or telemetry integration
- company-specific data, connectors, or private dashboard binaries
- a Power BI Desktop-saved PBIP or PBIX stored in the public repo
- cloud orchestration or enterprise deployment infrastructure
- engineering-grade mine planning realism or full corporate-finance depth

## Dashboard v1 Scope

Dashboard v1 is meant to read as a reproducible mining monitoring product rather than as a standalone `.pbix` artifact.

What is included:

- Python dataset generation
- BI-ready monthly marts
- Power BI semantic support catalogs
- public-safe documentation for the final five-page dashboard story
- PBIP/TMDL-oriented starter assets for continuation in Desktop

What remains manual in Power BI Desktop:

- final visual layout
- final formatting choices
- screenshot capture
- PBIX save/export

What is intentionally excluded:

- private data
- private local outputs
- a versioned public PBIX binary inside the repo
- any claim that the repo auto-generated the finished report canvas end to end

## Recommended Review Path

1. `README.md`
2. `powerbi/START_HERE.md`
3. `docs/MONTHLY_MONITORING_LAYER.md`
4. `docs/WORK_ADAPTATION.md`
5. `docs/BI_USAGE.md`
6. `outputs/bi/kpi_monthly_summary.csv`
7. `outputs/bi/fact_monthly_actual_vs_plan.csv`

## Stable Workflows In Scope

```bash
python scripts/build_bi_dataset.py
python scripts/build_monthly_monitoring_dataset.py
python scripts/run_local_profile.py --profile config/source_profiles/public_demo_profile.yaml --scope all
python scripts/build_powerbi_native_scaffold.py
python -m pytest -q
```

## Release Boundary

v1 should read as a mining planning, management-control, KPI monitoring, and BI handoff repository.

It should not read as a workbook reconstruction project, a pure valuation repository, or an enterprise product claim.
