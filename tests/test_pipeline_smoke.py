from pathlib import Path

import pandas as pd

from copper_risk_model.bi_export import build_bi_outputs
from copper_risk_model.dashboard_builder import build_portfolio_dashboard


def test_build_bi_outputs_smoke():
    bi_dir = Path("outputs") / "test-smoke-bi"
    dashboard_dir = Path("outputs") / "test-smoke-dashboard"

    outputs = build_bi_outputs(output_dir=bi_dir)
    assert outputs["fact_simulation_distribution"].exists()
    assert outputs["dim_metric"].exists()
    assert outputs["simulation_summary"].exists()
    assert outputs["benchmark_comparison"].exists()
    assert outputs["dim_scenario"].exists()
    assert outputs["fact_tornado_sensitivity"].exists()

    dim_scenario = pd.read_csv(outputs["dim_scenario"])
    assert {"base", "committee_downside"}.issubset(set(dim_scenario["scenario_id"]))

    benchmark = pd.read_csv(outputs["benchmark_comparison"])
    assert {"metric", "comparable_flag", "reconciliation_status", "reconciliation_note", "gap", "pct_gap"}.issubset(
        benchmark.columns
    )
    assert {"incremental_npv", "incremental_irr", "expected_npv"}.issubset(set(benchmark["metric"]))

    fact_heatmap = pd.read_csv(outputs["fact_heatmap_price_grade"])
    assert len(fact_heatmap) == 35

    dashboard_outputs = build_portfolio_dashboard(data_dir=bi_dir, output_dir=dashboard_dir)
    assert dashboard_outputs["dashboard_html"].exists()
    assert dashboard_outputs["dashboard_data"].exists()

    html = dashboard_outputs["dashboard_html"].read_text(encoding="utf-8")
    assert "Copper Mining Planning and Performance Command Center" in html
