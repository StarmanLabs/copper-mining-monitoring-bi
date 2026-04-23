from __future__ import annotations

import numpy as np
import pandas as pd
import pandas.testing as pdt

from copper_risk_model.advanced_appendix import build_advanced_appendix_outputs, load_advanced_appendix_context
from copper_risk_model.bi_export import build_bi_outputs
from copper_risk_model.valuation_model import (
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
from conftest import scratch_output_dir


def _load_context() -> tuple[object, SimulationConfig]:
    context = load_advanced_appendix_context()
    sim_config = SimulationConfig(
        iterations=256,
        random_seed=context.simulation_config.random_seed,
        var_alpha=context.simulation_config.var_alpha,
        sigma_price_returns=context.simulation_config.sigma_price_returns,
        grade_cv=context.simulation_config.grade_cv,
        recovery_cv=context.simulation_config.recovery_cv,
        price_path_autocorrelation=context.simulation_config.price_path_autocorrelation,
    )
    return context, sim_config


def test_deterministic_model_invariants():
    context, _ = _load_context()
    annual_inputs = context.annual_inputs
    params = context.params

    assert context.input_mode == "canonical"
    assert context.benchmark_mode == "canonical"
    assert context.legacy_workbook_data is None

    profile = build_expansion_profile(annual_inputs, params)
    incremental = build_incremental_expansion_profile(annual_inputs, params)

    assert (profile["expanded_tonnes"] >= profile["base_processed_tonnes"]).all()
    assert (profile["scenario_recovery"].between(0.0, 1.0)).all()
    assert float(profile.attrs["initial_capex_year0_usd"]) == params.initial_capex_schedule_usd[0]
    assert float(profile.loc[profile["year"] == 1, "initial_capex_usd"].iloc[0]) == float(
        annual_inputs.loc[annual_inputs["year"] == 1, "initial_capex_usd"].iloc[0]
    )
    assert float(profile.loc[profile["year"] == 2, "sustaining_capex_usd"].iloc[0]) == params.annual_sustaining_capex_usd
    assert npv_from_profile(profile) > 0
    assert irr_from_profile(profile) > 0
    assert float(incremental.loc[incremental["year"] == 1, "free_cash_flow_usd"].iloc[0]) < 0
    assert float(incremental.loc[incremental["year"] == 15, "working_capital_release_usd"].iloc[0]) < 0


def test_scenario_directionality_and_sensitivity_shapes():
    context, _ = _load_context()
    scenario_dim, _, scenario_kpis = build_multi_scenario_outputs(
        annual_inputs=context.annual_inputs,
        params=context.params,
        scenario_registry=context.scenario_registry,
    )
    scenario_values = scenario_kpis.pivot_table(index="scenario_id", columns="metric", values="value", aggfunc="first")

    assert scenario_values.loc["bull_market", "scenario_npv_usd"] > scenario_values.loc["base", "scenario_npv_usd"]
    assert scenario_values.loc["bear_market", "scenario_npv_usd"] < scenario_values.loc["base", "scenario_npv_usd"]
    assert scenario_values.loc["capex_overrun", "scenario_npv_usd"] < scenario_values.loc["base", "scenario_npv_usd"]
    assert scenario_values.loc["committee_downside", "scenario_npv_usd"] < scenario_values.loc["bear_market", "scenario_npv_usd"]
    assert scenario_values.loc["base", "scenario_irr"] > 0
    assert scenario_values.loc["operational_stress", "average_processed_tonnes"] < scenario_values.loc["base", "average_processed_tonnes"]
    assert scenario_values.loc["operational_stress", "average_unit_opex_usd_per_tonne"] > scenario_values.loc["base", "average_unit_opex_usd_per_tonne"]
    assert scenario_values.loc["bull_market", "average_net_price_usd_per_lb"] > scenario_values.loc["base", "average_net_price_usd_per_lb"]
    assert scenario_values.loc["committee_downside", "ebitda_margin_proxy"] < scenario_values.loc["base", "ebitda_margin_proxy"]
    assert {"base", "committee_downside"}.issubset(set(scenario_dim["scenario_id"]))

    tornado = build_tornado_table(
        annual_inputs=context.annual_inputs,
        params=context.params,
        tornado_specs=context.config["portfolio_bi"]["tornado"],
    )
    heatmap = build_price_grade_heatmap(
        annual_inputs=context.annual_inputs,
        params=context.params,
        price_factors=context.config["portfolio_bi"]["heatmap"]["price_factors"],
        grade_factors=context.config["portfolio_bi"]["heatmap"]["grade_factors"],
        recovery_factor=float(context.config["portfolio_bi"]["heatmap"]["recovery_factor"]),
        throughput_factor=float(context.config["portfolio_bi"]["heatmap"]["throughput_factor"]),
        opex_factor=float(context.config["portfolio_bi"]["heatmap"]["opex_factor"]),
        capex_factor=float(context.config["portfolio_bi"]["heatmap"]["capex_factor"]),
        wacc_shift_bps=float(context.config["portfolio_bi"]["heatmap"]["wacc_shift_bps"]),
    )

    assert tornado["direction"].value_counts().to_dict() == {"down": 7, "up": 7}
    assert len(heatmap) == 35
    assert set(heatmap["npv_sign"]) == {"Positive", "Negative"}


def test_simulation_reproducibility_and_path_variation():
    context, sim_config = _load_context()

    distribution_a, summary_a = run_monte_carlo(context.annual_inputs, context.params, sim_config)
    distribution_b, summary_b = run_monte_carlo(context.annual_inputs, context.params, sim_config)
    pdt.assert_frame_equal(distribution_a, distribution_b)
    pdt.assert_frame_equal(summary_a, summary_b)

    rng = np.random.default_rng(sim_config.random_seed)
    base_prices = context.annual_inputs["copper_price_usd_per_lb"].to_numpy(dtype=float)
    price_paths = simulate_price_paths(base_prices=base_prices, config=sim_config, rng=rng)
    recovery_paths = sample_recovery_paths(
        base_recovery=context.annual_inputs["base_recovery"].to_numpy(dtype=float),
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


def test_appendix_monte_carlo_exports_are_rounded_for_cross_platform_stability():
    with scratch_output_dir("test-appendix-rounded-exports") as output_dir:
        outputs = build_advanced_appendix_outputs(output_dir=output_dir)

        simulation_distribution = pd.read_csv(outputs["fact_simulation_distribution"])
        simulation_summary = pd.read_csv(outputs["simulation_summary"])
        simulation_percentiles = pd.read_csv(outputs["simulation_percentiles"])
        benchmark_comparison = pd.read_csv(outputs["benchmark_comparison"])

        distribution_float_columns = [
            "average_price_usd_per_lb",
            "terminal_price_usd_per_lb",
            "price_path_std_usd_per_lb",
            "grade_factor",
            "average_recovery",
            "recovery_std",
        ]
        for column_name in distribution_float_columns:
            assert np.allclose(
                simulation_distribution[column_name].to_numpy(),
                simulation_distribution[column_name].round(5).to_numpy(),
                equal_nan=True,
                atol=1e-12,
            )
        assert np.allclose(
            simulation_distribution["npv_usd"].to_numpy(),
            simulation_distribution["npv_usd"].round(2).to_numpy(),
            equal_nan=True,
            atol=1e-12,
        )

        assert np.allclose(
            simulation_summary["value"].to_numpy(),
            simulation_summary["value"].round(5).to_numpy(),
            equal_nan=True,
            atol=1e-12,
        )
        assert np.allclose(
            simulation_percentiles["npv_usd"].to_numpy(),
            simulation_percentiles["npv_usd"].round(5).to_numpy(),
            equal_nan=True,
            atol=1e-12,
        )

        for column_name in ["python_value", "benchmark_value", "gap", "pct_gap"]:
            comparable_values = benchmark_comparison[column_name].dropna().to_numpy()
            assert np.allclose(
                comparable_values,
                np.round(comparable_values, 5),
                atol=1e-12,
            )


def test_legacy_appendix_adapter_path_still_runs():
    with scratch_output_dir("test-appendix-legacy") as output_dir:
        outputs = build_advanced_appendix_outputs(
            output_dir=output_dir,
            input_mode="legacy_workbook",
            benchmark_mode="legacy_workbook",
        )

        benchmark = pd.read_csv(outputs["benchmark_comparison"])
        assumptions = pd.read_csv(outputs["advanced_appendix_assumption_catalog"])
        output_catalog = pd.read_csv(outputs["advanced_appendix_output_catalog"])

        assert benchmark["benchmark_source"].eq("Legacy workbook reference").all()
        assert assumptions["source_type"].str.contains("legacy_workbook_adapter").any()
        assert output_catalog["generated_from"].isin(
            {"Legacy workbook adapter", "Legacy workbook reference"}
        ).all()


def test_bi_output_schema_integrity():
    with scratch_output_dir("test-bi-schema") as output_dir:
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
            "comparability_class",
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
        assert set(benchmark["comparability_class"]) == {"direct_comparison", "reference_only"}
        assert comparable["gap"].notna().all()
        assert set(comparable["reconciliation_status"]).issubset({"close_match", "material_gap"})
        assert reference_only["gap"].isna().all()

        annual = pd.read_csv(outputs["fact_annual_metrics"])
        annual_dataset_catalog = pd.read_csv(outputs["annual_appendix_dataset_catalog"])
        annual_field_catalog = pd.read_csv(outputs["annual_appendix_field_catalog"])
        metrics = pd.read_csv(outputs["dim_metric"])
        scenario_kpis = pd.read_csv(outputs["fact_scenario_kpis"])
        appendix_kpis = pd.read_csv(outputs["appendix_kpi_catalog"])
        appendix_outputs = pd.read_csv(outputs["advanced_appendix_output_catalog"])
        appendix_assumptions = pd.read_csv(outputs["advanced_appendix_assumption_catalog"])
        benchmark_scope = pd.read_csv(outputs["benchmark_scope_catalog"])
        simulation_distribution = pd.read_csv(outputs["fact_simulation_distribution"])
        monthly_summary = pd.read_csv(outputs["kpi_monthly_summary"])
        monthly_fact = pd.read_csv(outputs["fact_monthly_actual_vs_plan"])
        monthly_dictionary = pd.read_csv(outputs["monthly_kpi_dictionary"])
        data_quality_report = pd.read_csv(outputs["data_quality_report"])
        kpi_exceptions = pd.read_csv(outputs["kpi_exceptions"])
        source_mapping_audit = pd.read_csv(outputs["source_mapping_audit"])
        powerbi_table_catalog = pd.read_csv(outputs["powerbi_table_catalog"])
        powerbi_query_catalog = pd.read_csv(outputs["powerbi_query_catalog"])
        powerbi_relationship_catalog = pd.read_csv(outputs["powerbi_relationship_catalog"])
        powerbi_visual_binding_catalog = pd.read_csv(outputs["powerbi_visual_binding_catalog"])
        powerbi_measure_catalog = pd.read_csv(outputs["powerbi_measure_catalog"])
        page_catalog = pd.read_csv(outputs["dashboard_page_catalog"])
        assert annual["category"].notna().all()
        assert {"annual_appendix_inputs", "appendix_parameters", "appendix_scenarios", "appendix_benchmark_metrics"}.issubset(
            set(annual_dataset_catalog["dataset_name"])
        )
        assert {"dataset_name", "column_name", "description", "required_flag"}.issubset(annual_field_catalog.columns)
        assert {"gross_revenue_usd", "cash_tax_proxy_usd", "working_capital_release_usd"}.issubset(set(metrics["metric"]))
        assert {
            "average_processed_tonnes",
            "average_copper_fine_lb",
            "average_unit_opex_usd_per_tonne",
            "ebitda_margin_proxy",
            "total_operating_cash_flow_usd",
        }.issubset(set(scenario_kpis["metric"]))
        assert {"scenario_npv_usd", "scenario_irr", "payback_year"}.issubset(set(appendix_kpis["metric"]))
        assert {
            "dataset_name",
            "appendix_submodule",
            "why_secondary",
            "public_safe_boundary",
            "input_dependency_role",
            "generated_from",
        }.issubset(appendix_outputs.columns)
        assert {
            "parameter_name",
            "source_type",
            "practical_use",
            "limitation_note",
            "secondary_role_note",
        }.issubset(appendix_assumptions.columns)
        assert {
            "comparison_role",
            "when_to_use",
            "limitation_note",
            "secondary_role_note",
        }.issubset(benchmark_scope.columns)
        assert benchmark_scope["benchmark_source"].isin({"Canonical appendix benchmark table", "Legacy workbook reference"}).all()
        assert {
            "average_price_usd_per_lb",
            "terminal_price_usd_per_lb",
            "price_path_std_usd_per_lb",
            "grade_factor",
            "average_recovery",
            "recovery_std",
            "npv_usd",
        }.issubset(simulation_distribution.columns)
        assert {
            "throughput_tonnes_variance_pct",
            "unit_cost_usd_per_tonne_variance_pct",
            "overall_alert_level",
            "primary_alert_metric",
        }.issubset(monthly_summary.columns)
        assert {
            "metric",
            "metric_display_name",
            "metric_group",
            "plan_value",
            "actual_value",
            "variance_pct",
            "alert_level",
        }.issubset(monthly_fact.columns)
        assert {
            "business_meaning",
            "proxy_flag",
            "plan_field",
            "actual_field",
            "variance_field",
            "variance_pct_field",
            "primary_dashboard_page",
        }.issubset(monthly_dictionary.columns)
        assert {
            "dataset_name",
            "check_name",
            "status",
            "issue_count",
        }.issubset(data_quality_report.columns)
        assert {
            "exception_code",
            "exception_title",
            "severity",
            "management_question",
        }.issubset(kpi_exceptions.columns)
        assert {
            "dataset_name",
            "source_dataset_label",
            "source_file",
            "status",
        }.issubset(source_mapping_audit.columns)
        assert {
            "table_name",
            "source_file",
            "table_role",
            "recommended_action",
        }.issubset(powerbi_table_catalog.columns)
        assert {
            "query_name",
            "relative_source_path",
            "power_query_file",
            "load_recommendation",
        }.issubset(powerbi_query_catalog.columns)
        assert {
            "from_table",
            "from_column",
            "to_table",
            "to_column",
            "cardinality",
        }.issubset(powerbi_relationship_catalog.columns)
        assert {
            "page_name",
            "visual_title",
            "source_table",
            "key_dimensions",
            "key_measures",
            "business_question",
        }.issubset(powerbi_visual_binding_catalog.columns)
        assert {
            "measure_group",
            "starter_kit_scope",
            "context_requirement",
            "preferred_visual_type",
            "business_question",
        }.issubset(powerbi_measure_catalog.columns)
        assert list(page_catalog["page_name"]) == [
            "Executive Overview",
            "Monthly Actual vs Plan",
            "Process Performance",
            "Cost and Margin",
            "Advanced Scenario / Risk Appendix",
        ]
