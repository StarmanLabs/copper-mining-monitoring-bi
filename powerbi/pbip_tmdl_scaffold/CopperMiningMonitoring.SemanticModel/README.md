# Semantic Model Scaffold

This folder is the semantic-model continuation layer for the public-safe Power BI handoff.

Recommended build sequence in Power BI Desktop:

1. Create a blank PBIX or PBIP.
2. Add these parameter queries from `PowerQuery/parameters/`:
   - `ProjectRoot.pq`
   - `StarterKitOutputRoot.pq`
   - `MonthlyOutputRoot.pq`
   - `AdvancedAppendixOutputRoot.pq`
3. Replace the placeholder in `ProjectRoot` and change only the output-root queries that need to follow your local runner folders.
4. Import the `.pq` queries from `PowerQuery/queries/` in query order.
5. Apply the TMDL scripts from `TMDLScripts/` in this order:
   - `00_model_ordering.tmdl`
   - `01_sort_and_visibility.tmdl`
   - `02_core_monthly_measures.tmdl`
   - `03_advanced_appendix_measures.tmdl`
   - `04_relationships.tmdl`
6. Check `catalogs/powerbi_sort_by_catalog.csv` and `catalogs/powerbi_field_visibility_catalog.csv` for any manual cleanup that still makes sense in your adapted model.
7. Verify that `dim_site` and `dim_month` remain the shared monthly filter center.
8. Save the result as PBIP if you want a fully source-control-friendly local continuation.

This scaffold is intentionally generic:

- no private connectors
- no internal company tables
- no proprietary mappings
- no hidden enterprise model claims

Current default output roots:

- starter-kit references: `outputs/bi`
- monthly model tables: `outputs/bi`
- appendix tables: `outputs/bi`
