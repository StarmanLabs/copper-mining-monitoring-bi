# Portfolio Handoff Checklist

## Final Local Dashboard File

- save the final local dashboard as `copper_monitoring_dashboard_v1.pbix`
- keep the PBIX outside the public repo or in an ignored local folder unless you intentionally accept binary versioning tradeoffs

## Export Assets

- export a PDF if you want a static presentation artifact
- capture these five screenshots from the finalized PBIX:
  - `Executive Overview`
  - `Monthly Actual vs Plan`
  - `Process Performance`
  - `Cost & Margin`
  - `Scenario / Risk Appendix`
- copy the screenshots into `docs/assets/powerbi/` with these exact filenames:
  - `executive_overview.png`
  - `monthly_actual_vs_plan.png`
  - `process_performance.png`
  - `cost_margin.png`
  - `scenario_risk_appendix.png`

## Repository Checks

- verify that `README.md` renders correctly on GitHub
- verify that `docs/dashboard/POWER_BI_DASHBOARD.md` reflects the actual final page story
- verify that screenshots are public-safe and contain no private bookmarks, local machine paths, or internal metadata

## Reproducibility Checks

Run:

```bash
python -m pytest -q
python scripts/build_bi_dataset.py
python scripts/run_local_profile.py --profile config/source_profiles/public_demo_profile.yaml --scope all
```

## Final Git Hygiene

- run `git status`
- confirm there are no private files staged
- confirm no local-only profiles or mappings appear in the diff
- confirm no `.pbix` file is staged unless you intentionally want to version it

## Suggested Commit Message

```text
Package Power BI dashboard portfolio handoff for v1
```

## Suggested GitHub Repository Description

```text
Public-safe mining performance monitoring with Python-generated KPI marts, monthly actual-vs-plan control, and Power BI dashboard handoff.
```

## Suggested GitHub Topics

- `mining-analytics`
- `powerbi`
- `business-intelligence`
- `monthly-monitoring`
- `management-control`
- `planning-analytics`
- `kpi-monitoring`
- `python`
- `decision-support`
- `scenario-analysis`

## Suggested LinkedIn Post Draft

```text
I just packaged a public-safe mining analytics portfolio project that combines Python data pipelines with a Power BI dashboard for copper performance monitoring.

The project focuses on monthly actual-vs-plan control, KPI alerting, operational driver analysis, cost and margin pressure review, and a secondary scenario/risk appendix.

The repository is designed as a reproducible workflow rather than just a dashboard file:

- Python pipeline for canonical monthly and annual demo datasets
- BI-ready CSV marts and semantic support catalogs
- Power BI starter kit plus PBIP/TMDL-oriented continuation scaffold
- Public-safe/private adaptation pattern for future real-work reuse

It is positioned as a mining planning, management-control, and BI handoff project first. The scenario/risk appendix remains secondary to the monthly monitoring story.

Repository:
https://github.com/StarmanLabs/copper-mining-monitoring-bi
```
