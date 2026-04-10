import pandas as pd

from copper_risk_model.bi_export import build_bi_outputs


def test_build_bi_outputs_smoke(tmp_path):
    outputs = build_bi_outputs(output_dir=tmp_path)
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
