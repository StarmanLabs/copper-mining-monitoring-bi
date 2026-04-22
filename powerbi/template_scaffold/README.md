# Power BI Template Scaffold

This folder is the repository's fastest honest Power BI Desktop finalization package.

What this scaffold gives you:

- ready-to-paste Power Query imports for each exported mart, fact, and dimension
- separate output-root parameters for starter-kit references, monthly marts, and the secondary appendix
- shared monthly dimensions for site, month, process area, and cost center
- DAX measure bundles grouped by the report page order
- copied model and report catalogs for relationships, page order, visual intent, sort-by, and technical-field visibility
- a portable theme file for the starter report
- a parameter manifest that tells you exactly what still must be changed in Desktop

Use it like this:

1. Run `python scripts/build_bi_dataset.py` for the public demo baseline.
2. If you want local-runner-compatible defaults, rebuild with `python scripts/build_powerbi_template_layer.py --profile config/source_profiles/local/my_company_profile.yaml`.
3. In Power BI Desktop create a blank report.
4. Add the queries from `parameters/`:
   - `ProjectRoot.pq`
   - `StarterKitOutputRoot.pq`
   - `MonthlyOutputRoot.pq`
   - `AdvancedAppendixOutputRoot.pq`
5. Replace the placeholder in `ProjectRoot` and change only the output-root queries that need to follow your local runner outputs.
6. Import the `.pq` files from `queries/` in query order.
7. Disable load for any query marked `disable_load_after_import` in `model/powerbi_query_catalog.csv`.
8. Create relationships from `model/powerbi_relationship_catalog.csv`, starting with `dim_site` and `dim_month` as the monthly semantic center.
9. Paste the DAX bundles from `measures/`.
10. Apply sort-by and hidden-column cleanup from `model/powerbi_sort_by_catalog.csv` and `model/powerbi_field_visibility_catalog.csv`.
11. Build pages in the order described in `report/dashboard_page_catalog.csv` and `report/report_manifest.json`.

This scaffold is intentionally public-safe:

- it uses only repository exports
- it does not contain company connections
- it does not claim live ERP, plant, or telemetry integration
- it is a finalization package, not a fake Desktop-saved `.pbip`

Profile defaults:

- starter-kit references default to `outputs/bi`
- monthly queries default to `outputs/bi`
- appendix queries default to `outputs/bi`

Current report order:

1. Executive Overview
2. Monthly Actual vs Plan
3. Process Performance
4. Cost and Margin
5. Advanced Scenario / Risk Appendix

It is near plug-and-play rather than a binary `.pbit`.

If you want the more native-feeling continuation path, use `powerbi/pbip_tmdl_scaffold/` after running the BI build.
