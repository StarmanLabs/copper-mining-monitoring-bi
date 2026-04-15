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
    "gross_revenue_usd": "Economics",
    "payable_revenue_usd": "Economics",
    "tcrc_usd": "Commercial",
    "revenue_usd": "Economics",
    "unit_opex_usd_per_tonne": "Economics",
    "opex_usd": "Economics",
    "ebitda_usd": "Economics",
    "taxes_usd": "Economics",
    "operating_cash_flow_usd": "Cash Flow",
    "initial_capex_usd": "Investment",
    "sustaining_capex_usd": "Investment",
    "capex_usd": "Investment",
    "working_capital_investment_usd": "Working Capital",
    "working_capital_release_usd": "Working Capital",
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
            {"metric": "gross_revenue_usd", "display_name": "Gross Revenue", "unit": "USD", "category": "Economics", "dashboard_page": "Value Creation"},
            {"metric": "payable_revenue_usd", "display_name": "Payable Revenue", "unit": "USD", "category": "Economics", "dashboard_page": "Value Creation"},
            {"metric": "tcrc_usd", "display_name": "Treatment and Refining Charges", "unit": "USD", "category": "Commercial", "dashboard_page": "Value Creation"},
            {"metric": "revenue_usd", "display_name": "Revenue", "unit": "USD", "category": "Economics", "dashboard_page": "Value Creation"},
            {"metric": "unit_opex_usd_per_tonne", "display_name": "Unit Opex", "unit": "USD/t", "category": "Economics", "dashboard_page": "Value Creation"},
            {"metric": "opex_usd", "display_name": "Operating Cost", "unit": "USD", "category": "Economics", "dashboard_page": "Value Creation"},
            {"metric": "ebitda_usd", "display_name": "EBITDA", "unit": "USD", "category": "Economics", "dashboard_page": "Value Creation"},
            {"metric": "taxes_usd", "display_name": "Taxes", "unit": "USD", "category": "Economics", "dashboard_page": "Value Creation"},
            {"metric": "operating_cash_flow_usd", "display_name": "Operating Cash Flow", "unit": "USD", "category": "Cash Flow", "dashboard_page": "Value Creation"},
            {"metric": "initial_capex_usd", "display_name": "Initial Capex", "unit": "USD", "category": "Investment", "dashboard_page": "Value Creation"},
            {"metric": "sustaining_capex_usd", "display_name": "Sustaining Capex", "unit": "USD", "category": "Investment", "dashboard_page": "Value Creation"},
            {"metric": "capex_usd", "display_name": "Capex", "unit": "USD", "category": "Investment", "dashboard_page": "Value Creation"},
            {"metric": "working_capital_investment_usd", "display_name": "Working Capital Investment", "unit": "USD", "category": "Working Capital", "dashboard_page": "Value Creation"},
            {"metric": "working_capital_release_usd", "display_name": "Working Capital Release", "unit": "USD", "category": "Working Capital", "dashboard_page": "Value Creation"},
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
            {"metric": "base_irr", "display_name": "Scenario IRR", "unit": "decimal", "dashboard_page": "Scenario Comparison"},
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
                "measure_name": "Selected Scenario NPV",
                "table_name": "fact_scenario_kpis",
                "dax_template": 'Selected Scenario NPV = CALCULATE(MAX(fact_scenario_kpis[value]), fact_scenario_kpis[metric] = "base_npv_usd")',
                "format_hint": "Currency",
                "dashboard_page": "Executive Summary",
                "description": "Headline NPV for the selected deterministic scenario.",
            },
            {
                "measure_name": "Base Case NPV",
                "table_name": "fact_scenario_kpis",
                "dax_template": 'Base Case NPV = CALCULATE(MAX(fact_scenario_kpis[value]), fact_scenario_kpis[metric] = "base_npv_usd", dim_scenario[scenario_id] = "base")',
                "format_hint": "Currency",
                "dashboard_page": "Executive Summary",
                "description": "Reference NPV used for deltas and variance versus the selected scenario.",
            },
            {
                "measure_name": "Committee Downside NPV",
                "table_name": "fact_scenario_kpis",
                "dax_template": 'Committee Downside NPV = CALCULATE(MAX(fact_scenario_kpis[value]), fact_scenario_kpis[metric] = "base_npv_usd", dim_scenario[scenario_id] = "committee_downside")',
                "format_hint": "Currency",
                "dashboard_page": "Executive Summary",
                "description": "Hard downside deterministic case for investment committee framing.",
            },
            {
                "measure_name": "NPV Delta vs Base",
                "table_name": "fact_scenario_kpis",
                "dax_template": "NPV Delta vs Base = [Selected Scenario NPV] - [Base Case NPV]",
                "format_hint": "Currency",
                "dashboard_page": "Executive Summary",
                "description": "Change in scenario NPV relative to the base case.",
            },
            {
                "measure_name": "Selected Scenario IRR",
                "table_name": "fact_scenario_kpis",
                "dax_template": 'Selected Scenario IRR = CALCULATE(MAX(fact_scenario_kpis[value]), fact_scenario_kpis[metric] = "base_irr")',
                "format_hint": "Percentage",
                "dashboard_page": "Executive Summary",
                "description": "IRR for the selected deterministic scenario using explicit year-0 cash flows.",
            },
            {
                "measure_name": "Scenario Revenue",
                "table_name": "fact_scenario_kpis",
                "dax_template": 'Scenario Revenue = CALCULATE(MAX(fact_scenario_kpis[value]), fact_scenario_kpis[metric] = "total_revenue_usd")',
                "format_hint": "Currency",
                "dashboard_page": "Scenario Comparison",
                "description": "Total revenue over the project horizon for the selected scenario.",
            },
            {
                "measure_name": "Scenario EBITDA",
                "table_name": "fact_scenario_kpis",
                "dax_template": 'Scenario EBITDA = CALCULATE(MAX(fact_scenario_kpis[value]), fact_scenario_kpis[metric] = "total_ebitda_usd")',
                "format_hint": "Currency",
                "dashboard_page": "Scenario Comparison",
                "description": "Total EBITDA over the project horizon for the selected scenario.",
            },
            {
                "measure_name": "Scenario Free Cash Flow",
                "table_name": "fact_scenario_kpis",
                "dax_template": 'Scenario Free Cash Flow = CALCULATE(MAX(fact_scenario_kpis[value]), fact_scenario_kpis[metric] = "total_free_cash_flow_usd")',
                "format_hint": "Currency",
                "dashboard_page": "Scenario Comparison",
                "description": "Total free cash flow over the project horizon for the selected scenario.",
            },
            {
                "measure_name": "Scenario Capex",
                "table_name": "fact_scenario_kpis",
                "dax_template": 'Scenario Capex = CALCULATE(MAX(fact_scenario_kpis[value]), fact_scenario_kpis[metric] = "total_capex_usd")',
                "format_hint": "Currency",
                "dashboard_page": "Scenario Comparison",
                "description": "Total capex burden for the selected scenario.",
            },
            {
                "measure_name": "Scenario Payback Year",
                "table_name": "fact_scenario_kpis",
                "dax_template": 'Scenario Payback Year = CALCULATE(MAX(fact_scenario_kpis[value]), fact_scenario_kpis[metric] = "payback_year")',
                "format_hint": "Whole Number",
                "dashboard_page": "Scenario Comparison",
                "description": "Payback timing for the selected scenario, when available.",
            },
            {
                "measure_name": "Annual Revenue",
                "table_name": "fact_annual_metrics",
                "dax_template": 'Annual Revenue = CALCULATE(SUM(fact_annual_metrics[value]), fact_annual_metrics[metric] = "revenue_usd")',
                "format_hint": "Currency",
                "dashboard_page": "Annual Economics",
                "description": "Yearly revenue profile.",
            },
            {
                "measure_name": "Annual EBITDA",
                "table_name": "fact_annual_metrics",
                "dax_template": 'Annual EBITDA = CALCULATE(SUM(fact_annual_metrics[value]), fact_annual_metrics[metric] = "ebitda_usd")',
                "format_hint": "Currency",
                "dashboard_page": "Annual Economics",
                "description": "Yearly EBITDA profile.",
            },
            {
                "measure_name": "Annual Free Cash Flow",
                "table_name": "fact_annual_metrics",
                "dax_template": 'Annual Free Cash Flow = CALCULATE(SUM(fact_annual_metrics[value]), fact_annual_metrics[metric] = "free_cash_flow_usd")',
                "format_hint": "Currency",
                "dashboard_page": "Annual Economics",
                "description": "Yearly free cash flow profile.",
            },
            {
                "measure_name": "Annual Capex",
                "table_name": "fact_annual_metrics",
                "dax_template": 'Annual Capex = CALCULATE(SUM(fact_annual_metrics[value]), fact_annual_metrics[metric] = "capex_usd")',
                "format_hint": "Currency",
                "dashboard_page": "Annual Economics",
                "description": "Yearly capex profile.",
            },
            {
                "measure_name": "Annual Processed Tonnes",
                "table_name": "fact_annual_metrics",
                "dax_template": 'Annual Processed Tonnes = CALCULATE(SUM(fact_annual_metrics[value]), fact_annual_metrics[metric] = "expanded_tonnes")',
                "format_hint": "Whole Number",
                "dashboard_page": "Annual Economics",
                "description": "Expanded throughput by project year.",
            },
            {
                "measure_name": "Annual Net Price",
                "table_name": "fact_annual_metrics",
                "dax_template": 'Annual Net Price = CALCULATE(AVERAGE(fact_annual_metrics[value]), fact_annual_metrics[metric] = "scenario_net_price_usd_per_lb")',
                "format_hint": "Decimal Number",
                "dashboard_page": "Drivers",
                "description": "Net realized copper price per pound by year.",
            },
            {
                "measure_name": "Annual Head Grade %",
                "table_name": "fact_annual_metrics",
                "dax_template": 'Annual Head Grade % = CALCULATE(AVERAGE(fact_annual_metrics[value]), fact_annual_metrics[metric] = "scenario_grade") * 100',
                "format_hint": "Percentage",
                "dashboard_page": "Drivers",
                "description": "Head grade expressed as a percentage for charting.",
            },
            {
                "measure_name": "Annual Recovery %",
                "table_name": "fact_annual_metrics",
                "dax_template": 'Annual Recovery % = CALCULATE(AVERAGE(fact_annual_metrics[value]), fact_annual_metrics[metric] = "scenario_recovery") * 100',
                "format_hint": "Percentage",
                "dashboard_page": "Drivers",
                "description": "Metallurgical recovery expressed as a percentage for charting.",
            },
            {
                "measure_name": "Expected NPV",
                "table_name": "simulation_summary",
                "dax_template": 'Expected NPV = CALCULATE(MAX(simulation_summary[value]), simulation_summary[metric] = "expected_npv_usd")',
                "format_hint": "Currency",
                "dashboard_page": "Risk Distribution",
                "description": "Expected NPV from the Monte Carlo simulation.",
            },
            {
                "measure_name": "Median NPV",
                "table_name": "simulation_summary",
                "dax_template": 'Median NPV = CALCULATE(MAX(simulation_summary[value]), simulation_summary[metric] = "median_npv_usd")',
                "format_hint": "Currency",
                "dashboard_page": "Risk Distribution",
                "description": "Median NPV from the Monte Carlo simulation.",
            },
            {
                "measure_name": "Probability of Loss",
                "table_name": "simulation_summary",
                "dax_template": 'Probability of Loss = CALCULATE(MAX(simulation_summary[value]), simulation_summary[metric] = "probability_of_loss")',
                "format_hint": "Percentage",
                "dashboard_page": "Risk Distribution",
                "description": "Probability that simulated NPV is below zero.",
            },
            {
                "measure_name": "VaR 5%",
                "table_name": "simulation_summary",
                "dax_template": 'VaR 5% = CALCULATE(MAX(simulation_summary[value]), simulation_summary[metric] = "var_usd")',
                "format_hint": "Currency",
                "dashboard_page": "Risk Distribution",
                "description": "5th percentile Value at Risk from the simulation.",
            },
            {
                "measure_name": "CVaR 5%",
                "table_name": "simulation_summary",
                "dax_template": 'CVaR 5% = CALCULATE(MAX(simulation_summary[value]), simulation_summary[metric] = "cvar_usd")',
                "format_hint": "Currency",
                "dashboard_page": "Risk Distribution",
                "description": "Average outcome beyond the 5th percentile threshold.",
            },
            {
                "measure_name": "Tornado Impact",
                "table_name": "fact_tornado_sensitivity",
                "dax_template": "Tornado Impact = MAX(fact_tornado_sensitivity[impact_vs_base_usd])",
                "format_hint": "Currency",
                "dashboard_page": "Sensitivity",
                "description": "Directional impact versus the base case for a selected tornado bar.",
            },
        ]
    )
