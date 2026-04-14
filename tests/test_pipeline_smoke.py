import pandas as pd

from copper_risk_model.bi_export import build_bi_outputs
from copper_risk_model.dashboard_builder import build_portfolio_dashboard


def test_build_bi_outputs_smoke(tmp_path):
    bi_dir = tmp_path / "bi"
    dashboard_dir = tmp_path / "dashboard"

    outputs = build_bi_outputs(output_dir=bi_dir)
    assert outputs["dashboard_kpis"].exists()
    assert outputs["simulation_distribution"].exists()
    assert outputs["metric_catalog"].exists()
    assert outputs["benchmark_comparison"].exists()
    assert outputs["dim_scenario"].exists()
    assert outputs["fact_tornado_sensitivity"].exists()

    dim_scenario = pd.read_csv(outputs["dim_scenario"])
    assert {"base", "committee_downside"}.issubset(set(dim_scenario["scenario_id"]))

    fact_heatmap = pd.read_csv(outputs["fact_heatmap_price_grade"])
    assert len(fact_heatmap) == 35

    dashboard_outputs = build_portfolio_dashboard(data_dir=bi_dir, output_dir=dashboard_dir)
    assert dashboard_outputs["dashboard_html"].exists()
    assert dashboard_outputs["dashboard_data"].exists()

    html = dashboard_outputs["dashboard_html"].read_text(encoding="utf-8")
    assert "Copper Mining Risk Command Center" in html
