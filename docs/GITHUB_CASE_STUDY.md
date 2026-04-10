# From Excel Workbook to Python Risk Platform

## Why this project exists

The original version of this project lived inside an Excel workbook. That workbook already had valuable domain logic: price assumptions, grade decline, recovery, throughput, capex, and Monte Carlo simulation. It was useful as a valuation prototype, but it was still difficult to audit, difficult to scale, and almost impossible to connect cleanly to modern BI workflows.

The purpose of the rebuild was not to discard Excel. It was to preserve its economic reasoning while moving the project into a more serious analytical environment.

## The original challenge

The workbook did several things well:

- organized annual project economics
- modeled production and value creation
- simulated uncertainty
- provided a dashboard view

But it also had important structural limitations:

- assumptions were embedded in formulas
- validation was difficult
- extensibility was weak
- scenario management was manual
- outputs were not modeled for BI tools
- the analytical story remained trapped inside the spreadsheet

## Rebuild strategy

The rebuild followed a layered approach.

### 1. Extract the spreadsheet logic

The first step was to treat the workbook as a source system:

- identify key sheets
- recover assumptions
- separate empirical data from modeled data
- preserve benchmark outputs for later comparison

### 2. Recreate the valuation engine in Python

The next step was to move the economics into explicit modules:

- workbook ingestion
- valuation logic
- stochastic simulation
- deterministic scenarios
- sensitivity analysis

This step turned hidden spreadsheet formulas into inspectable analytical code.

### 3. Build a BI-ready export layer

The project was then extended beyond modeling.

Instead of exporting only a few tables, the repository now produces:

- dimensions
- fact tables
- KPI catalogs
- dashboard page definitions
- Power BI measure templates

This is the shift that turns the repository into a portfolio-grade analytical product instead of a notebook or spreadsheet conversion.

## What changed conceptually

The strongest change is not technical. It is conceptual.

The project moved:

- from spreadsheet logic to explicit model architecture
- from isolated outputs to semantic reporting tables
- from one base case to a scenario framework
- from one simulation output to multiple portfolio-facing analytical views

## Tools used across the transformation

- Excel and VBA for the original prototype
- Python for the rebuild
- pandas and numpy for data and simulation workflows
- openpyxl for workbook extraction
- pytest for pipeline verification
- Power BI / Tableau semantic preparation through star-schema style exports

## Why this matters for GitHub

On GitHub, this project should not be framed as "I made a Monte Carlo model."

A stronger framing is:

> I took a mining valuation model that existed as a workbook and rebuilt it into a reproducible risk analytics system with scenario analysis, sensitivity layers, and BI-ready data products.

That story signals:

- domain knowledge
- analytical discipline
- engineering maturity
- reporting awareness

## Honest limitation

The Python engine does not yet fully reconcile to the original workbook.

That is not something to hide in the repository. It is a sign of seriousness to keep benchmark gaps visible while showing the roadmap for reconciliation and extension.

## Best GitHub angle

The strongest portfolio narrative is:

1. Start with the Excel workbook as the origin.
2. Explain why Excel was analytically useful but operationally limited.
3. Show how Python modularized the model.
4. Show how BI exports made the project usable as a reporting product.
5. Make benchmark gaps explicit and frame them as the next step.
