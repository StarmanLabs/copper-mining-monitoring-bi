# Desktop Finalization

Artifact strategy:

- this repository does not claim to ship a real Desktop-saved PBIP
- this folder is the strongest honest PBIP finalization package that can be produced in a public-safe environment

What is already done:

- query grouping and output-root parameterization
- measure bundles and TMDL scripts
- relationship, sort-by, and hidden-field catalogs
- report page shells in monthly-first order

What still must be done in Desktop:

1. set `ProjectRoot` and the output-root queries included with this scaffold
2. import the Power Query files
3. apply the TMDL scripts
4. lay out the report canvas from the page shells
5. save the final local result as PBIP or PBIX

How to verify the model:

1. confirm `dim_site` and `dim_month` are the shared monthly filters
2. confirm the first four pages remain the operational story
3. confirm the appendix stays secondary
4. confirm the model points only to public-safe outputs or to ignored local runner outputs

Current defaults:

- starter-kit references: `outputs/bi`
- monthly model tables: `outputs/bi`
- appendix tables: `outputs/bi`
