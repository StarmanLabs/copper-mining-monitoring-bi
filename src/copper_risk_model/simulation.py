"""Monte Carlo simulation and risk metrics."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import truncnorm

from .model import ScenarioParameters, build_expansion_profile


@dataclass(frozen=True)
class SimulationConfig:
    iterations: int
    random_seed: int
    var_alpha: float
    sigma_price_returns: float
    grade_cv: float
    recovery_cv: float
    price_path_autocorrelation: float = 0.55
    grade_lower_bound: float = 0.85
    grade_upper_bound: float = 1.15
    recovery_lower_bound: float = 0.92
    recovery_upper_bound: float = 1.08


def _truncated_normal_samples(
    rng: np.random.Generator,
    mean: float,
    sd: float,
    lower: float,
    upper: float,
    size: int | tuple[int, ...],
) -> np.ndarray:
    if sd <= 0:
        return np.full(size, mean, dtype=float)
    a = (lower - mean) / sd
    b = (upper - mean) / sd
    return truncnorm.rvs(a, b, loc=mean, scale=sd, size=size, random_state=rng)


def simulate_price_paths(
    base_prices: np.ndarray,
    config: SimulationConfig,
    rng: np.random.Generator,
) -> np.ndarray:
    """Generate annual copper price paths with autocorrelated deck-centered lognormal shocks.

    The workbook already contains an explicit annual price deck, so the stochastic
    engine perturbs each project year around that deck instead of extrapolating a
    long-run directional commodity trend. A simple AR(1)-style dependence in log
    deviations makes the paths temporally coherent without pretending to estimate
    a structural commodity regime model.
    """

    year_count = base_prices.size
    sigma = max(float(config.sigma_price_returns), 0.0)
    if sigma == 0.0:
        return np.repeat(base_prices[None, :], config.iterations, axis=0)

    rho = float(np.clip(config.price_path_autocorrelation, 0.0, 0.95))
    long_run_mean = -0.5 * sigma**2
    innovation_sd = sigma * np.sqrt(1.0 - rho**2)

    log_shocks = np.empty((config.iterations, year_count), dtype=float)
    log_shocks[:, 0] = rng.normal(loc=long_run_mean, scale=sigma, size=config.iterations)
    for year_index in range(1, year_count):
        innovations = rng.normal(loc=0.0, scale=innovation_sd, size=config.iterations)
        log_shocks[:, year_index] = long_run_mean + rho * (log_shocks[:, year_index - 1] - long_run_mean) + innovations
    path_factors = np.exp(log_shocks)
    return base_prices[None, :] * path_factors


def sample_grade_factors(config: SimulationConfig, rng: np.random.Generator) -> np.ndarray:
    """Project-level grade uncertainty is modeled as one multiplier per simulation."""

    return _truncated_normal_samples(
        rng=rng,
        mean=1.0,
        sd=config.grade_cv,
        lower=config.grade_lower_bound,
        upper=config.grade_upper_bound,
        size=config.iterations,
    )


def sample_recovery_paths(
    base_recovery: np.ndarray,
    config: SimulationConfig,
    rng: np.random.Generator,
) -> np.ndarray:
    """Recovery varies year by year because plant performance can drift around the baseline."""

    recovery_factors = _truncated_normal_samples(
        rng=rng,
        mean=1.0,
        sd=config.recovery_cv,
        lower=config.recovery_lower_bound,
        upper=config.recovery_upper_bound,
        size=(config.iterations, base_recovery.size),
    )
    return np.clip(base_recovery[None, :] * recovery_factors, 0.0, 1.0)


def _working_capital_delta_matrix(revenue: np.ndarray, working_capital_ratio: float) -> np.ndarray:
    working_capital_balance = revenue * working_capital_ratio
    working_capital_delta = np.zeros_like(working_capital_balance)
    working_capital_delta[:, 0] = working_capital_balance[:, 0]
    working_capital_delta[:, 1:] = working_capital_balance[:, 1:] - working_capital_balance[:, :-1]
    working_capital_delta[:, -1] = working_capital_delta[:, -1] - working_capital_balance[:, -1]
    return working_capital_delta


def run_monte_carlo(
    annual_inputs: pd.DataFrame,
    params: ScenarioParameters,
    config: SimulationConfig,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(config.random_seed)
    base_profile = build_expansion_profile(annual_inputs=annual_inputs, params=params)
    base_prices = annual_inputs["copper_price_usd_per_lb"].to_numpy(dtype=float)
    base_grade = annual_inputs["base_head_grade"].to_numpy(dtype=float)
    tonnes = base_profile["expanded_tonnes"].to_numpy(dtype=float)
    discount_factor = base_profile["discount_factor"].to_numpy(dtype=float)
    capex = base_profile["capex_usd"].to_numpy(dtype=float)
    initial_capex_year0 = float(base_profile.attrs.get("initial_capex_year0_usd", 0.0))

    scenario_prices = simulate_price_paths(base_prices=base_prices, config=config, rng=rng)
    grade_factors = sample_grade_factors(config=config, rng=rng)
    scenario_grade = np.clip(base_grade[None, :] * grade_factors[:, None], 0.0, None)
    scenario_recovery = sample_recovery_paths(
        base_recovery=annual_inputs["base_recovery"].to_numpy(dtype=float),
        config=config,
        rng=rng,
    )

    net_price = scenario_prices * params.payable_rate - params.tc_rc_usd_per_lb
    copper_fine_lb = tonnes[None, :] * scenario_grade * scenario_recovery * 2204.62
    payable_revenue = copper_fine_lb * scenario_prices * params.payable_rate
    tcrc = copper_fine_lb * params.tc_rc_usd_per_lb
    revenue = payable_revenue - tcrc
    opex = tonnes[None, :] * params.expansion_unit_cost_usd_per_tonne
    ebitda = revenue - opex
    taxes = np.where(ebitda > 0, ebitda * params.cash_tax_proxy_rate, 0.0)
    operating_cash_flow = ebitda - taxes
    working_capital_delta = _working_capital_delta_matrix(revenue, params.working_capital_ratio)
    free_cash_flow = operating_cash_flow - capex[None, :] - working_capital_delta
    npv_values = -initial_capex_year0 + (free_cash_flow * discount_factor[None, :]).sum(axis=1)

    distribution = pd.DataFrame(
        {
            "iteration": np.arange(1, config.iterations + 1, dtype=int),
            "average_price_usd_per_lb": scenario_prices.mean(axis=1),
            "terminal_price_usd_per_lb": scenario_prices[:, -1],
            "price_path_std_usd_per_lb": scenario_prices.std(axis=1, ddof=0),
            "grade_factor": grade_factors,
            "average_recovery": scenario_recovery.mean(axis=1),
            "recovery_std": scenario_recovery.std(axis=1, ddof=0),
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
