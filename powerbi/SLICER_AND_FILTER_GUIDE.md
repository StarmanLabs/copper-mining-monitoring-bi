# Slicer And Filter Guide

Use slicers and filters to support the business story, not to fragment it.

## Core Monthly Slicers

Use these slicers across the first four pages:

- `dim_site[site_name]`
- `dim_month[month_label]`

Optional detail-page slicers:

- `dim_process_area[process_area]`
- `dim_cost_center[cost_center]`

Recommended behavior:

- keep `dim_site[site_name]` available on all monthly pages
- use `dim_month[month_label]` as the main time selector for cards and page-specific review
- prefer a single-month selection on pages with KPI cards
- prefer a single-site selection on pages that use site-level KPI cards
- use `dim_process_area` only on process-driver visuals
- use `dim_cost_center` only on cost-pressure visuals

## Appendix-Only Slicers

Use these only on the appendix page:

- `scenario_name`
- `scenario_category`

Do not apply appendix scenario slicers to the first four pages.

## Suggested Global Filter Logic

For the core report:

- keep the report scoped to sample monthly monitoring data
- preserve the sample/demo context in titles or subtitles when useful

For the appendix:

- allow scenario selection
- allow deterministic scenario comparison
- keep benchmark transparency visible but secondary

## Page-Level Filter Suggestions

Executive Overview:

- prefer one selected month
- use `dim_site[site_name]` because the public demo now includes multiple synthetic sites

Monthly Actual vs Plan:

- allow month trend analysis
- keep metric selection controlled by the visual or `dim_monthly_metric`

Process Performance:

- allow multiple months for trend reading
- do not overload the page with scenario filters

Cost and Margin:

- allow multiple months for trend reading
- keep the story tied to monthly economics, not scenario context

Advanced Scenario / Risk Appendix:

- allow `scenario_name`
- keep scenario filters local to the appendix

## What To Avoid

Avoid:

- report-wide scenario filters
- mixed monthly and appendix slicers on the same page
- page-local slicers built from monthly marts when a shared dimension already exists
- unconstrained KPI cards with multiple months selected
- filters that make the executive cards show an arbitrary max value without clear context

## Safe Default Behavior

If you need a clean default report state:

1. select one site
2. select the latest month for the first four pages
3. leave scenario selection for the appendix only

That default preserves the intended business narrative of the starter kit.
