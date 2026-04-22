# Power BI Dashboard Blueprint

This file is the high-level blueprint for the Power BI Starter Kit.

Use it as the short narrative overview.

For the practical build sequence, use:

- `powerbi/START_HERE.md`
- `powerbi/RELATIONSHIP_BLUEPRINT.md`
- `powerbi/REPORT_BUILD_CHECKLIST.md`
- `powerbi/PAGE_BUILD_GUIDE.md`
- `powerbi/SLICER_AND_FILTER_GUIDE.md`
- `powerbi/VISUAL_BINDING_CATALOG.csv`

## Report Story

The report should read in this order:

1. Executive Overview
2. Monthly Actual vs Plan
3. Process Performance
4. Cost and Margin
5. Advanced Scenario / Risk Appendix

Pages 1 to 4 are the core product story.

Page 5 is valuable, but it remains clearly secondary.

## Modeling Rule

Keep the monthly story simple:

- connect `dim_site` and `dim_month` to the monthly marts and the monthly fact
- connect `dim_monthly_metric` to `fact_monthly_actual_vs_plan`
- connect `dim_process_area` and `dim_cost_center` only to their detail marts when those pages need reusable drill filters
- avoid mart-to-mart joins
- keep the appendix tables disconnected unless a specific appendix visual needs a dimension relationship

## Consumption Rule

Use the exports as a handoff package, not as raw ingredients that require users to reverse-engineer the intended report.

That means the starter kit should make these decisions explicit:

- which tables to import first
- which relationships to create
- which measures to create first
- which pages to build in order
- which visuals belong to which marts

## Appendix Rule

Scenario, valuation, Monte Carlo, tornado, heatmap, and benchmark materials belong in the appendix.

They should:

- enrich the report
- not lead the report
- not displace the monthly monitoring story
