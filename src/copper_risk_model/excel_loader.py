"""Utilities to extract structured assumptions and benchmarks from the Excel model."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook


LB_PER_TONNE = 2204.62


@dataclass
class WorkbookData:
    annual_inputs: pd.DataFrame
    assumptions: pd.DataFrame
    historical_prices: pd.DataFrame
    operational_history: pd.DataFrame
    benchmark_metrics: pd.DataFrame
    benchmark_distribution: pd.DataFrame


def _series_from_rows(
    worksheet,
    year_col: int,
    value_col: int,
    row_start: int,
    row_end: int,
    metric_name: str,
    unit: str,
) -> pd.DataFrame:
    records = []
    for row in range(row_start, row_end + 1):
        year = worksheet.cell(row, year_col).value
        value = worksheet.cell(row, value_col).value
        if year is None or value is None:
            continue
        records.append(
            {
                "year": int(year),
                "metric": metric_name,
                "value": float(value),
                "unit": unit,
            }
        )
    return pd.DataFrame(records)


def load_workbook_data(workbook_path: str | Path) -> WorkbookData:
    workbook_path = Path(workbook_path)
    wb = load_workbook(workbook_path, data_only=True, keep_vba=True)

    market = wb["Market_Data"]
    empirical = wb["Empírical_Data"]
    expansion = wb["Expansion_Model"]
    monte_carlo = wb["Monte_carlo"]

    prices = _series_from_rows(market, 5, 6, 3, 17, "copper_price_usd_per_lb", "USD/lb")
    tonnes = _series_from_rows(market, 12, 13, 3, 17, "base_processed_tonnes", "tonnes")
    grade = _series_from_rows(market, 19, 20, 3, 17, "base_head_grade", "grade_decimal")
    recovery = _series_from_rows(market, 19, 20, 20, 34, "base_recovery", "recovery_decimal")

    annual_inputs = (
        prices.merge(tonnes[["year", "value"]].rename(columns={"value": "base_processed_tonnes"}), on="year")
        .merge(grade[["year", "value"]].rename(columns={"value": "base_head_grade"}), on="year")
        .merge(recovery[["year", "value"]].rename(columns={"value": "base_recovery"}), on="year")
        .rename(columns={"value": "copper_price_usd_per_lb"})
    )
    annual_inputs["net_price_usd_per_lb"] = annual_inputs["copper_price_usd_per_lb"] * 0.96 - 0.053

    assumptions = pd.DataFrame(
        [
            {"parameter": "mine_cost_usd_per_tonne", "value": float(market["F22"].value), "unit": "USD/t"},
            {"parameter": "plant_cost_usd_per_tonne", "value": float(market["F23"].value), "unit": "USD/t"},
            {"parameter": "g_and_a_cost_usd_per_tonne", "value": float(market["F24"].value), "unit": "USD/t"},
            {"parameter": "base_unit_cost_usd_per_tonne", "value": float(market["F25"].value), "unit": "USD/t"},
            {"parameter": "expansion_unit_cost_usd_per_tonne", "value": float(market["G25"].value), "unit": "USD/t"},
            {"parameter": "income_tax_rate", "value": float(market["M22"].value), "unit": "decimal"},
            {"parameter": "royalty_rate", "value": float(market["M23"].value), "unit": "decimal"},
            {"parameter": "special_levy_rate", "value": float(market["M24"].value), "unit": "decimal"},
            {"parameter": "wacc", "value": float(market["M25"].value), "unit": "decimal"},
            {"parameter": "working_capital_ratio", "value": float(market["M26"].value), "unit": "decimal"},
            {"parameter": "payable_rate", "value": float(market["F29"].value), "unit": "decimal"},
            {"parameter": "tc_rc_usd_per_lb", "value": float(market["F30"].value), "unit": "USD/lb"},
            {"parameter": "initial_capex_year0_usd", "value": float(market["M30"].value) * 1_000_000, "unit": "USD"},
            {"parameter": "initial_capex_year1_usd", "value": float(market["M31"].value) * 1_000_000, "unit": "USD"},
            {"parameter": "sustaining_capex_usd", "value": 10_000_000.0, "unit": "USD"},
            {"parameter": "expansion_uplift_pct", "value": float(expansion["B1"].value), "unit": "decimal"},
            {"parameter": "expansion_midpoint_year", "value": float(expansion["D1"].value), "unit": "year"},
            {"parameter": "expansion_steepness", "value": float(expansion["E1"].value), "unit": "decimal"},
            {"parameter": "benchmark_npv_excel", "value": float(expansion["L99"].value), "unit": "PEN"},
            {"parameter": "benchmark_irr_excel", "value": float(expansion["L101"].value), "unit": "decimal"},
            {"parameter": "mu_price_returns", "value": float(empirical["P26"].value), "unit": "decimal"},
            {"parameter": "sigma_price_returns", "value": float(empirical["P29"].value), "unit": "decimal"},
            {"parameter": "grade_trend_slope", "value": float(empirical["I40"].value), "unit": "grade_decimal"},
            {"parameter": "grade_trend_intercept", "value": float(empirical["J40"].value), "unit": "grade_decimal"},
            {"parameter": "average_recovery", "value": float(empirical["L39"].value), "unit": "decimal"},
            {"parameter": "annual_decline_rate", "value": float(empirical["O42"].value), "unit": "decimal"},
        ]
    )

    historical_price_records = []
    for row in range(3, 24):
        year = empirical.cell(row, 1).value
        usd_per_mt = empirical.cell(row, 2).value
        usd_per_lb = empirical.cell(row, 4).value
        log_return = empirical.cell(row, 16).value
        if year is None:
            continue
        historical_price_records.append(
            {
                "calendar_year": int(year),
                "copper_price_usd_per_mt": float(usd_per_mt),
                "copper_price_usd_per_lb": float(usd_per_lb),
                "log_return": None if log_return is None else float(log_return),
            }
        )
    historical_prices = pd.DataFrame(historical_price_records)

    operational_records = []
    for row in range(44, 55):
        calendar_year = empirical.cell(row, 1).value
        grade_decimal = empirical.cell(row, 3).value
        recovery_decimal = empirical.cell(row, 5).value
        if calendar_year is None:
            continue
        operational_records.append(
            {
                "calendar_year": int(calendar_year),
                "head_grade": float(grade_decimal),
                "recovery": float(recovery_decimal),
            }
        )
    operational_history = pd.DataFrame(operational_records)

    benchmark_metrics = pd.DataFrame(
        [
            {"metric": "expected_npv", "value": float(monte_carlo["H17"].value), "unit": "PEN"},
            {"metric": "median_npv", "value": float(monte_carlo["H20"].value), "unit": "PEN"},
            {"metric": "std_npv", "value": float(monte_carlo["H23"].value), "unit": "PEN"},
            {"metric": "min_npv", "value": float(monte_carlo["H26"].value), "unit": "PEN"},
            {"metric": "max_npv", "value": float(monte_carlo["H29"].value), "unit": "PEN"},
            {"metric": "cv_npv", "value": float(monte_carlo["H32"].value), "unit": "ratio"},
            {"metric": "var_5pct", "value": float(monte_carlo["H35"].value), "unit": "PEN"},
            {"metric": "cvar_5pct", "value": float(monte_carlo["H38"].value), "unit": "PEN"},
        ]
    )

    distribution_records = []
    for row in range(17, 10017):
        npv_sorted = monte_carlo.cell(row, 11).value
        cumulative_probability = monte_carlo.cell(row, 12).value
        if npv_sorted is None or cumulative_probability is None:
            continue
        distribution_records.append(
            {
                "npv_sorted": float(npv_sorted),
                "cumulative_probability": float(cumulative_probability),
            }
        )
    benchmark_distribution = pd.DataFrame(distribution_records)

    return WorkbookData(
        annual_inputs=annual_inputs,
        assumptions=assumptions,
        historical_prices=historical_prices,
        operational_history=operational_history,
        benchmark_metrics=benchmark_metrics,
        benchmark_distribution=benchmark_distribution,
    )
