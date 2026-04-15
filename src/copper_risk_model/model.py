"""Deterministic mining valuation model."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import brentq


LB_PER_TONNE = 2204.62


@dataclass(frozen=True)
class ScenarioParameters:
    payable_rate: float
    tc_rc_usd_per_lb: float
    mine_cost_usd_per_tonne: float
    plant_cost_usd_per_tonne: float
    g_and_a_cost_usd_per_tonne: float
    base_unit_cost_usd_per_tonne: float
    expansion_unit_cost_usd_per_tonne: float
    income_tax_rate: float
    royalty_rate: float
    special_levy_rate: float
    wacc: float
    annual_sustaining_capex_usd: float
    initial_capex_schedule_usd: dict[int, float]
    working_capital_ratio: float
    uplift_pct: float
    logistic_midpoint: float
    logistic_steepness: float

    @property
    def cash_tax_proxy_rate(self) -> float:
        """Tax proxy aligned with the workbook cash-flow chain."""
        return self.income_tax_rate

    @property
    def base_site_cost_usd_per_tonne(self) -> float:
        return self.base_unit_cost_usd_per_tonne or (
            self.mine_cost_usd_per_tonne + self.plant_cost_usd_per_tonne + self.g_and_a_cost_usd_per_tonne
        )


def _as_year_vector(value: float | np.ndarray, size: int) -> np.ndarray:
    vector = np.asarray(value, dtype=float)
    if vector.ndim == 0:
        return np.full(size, float(vector), dtype=float)
    if vector.shape != (size,):
        raise ValueError(f"Expected yearly factor with shape ({size},) but received {vector.shape}.")
    return vector


def _initial_capex_year0(params: ScenarioParameters, capex_factor: float = 1.0) -> float:
    return float(params.initial_capex_schedule_usd.get(0, 0.0) * capex_factor)


def _annual_capex_schedule(years: pd.Series, params: ScenarioParameters, capex_factor: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    initial_capex = np.array([params.initial_capex_schedule_usd.get(int(year), 0.0) for year in years], dtype=float)
    sustaining_capex = np.array(
        [params.annual_sustaining_capex_usd if int(year) >= 2 else 0.0 for year in years],
        dtype=float,
    )
    total_capex = (initial_capex + sustaining_capex) * capex_factor
    return initial_capex * capex_factor, sustaining_capex * capex_factor, total_capex


def _working_capital_delta(
    revenue_usd: pd.Series, working_capital_ratio: float
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    working_capital_balance = revenue_usd * working_capital_ratio
    working_capital_investment = working_capital_balance.diff().fillna(working_capital_balance.iloc[0])
    working_capital_release = pd.Series(0.0, index=revenue_usd.index, dtype=float)
    if not working_capital_release.empty:
        working_capital_release.iloc[-1] = -working_capital_balance.iloc[-1]
    working_capital_delta = working_capital_investment + working_capital_release
    return working_capital_balance, working_capital_investment, working_capital_release, working_capital_delta


def _build_operating_profile(
    annual_inputs: pd.DataFrame,
    params: ScenarioParameters,
    tonnes: np.ndarray,
    unit_cost_usd_per_tonne: float,
    price_factor: float | np.ndarray,
    grade_factor: float | np.ndarray,
    recovery_factor: float | np.ndarray,
    opex_factor: float | np.ndarray,
) -> pd.DataFrame:
    df = annual_inputs.copy()
    size = len(df)
    price_vector = _as_year_vector(price_factor, size)
    grade_vector = _as_year_vector(grade_factor, size)
    recovery_vector = _as_year_vector(recovery_factor, size)
    opex_vector = _as_year_vector(opex_factor, size)

    df["tonnes_processed"] = tonnes
    df["scenario_price_usd_per_lb"] = df["copper_price_usd_per_lb"] * price_vector
    df["scenario_grade"] = (df["base_head_grade"] * grade_vector).clip(lower=0.0)
    df["scenario_recovery"] = (df["base_recovery"] * recovery_vector).clip(lower=0.0, upper=1.0)
    df["scenario_net_price_usd_per_lb"] = df["scenario_price_usd_per_lb"] * params.payable_rate - params.tc_rc_usd_per_lb
    df["copper_fine_lb"] = df["tonnes_processed"] * df["scenario_grade"] * df["scenario_recovery"] * LB_PER_TONNE
    df["gross_revenue_usd"] = df["copper_fine_lb"] * df["scenario_price_usd_per_lb"]
    df["payable_revenue_usd"] = df["gross_revenue_usd"] * params.payable_rate
    df["tcrc_usd"] = df["copper_fine_lb"] * params.tc_rc_usd_per_lb
    df["revenue_usd"] = df["payable_revenue_usd"] - df["tcrc_usd"]
    df["unit_opex_usd_per_tonne"] = unit_cost_usd_per_tonne * opex_vector
    df["opex_usd"] = df["tonnes_processed"] * df["unit_opex_usd_per_tonne"]
    df["ebitda_usd"] = df["revenue_usd"] - df["opex_usd"]
    df["taxes_usd"] = np.where(df["ebitda_usd"] > 0, df["ebitda_usd"] * params.cash_tax_proxy_rate, 0.0)
    df["operating_cash_flow_usd"] = df["ebitda_usd"] - df["taxes_usd"]
    return df


def build_base_operation_profile(
    annual_inputs: pd.DataFrame,
    params: ScenarioParameters,
    price_factor: float | np.ndarray = 1.0,
    grade_factor: float | np.ndarray = 1.0,
    recovery_factor: float | np.ndarray = 1.0,
    opex_factor: float | np.ndarray = 1.0,
) -> pd.DataFrame:
    df = _build_operating_profile(
        annual_inputs=annual_inputs,
        params=params,
        tonnes=annual_inputs["base_processed_tonnes"].to_numpy(dtype=float),
        unit_cost_usd_per_tonne=params.base_site_cost_usd_per_tonne,
        price_factor=price_factor,
        grade_factor=grade_factor,
        recovery_factor=recovery_factor,
        opex_factor=opex_factor,
    )
    df = df.rename(columns={"tonnes_processed": "base_processed_tonnes"})
    df["capex_usd"] = 0.0
    df["initial_capex_usd"] = 0.0
    df["sustaining_capex_usd"] = 0.0
    _, wc_investment, wc_release, wc_delta = _working_capital_delta(df["revenue_usd"], params.working_capital_ratio)
    df["working_capital_investment_usd"] = wc_investment
    df["working_capital_release_usd"] = wc_release
    df["working_capital_delta_usd"] = wc_delta
    df["free_cash_flow_usd"] = df["operating_cash_flow_usd"] - df["working_capital_delta_usd"]
    df["applied_wacc"] = params.wacc
    df["discount_factor"] = 1.0 / np.power(1.0 + params.wacc, df["year"])
    df["discounted_fcf_usd"] = df["free_cash_flow_usd"] * df["discount_factor"]
    df.attrs["initial_capex_year0_usd"] = 0.0
    return df


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
    size = len(df)
    years = df["year"].to_numpy(dtype=float)
    throughput_vector = _as_year_vector(throughput_factor, size)
    logistic_term = 1.0 / (1.0 + np.exp(-params.logistic_steepness * (years - params.logistic_midpoint)))
    expanded_tonnes = df["base_processed_tonnes"].to_numpy(dtype=float) * throughput_vector * (1.0 + params.uplift_pct * logistic_term)

    df = _build_operating_profile(
        annual_inputs=df,
        params=params,
        tonnes=expanded_tonnes,
        unit_cost_usd_per_tonne=params.expansion_unit_cost_usd_per_tonne,
        price_factor=price_factor,
        grade_factor=grade_factor,
        recovery_factor=recovery_factor,
        opex_factor=opex_factor,
    )
    df = df.rename(columns={"tonnes_processed": "expanded_tonnes"})
    df["base_processed_tonnes"] = annual_inputs["base_processed_tonnes"].to_numpy(dtype=float)
    initial_capex, sustaining_capex, total_capex = _annual_capex_schedule(
        df["year"], params, float(np.asarray(capex_factor, dtype=float))
    )
    df["initial_capex_usd"] = initial_capex
    df["sustaining_capex_usd"] = sustaining_capex
    df["capex_usd"] = total_capex
    _, wc_investment, wc_release, wc_delta = _working_capital_delta(df["revenue_usd"], params.working_capital_ratio)
    df["working_capital_investment_usd"] = wc_investment
    df["working_capital_release_usd"] = wc_release
    df["working_capital_delta_usd"] = wc_delta
    df["free_cash_flow_usd"] = df["operating_cash_flow_usd"] - df["capex_usd"] - df["working_capital_delta_usd"]
    applied_wacc = params.wacc if wacc_override is None else wacc_override
    df["applied_wacc"] = applied_wacc
    df["discount_factor"] = 1.0 / np.power(1.0 + applied_wacc, df["year"])
    df["discounted_fcf_usd"] = df["free_cash_flow_usd"] * df["discount_factor"]
    df.attrs["initial_capex_year0_usd"] = _initial_capex_year0(params, float(np.asarray(capex_factor, dtype=float)))
    return df


def build_incremental_expansion_profile(
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
    expanded = build_expansion_profile(
        annual_inputs=annual_inputs,
        params=params,
        price_factor=price_factor,
        grade_factor=grade_factor,
        recovery_factor=recovery_factor,
        throughput_factor=throughput_factor,
        opex_factor=opex_factor,
        capex_factor=capex_factor,
        wacc_override=wacc_override,
    )
    base = build_base_operation_profile(
        annual_inputs=annual_inputs,
        params=params,
        price_factor=price_factor,
        grade_factor=grade_factor,
        recovery_factor=recovery_factor,
        opex_factor=opex_factor,
    )

    incremental = pd.DataFrame({"year": annual_inputs["year"].to_numpy(dtype=int)})
    incremental["base_processed_tonnes"] = annual_inputs["base_processed_tonnes"].to_numpy(dtype=float)
    incremental["expanded_tonnes"] = expanded["expanded_tonnes"].to_numpy(dtype=float)
    incremental["scenario_price_usd_per_lb"] = expanded["scenario_price_usd_per_lb"].to_numpy(dtype=float)
    incremental["scenario_grade"] = expanded["scenario_grade"].to_numpy(dtype=float)
    incremental["scenario_recovery"] = expanded["scenario_recovery"].to_numpy(dtype=float)
    incremental["scenario_net_price_usd_per_lb"] = expanded["scenario_net_price_usd_per_lb"].to_numpy(dtype=float)
    incremental["copper_fine_lb"] = expanded["copper_fine_lb"].to_numpy(dtype=float) - base["copper_fine_lb"].to_numpy(dtype=float)
    incremental["revenue_usd"] = expanded["revenue_usd"].to_numpy(dtype=float) - base["revenue_usd"].to_numpy(dtype=float)
    incremental["opex_usd"] = expanded["opex_usd"].to_numpy(dtype=float) - base["opex_usd"].to_numpy(dtype=float)
    incremental["ebitda_usd"] = expanded["ebitda_usd"].to_numpy(dtype=float) - base["ebitda_usd"].to_numpy(dtype=float)
    incremental["taxes_usd"] = expanded["taxes_usd"].to_numpy(dtype=float) - base["taxes_usd"].to_numpy(dtype=float)
    incremental["operating_cash_flow_usd"] = (
        expanded["operating_cash_flow_usd"].to_numpy(dtype=float) - base["operating_cash_flow_usd"].to_numpy(dtype=float)
    )
    incremental["initial_capex_usd"] = expanded["initial_capex_usd"].to_numpy(dtype=float)
    incremental["sustaining_capex_usd"] = expanded["sustaining_capex_usd"].to_numpy(dtype=float)
    incremental["capex_usd"] = expanded["capex_usd"].to_numpy(dtype=float)
    working_capital_balance = incremental["revenue_usd"] * params.working_capital_ratio
    working_capital_investment = working_capital_balance.copy()
    working_capital_release = pd.Series(0.0, index=incremental.index, dtype=float)
    if not working_capital_release.empty:
        working_capital_investment.iloc[-1] = 0.0
        working_capital_release.iloc[-1] = -working_capital_balance.iloc[-1]
    incremental["working_capital_investment_usd"] = working_capital_investment
    incremental["working_capital_release_usd"] = working_capital_release
    incremental["working_capital_delta_usd"] = working_capital_investment + working_capital_release
    incremental["free_cash_flow_usd"] = (
        incremental["operating_cash_flow_usd"] - incremental["capex_usd"] - incremental["working_capital_delta_usd"]
    )
    applied_wacc = params.wacc if wacc_override is None else wacc_override
    incremental["applied_wacc"] = applied_wacc
    incremental["discount_factor"] = 1.0 / np.power(1.0 + applied_wacc, incremental["year"])
    incremental["discounted_fcf_usd"] = incremental["free_cash_flow_usd"] * incremental["discount_factor"]
    incremental.attrs["initial_capex_year0_usd"] = expanded.attrs["initial_capex_year0_usd"]
    return incremental


def cash_flows_from_profile(profile: pd.DataFrame) -> np.ndarray:
    initial_capex_year0 = float(profile.attrs.get("initial_capex_year0_usd", 0.0))
    return np.concatenate(([-initial_capex_year0], profile["free_cash_flow_usd"].to_numpy(dtype=float)))


def npv_from_profile(profile: pd.DataFrame) -> float:
    initial_capex_year0 = float(profile.attrs.get("initial_capex_year0_usd", 0.0))
    return float(-initial_capex_year0 + profile["discounted_fcf_usd"].sum())


def irr_from_profile(profile: pd.DataFrame) -> float:
    cash_flows = cash_flows_from_profile(profile)
    if np.all(cash_flows >= 0) or np.all(cash_flows <= 0):
        return float("nan")

    def npv_at_rate(rate: float) -> float:
        periods = np.arange(cash_flows.size, dtype=float)
        return float(np.sum(cash_flows / np.power(1.0 + rate, periods)))

    grid = np.linspace(-0.95, 5.0, 256)
    values = np.array([npv_at_rate(rate) for rate in grid])
    sign_changes = np.where(np.signbit(values[:-1]) != np.signbit(values[1:]))[0]
    if sign_changes.size == 0:
        return float("nan")

    index = int(sign_changes[0])
    return float(brentq(npv_at_rate, grid[index], grid[index + 1]))
