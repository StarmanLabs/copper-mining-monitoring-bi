"""Build BI-ready datasets from the workbook and the Python simulation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from .bi_semantic import (
    METRIC_CATEGORY_MAP,
    build_metric_catalog,
    build_powerbi_measure_catalog,
)
from .excel_loader import load_workbook_data
from .model import (
    ScenarioParameters,
    build_expansion_profile,
    build_incremental_expansion_profile,
    irr_from_profile,
    npv_from_profile,
)
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


def _summary_value(summary: pd.DataFrame, metric: str) -> float:
    return float(summary.loc[summary["metric"] == metric, "value"].iloc[0])


def _assumption_row(workbook_data, parameter: str) -> pd.Series:
    return workbook_data.assumptions.loc[workbook_data.assumptions["parameter"] == parameter].iloc[0]


def _benchmark_row(workbook_data, metric: str) -> pd.Series:
    return workbook_data.benchmark_metrics.loc[workbook_data.benchmark_metrics["metric"] == metric].iloc[0]


def _reconciliation_row(
    metric: str,
    python_value: float,
    python_unit: str,
    python_currency: str | None,
    python_basis: str,
    python_timing: str,
    benchmark_value: float | None,
    benchmark_unit: str | None,
    benchmark_currency: str | None,
    benchmark_basis: str | None,
    benchmark_timing: str | None,
    benchmark_note: str,
    issues: list[str] | None = None,
) -> dict[str, object]:
    issues = [] if issues is None else [issue for issue in issues if issue]
    if benchmark_value is None:
        issues.append("missing_benchmark_value")
    if benchmark_unit is not None and python_unit != benchmark_unit:
        issues.append("unit_mismatch")
    if python_currency != benchmark_currency:
        issues.append("currency_mismatch")
    if benchmark_basis is not None and python_basis != benchmark_basis:
        issues.append("basis_mismatch")
    if benchmark_timing is not None and python_timing != benchmark_timing:
        issues.append("timing_mismatch")

    comparable = len(issues) == 0
    gap = python_value - benchmark_value if comparable and benchmark_value is not None else pd.NA
    pct_gap = gap / benchmark_value if comparable and benchmark_value not in (None, 0) else pd.NA

    note_parts = []
    if benchmark_note:
        note_parts.append(benchmark_note)
    if issues:
        note_parts.append("Comparison blocked by: " + ", ".join(issues) + ".")

    return {
        "metric": metric,
        "python_value": python_value,
        "python_unit": python_unit,
        "python_currency": python_currency,
        "python_basis": python_basis,
        "python_timing_basis": python_timing,
        "benchmark_value": benchmark_value,
        "benchmark_unit": benchmark_unit,
        "benchmark_currency": benchmark_currency,
        "benchmark_basis": benchmark_basis,
        "benchmark_timing_basis": benchmark_timing,
        "comparable_flag": comparable,
        "reconciliation_status": "comparable" if comparable else "reference_only",
        "reconciliation_note": " ".join(note_parts).strip(),
        "gap": gap,
        "pct_gap": pct_gap,
    }


def _build_benchmark_comparison(
    incremental_profile: pd.DataFrame,
    simulation_summary: pd.DataFrame,
    workbook_data,
    project_currency: str,
) -> pd.DataFrame:
    benchmark_npv = _assumption_row(workbook_data, "benchmark_npv_excel")
    benchmark_irr = _assumption_row(workbook_data, "benchmark_irr_excel")
    expected_npv_row = _benchmark_row(workbook_data, "expected_npv")
    var_row = _benchmark_row(workbook_data, "var_5pct")
    cvar_row = _benchmark_row(workbook_data, "cvar_5pct")
    deterministic_issues: list[str] = []
    if abs(float(incremental_profile.attrs.get("initial_capex_year0_usd", 0.0)) - float(_assumption_row(workbook_data, "initial_capex_year0_usd")["value"])) > 1e-6:
        deterministic_issues.append("year0_capex_mismatch")
    if abs(float(incremental_profile.loc[incremental_profile["year"] == 1, "initial_capex_usd"].iloc[0]) - float(_assumption_row(workbook_data, "initial_capex_year1_usd")["value"])) > 1e-6:
        deterministic_issues.append("year1_capex_mismatch")
    if abs(float(incremental_profile.loc[incremental_profile["year"] == 2, "sustaining_capex_usd"].iloc[0]) - float(_assumption_row(workbook_data, "sustaining_capex_usd")["value"])) > 1e-6:
        deterministic_issues.append("sustaining_capex_mismatch")

    rows = [
        _reconciliation_row(
            metric="incremental_npv",
            python_value=npv_from_profile(incremental_profile),
            python_unit="USD",
            python_currency=project_currency,
            python_basis="incremental_expansion",
            python_timing="year0_initial_outlay_plus_discounted_year1_to_year15",
            benchmark_value=float(benchmark_npv["value"]),
            benchmark_unit=str(benchmark_npv["unit"]),
            benchmark_currency="USD",
            benchmark_basis="incremental_expansion",
            benchmark_timing="year0_initial_outlay_plus_discounted_year1_to_year15",
            benchmark_note=str(benchmark_npv["note"] or ""),
            issues=deterministic_issues.copy(),
        ),
        _reconciliation_row(
            metric="incremental_irr",
            python_value=irr_from_profile(incremental_profile),
            python_unit="decimal",
            python_currency=None,
            python_basis="incremental_expansion",
            python_timing="year0_initial_outlay_plus_discounted_year1_to_year15",
            benchmark_value=float(benchmark_irr["value"]),
            benchmark_unit=str(benchmark_irr["unit"]),
            benchmark_currency=None,
            benchmark_basis="incremental_expansion",
            benchmark_timing="year0_initial_outlay_plus_discounted_year1_to_year15",
            benchmark_note=str(benchmark_irr["note"] or ""),
            issues=deterministic_issues.copy(),
        ),
        _reconciliation_row(
            metric="expected_npv",
            python_value=_summary_value(simulation_summary, "expected_npv_usd"),
            python_unit="USD",
            python_currency=project_currency,
            python_basis="total_project_expanded_operation",
            python_timing="year0_initial_outlay_plus_discounted_year1_to_year15",
            benchmark_value=float(expected_npv_row["value"]),
            benchmark_unit=str(expected_npv_row["unit"]),
            benchmark_currency=expected_npv_row["currency"],
            benchmark_basis=str(expected_npv_row["valuation_basis"]),
            benchmark_timing=str(expected_npv_row["timing_basis"]),
            benchmark_note=str(expected_npv_row["note"]),
            issues=["stochastic_design_mismatch"],
        ),
        _reconciliation_row(
            metric="var_5pct",
            python_value=_summary_value(simulation_summary, "var_usd"),
            python_unit="USD",
            python_currency=project_currency,
            python_basis="total_project_expanded_operation",
            python_timing="year0_initial_outlay_plus_discounted_year1_to_year15",
            benchmark_value=float(var_row["value"]),
            benchmark_unit=str(var_row["unit"]),
            benchmark_currency=var_row["currency"],
            benchmark_basis=str(var_row["valuation_basis"]),
            benchmark_timing=str(var_row["timing_basis"]),
            benchmark_note=str(var_row["note"]),
            issues=["stochastic_design_mismatch"],
        ),
        _reconciliation_row(
            metric="cvar_5pct",
            python_value=_summary_value(simulation_summary, "cvar_usd"),
            python_unit="USD",
            python_currency=project_currency,
            python_basis="total_project_expanded_operation",
            python_timing="year0_initial_outlay_plus_discounted_year1_to_year15",
            benchmark_value=float(cvar_row["value"]),
            benchmark_unit=str(cvar_row["unit"]),
            benchmark_currency=cvar_row["currency"],
            benchmark_basis=str(cvar_row["valuation_basis"]),
            benchmark_timing=str(cvar_row["timing_basis"]),
            benchmark_note=str(cvar_row["note"]),
            issues=["stochastic_design_mismatch"],
        ),
    ]
    return pd.DataFrame(rows)


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
    incremental_profile = build_incremental_expansion_profile(workbook_data.annual_inputs, params)
    distribution, simulation_summary = run_monte_carlo(workbook_data.annual_inputs, params, sim_config)

    simulation_distribution = distribution.copy()
    simulation_distribution["scenario_id"] = "mc_base"
    simulation_distribution["scenario_name"] = "Monte Carlo Base"
    simulation_distribution["valuation_basis"] = "total_project_expanded_operation"

    scenario_dim, fact_annual_metrics, fact_scenario_kpis = build_multi_scenario_outputs(
        annual_inputs=workbook_data.annual_inputs,
        params=params,
        scenario_registry=config["portfolio_bi"]["deterministic_scenarios"],
    )
    fact_annual_metrics["category"] = fact_annual_metrics["metric"].map(METRIC_CATEGORY_MAP)

    benchmark_comparison = _build_benchmark_comparison(
        incremental_profile=incremental_profile,
        simulation_summary=simulation_summary,
        workbook_data=workbook_data,
        project_currency=str(config["project"]["currency"]),
    )
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
    powerbi_measure_catalog = build_powerbi_measure_catalog()
    dim_year = build_year_dimension(
        project_years=workbook_data.annual_inputs["year"].tolist(),
        start_calendar_year=int(config["project"]["project_start_calendar_year"]),
    )
    simulation_percentiles = _build_simulation_percentiles(simulation_distribution, config["portfolio_bi"]["simulation_percentiles"])

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    outputs = {
        "powerbi_measure_catalog": output_dir / "powerbi_measure_catalog.csv",
        "simulation_summary": output_dir / "simulation_summary.csv",
        "simulation_percentiles": output_dir / "simulation_percentiles.csv",
        "benchmark_comparison": output_dir / "benchmark_comparison.csv",
        "dim_year": output_dir / "dim_year.csv",
        "dim_metric": output_dir / "dim_metric.csv",
        "dim_scenario": output_dir / "dim_scenario.csv",
        "fact_annual_metrics": output_dir / "fact_annual_metrics.csv",
        "fact_scenario_kpis": output_dir / "fact_scenario_kpis.csv",
        "fact_simulation_distribution": output_dir / "fact_simulation_distribution.csv",
        "fact_tornado_sensitivity": output_dir / "fact_tornado_sensitivity.csv",
        "fact_heatmap_price_grade": output_dir / "fact_heatmap_price_grade.csv",
    }

    powerbi_measure_catalog.to_csv(outputs["powerbi_measure_catalog"], index=False)
    simulation_summary.to_csv(outputs["simulation_summary"], index=False)
    simulation_percentiles.to_csv(outputs["simulation_percentiles"], index=False)
    benchmark_comparison.to_csv(outputs["benchmark_comparison"], index=False)
    dim_year.to_csv(outputs["dim_year"], index=False)
    metric_catalog.to_csv(outputs["dim_metric"], index=False)
    scenario_dim.to_csv(outputs["dim_scenario"], index=False)
    fact_annual_metrics.to_csv(outputs["fact_annual_metrics"], index=False)
    fact_scenario_kpis.to_csv(outputs["fact_scenario_kpis"], index=False)
    simulation_distribution.to_csv(outputs["fact_simulation_distribution"], index=False)
    fact_tornado_sensitivity.to_csv(outputs["fact_tornado_sensitivity"], index=False)
    fact_heatmap_price_grade.to_csv(outputs["fact_heatmap_price_grade"], index=False)
    return outputs
