"""Deterministic mining valuation model."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


LB_PER_TONNE = 2204.62


@dataclass
class ScenarioParameters:
    payable_rate: float
    tc_rc_usd_per_lb: float
    expansion_unit_cost_usd_per_tonne: float
    tax_rate_total: float
    wacc: float
    annual_sustaining_capex_usd: float
    initial_capex_schedule_usd: dict[int, float]
    working_capital_ratio: float
    uplift_pct: float
    logistic_midpoint: float
    logistic_steepness: float


def build_expansion_profile(
    annual_inputs: pd.DataFrame,
    params: ScenarioParameters,
    price_factor: float | np.ndarray = 1.0,
    grade_factor: float | np.ndarray = 1.0,
    recovery_factor: float | np.ndarray = 1.0,
    throughput_factor: float | np.ndarray = 1.0,
    opex_factor: float | np.ndarray = 1.0,
    capex_factor: float | np.ndarray = 1.0,
    wacc_override: float | None = None,
) -> pd.DataFrame:
    df = annual_inputs.copy()
    years = df["year"].to_numpy(dtype=float)
    logistic_term = 1.0 / (1.0 + np.exp(-params.logistic_steepness * (years - params.logistic_midpoint)))

    df["expanded_tonnes"] = df["base_processed_tonnes"] * throughput_factor * (1.0 + params.uplift_pct * logistic_term)
    df["scenario_price_usd_per_lb"] = df["copper_price_usd_per_lb"] * price_factor
    df["scenario_grade"] = df["base_head_grade"] * grade_factor
    df["scenario_recovery"] = df["base_recovery"] * recovery_factor
    df["scenario_net_price_usd_per_lb"] = df["scenario_price_usd_per_lb"] * params.payable_rate - params.tc_rc_usd_per_lb
    df["copper_fine_lb"] = (
        df["expanded_tonnes"] * df["scenario_grade"] * df["scenario_recovery"] * LB_PER_TONNE
    )
    df["revenue_usd"] = df["copper_fine_lb"] * df["scenario_net_price_usd_per_lb"]
    df["opex_usd"] = df["expanded_tonnes"] * params.expansion_unit_cost_usd_per_tonne * opex_factor
    df["ebitda_usd"] = df["revenue_usd"] - df["opex_usd"]
    df["taxes_usd"] = np.where(df["ebitda_usd"] > 0, df["ebitda_usd"] * params.tax_rate_total, 0.0)
    df["operating_cash_flow_usd"] = df["ebitda_usd"] - df["taxes_usd"]

    capex = []
    for year in df["year"]:
        year_index = int(year) - 1
        initial = params.initial_capex_schedule_usd.get(year_index, 0.0)
        capex.append((initial + params.annual_sustaining_capex_usd) * capex_factor)
    df["capex_usd"] = capex

    working_capital_base = df["revenue_usd"] * params.working_capital_ratio
    working_capital_delta = working_capital_base.diff().fillna(working_capital_base.iloc[0])
    working_capital_delta.iloc[-1] = -working_capital_base.iloc[-1]
    df["working_capital_delta_usd"] = working_capital_delta
    df["free_cash_flow_usd"] = df["operating_cash_flow_usd"] - df["capex_usd"] - df["working_capital_delta_usd"]
    applied_wacc = params.wacc if wacc_override is None else wacc_override
    df["applied_wacc"] = applied_wacc
    df["discount_factor"] = 1.0 / np.power(1.0 + applied_wacc, df["year"])
    df["discounted_fcf_usd"] = df["free_cash_flow_usd"] * df["discount_factor"]
    return df


def npv_from_profile(profile: pd.DataFrame) -> float:
    return float(profile["discounted_fcf_usd"].sum() - profile["capex_usd"].iloc[0] * 0.0)


def irr_from_profile(profile: pd.DataFrame, initial_capex_year0: float) -> float:
    cash_flows = [-initial_capex_year0] + profile["free_cash_flow_usd"].tolist()
    return float(np.irr(cash_flows))
