# Final Dashboard Layer

## What this adds

This repository now includes a portfolio-facing dashboard layer on top of the Python risk engine and BI exports.

The dashboard package is designed to do two jobs at once:

- show the analytical story visually for GitHub reviewers
- provide a clear handoff path into Power BI or Tableau

## Deliverables

- `outputs/dashboard/index.html`
  Self-contained interactive dashboard showcase built from the generated CSV exports.
- `outputs/dashboard/data_snapshot.json`
  Structured dashboard payload used by the HTML layer.
- `powerbi/copper_risk_theme.json`
  Theme file for Power BI with the same copper-and-charcoal visual language used in the showcase.
- `outputs/bi/*.csv`
  Facts, dimensions, KPI tables, sensitivity tables, and Monte Carlo summaries ready for BI ingestion.

## How to build it

```bash
python scripts/build_portfolio_dashboard.py
```

That script rebuilds the BI exports first and then generates the dashboard showcase.

## Dashboard story

The final dashboard is intentionally structured around the main decision questions:

1. Does the project create value in the base case?
2. How severe is downside risk under uncertainty?
3. Which drivers explain fragility: market, grade, recovery, or capex?
4. How wide is the gap between deterministic upside and committee-downside views?

## Recommended Power BI pages

1. Executive overview
   Use KPI cards, scenario selector, and NPV comparison.
2. Cash flow and operating profile
   Use annual revenue, EBITDA, free cash flow, price, grade, and recovery.
3. Risk and sensitivity
   Use distribution, percentile markers, tornado, and heatmap.
4. Reconciliation and model credibility
   Use Excel vs Python benchmark table and migration notes.

## Suggested GitHub usage

- Keep one screenshot of the hero section near the top of the README.
- Link directly to `docs/DASHBOARD_FINAL.md` and `outputs/dashboard/index.html`.
- Mention that the same semantic layer feeds both the HTML showcase and Power BI or Tableau.

## Important analytical note

This dashboard is serious as a portfolio and communication layer, but the underlying Python engine is still a reconstruction rather than a full financial reconciliation of every workbook formula.

The reconciliation view is intentionally conservative:

- workbook benchmarks are still legacy PEN values
- Python rebuild outputs are displayed in USD
- benchmark comparisons are therefore directional, not yet currency-harmonized

That is a strength if you present it honestly:

- Excel prototype
- Python rebuild
- BI semantic layer
- dashboard product layer
- open reconciliation roadmap
