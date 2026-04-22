# Power BI Scaffold Layers

This repository now exposes two public-safe Power BI continuation layers.

Use them differently:

1. `powerbi/template_scaffold/`
   Fastest route from exported marts to a first working report.
2. `powerbi/pbip_tmdl_scaffold/`
   More native-feeling, source-control-friendly continuation path closer to PBIP/TMDL work.

## Artifact Strategy Chosen

The chosen strategy is now an honest PBIP finalization package, supported by a faster query-first fallback scaffold:

- keep `template_scaffold/` as the fastest first build path
- strengthen `pbip_tmdl_scaffold/` into the repository's strongest realistic Desktop continuation artifact
- do not pretend that the repo already contains a real Desktop-saved PBIP

Why this is the best fit:

- a real `.pbix` or `.pbit` cannot be generated honestly and reproducibly from this repository environment
- Microsoft positions PBIP and TMDL as text-based, source-control-friendly project formats
- the repository can realistically generate Power Query imports, TMDL apply scripts, relationship metadata, and page shells without pretending that Power BI Desktop already saved a finished native project

Relevant Microsoft references:

- [Power BI Desktop projects (PBIP)](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview)
- [Power BI Desktop project report folder](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report)
- [Work with TMDL view in Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-tmdl-view)
- [Tabular Model Definition Language (TMDL)](https://learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-overview?view=asallproducts-allversions)
- [TMDL scripts](https://learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-scripts?view=asallproducts-allversions)

## What Is Truly Native-Like

`powerbi/pbip_tmdl_scaffold/` includes:

- PBIP-style `SemanticModel` and `Report` folders
- reusable Power Query imports packaged inside the semantic-model scaffold
- separated output-root parameters for:
  - starter-kit references
  - monthly monitoring tables
  - secondary appendix tables
- TMDL apply scripts for:
  - model ordering
  - sort-by rules
  - hidden technical fields
  - core monthly measures
  - appendix measures
  - relationships
- source-control-friendly manifests and page-shell JSON files

This is the repository's strongest honest approximation of a native Power BI continuation package.

The scaffold stack is now profile-aware at the package level:

- if the selected local profile keeps the appendix enabled, the appendix queries, measures, and page shells stay in the package as a secondary layer
- if the selected local profile disables the appendix path, the current manifests omit appendix assets from the active continuation flow
- if the package is regenerated over an older scaffold in a constrained local environment, previously generated files outside the current package are explicitly marked as obsolete instead of being silently reused

## What Remains Scaffolded Or Manual

The repository still does not claim:

- a binary `.pbix`
- a binary `.pbit`
- a Power BI Desktop-authored PBIP already saved from a real semantic model

The following steps still require manual continuation in Power BI Desktop:

1. create or open a blank PBIX or PBIP
2. paste or recreate the Power Query assets
3. apply the TMDL scripts from TMDL view
4. lay out the report canvas from the page shells
5. save the local result as PBIP or PBIX

The new difference is that the package now tells the user more precisely what to change:

- `ProjectRoot`
- `StarterKitOutputRoot`
- `MonthlyOutputRoot`
- `AdvancedAppendixOutputRoot`

## Shortest Paths

If you want the fastest first report:

1. `powerbi/template_scaffold/README.md`
2. `powerbi/template_scaffold/model/powerbi_query_catalog.csv`
3. `powerbi/template_scaffold/measures/00_all_measures.dax`
4. `powerbi/template_scaffold/report/report_manifest.json`

If you want the more native continuation path:

1. `powerbi/pbip_tmdl_scaffold/README.md`
2. `powerbi/pbip_tmdl_scaffold/DESKTOP_FINALIZATION.md`
3. `powerbi/pbip_tmdl_scaffold/CopperMiningMonitoring.SemanticModel/README.md`
4. `powerbi/pbip_tmdl_scaffold/CopperMiningMonitoring.SemanticModel/TMDLScripts/`
5. `powerbi/pbip_tmdl_scaffold/CopperMiningMonitoring.Report/report_shell_manifest.json`

## Semantic Model Improvements In This Layer

The PBIP/TMDL-oriented scaffold now packages:

- shared monthly dimensions as the semantic center
- relationship logic aligned with the shared-dimension model
- display-folder-ready measure organization
- sort-by rules for `site`, `month`, `metric`, `process_area`, and `cost_center`
- hidden-column guidance for repeated keys and technical metadata
- page shells aligned to the monthly-first report story

## Business Narrative Rule

The intended page order remains:

1. Executive Overview
2. Monthly Actual vs Plan
3. Process Performance
4. Cost and Margin
5. Advanced Scenario / Risk Appendix

Pages 1 to 4 remain the main product story.

The appendix remains secondary.

## Regeneration

```bash
python scripts/build_bi_dataset.py
```

If you only want to rebuild the PBIP/TMDL-oriented scaffold:

```bash
python scripts/build_powerbi_native_scaffold.py
```

If you want the PBIP finalization package to follow a local runner profile:

```bash
python scripts/build_powerbi_native_scaffold.py --profile config/source_profiles/local/my_company_profile.yaml
```

The same profile-aware option is also available for the faster fallback scaffold:

```bash
python scripts/build_powerbi_template_layer.py --profile config/source_profiles/local/my_company_profile.yaml
```
