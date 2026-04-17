from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pandas.testing as pdt

from copper_risk_model.bi_export import _load_yaml, build_bi_outputs
from copper_risk_model.excel_loader import load_workbook_data
from copper_risk_model.model import (
    ScenarioParameters,
    build_expansion_profile,
    build_incremental_expansion_profile,
    irr_from_profile,
    npv_from_profile,
)
from copper_risk_model.scenario_analysis import (
    build_multi_scenario_outputs,
    build_price_grade_heatmap,
    build_tornado_table,
)
from copper_risk_model.simulation import (
    SimulationConfig,
    run_monte_carlo,
    sample_grade_factors,
    sample_recovery_paths,
    simulate_price_paths,
)


def _load_context() -> tuple[dict, object, ScenarioParameters, SimulationConfig]:
    config = _load_yaml("config/project.yaml")
    workbook_data = load_workbook_data(config["project"]["workbook_path"])
    assumptions = workbook_data.assumptions.set_index("parameter")["value"]

    params = ScenarioParameters(
        payable_rate=float(assumptions["payable_rate"]),
        tc_rc_usd_per_lb=float(assumptions["tc_rc_usd_per_lb"]),
        mine_cost_usd_per_tonne=float(assumptions["mine_cost_usd_per_tonne"]),
        plant_cost_usd_per_tonne=float(assumptions["plant_cost_usd_per_tonne"]),
        g_and_a_cost_usd_per_tonne=float(assumptions["g_and_a_cost_usd_per_tonne"]),
        base_unit_cost_usd_per_tonne=float(assumptions["base_unit_cost_usd_per_tonne"]),
        expansion_unit_cost_usd_per_tonne=float(assumptions["expansion_unit_cost_usd_per_tonne"]),
        income_tax_rate=float(assumptions["income_tax_rate"]),
        royalty_rate=float(assumptions["royalty_rate"]),
        special_levy_rate=float(assumptions["special_levy_rate"]),
        wacc=float(assumptions["wacc"]),
        annual_sustaining_capex_usd=float(config["scenario"]["finance"]["annual_sustaining_capex_usd"]),
        initial_capex_schedule_usd={
            int(key): float(value) for key, value in config["scenario"]["finance"]["initial_capex_schedule_usd"].items()
        },
        working_capital_ratio=float(config["scenario"]["finance"]["working_capital_ratio"]),
        uplift_pct=float(config["scenario"]["expansion"]["uplift_pct"]),
        logistic_midpoint=float(config["scenario"]["expansion"]["logistic_midpoint"]),
        logistic_steepness=float(config["scenario"]["expansion"]["logistic_steepness"]),
    )
    sim_config = SimulationConfig(
        iterations=256,
        random_seed=int(config["simulation"]["random_seed"]),
        var_alpha=float(config["simulation"]["var_alpha"]),
        sigma_price_returns=float(assumptions["sigma_price_returns"]),
        grade_cv=float(
            workbook_data.operational_history["head_grade"].std(ddof=1)
            / workbook_data.operational_history["head_grade"].mean()
        ),
        recovery_cv=float(
            workbook_data.operational_history["recovery"].std(ddof=1)
            / workbook_data.operational_history["recovery"].mean()
        ),
        price_path_autocorrelation=float(config["simulation"]["price_path_autocorrelation"]),
    )
    return config, workbook_data, params, sim_config


def test_deterministic_model_invariants():
    _, workbook_data, params, _ = _load_context()

    profile = build_expansion_profile(workbook_data.annual_inputs, params)
    incremental = build_incremental_expansion_profile(workbook_data.annual_inputs, params)

    assert (profile["expanded_tonnes"] >= profile["base_processed_tonnes"]).all()
    assert (profile["scenario_recovery"].between(0.0, 1.0)).all()
    assert float(profile.attrs["initial_capex_year0_usd"]) == params.initial_capex_schedule_usd[0]
    assert float(profile.loc[profile["year"] == 1, "initial_capex_usd"].iloc[0]) == params.initial_capex_schedule_usd[1]
    assert float(profile.loc[profile["year"] == 2, "sustaining_capex_usd"].iloc[0]) == params.annual_sustaining_capex_usd
    assert npv_from_profile(profile) > 0
    assert irr_from_profile(profile) > 0
    assert float(incremental.loc[incremental["year"] == 1, "free_cash_flow_usd"].iloc[0]) < 0
    assert float(incremental.loc[incremental["year"] == 15, "working_capital_release_usd"].iloc[0]) < 0


def test_scenario_directionality_and_sensitivity_shapes():
    config, workbook_data, params, _ = _load_context()
    scenario_dim, _, scenario_kpis = build_multi_scenario_outputs(
        annual_inputs=workbook_data.annual_inputs,
        params=params,
        scenario_registry=config["portfolio_bi"]["deterministic_scenarios"],
    )
    scenario_values = scenario_kpis.pivot_table(index="scenario_id", columns="metric", values="value", aggfunc="first")

    assert scenario_values.loc["bull_market", "scenario_npv_usd"] > scenario_values.loc["base", "scenario_npv_usd"]
    assert scenario_values.loc["bear_market", "scenario_npv_usd"] < scenario_values.loc["base", "scenario_npv_usd"]
    assert scenario_values.loc["capex_overrun", "scenario_npv_usd"] < scenario_values.loc["base", "scenario_npv_usd"]
    assert scenario_values.loc["committee_downside", "scenario_npv_usd"] < scenario_values.loc["bear_market", "scenario_npv_usd"]
    assert scenario_values.loc["base", "scenario_irr"] > 0
    assert {"base", "committee_downside"}.issubset(set(scenario_dim["scenario_id"]))

    tornado = build_tornado_table(
        annual_inputs=workbook_data.annual_inputs,
        params=params,
        tornado_specs=config["portfolio_bi"]["tornado"],
    )
    heatmap = build_price_grade_heatmap(
        annual_inputs=workbook_data.annual_inputs,
        params=params,
        price_factors=config["portfolio_bi"]["heatmap"]["price_factors"],
        grade_factors=config["portfolio_bi"]["heatmap"]["grade_factors"],
        recovery_factor=float(config["portfolio_bi"]["heatmap"]["recovery_factor"]),
        throughput_factor=float(config["portfolio_bi"]["heatmap"]["throughput_factor"]),
        opex_factor=float(config["portfolio_bi"]["heatmap"]["opex_factor"]),
        capex_factor=float(config["portfolio_bi"]["heatmap"]["capex_factor"]),
        wacc_shift_bps=float(config["portfolio_bi"]["heatmap"]["wacc_shift_bps"]),
    )

    assert tornado["direction"].value_counts().to_dict() == {"down": 7, "up": 7}
    assert len(heatmap) == 35
    assert set(heatmap["npv_sign"]) == {"Positive", "Negative"}


def test_simulation_reproducibility_and_path_variation():
    _, workbook_data, params, sim_config = _load_context()

    distribution_a, summary_a = run_monte_carlo(workbook_data.annual_inputs, params, sim_config)
    distribution_b, summary_b = run_monte_carlo(workbook_data.annual_inputs, params, sim_config)
    pdt.assert_frame_equal(distribution_a, distribution_b)
    pdt.assert_frame_equal(summary_a, summary_b)

    rng = np.random.default_rng(sim_config.random_seed)
    base_prices = workbook_data.annual_inputs["copper_price_usd_per_lb"].to_numpy(dtype=float)
    price_paths = simulate_price_paths(base_prices=base_prices, config=sim_config, rng=rng)
    recovery_paths = sample_recovery_paths(
        base_recovery=workbook_data.annual_inputs["base_recovery"].to_numpy(dtype=float),
        config=sim_config,
        rng=np.random.default_rng(sim_config.random_seed + 1),
    )
    grade_factors = sample_grade_factors(
        config=sim_config,
        rng=np.random.default_rng(sim_config.random_seed + 2),
    )

    assert price_paths.shape == (sim_config.iterations, len(base_prices))
    assert (price_paths.std(axis=1) > 0).all()
    log_deviations = np.log(price_paths / base_prices[None, :])
    lagged_correlation = np.corrcoef(log_deviations[:, :-1].ravel(), log_deviations[:, 1:].ravel())[0, 1]
    assert lagged_correlation > 0.2
    assert recovery_paths.shape == (sim_config.iterations, len(base_prices))
    assert ((recovery_paths >= 0.0) & (recovery_paths <= 1.0)).all()
    assert grade_factors.shape == (sim_config.iterations,)
    assert summary_a.loc[summary_a["metric"] == "max_npv_usd", "value"].iloc[0] >= summary_a.loc[
        summary_a["metric"] == "median_npv_usd", "value"
    ].iloc[0]


def test_bi_output_schema_integrity():
    output_dir = Path("outputs") / "test-bi-schema"
    outputs = build_bi_outputs(output_dir=output_dir)

    benchmark = pd.read_csv(outputs["benchmark_comparison"])
    assert {
        "metric",
        "python_value",
        "python_unit",
        "python_currency",
        "benchmark_value",
        "benchmark_unit",
        "benchmark_currency",
        "comparable_flag",
        "reconciliation_status",
        "reconciliation_note",
        "gap",
        "pct_gap",
    }.issubset(benchmark.columns)

    comparable = benchmark.loc[benchmark["comparable_flag"]]
    reference_only = benchmark.loc[~benchmark["comparable_flag"]]
    assert set(comparable["metric"]) == {"incremental_npv", "incremental_irr"}
    assert {"expected_npv", "var_5pct", "cvar_5pct"}.issubset(set(reference_only["metric"]))
    assert comparable["gap"].notna().all()
    assert set(comparable["reconciliation_status"]).issubset({"close_match", "material_gap"})
    assert reference_only["gap"].isna().all()

    annual = pd.read_csv(outputs["fact_annual_metrics"])
    metrics = pd.read_csv(outputs["dim_metric"])
    simulation_distribution = pd.read_csv(outputs["fact_simulation_distribution"])
    assert annual["category"].notna().all()
    assert {"gross_revenue_usd", "cash_tax_proxy_usd", "working_capital_release_usd"}.issubset(set(metrics["metric"]))
    assert {
        "average_price_usd_per_lb",
        "terminal_price_usd_per_lb",
        "price_path_std_usd_per_lb",
        "grade_factor",
        "average_recovery",
        "recovery_std",
        "npv_usd",
    }.issubset(simulation_distribution.columns)
