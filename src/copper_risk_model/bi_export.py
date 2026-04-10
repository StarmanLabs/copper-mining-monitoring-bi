"""Build BI-ready datasets from the workbook and the Python simulation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from .bi_semantic import (
    METRIC_CATEGORY_MAP,
    build_dashboard_pages,
    build_kpi_catalog,
    build_metric_catalog,
    build_powerbi_measure_catalog,
)
from .excel_loader import load_workbook_data
from .model import ScenarioParameters, build_expansion_profile
from .scenario_analysis import (
    build_multi_scenario_outputs,
    build_price_grade_heatmap,
    build_tornado_table,
    build_year_dimension,
)
from .simulation import SimulationConfig, run_monte_carlo


def _load_yaml(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _build_dashboard_kpis(base_profile: pd.DataFrame, assumptions: pd.Series, simulation_summary: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"metric": "python_base_npv_usd", "value": float(base_profile["discounted_fcf_usd"].sum())},
            {"metric": "excel_benchmark_npv_pen", "value": float(assumptions["benchmark_npv_excel"])},
            {"metric": "python_expected_npv_usd", "value": float(simulation_summary.loc[simulation_summary["metric"] == "expected_npv_usd", "value"].iloc[0])},
            {"metric": "python_probability_of_loss", "value": float(simulation_summary.loc[simulation_summary["metric"] == "probability_of_loss", "value"].iloc[0])},
            {"metric": "python_var_usd", "value": float(simulation_summary.loc[simulation_summary["metric"] == "var_usd", "value"].iloc[0])},
            {"metric": "python_cvar_usd", "value": float(simulation_summary.loc[simulation_summary["metric"] == "cvar_usd", "value"].iloc[0])},
        ]
    )


def _build_benchmark_comparison(base_profile: pd.DataFrame, simulation_summary: pd.DataFrame, workbook_data, assumptions: pd.Series) -> pd.DataFrame:
    comparison = pd.DataFrame(
        [
            {
                "metric": "base_npv",
                "python_value": float(base_profile["discounted_fcf_usd"].sum()),
                "excel_value": float(assumptions["benchmark_npv_excel"]),
            },
            {
                "metric": "expected_npv",
                "python_value": float(simulation_summary.loc[simulation_summary["metric"] == "expected_npv_usd", "value"].iloc[0]),
                "excel_value": float(workbook_data.benchmark_metrics.loc[workbook_data.benchmark_metrics["metric"] == "expected_npv", "value"].iloc[0]),
            },
            {
                "metric": "var_5pct",
                "python_value": float(simulation_summary.loc[simulation_summary["metric"] == "var_usd", "value"].iloc[0]),
                "excel_value": float(workbook_data.benchmark_metrics.loc[workbook_data.benchmark_metrics["metric"] == "var_5pct", "value"].iloc[0]),
            },
            {
                "metric": "cvar_5pct",
                "python_value": float(simulation_summary.loc[simulation_summary["metric"] == "cvar_usd", "value"].iloc[0]),
                "excel_value": float(workbook_data.benchmark_metrics.loc[workbook_data.benchmark_metrics["metric"] == "cvar_5pct", "value"].iloc[0]),
            },
        ]
    )
    comparison["gap"] = comparison["python_value"] - comparison["excel_value"]
    comparison["pct_gap_vs_excel"] = comparison["gap"] / comparison["excel_value"].replace(0, pd.NA)
    return comparison


def _build_simulation_percentiles(distribution: pd.DataFrame, percentiles: list[float]) -> pd.DataFrame:
    return pd.DataFrame(
        [{"percentile": percentile, "npv_usd": float(distribution["npv_usd"].quantile(percentile))} for percentile in percentiles]
    )


def build_bi_outputs(config_path: str | Path = "config/project.yaml", output_dir: str | Path = "outputs/bi") -> dict[str, Path]:
    config = _load_yaml(config_path)
    workbook_data = load_workbook_data(config["project"]["workbook_path"])

    assumptions = workbook_data.assumptions.set_index("parameter")["value"]
    params = ScenarioParameters(
        payable_rate=float(assumptions["payable_rate"]),
        tc_rc_usd_per_lb=float(assumptions["tc_rc_usd_per_lb"]),
        expansion_unit_cost_usd_per_tonne=float(assumptions["expansion_unit_cost_usd_per_tonne"]),
        tax_rate_total=float(assumptions["income_tax_rate"] + assumptions["royalty_rate"] + assumptions["special_levy_rate"]),
        wacc=float(assumptions["wacc"]),
        annual_sustaining_capex_usd=float(config["scenario"]["finance"]["annual_sustaining_capex_usd"]),
        initial_capex_schedule_usd={int(k): float(v) for k, v in config["scenario"]["finance"]["initial_capex_schedule_usd"].items()},
        working_capital_ratio=float(config["scenario"]["finance"]["working_capital_ratio"]),
        uplift_pct=float(config["scenario"]["expansion"]["uplift_pct"]),
        logistic_midpoint=float(config["scenario"]["expansion"]["logistic_midpoint"]),
        logistic_steepness=float(config["scenario"]["expansion"]["logistic_steepness"]),
    )
    sim_config = SimulationConfig(
        iterations=int(config["simulation"]["iterations"]),
        random_seed=int(config["simulation"]["random_seed"]),
        var_alpha=float(config["simulation"]["var_alpha"]),
        mu_price_returns=float(assumptions["mu_price_returns"]),
        sigma_price_returns=float(assumptions["sigma_price_returns"]),
        grade_cv=float(workbook_data.operational_history["head_grade"].std(ddof=1) / workbook_data.operational_history["head_grade"].mean()),
        recovery_cv=float(workbook_data.operational_history["recovery"].std(ddof=1) / workbook_data.operational_history["recovery"].mean()),
    )

    base_profile = build_expansion_profile(workbook_data.annual_inputs, params)
    distribution, simulation_summary = run_monte_carlo(workbook_data.annual_inputs, params, sim_config)

    simulation_distribution = distribution.copy()
    simulation_distribution["scenario_id"] = "mc_base"
    simulation_distribution["scenario_name"] = "Monte Carlo Base"

    scenario_dim, fact_annual_metrics, fact_scenario_kpis = build_multi_scenario_outputs(
        annual_inputs=workbook_data.annual_inputs,
        params=params,
        scenario_registry=config["portfolio_bi"]["deterministic_scenarios"],
    )
    fact_annual_metrics["category"] = fact_annual_metrics["metric"].map(METRIC_CATEGORY_MAP)

    dashboard_kpis = _build_dashboard_kpis(base_profile, assumptions, simulation_summary)
    benchmark_comparison = _build_benchmark_comparison(base_profile, simulation_summary, workbook_data, assumptions)
    fact_tornado_sensitivity = build_tornado_table(
        annual_inputs=workbook_data.annual_inputs,
        params=params,
        tornado_specs=config["portfolio_bi"]["tornado"],
    )
    fact_heatmap_price_grade = build_price_grade_heatmap(
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

    metric_catalog = build_metric_catalog()
    kpi_catalog = build_kpi_catalog()
    dashboard_pages = build_dashboard_pages()
    powerbi_measure_catalog = build_powerbi_measure_catalog()
    dim_year = build_year_dimension(
        project_years=workbook_data.annual_inputs["year"].tolist(),
        start_calendar_year=int(config["project"]["project_start_calendar_year"]),
    )
    simulation_percentiles = _build_simulation_percentiles(simulation_distribution, config["portfolio_bi"]["simulation_percentiles"])

    cdf = simulation_distribution[["scenario_id", "scenario_name", "npv_usd"]].sort_values("npv_usd").reset_index(drop=True)
    cdf["cumulative_probability"] = (cdf.index + 1) / len(cdf)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    outputs = {
        "annual_inputs": output_dir / "annual_inputs.csv",
        "assumptions": output_dir / "assumptions.csv",
        "historical_prices": output_dir / "historical_prices.csv",
        "operational_history": output_dir / "operational_history.csv",
        "annual_profile_wide": output_dir / "annual_profile_wide.csv",
        "annual_profile_long": output_dir / "annual_profile_long.csv",
        "metric_catalog": output_dir / "metric_catalog.csv",
        "kpi_catalog": output_dir / "kpi_catalog.csv",
        "dashboard_pages": output_dir / "dashboard_pages.csv",
        "powerbi_measure_catalog": output_dir / "powerbi_measure_catalog.csv",
        "simulation_distribution": output_dir / "simulation_distribution.csv",
        "simulation_summary": output_dir / "simulation_summary.csv",
        "simulation_percentiles": output_dir / "simulation_percentiles.csv",
        "dashboard_kpis": output_dir / "dashboard_kpis.csv",
        "benchmark_comparison": output_dir / "benchmark_comparison.csv",
        "excel_benchmark_metrics": output_dir / "excel_benchmark_metrics.csv",
        "excel_benchmark_distribution": output_dir / "excel_benchmark_distribution.csv",
        "simulation_cdf": output_dir / "simulation_cdf.csv",
        "dim_year": output_dir / "dim_year.csv",
        "dim_metric": output_dir / "dim_metric.csv",
        "dim_scenario": output_dir / "dim_scenario.csv",
        "fact_annual_metrics": output_dir / "fact_annual_metrics.csv",
        "fact_scenario_kpis": output_dir / "fact_scenario_kpis.csv",
        "fact_simulation_distribution": output_dir / "fact_simulation_distribution.csv",
        "fact_tornado_sensitivity": output_dir / "fact_tornado_sensitivity.csv",
        "fact_heatmap_price_grade": output_dir / "fact_heatmap_price_grade.csv",
    }

    workbook_data.annual_inputs.to_csv(outputs["annual_inputs"], index=False)
    workbook_data.assumptions.to_csv(outputs["assumptions"], index=False)
    workbook_data.historical_prices.to_csv(outputs["historical_prices"], index=False)
    workbook_data.operational_history.to_csv(outputs["operational_history"], index=False)
    base_profile.to_csv(outputs["annual_profile_wide"], index=False)
    fact_annual_metrics.to_csv(outputs["annual_profile_long"], index=False)
    metric_catalog.to_csv(outputs["metric_catalog"], index=False)
    kpi_catalog.to_csv(outputs["kpi_catalog"], index=False)
    dashboard_pages.to_csv(outputs["dashboard_pages"], index=False)
    powerbi_measure_catalog.to_csv(outputs["powerbi_measure_catalog"], index=False)
    simulation_distribution.to_csv(outputs["simulation_distribution"], index=False)
    simulation_summary.to_csv(outputs["simulation_summary"], index=False)
    simulation_percentiles.to_csv(outputs["simulation_percentiles"], index=False)
    dashboard_kpis.to_csv(outputs["dashboard_kpis"], index=False)
    benchmark_comparison.to_csv(outputs["benchmark_comparison"], index=False)
    workbook_data.benchmark_metrics.to_csv(outputs["excel_benchmark_metrics"], index=False)
    workbook_data.benchmark_distribution.to_csv(outputs["excel_benchmark_distribution"], index=False)
    cdf.to_csv(outputs["simulation_cdf"], index=False)
    dim_year.to_csv(outputs["dim_year"], index=False)
    metric_catalog.to_csv(outputs["dim_metric"], index=False)
    scenario_dim.to_csv(outputs["dim_scenario"], index=False)
    fact_annual_metrics.to_csv(outputs["fact_annual_metrics"], index=False)
    fact_scenario_kpis.to_csv(outputs["fact_scenario_kpis"], index=False)
    simulation_distribution.to_csv(outputs["fact_simulation_distribution"], index=False)
    fact_tornado_sensitivity.to_csv(outputs["fact_tornado_sensitivity"], index=False)
    fact_heatmap_price_grade.to_csv(outputs["fact_heatmap_price_grade"], index=False)
    return outputs
