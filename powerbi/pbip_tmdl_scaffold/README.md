# PBIP Finalization Package

This folder is the repository's strongest honest public-safe Power BI Desktop continuation package.

What it is:

- a PBIP-style folder structure with separate SemanticModel and Report folders
- reusable Power Query imports grouped by starter-kit references, monthly marts, and secondary appendix tables only when the selected profile keeps the appendix active
- output-root parameters that can follow either the public demo build or a unified local profile
- TMDL apply scripts for model ordering, measure bundles, relationships, sort-by rules, and hidden technical fields
- page-shell JSON files that preserve the intended report narrative and visual intent
- Desktop finalization manifests that explain what is already packaged and what still remains manual

What it is not:

- not a binary `.pbix`
- not a binary `.pbit`
- not a Power BI Desktop-authored PBIP already saved from a finished semantic model

Use this package when you want the repository handoff to feel as close as honestly possible to native PBIP continuation without pretending the final Desktop save already exists.

Recommended path:

1. Run `python scripts/build_bi_dataset.py` for the public-safe baseline.
2. If you want local-runner-aware defaults, rebuild with `python scripts/build_powerbi_native_scaffold.py --profile config/source_profiles/local/my_company_profile.yaml`.
3. Read `DESKTOP_FINALIZATION.md`.
4. Open `CopperMiningMonitoring.SemanticModel/README.md`.
5. Import the Power Query assets from `CopperMiningMonitoring.SemanticModel/PowerQuery/`.
6. Apply the TMDL scripts in `CopperMiningMonitoring.SemanticModel/TMDLScripts/`.
7. Build the report canvas from `CopperMiningMonitoring.Report/page_shells/`.
8. Save your local file as PBIP or PBIX from Power BI Desktop.

This scaffold keeps the monthly business story first:

1. Executive Overview
2. Monthly Actual vs Plan
3. Process Performance
4. Cost and Margin
5. Advanced Scenario / Risk Appendix

Profile defaults:

- starter-kit references default to `outputs/bi`
- monthly queries default to `outputs/bi`
- appendix queries default to `outputs/bi`
