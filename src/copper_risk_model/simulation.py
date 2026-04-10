"""Monte Carlo simulation and risk metrics."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import truncnorm

from .model import ScenarioParameters, build_expansion_profile


@dataclass
class SimulationConfig:
    iterations: int
    random_seed: int
    var_alpha: float
    mu_price_returns: float
    sigma_price_returns: float
    grade_cv: float
    recovery_cv: float


def _truncated_normal_samples(
    rng: np.random.Generator,
    mean: float,
    sd: float,
    lower: float,
    upper: float,
    size: int,
) -> np.ndarray:
    a = (lower - mean) / sd
    b = (upper - mean) / sd
    return truncnorm.rvs(a, b, loc=mean, scale=sd, size=size, random_state=rng)


def run_monte_carlo(
    annual_inputs: pd.DataFrame,
    params: ScenarioParameters,
    config: SimulationConfig,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(config.random_seed)
    price_shocks = rng.normal(
        loc=config.mu_price_returns - 0.5 * config.sigma_price_returns**2,
        scale=config.sigma_price_returns,
        size=config.iterations,
    )
    price_factors = np.exp(price_shocks)

    grade_factors = _truncated_normal_samples(
        rng=rng,
        mean=1.0,
        sd=config.grade_cv,
        lower=0.75,
        upper=1.25,
        size=config.iterations,
    )
    recovery_factors = _truncated_normal_samples(
        rng=rng,
        mean=1.0,
        sd=config.recovery_cv,
        lower=0.85,
        upper=1.15,
        size=config.iterations,
    )

    base_profile = build_expansion_profile(annual_inputs=annual_inputs, params=params)
    tonnes = base_profile["expanded_tonnes"].to_numpy(dtype=float)
    base_prices = annual_inputs["copper_price_usd_per_lb"].to_numpy(dtype=float)
    base_grade = annual_inputs["base_head_grade"].to_numpy(dtype=float)
    base_recovery = annual_inputs["base_recovery"].to_numpy(dtype=float)
    discount_factor = base_profile["discount_factor"].to_numpy(dtype=float)
    capex = base_profile["capex_usd"].to_numpy(dtype=float)

    scenario_prices = price_factors[:, None] * base_prices[None, :]
    scenario_grade = grade_factors[:, None] * base_grade[None, :]
    scenario_recovery = recovery_factors[:, None] * base_recovery[None, :]
    net_price = scenario_prices * params.payable_rate - params.tc_rc_usd_per_lb
    copper_fine_lb = tonnes[None, :] * scenario_grade * scenario_recovery * 2204.62
    revenue = copper_fine_lb * net_price
    opex = tonnes[None, :] * params.expansion_unit_cost_usd_per_tonne
    ebitda = revenue - opex
    taxes = np.where(ebitda > 0, ebitda * params.tax_rate_total, 0.0)
    operating_cash_flow = ebitda - taxes

    working_capital_base = revenue * params.working_capital_ratio
    working_capital_delta = np.zeros_like(working_capital_base)
    working_capital_delta[:, 0] = working_capital_base[:, 0]
    working_capital_delta[:, 1:] = working_capital_base[:, 1:] - working_capital_base[:, :-1]
    working_capital_delta[:, -1] = -working_capital_base[:, -1]

    free_cash_flow = operating_cash_flow - capex[None, :] - working_capital_delta
    npv_values = (free_cash_flow * discount_factor[None, :]).sum(axis=1)

    distribution = pd.DataFrame(
        {
            "iteration": np.arange(1, config.iterations + 1, dtype=int),
            "price_factor": price_factors,
            "grade_factor": grade_factors,
            "recovery_factor": recovery_factors,
            "npv_usd": npv_values,
        }
    )
    alpha = config.var_alpha
    var_threshold = float(distribution["npv_usd"].quantile(alpha))
    cvar_value = float(distribution.loc[distribution["npv_usd"] <= var_threshold, "npv_usd"].mean())

    summary = pd.DataFrame(
        [
            {"metric": "expected_npv_usd", "value": float(distribution["npv_usd"].mean())},
            {"metric": "median_npv_usd", "value": float(distribution["npv_usd"].median())},
            {"metric": "std_npv_usd", "value": float(distribution["npv_usd"].std(ddof=0))},
            {"metric": "min_npv_usd", "value": float(distribution["npv_usd"].min())},
            {"metric": "max_npv_usd", "value": float(distribution["npv_usd"].max())},
            {"metric": "probability_of_loss", "value": float((distribution["npv_usd"] < 0).mean())},
            {"metric": "var_alpha", "value": alpha},
            {"metric": "var_usd", "value": var_threshold},
            {"metric": "cvar_usd", "value": cvar_value},
        ]
    )
    return distribution, summary
