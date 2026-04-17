"""Deterministic scenarios, sensitivity, and BI-oriented analytical outputs."""

from __future__ import annotations

from typing import Iterable

import pandas as pd

from .model import (
    ScenarioParameters,
    build_expansion_profile,
    cash_flows_from_profile,
    irr_from_profile,
    npv_from_profile,
)


DEFAULT_SCENARIO_VALUES = {
    "price_factor": 1.0,
    "grade_factor": 1.0,
    "recovery_factor": 1.0,
    "throughput_factor": 1.0,
    "opex_factor": 1.0,
    "capex_factor": 1.0,
    "wacc_shift_bps": 0.0,
}


def profile_to_long(profile: pd.DataFrame, scenario_id: str, scenario_name: str, scenario_category: str) -> pd.DataFrame:
    metric_columns = [
        "base_processed_tonnes",
        "expanded_tonnes",
        "scenario_price_usd_per_lb",
        "scenario_grade",
        "scenario_recovery",
        "scenario_net_price_usd_per_lb",
        "copper_fine_lb",
        "gross_revenue_usd",
        "payable_revenue_usd",
        "tcrc_usd",
        "revenue_usd",
        "unit_opex_usd_per_tonne",
        "opex_usd",
        "ebitda_usd",
        "cash_tax_proxy_usd",
        "operating_cash_flow_usd",
        "initial_capex_usd",
        "sustaining_capex_usd",
        "capex_usd",
        "working_capital_investment_usd",
        "working_capital_release_usd",
        "working_capital_delta_usd",
        "free_cash_flow_usd",
        "discounted_fcf_usd",
    ]
    long_df = profile.melt(id_vars=["year"], value_vars=metric_columns, var_name="metric", value_name="value")
    long_df["scenario_id"] = scenario_id
    long_df["scenario_name"] = scenario_name
    long_df["scenario_category"] = scenario_category
    return long_df


def summarize_profile(profile: pd.DataFrame, scenario_id: str, scenario_name: str, scenario_category: str) -> pd.DataFrame:
    cumulative_fcf = cash_flows_from_profile(profile).cumsum()
    payback_years = profile.loc[cumulative_fcf[1:] >= 0, "year"]
    payback_year = int(payback_years.iloc[0]) if not payback_years.empty else None
    peak_revenue_year = int(profile.loc[profile["revenue_usd"].idxmax(), "year"])
    peak_fcf_year = int(profile.loc[profile["free_cash_flow_usd"].idxmax(), "year"])
    total_revenue = float(profile["revenue_usd"].sum())
    total_ebitda = float(profile["ebitda_usd"].sum())
    kpis = [
        ("total_revenue_usd", total_revenue),
        ("total_ebitda_usd", total_ebitda),
        ("total_opex_usd", float(profile["opex_usd"].sum())),
        ("total_operating_cash_flow_usd", float(profile["operating_cash_flow_usd"].sum())),
        ("total_capex_usd", float(profile.attrs.get("initial_capex_year0_usd", 0.0) + profile["capex_usd"].sum())),
        ("total_free_cash_flow_usd", float(profile["free_cash_flow_usd"].sum())),
        ("average_processed_tonnes", float(profile["expanded_tonnes"].mean())),
        ("average_copper_fine_lb", float(profile["copper_fine_lb"].mean())),
        ("average_net_price_usd_per_lb", float(profile["scenario_net_price_usd_per_lb"].mean())),
        ("average_head_grade", float(profile["scenario_grade"].mean())),
        ("average_recovery", float(profile["scenario_recovery"].mean())),
        ("average_unit_opex_usd_per_tonne", float(profile["unit_opex_usd_per_tonne"].mean())),
        ("ebitda_margin_proxy", float(total_ebitda / total_revenue) if total_revenue else 0.0),
        ("scenario_npv_usd", npv_from_profile(profile)),
        ("scenario_irr", irr_from_profile(profile)),
        ("peak_revenue_year", peak_revenue_year),
        ("peak_fcf_year", peak_fcf_year),
        ("payback_year", payback_year),
    ]
    return pd.DataFrame(
        {
            "scenario_id": scenario_id,
            "scenario_name": scenario_name,
            "scenario_category": scenario_category,
            "metric": [metric for metric, _ in kpis],
            "value": [value for _, value in kpis],
        }
    )


def build_multi_scenario_outputs(
    annual_inputs: pd.DataFrame,
    params: ScenarioParameters,
    scenario_registry: Iterable[dict],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    scenario_dim_records = []
    annual_frames = []
    kpi_frames = []

    for order, scenario in enumerate(scenario_registry, start=1):
        scenario_id = scenario["scenario_id"]
        scenario_name = scenario["scenario_name"]
        scenario_category = scenario["category"]
        profile = build_expansion_profile(
            annual_inputs=annual_inputs,
            params=params,
            price_factor=float(scenario.get("price_factor", 1.0)),
            grade_factor=float(scenario.get("grade_factor", 1.0)),
            recovery_factor=float(scenario.get("recovery_factor", 1.0)),
            throughput_factor=float(scenario.get("throughput_factor", 1.0)),
            opex_factor=float(scenario.get("opex_factor", 1.0)),
            capex_factor=float(scenario.get("capex_factor", 1.0)),
            wacc_override=float(params.wacc + scenario.get("wacc_shift_bps", 0.0) / 10000),
        )
        profile["scenario_id"] = scenario_id
        profile["scenario_name"] = scenario_name
        profile["scenario_category"] = scenario_category

        annual_frames.append(profile_to_long(profile, scenario_id, scenario_name, scenario_category))
        kpi_frames.append(summarize_profile(profile, scenario_id, scenario_name, scenario_category))
        scenario_dim_records.append(
            {
                "scenario_id": scenario_id,
                "scenario_name": scenario_name,
                "scenario_category": scenario_category,
                "description": scenario.get("description"),
                "sort_order": order,
                "price_factor": float(scenario.get("price_factor", 1.0)),
                "grade_factor": float(scenario.get("grade_factor", 1.0)),
                "recovery_factor": float(scenario.get("recovery_factor", 1.0)),
                "throughput_factor": float(scenario.get("throughput_factor", 1.0)),
                "opex_factor": float(scenario.get("opex_factor", 1.0)),
                "capex_factor": float(scenario.get("capex_factor", 1.0)),
                "wacc_shift_bps": float(scenario.get("wacc_shift_bps", 0.0)),
            }
        )

    return (
        pd.DataFrame(scenario_dim_records),
        pd.concat(annual_frames, ignore_index=True),
        pd.concat(kpi_frames, ignore_index=True),
    )


def build_tornado_table(
    annual_inputs: pd.DataFrame,
    params: ScenarioParameters,
    tornado_specs: Iterable[dict],
) -> pd.DataFrame:
    base_profile = build_expansion_profile(annual_inputs=annual_inputs, params=params)
    base_npv = npv_from_profile(base_profile)
    records = []

    for spec in tornado_specs:
        driver = spec["driver"]
        label = spec["label"]
        base_value = spec["base_value"]
        for direction, shock in [("down", spec["shock_down"]), ("up", spec["shock_up"])]:
            values = DEFAULT_SCENARIO_VALUES.copy()
            values[driver] = base_value + shock
            wacc_override = params.wacc + values["wacc_shift_bps"] / 10000
            profile = build_expansion_profile(
                annual_inputs=annual_inputs,
                params=params,
                price_factor=values["price_factor"],
                grade_factor=values["grade_factor"],
                recovery_factor=values["recovery_factor"],
                throughput_factor=values["throughput_factor"],
                opex_factor=values["opex_factor"],
                capex_factor=values["capex_factor"],
                wacc_override=wacc_override,
            )
            npv_value = npv_from_profile(profile)
            records.append(
                {
                    "driver": driver,
                    "driver_label": label,
                    "direction": direction,
                    "shock": shock,
                    "scenario_value": values[driver],
                    "npv_usd": npv_value,
                    "impact_vs_base_usd": npv_value - base_npv,
                    "abs_impact_vs_base_usd": abs(npv_value - base_npv),
                }
            )

    tornado = pd.DataFrame(records)
    tornado["impact_rank"] = tornado.groupby("driver")["abs_impact_vs_base_usd"].transform("max")
    tornado = tornado.sort_values(["impact_rank", "driver_label", "direction"], ascending=[False, True, True]).reset_index(drop=True)
    return tornado


def build_price_grade_heatmap(
    annual_inputs: pd.DataFrame,
    params: ScenarioParameters,
    price_factors: Iterable[float],
    grade_factors: Iterable[float],
    recovery_factor: float,
    throughput_factor: float,
    opex_factor: float,
    capex_factor: float,
    wacc_shift_bps: float,
) -> pd.DataFrame:
    records = []
    wacc_override = params.wacc + wacc_shift_bps / 10000

    for price_factor in price_factors:
        for grade_factor in grade_factors:
            profile = build_expansion_profile(
                annual_inputs=annual_inputs,
                params=params,
                price_factor=float(price_factor),
                grade_factor=float(grade_factor),
                recovery_factor=float(recovery_factor),
                throughput_factor=float(throughput_factor),
                opex_factor=float(opex_factor),
                capex_factor=float(capex_factor),
                wacc_override=wacc_override,
            )
            npv_value = npv_from_profile(profile)
            records.append(
                {
                    "price_factor": float(price_factor),
                    "grade_factor": float(grade_factor),
                    "recovery_factor": float(recovery_factor),
                    "throughput_factor": float(throughput_factor),
                    "opex_factor": float(opex_factor),
                    "capex_factor": float(capex_factor),
                    "wacc_shift_bps": float(wacc_shift_bps),
                    "npv_usd": npv_value,
                    "npv_sign": "Positive" if npv_value >= 0 else "Negative",
                }
            )

    return pd.DataFrame(records)


def build_year_dimension(project_years: Iterable[int], start_calendar_year: int) -> pd.DataFrame:
    records = []
    for year in project_years:
        calendar_year = start_calendar_year + int(year) - 1
        if year <= 3:
            phase = "Ramp-up"
        elif year <= 10:
            phase = "Steady State"
        else:
            phase = "Mature Depletion"
        records.append(
            {
                "year": int(year),
                "calendar_year": int(calendar_year),
                "phase": phase,
                "year_label": f"Year {int(year)}",
            }
        )
    return pd.DataFrame(records)
