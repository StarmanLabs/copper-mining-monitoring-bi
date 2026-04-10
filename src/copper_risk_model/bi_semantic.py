"""Semantic layer helpers for BI exports."""

from __future__ import annotations

import pandas as pd


METRIC_CATEGORY_MAP = {
    "base_processed_tonnes": "Operations",
    "expanded_tonnes": "Operations",
    "scenario_price_usd_per_lb": "Market",
    "scenario_grade": "Geology",
    "scenario_recovery": "Metallurgy",
    "scenario_net_price_usd_per_lb": "Commercial",
    "copper_fine_lb": "Production",
    "revenue_usd": "Economics",
    "opex_usd": "Economics",
    "ebitda_usd": "Economics",
    "taxes_usd": "Economics",
    "operating_cash_flow_usd": "Cash Flow",
    "capex_usd": "Investment",
    "working_capital_delta_usd": "Working Capital",
    "free_cash_flow_usd": "Cash Flow",
    "discounted_fcf_usd": "Valuation",
}


def build_metric_catalog() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"metric": "base_processed_tonnes", "display_name": "Base Processed Tonnes", "unit": "tonnes", "category": "Operations", "dashboard_page": "Operating Profile"},
            {"metric": "expanded_tonnes", "display_name": "Expanded Processed Tonnes", "unit": "tonnes", "category": "Operations", "dashboard_page": "Operating Profile"},
            {"metric": "scenario_price_usd_per_lb", "display_name": "Copper Price", "unit": "USD/lb", "category": "Market", "dashboard_page": "Drivers"},
            {"metric": "scenario_grade", "display_name": "Head Grade", "unit": "decimal", "category": "Geology", "dashboard_page": "Drivers"},
            {"metric": "scenario_recovery", "display_name": "Recovery", "unit": "decimal", "category": "Metallurgy", "dashboard_page": "Drivers"},
            {"metric": "scenario_net_price_usd_per_lb", "display_name": "Net Realized Price", "unit": "USD/lb", "category": "Commercial", "dashboard_page": "Drivers"},
            {"metric": "copper_fine_lb", "display_name": "Copper Fine Production", "unit": "lb", "category": "Production", "dashboard_page": "Operating Profile"},
            {"metric": "revenue_usd", "display_name": "Revenue", "unit": "USD", "category": "Economics", "dashboard_page": "Value Creation"},
            {"metric": "opex_usd", "display_name": "Operating Cost", "unit": "USD", "category": "Economics", "dashboard_page": "Value Creation"},
            {"metric": "ebitda_usd", "display_name": "EBITDA", "unit": "USD", "category": "Economics", "dashboard_page": "Value Creation"},
            {"metric": "taxes_usd", "display_name": "Taxes", "unit": "USD", "category": "Economics", "dashboard_page": "Value Creation"},
            {"metric": "operating_cash_flow_usd", "display_name": "Operating Cash Flow", "unit": "USD", "category": "Cash Flow", "dashboard_page": "Value Creation"},
            {"metric": "capex_usd", "display_name": "Capex", "unit": "USD", "category": "Investment", "dashboard_page": "Value Creation"},
            {"metric": "working_capital_delta_usd", "display_name": "Working Capital Delta", "unit": "USD", "category": "Working Capital", "dashboard_page": "Value Creation"},
            {"metric": "free_cash_flow_usd", "display_name": "Free Cash Flow", "unit": "USD", "category": "Cash Flow", "dashboard_page": "Value Creation"},
            {"metric": "discounted_fcf_usd", "display_name": "Discounted FCF", "unit": "USD", "category": "Valuation", "dashboard_page": "Executive View"},
        ]
    )


def build_kpi_catalog() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"metric": "python_base_npv_usd", "display_name": "Python Base NPV", "unit": "USD", "dashboard_page": "Executive View"},
            {"metric": "excel_benchmark_npv_pen", "display_name": "Excel Benchmark NPV", "unit": "PEN", "dashboard_page": "Benchmark"},
            {"metric": "python_expected_npv_usd", "display_name": "Expected NPV", "unit": "USD", "dashboard_page": "Executive View"},
            {"metric": "python_probability_of_loss", "display_name": "Probability of Loss", "unit": "ratio", "dashboard_page": "Executive View"},
            {"metric": "python_var_usd", "display_name": "VaR 5%", "unit": "USD", "dashboard_page": "Risk Distribution"},
            {"metric": "python_cvar_usd", "display_name": "CVaR 5%", "unit": "USD", "dashboard_page": "Risk Distribution"},
            {"metric": "base_npv_usd", "display_name": "Scenario NPV", "unit": "USD", "dashboard_page": "Scenario Comparison"},
            {"metric": "total_revenue_usd", "display_name": "Total Revenue", "unit": "USD", "dashboard_page": "Scenario Comparison"},
            {"metric": "total_ebitda_usd", "display_name": "Total EBITDA", "unit": "USD", "dashboard_page": "Scenario Comparison"},
            {"metric": "total_capex_usd", "display_name": "Total Capex", "unit": "USD", "dashboard_page": "Scenario Comparison"},
            {"metric": "total_free_cash_flow_usd", "display_name": "Total Free Cash Flow", "unit": "USD", "dashboard_page": "Scenario Comparison"},
            {"metric": "average_net_price_usd_per_lb", "display_name": "Average Net Price", "unit": "USD/lb", "dashboard_page": "Scenario Comparison"},
            {"metric": "average_head_grade", "display_name": "Average Head Grade", "unit": "decimal", "dashboard_page": "Scenario Comparison"},
            {"metric": "average_recovery", "display_name": "Average Recovery", "unit": "decimal", "dashboard_page": "Scenario Comparison"},
            {"metric": "peak_revenue_year", "display_name": "Peak Revenue Year", "unit": "year", "dashboard_page": "Scenario Comparison"},
            {"metric": "peak_fcf_year", "display_name": "Peak FCF Year", "unit": "year", "dashboard_page": "Scenario Comparison"},
            {"metric": "payback_year", "display_name": "Payback Year", "unit": "year", "dashboard_page": "Scenario Comparison"},
        ]
    )


def build_dashboard_pages() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"page_name": "Executive View", "goal": "Show value creation and headline downside risk.", "primary_dataset": "dashboard_kpis.csv"},
            {"page_name": "Scenario Comparison", "goal": "Compare base, upside, downside, and stress scenarios.", "primary_dataset": "fact_scenario_kpis.csv"},
            {"page_name": "Value Creation", "goal": "Track revenue, EBITDA, capex, and free cash flow by year.", "primary_dataset": "fact_annual_metrics.csv"},
            {"page_name": "Risk Distribution", "goal": "Show histogram, CDF, and tail metrics of NPV.", "primary_dataset": "fact_simulation_distribution.csv"},
            {"page_name": "Drivers", "goal": "Explain how price, grade, recovery, and throughput evolve.", "primary_dataset": "annual_inputs.csv"},
            {"page_name": "Sensitivity", "goal": "Show tornado and price-grade stress matrix.", "primary_dataset": "fact_tornado_sensitivity.csv"},
            {"page_name": "Benchmark", "goal": "Compare Python outputs against the Excel workbook.", "primary_dataset": "benchmark_comparison.csv"},
        ]
    )


def build_powerbi_measure_catalog() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "measure_name": "Base NPV",
                "table_name": "dashboard_kpis",
                "dax_template": 'Base NPV = CALCULATE(MAX(dashboard_kpis[value]), dashboard_kpis[metric] = "python_base_npv_usd")',
                "format_hint": "Currency",
            },
            {
                "measure_name": "Expected NPV",
                "table_name": "dashboard_kpis",
                "dax_template": 'Expected NPV = CALCULATE(MAX(dashboard_kpis[value]), dashboard_kpis[metric] = "python_expected_npv_usd")',
                "format_hint": "Currency",
            },
            {
                "measure_name": "Probability of Loss",
                "table_name": "dashboard_kpis",
                "dax_template": 'Probability of Loss = CALCULATE(MAX(dashboard_kpis[value]), dashboard_kpis[metric] = "python_probability_of_loss")',
                "format_hint": "Percentage",
            },
            {
                "measure_name": "Scenario NPV",
                "table_name": "fact_scenario_kpis",
                "dax_template": 'Scenario NPV = CALCULATE(SUM(fact_scenario_kpis[value]), fact_scenario_kpis[metric] = "base_npv_usd")',
                "format_hint": "Currency",
            },
            {
                "measure_name": "Scenario Revenue",
                "table_name": "fact_scenario_kpis",
                "dax_template": 'Scenario Revenue = CALCULATE(SUM(fact_scenario_kpis[value]), fact_scenario_kpis[metric] = "total_revenue_usd")',
                "format_hint": "Currency",
            },
            {
                "measure_name": "Tornado Impact",
                "table_name": "fact_tornado_sensitivity",
                "dax_template": "Tornado Impact = MAX(fact_tornado_sensitivity[impact_vs_base_usd])",
                "format_hint": "Currency",
            },
        ]
    )
