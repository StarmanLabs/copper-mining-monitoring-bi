"""Builders and metadata exports for the advanced valuation and risk appendix."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from .annual_appendix_inputs import (
    AppendixInputBundle,
    build_annual_appendix_dataset_catalog,
    build_annual_appendix_field_catalog,
    load_appendix_input_bundle,
)
from .benchmark_reconciliation import build_benchmark_comparison, build_benchmark_scope_catalog
from .bi_semantic import build_kpi_catalog, build_metric_catalog
from .excel_loader import WorkbookData
from .file_outputs import write_csv_output
from .scenario_analysis import (
    build_multi_scenario_outputs,
    build_price_grade_heatmap,
    build_tornado_table,
    build_year_dimension,
)
from .simulation import SimulationConfig, run_monte_carlo
from .valuation_model import ScenarioParameters, build_incremental_expansion_profile

MONTE_CARLO_EXPORT_DECIMALS = 5
MONTE_CARLO_DISTRIBUTION_NPV_DECIMALS = 2


@dataclass(frozen=True)
class AdvancedAppendixContext:
    """Runtime context for the secondary valuation and risk appendix."""

    config: dict
    annual_inputs: pd.DataFrame
    parameter_table: pd.DataFrame
    scenario_registry: list[dict]
    benchmark_metrics: pd.DataFrame | None
    params: ScenarioParameters
    simulation_config: SimulationConfig
    project_currency: str
    input_mode: str
    benchmark_mode: str
    input_source_label: str
    benchmark_source_label: str
    legacy_workbook_data: WorkbookData | None = None

    @property
    def workbook_data(self) -> WorkbookData | None:
        """Backward-compatible alias for the optional legacy workbook payload."""

        return self.legacy_workbook_data


def _load_yaml(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _context_from_bundle(config: dict, bundle: AppendixInputBundle) -> AdvancedAppendixContext:
    return AdvancedAppendixContext(
        config=config,
        annual_inputs=bundle.annual_inputs,
        parameter_table=bundle.parameter_table,
        scenario_registry=bundle.scenario_registry,
        benchmark_metrics=bundle.benchmark_metrics,
        params=bundle.params,
        simulation_config=bundle.simulation_config,
        project_currency=bundle.project_currency,
        input_mode=bundle.input_mode,
        benchmark_mode=bundle.benchmark_mode,
        input_source_label=bundle.input_source_label,
        benchmark_source_label=bundle.benchmark_source_label,
        legacy_workbook_data=bundle.legacy_workbook_data,
    )


def load_advanced_appendix_context(
    config_path: str | Path = "config/project.yaml",
    input_mode: str | None = None,
    benchmark_mode: str | None = None,
    data_dir: str | Path | None = None,
) -> AdvancedAppendixContext:
    """Load appendix inputs from the canonical annual path or the legacy adapter."""

    config = _load_yaml(config_path)
    bundle = load_appendix_input_bundle(
        config_path=config_path,
        input_mode=input_mode,
        benchmark_mode=benchmark_mode,
        data_dir=data_dir,
    )
    return _context_from_bundle(config, bundle)


def _build_simulation_percentiles(distribution: pd.DataFrame, percentiles: list[float]) -> pd.DataFrame:
    return pd.DataFrame(
        [{"percentile": percentile, "npv_usd": float(distribution["npv_usd"].quantile(percentile))} for percentile in percentiles]
    )


def _round_public_export_frame(frame: pd.DataFrame, *, decimals: int = MONTE_CARLO_EXPORT_DECIMALS) -> pd.DataFrame:
    """Round float-like export fields to avoid cross-platform noise in public artifacts."""

    rounded = frame.copy()
    for column_name in rounded.columns:
        series = rounded[column_name]
        if pd.api.types.is_float_dtype(series):
            rounded[column_name] = series.round(decimals)
            continue
        if series.dtype != "object":
            continue
        rounded[column_name] = series.map(
            lambda value: round(float(value), decimals)
            if isinstance(value, (float, np.floating)) and not pd.isna(value)
            else value
        )
    return rounded


def _annual_input_source_type(context: AdvancedAppendixContext) -> str:
    if context.input_mode == "canonical":
        return "canonical_annual_input_table"
    return "legacy_workbook_adapter"


def _annual_input_source_reference(context: AdvancedAppendixContext) -> str:
    if context.input_mode == "canonical":
        return "data/sample_data/annual_appendix/annual_appendix_inputs.csv"
    return "Legacy workbook annual adapter"


def _assumption_catalog_row(
    *,
    assumption_order: int,
    assumption_group: str,
    parameter_name: str,
    parameter_value: float | int,
    unit: str,
    source_type: str,
    source_reference: str,
    appendix_submodule: str,
    practical_use: str,
    limitation_note: str,
) -> dict[str, object]:
    return {
        "assumption_order": assumption_order,
        "assumption_group": assumption_group,
        "parameter_name": parameter_name,
        "parameter_value": parameter_value,
        "unit": unit,
        "source_type": source_type,
        "source_reference": source_reference,
        "appendix_submodule": appendix_submodule,
        "practical_use": practical_use,
        "limitation_note": limitation_note,
        "secondary_role_note": "Appendix assumptions support scenario and downside interpretation; they are not the main monthly operating model.",
    }


PARAMETER_ASSUMPTION_METADATA: dict[str, dict[str, object]] = {
    "payable_rate": {
        "assumption_order": 1,
        "assumption_group": "Deterministic valuation",
        "appendix_submodule": "Deterministic Valuation",
        "practical_use": "Realized price bridge from copper price to payable revenue.",
        "limitation_note": "This is a simplified commercial assumption carried into the public appendix flow.",
    },
    "tc_rc_usd_per_lb": {
        "assumption_order": 2,
        "assumption_group": "Deterministic valuation",
        "appendix_submodule": "Deterministic Valuation",
        "practical_use": "Commercial deduction between payable revenue and net realized price.",
        "limitation_note": "Used as a planning-style charge, not as a detailed commercial contract model.",
    },
    "income_tax_rate": {
        "assumption_order": 5,
        "assumption_group": "Deterministic valuation",
        "appendix_submodule": "Deterministic Valuation",
        "practical_use": "Cash-tax proxy applied to positive EBITDA in the public appendix flow.",
        "limitation_note": "The appendix uses a simplified tax proxy and does not claim full fiscal-regime realism.",
    },
    "royalty_rate": {
        "assumption_order": 6,
        "assumption_group": "Deterministic valuation",
        "appendix_submodule": "Deterministic Valuation",
        "practical_use": "Visible for benchmark transparency and model traceability.",
        "limitation_note": "Tracked for transparency but not applied in the current appendix cash-flow chain.",
    },
    "special_levy_rate": {
        "assumption_order": 7,
        "assumption_group": "Deterministic valuation",
        "appendix_submodule": "Deterministic Valuation",
        "practical_use": "Visible for benchmark transparency and model traceability.",
        "limitation_note": "Tracked for transparency but not applied in the current appendix cash-flow chain.",
    },
    "wacc": {
        "assumption_order": 8,
        "assumption_group": "Deterministic valuation",
        "appendix_submodule": "Deterministic Valuation",
        "practical_use": "Discount-rate anchor for deterministic and downside valuation summaries.",
        "limitation_note": "This is a planning discount rate, not a full capital-structure model.",
    },
    "initial_capex_year0_usd": {
        "assumption_order": 9,
        "assumption_group": "Deterministic valuation",
        "appendix_submodule": "Deterministic Valuation",
        "practical_use": "Year-0 outlay used in explicit NPV and IRR construction.",
        "limitation_note": "Kept explicit for transparency, but not presented as a full capex schedule.",
    },
    "working_capital_ratio": {
        "assumption_order": 12,
        "assumption_group": "Deterministic valuation",
        "appendix_submodule": "Deterministic Valuation",
        "practical_use": "Revenue-linked working-capital proxy for deterministic and incremental cash-flow treatment.",
        "limitation_note": "Working-capital handling is deliberately simplified for transparent planning-style comparison.",
    },
    "uplift_pct": {
        "assumption_order": 13,
        "assumption_group": "Deterministic valuation",
        "appendix_submodule": "Scenario Framing",
        "practical_use": "High-level throughput uplift used in the expanded-operation profile.",
        "limitation_note": "This is a stylized planning uplift, not a detailed mine-plan schedule.",
    },
    "logistic_midpoint": {
        "assumption_order": 14,
        "assumption_group": "Deterministic valuation",
        "appendix_submodule": "Scenario Framing",
        "practical_use": "Controls the timing of the stylized throughput ramp.",
        "limitation_note": "Ramp timing is intentionally simplified for scenario readability.",
    },
    "logistic_steepness": {
        "assumption_order": 15,
        "assumption_group": "Deterministic valuation",
        "appendix_submodule": "Scenario Framing",
        "practical_use": "Controls how quickly the stylized throughput ramp converges.",
        "limitation_note": "Ramp shape is intentionally simplified for scenario readability.",
    },
    "iterations": {
        "assumption_order": 16,
        "assumption_group": "Monte Carlo design",
        "appendix_submodule": "Monte Carlo Downside",
        "practical_use": "Controls simulation sample size for downside distribution estimates.",
        "limitation_note": "Higher iteration count improves numerical stability, not model realism.",
    },
    "random_seed": {
        "assumption_order": 17,
        "assumption_group": "Monte Carlo design",
        "appendix_submodule": "Monte Carlo Downside",
        "practical_use": "Keeps the public appendix reproducible across builds.",
        "limitation_note": "Reproducibility does not remove specification risk.",
    },
    "var_alpha": {
        "assumption_order": 18,
        "assumption_group": "Monte Carlo design",
        "appendix_submodule": "Monte Carlo Downside",
        "practical_use": "Tail percentile used for VaR and CVaR reporting.",
        "limitation_note": "Tail metrics remain planning-style downside indicators rather than asset-grade risk capital measures.",
    },
    "sigma_price_returns": {
        "assumption_order": 19,
        "assumption_group": "Monte Carlo design",
        "appendix_submodule": "Monte Carlo Downside",
        "practical_use": "Scales simulated copper-price variation around the base deck.",
        "limitation_note": "This is not a structural commodity-price model.",
    },
    "grade_cv": {
        "assumption_order": 20,
        "assumption_group": "Monte Carlo design",
        "appendix_submodule": "Monte Carlo Downside",
        "practical_use": "Adds public-safe grade dispersion to the downside distribution.",
        "limitation_note": "Dispersion remains stylized and should not be treated as an asset-grade ore-control model.",
    },
    "recovery_cv": {
        "assumption_order": 21,
        "assumption_group": "Monte Carlo design",
        "appendix_submodule": "Monte Carlo Downside",
        "practical_use": "Adds bounded recovery variation to the downside distribution.",
        "limitation_note": "Dispersion remains stylized and should not be treated as a plant-metallurgy forecast model.",
    },
    "price_path_autocorrelation": {
        "assumption_order": 22,
        "assumption_group": "Monte Carlo design",
        "appendix_submodule": "Monte Carlo Downside",
        "practical_use": "Smooths year-to-year price path persistence in the simulation.",
        "limitation_note": "Used for stylized downside continuity, not for market microstructure realism.",
    },
}


def _parameter_table_row(parameter_table: pd.DataFrame, parameter_name: str) -> pd.Series:
    return parameter_table.loc[parameter_table["parameter_name"] == parameter_name].iloc[0]


def _annual_input_row(
    *,
    context: AdvancedAppendixContext,
    assumption_order: int,
    assumption_group: str,
    parameter_name: str,
    parameter_value: float,
    unit: str,
    appendix_submodule: str,
    practical_use: str,
    limitation_note: str,
) -> dict[str, object]:
    return _assumption_catalog_row(
        assumption_order=assumption_order,
        assumption_group=assumption_group,
        parameter_name=parameter_name,
        parameter_value=parameter_value,
        unit=unit,
        source_type=_annual_input_source_type(context),
        source_reference=_annual_input_source_reference(context),
        appendix_submodule=appendix_submodule,
        practical_use=practical_use,
        limitation_note=limitation_note,
    )


def build_advanced_appendix_assumption_catalog(context: AdvancedAppendixContext) -> pd.DataFrame:
    """Return an explicit public-safe assumption register for the appendix."""

    rows = []
    for parameter_name, metadata in sorted(
        PARAMETER_ASSUMPTION_METADATA.items(),
        key=lambda item: int(item[1]["assumption_order"]),
    ):
        parameter_row = _parameter_table_row(context.parameter_table, parameter_name)
        rows.append(
            _assumption_catalog_row(
                assumption_order=int(metadata["assumption_order"]),
                assumption_group=str(metadata["assumption_group"]),
                parameter_name=parameter_name,
                parameter_value=float(parameter_row["value"]),
                unit=str(parameter_row["unit"]),
                source_type=str(parameter_row["source_type"]),
                source_reference=str(parameter_row["source_reference"]),
                appendix_submodule=str(metadata["appendix_submodule"]),
                practical_use=str(metadata["practical_use"]),
                limitation_note=str(metadata["limitation_note"]),
            )
        )

    sustaining_candidates = context.annual_inputs.loc[
        context.annual_inputs["sustaining_capex_usd"] > 0,
        "sustaining_capex_usd",
    ]
    annual_sustaining_capex = float(sustaining_candidates.iloc[0]) if not sustaining_candidates.empty else 0.0
    initial_capex_year1 = float(
        context.annual_inputs.loc[context.annual_inputs["year"] == 1, "initial_capex_usd"].iloc[0]
    )
    base_unit_cost = float(context.annual_inputs["base_unit_cost_usd_per_tonne"].iloc[0])
    expansion_unit_cost = float(context.annual_inputs["expansion_unit_cost_usd_per_tonne"].iloc[0])

    rows.extend(
        [
            _annual_input_row(
                context=context,
                assumption_order=3,
                assumption_group="Deterministic valuation",
                parameter_name="base_unit_cost_usd_per_tonne",
                parameter_value=base_unit_cost,
                unit="USD/t",
                appendix_submodule="Deterministic Valuation",
                practical_use="Base-operation unit cost reference for incremental comparison.",
                limitation_note="Yearly appendix cost logic is planning-facing and not a full cost accounting model.",
            ),
            _annual_input_row(
                context=context,
                assumption_order=4,
                assumption_group="Deterministic valuation",
                parameter_name="expansion_unit_cost_usd_per_tonne",
                parameter_value=expansion_unit_cost,
                unit="USD/t",
                appendix_submodule="Deterministic Valuation",
                practical_use="Expanded-operation unit cost reference for scenario comparison.",
                limitation_note="Values are table-driven by project year, but still simplified relative to cost-center accounting.",
            ),
            _annual_input_row(
                context=context,
                assumption_order=10,
                assumption_group="Deterministic valuation",
                parameter_name="initial_capex_year1_usd",
                parameter_value=initial_capex_year1,
                unit="USD",
                appendix_submodule="Deterministic Valuation",
                practical_use="Year-1 follow-on capex used in explicit NPV and IRR construction.",
                limitation_note="Yearly capex values live in the canonical annual input table and remain planning-style rather than engineering schedule detail.",
            ),
            _annual_input_row(
                context=context,
                assumption_order=11,
                assumption_group="Deterministic valuation",
                parameter_name="annual_sustaining_capex_usd",
                parameter_value=annual_sustaining_capex,
                unit="USD",
                appendix_submodule="Deterministic Valuation",
                practical_use="Recurring capex burden in the expansion case.",
                limitation_note="Recurring capex is table-driven by project year and intentionally simplified for public-safe appendix use.",
            ),
        ]
    )
    return pd.DataFrame(rows).sort_values("assumption_order").reset_index(drop=True)


def build_advanced_appendix_output_catalog(context: AdvancedAppendixContext) -> pd.DataFrame:
    """Describe appendix outputs without promoting them to the main repo story."""

    rows = [
        {
            "review_order": 1,
            "dataset_name": "annual_appendix_dataset_catalog",
            "source_file": "annual_appendix_dataset_catalog.csv",
            "appendix_submodule": "Appendix Input Governance",
            "output_role": "Annual input dataset catalog",
            "grain": "One row per annual appendix source table.",
            "primary_question_answered": "Which canonical annual appendix tables feed the secondary valuation and risk layer?",
            "when_to_use": "Use first when validating or adapting the appendix input contract.",
            "recommended_visual_or_review": "Read-only governance table.",
            "why_secondary": "It governs the appendix inputs rather than the main monthly monitoring layer.",
            "public_safe_boundary": "Documents a planning-style annual input contract, not a full mine-planning or finance platform.",
            "input_dependency_role": "appendix_input_governance",
            "generated_from": context.input_source_label,
        },
        {
            "review_order": 2,
            "dataset_name": "annual_appendix_field_catalog",
            "source_file": "annual_appendix_field_catalog.csv",
            "appendix_submodule": "Appendix Input Governance",
            "output_role": "Annual input field catalog",
            "grain": "One row per annual appendix input field.",
            "primary_question_answered": "What does each annual appendix field mean before running valuation, scenarios, or Monte Carlo?",
            "when_to_use": "Use before adapting the appendix to a private annual source.",
            "recommended_visual_or_review": "Read-only field dictionary.",
            "why_secondary": "It documents appendix input semantics rather than the core monthly BI model.",
            "public_safe_boundary": "Defines repository-governed annual contracts without implying ERP or planning-system integration.",
            "input_dependency_role": "appendix_input_governance",
            "generated_from": context.input_source_label,
        },
        {
            "review_order": 3,
            "dataset_name": "fact_scenario_kpis",
            "source_file": "fact_scenario_kpis.csv",
            "appendix_submodule": "Deterministic Scenario Comparison",
            "output_role": "Scenario KPI summary",
            "grain": "One row per scenario_id and KPI metric.",
            "primary_question_answered": "How do the main deterministic scenarios change NPV, IRR, throughput, margin proxy, and cash metrics?",
            "when_to_use": "Use after the monthly management story when you need planning-style scenario context.",
            "recommended_visual_or_review": "Scenario cards or a compact scenario comparison matrix.",
            "why_secondary": "These are strategic scenario summaries, not the operating control layer.",
            "public_safe_boundary": "Scenario definitions are synthetic and public-safe, not asset-grade investment cases.",
            "input_dependency_role": "canonical_or_adapter_driven_appendix_fact",
            "generated_from": context.input_source_label,
        },
        {
            "review_order": 4,
            "dataset_name": "fact_annual_metrics",
            "source_file": "fact_annual_metrics.csv",
            "appendix_submodule": "Deterministic Scenario Comparison",
            "output_role": "Annual scenario trend fact",
            "grain": "One row per scenario_id, year, and metric.",
            "primary_question_answered": "How do revenue, EBITDA, cash flow, capex, throughput, grade, and recovery evolve by year in each scenario?",
            "when_to_use": "Use only when an appendix reviewer needs yearly trend context behind a scenario headline.",
            "recommended_visual_or_review": "Annual lines or a focused trend matrix.",
            "why_secondary": "Annual scenario traces support strategy discussion but do not drive the monthly control story.",
            "public_safe_boundary": "Yearly profiles are planning-style reconstructions from governed annual inputs.",
            "input_dependency_role": "canonical_or_adapter_driven_appendix_fact",
            "generated_from": context.input_source_label,
        },
        {
            "review_order": 5,
            "dataset_name": "simulation_summary",
            "source_file": "simulation_summary.csv",
            "appendix_submodule": "Monte Carlo Downside",
            "output_role": "Downside summary",
            "grain": "One row per summary risk metric.",
            "primary_question_answered": "What do expected NPV, median NPV, loss probability, VaR, and CVaR look like under the public-safe downside design?",
            "when_to_use": "Use for downside framing after deterministic scenario review.",
            "recommended_visual_or_review": "KPI cards or a short downside table.",
            "why_secondary": "This is a communication appendix for uncertainty, not the primary BI layer.",
            "public_safe_boundary": "The simulation is stylized and should not be described as a structural commodity-risk engine.",
            "input_dependency_role": "canonical_or_adapter_driven_appendix_fact",
            "generated_from": context.input_source_label,
        },
        {
            "review_order": 6,
            "dataset_name": "fact_simulation_distribution",
            "source_file": "fact_simulation_distribution.csv",
            "appendix_submodule": "Monte Carlo Downside",
            "output_role": "Simulation distribution",
            "grain": "One row per simulation iteration.",
            "primary_question_answered": "How wide is the simulated NPV distribution?",
            "when_to_use": "Use when you need a histogram or percentiles behind the summary cards.",
            "recommended_visual_or_review": "Histogram only.",
            "why_secondary": "Iteration-level records are analytical support, not management control outputs.",
            "public_safe_boundary": "Distribution shape reflects the chosen public-safe simulation design rather than full asset uncertainty.",
            "input_dependency_role": "canonical_or_adapter_driven_appendix_fact",
            "generated_from": context.input_source_label,
        },
        {
            "review_order": 7,
            "dataset_name": "simulation_percentiles",
            "source_file": "simulation_percentiles.csv",
            "appendix_submodule": "Monte Carlo Downside",
            "output_role": "Percentile summary",
            "grain": "One row per percentile cutoff.",
            "primary_question_answered": "Where do key percentile checkpoints sit in the simulated NPV distribution?",
            "when_to_use": "Use for quick downside table readouts without loading the full iteration histogram.",
            "recommended_visual_or_review": "Percentile table.",
            "why_secondary": "Percentiles are supporting context for appendix interpretation.",
            "public_safe_boundary": "Percentiles inherit the same stylized simulation assumptions as the distribution.",
            "input_dependency_role": "canonical_or_adapter_driven_appendix_fact",
            "generated_from": context.input_source_label,
        },
        {
            "review_order": 8,
            "dataset_name": "fact_tornado_sensitivity",
            "source_file": "fact_tornado_sensitivity.csv",
            "appendix_submodule": "Sensitivity Framing",
            "output_role": "One-way sensitivity fact",
            "grain": "One row per driver and direction.",
            "primary_question_answered": "Which planning drivers move NPV the most in simple one-way shocks?",
            "when_to_use": "Use for investment-style discussion of dominant value drivers.",
            "recommended_visual_or_review": "Tornado chart.",
            "why_secondary": "This is strategic framing and should not displace the monthly operating narrative.",
            "public_safe_boundary": "Sensitivity shocks are simplified scenario shocks, not a full probabilistic factor model.",
            "input_dependency_role": "canonical_or_adapter_driven_appendix_fact",
            "generated_from": context.input_source_label,
        },
        {
            "review_order": 9,
            "dataset_name": "fact_heatmap_price_grade",
            "source_file": "fact_heatmap_price_grade.csv",
            "appendix_submodule": "Sensitivity Framing",
            "output_role": "Joint stress grid",
            "grain": "One row per price_factor and grade_factor combination.",
            "primary_question_answered": "How does NPV behave when copper price and head grade move together?",
            "when_to_use": "Use for compact stress-testing discussion after the scenario and downside readout.",
            "recommended_visual_or_review": "Heatmap.",
            "why_secondary": "This is an appendix stress surface, not an operating KPI view.",
            "public_safe_boundary": "The grid is a stylized stress-test surface and not a corporate planning system.",
            "input_dependency_role": "canonical_or_adapter_driven_appendix_fact",
            "generated_from": context.input_source_label,
        },
        {
            "review_order": 10,
            "dataset_name": "benchmark_comparison",
            "source_file": "benchmark_comparison.csv",
            "appendix_submodule": "Benchmark Transparency",
            "output_role": "Reconciliation audit",
            "grain": "One row per benchmarked metric.",
            "primary_question_answered": "Which appendix outputs are directly comparable to the benchmark source and which are reference-only?",
            "when_to_use": "Use whenever a reviewer asks about workbook parity or reconstruction credibility.",
            "recommended_visual_or_review": "Audit table.",
            "why_secondary": "Benchmarking explains appendix credibility, but it is not the repository's operating product.",
            "public_safe_boundary": "The table is intentionally explicit about mismatch and should not be used as a parity claim beyond its stated scope.",
            "input_dependency_role": "benchmark_transparency",
            "generated_from": context.benchmark_source_label,
        },
        {
            "review_order": 11,
            "dataset_name": "benchmark_scope_catalog",
            "source_file": "benchmark_scope_catalog.csv",
            "appendix_submodule": "Benchmark Transparency",
            "output_role": "Benchmark interpretation guide",
            "grain": "One row per benchmarked metric.",
            "primary_question_answered": "Why is each benchmark comparison direct or reference-only, and how should it be discussed?",
            "when_to_use": "Use alongside benchmark_comparison when explaining benchmark scope to reviewers.",
            "recommended_visual_or_review": "Read-only reference table.",
            "why_secondary": "This is interpretation metadata for the appendix audit, not a report table.",
            "public_safe_boundary": "It documents limits explicitly instead of implying full benchmark parity.",
            "input_dependency_role": "benchmark_transparency",
            "generated_from": context.benchmark_source_label,
        },
        {
            "review_order": 12,
            "dataset_name": "advanced_appendix_assumption_catalog",
            "source_file": "advanced_appendix_assumption_catalog.csv",
            "appendix_submodule": "Appendix Transparency",
            "output_role": "Assumption register",
            "grain": "One row per assumption or modeling parameter.",
            "primary_question_answered": "Which assumptions drive deterministic valuation and downside outputs, and what do they not claim?",
            "when_to_use": "Use when a reviewer wants explicit model assumptions before interpreting appendix outputs.",
            "recommended_visual_or_review": "Read-only reference table.",
            "why_secondary": "It documents appendix boundaries rather than driving the main BI flow.",
            "public_safe_boundary": "Assumptions are public-safe and intentionally simplified.",
            "input_dependency_role": "appendix_governance",
            "generated_from": context.input_source_label,
        },
        {
            "review_order": 13,
            "dataset_name": "appendix_kpi_catalog",
            "source_file": "appendix_kpi_catalog.csv",
            "appendix_submodule": "Appendix Semantics",
            "output_role": "Scenario KPI dictionary",
            "grain": "One row per deterministic appendix KPI.",
            "primary_question_answered": "What does each scenario KPI in fact_scenario_kpis mean and how should it be labeled?",
            "when_to_use": "Use when building appendix tables or reviewing scenario KPI meaning outside the report canvas.",
            "recommended_visual_or_review": "Read-only semantic reference.",
            "why_secondary": "It documents appendix semantics but does not change the main monthly BI narrative.",
            "public_safe_boundary": "It packages synthetic scenario KPI definitions without implying corporate planning-system depth.",
            "input_dependency_role": "appendix_governance",
            "generated_from": context.input_source_label,
        },
        {
            "review_order": 14,
            "dataset_name": "dim_year / dim_metric / dim_scenario",
            "source_file": "dim_year.csv; dim_metric.csv; dim_scenario.csv",
            "appendix_submodule": "Appendix Semantics",
            "output_role": "Shared appendix dimensions",
            "grain": "One row per year, annual metric, or scenario.",
            "primary_question_answered": "Which shared semantic selectors support the appendix facts?",
            "when_to_use": "Use only when building the appendix page in Power BI or Tableau.",
            "recommended_visual_or_review": "Modeling reference only.",
            "why_secondary": "These dimensions exist only to support the appendix page, not the core monthly model.",
            "public_safe_boundary": "They package appendix semantics without promoting the appendix to the main model center.",
            "input_dependency_role": "appendix_semantics",
            "generated_from": context.input_source_label,
        },
    ]
    return pd.DataFrame(rows)


def build_advanced_appendix_outputs(
    config_path: str | Path = "config/project.yaml",
    output_dir: str | Path = "outputs/bi",
    input_mode: str | None = None,
    benchmark_mode: str | None = None,
    data_dir: str | Path | None = None,
) -> dict[str, Path]:
    """Generate only the advanced appendix outputs and transparency catalogs."""

    context = load_advanced_appendix_context(
        config_path=config_path,
        input_mode=input_mode,
        benchmark_mode=benchmark_mode,
        data_dir=data_dir,
    )
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    incremental_profile = build_incremental_expansion_profile(context.annual_inputs, context.params)
    distribution, simulation_summary = run_monte_carlo(
        context.annual_inputs,
        context.params,
        context.simulation_config,
    )

    simulation_distribution = distribution.copy()
    simulation_distribution["scenario_id"] = "mc_base"
    simulation_distribution["scenario_name"] = "Monte Carlo Base"
    simulation_distribution["valuation_basis"] = "total_project_expanded_operation"

    scenario_dim, fact_annual_metrics, fact_scenario_kpis = build_multi_scenario_outputs(
        annual_inputs=context.annual_inputs,
        params=context.params,
        scenario_registry=context.scenario_registry,
    )
    metric_catalog = build_metric_catalog()
    scenario_kpi_catalog = build_kpi_catalog().assign(
        appendix_submodule="Deterministic Scenario Comparison",
        secondary_role_note="Scenario KPI definitions support the appendix and should not be mistaken for monthly operating KPIs.",
    )
    fact_annual_metrics["category"] = fact_annual_metrics["metric"].map(metric_catalog.set_index("metric")["category"])

    benchmark_comparison = build_benchmark_comparison(
        incremental_profile=incremental_profile,
        simulation_summary=simulation_summary,
        benchmark_metrics=context.benchmark_metrics,
        project_currency=context.project_currency,
        benchmark_source_label=context.benchmark_source_label,
    )
    benchmark_scope_catalog = build_benchmark_scope_catalog(benchmark_comparison)
    fact_tornado_sensitivity = build_tornado_table(
        annual_inputs=context.annual_inputs,
        params=context.params,
        tornado_specs=context.config["portfolio_bi"]["tornado"],
    )
    fact_heatmap_price_grade = build_price_grade_heatmap(
        annual_inputs=context.annual_inputs,
        params=context.params,
        price_factors=context.config["portfolio_bi"]["heatmap"]["price_factors"],
        grade_factors=context.config["portfolio_bi"]["heatmap"]["grade_factors"],
        recovery_factor=float(context.config["portfolio_bi"]["heatmap"]["recovery_factor"]),
        throughput_factor=float(context.config["portfolio_bi"]["heatmap"]["throughput_factor"]),
        opex_factor=float(context.config["portfolio_bi"]["heatmap"]["opex_factor"]),
        capex_factor=float(context.config["portfolio_bi"]["heatmap"]["capex_factor"]),
        wacc_shift_bps=float(context.config["portfolio_bi"]["heatmap"]["wacc_shift_bps"]),
    )
    start_calendar_year = (
        int(context.annual_inputs["calendar_year"].min())
        if "calendar_year" in context.annual_inputs.columns
        else int(context.config["project"]["project_start_calendar_year"])
    )
    dim_year = build_year_dimension(
        project_years=context.annual_inputs["year"].tolist(),
        start_calendar_year=start_calendar_year,
    )
    simulation_percentiles = _build_simulation_percentiles(
        simulation_distribution,
        context.config["portfolio_bi"]["simulation_percentiles"],
    )
    simulation_summary = _round_public_export_frame(simulation_summary)
    simulation_distribution = _round_public_export_frame(simulation_distribution)
    simulation_distribution["npv_usd"] = simulation_distribution["npv_usd"].round(MONTE_CARLO_DISTRIBUTION_NPV_DECIMALS)
    simulation_percentiles = _round_public_export_frame(simulation_percentiles)
    benchmark_comparison = _round_public_export_frame(benchmark_comparison)
    appendix_assumption_catalog = build_advanced_appendix_assumption_catalog(context)
    appendix_output_catalog = build_advanced_appendix_output_catalog(context)
    annual_appendix_dataset_catalog = build_annual_appendix_dataset_catalog()
    annual_appendix_field_catalog = build_annual_appendix_field_catalog()

    outputs = {
        "annual_appendix_dataset_catalog": output_dir / "annual_appendix_dataset_catalog.csv",
        "annual_appendix_field_catalog": output_dir / "annual_appendix_field_catalog.csv",
        "simulation_summary": output_dir / "simulation_summary.csv",
        "simulation_percentiles": output_dir / "simulation_percentiles.csv",
        "benchmark_comparison": output_dir / "benchmark_comparison.csv",
        "benchmark_scope_catalog": output_dir / "benchmark_scope_catalog.csv",
        "advanced_appendix_assumption_catalog": output_dir / "advanced_appendix_assumption_catalog.csv",
        "advanced_appendix_output_catalog": output_dir / "advanced_appendix_output_catalog.csv",
        "dim_year": output_dir / "dim_year.csv",
        "dim_metric": output_dir / "dim_metric.csv",
        "dim_scenario": output_dir / "dim_scenario.csv",
        "appendix_kpi_catalog": output_dir / "appendix_kpi_catalog.csv",
        "fact_annual_metrics": output_dir / "fact_annual_metrics.csv",
        "fact_scenario_kpis": output_dir / "fact_scenario_kpis.csv",
        "fact_simulation_distribution": output_dir / "fact_simulation_distribution.csv",
        "fact_tornado_sensitivity": output_dir / "fact_tornado_sensitivity.csv",
        "fact_heatmap_price_grade": output_dir / "fact_heatmap_price_grade.csv",
    }

    write_csv_output(annual_appendix_dataset_catalog, outputs["annual_appendix_dataset_catalog"])
    write_csv_output(annual_appendix_field_catalog, outputs["annual_appendix_field_catalog"])
    write_csv_output(simulation_summary, outputs["simulation_summary"])
    write_csv_output(simulation_percentiles, outputs["simulation_percentiles"])
    write_csv_output(benchmark_comparison, outputs["benchmark_comparison"])
    write_csv_output(benchmark_scope_catalog, outputs["benchmark_scope_catalog"])
    write_csv_output(appendix_assumption_catalog, outputs["advanced_appendix_assumption_catalog"])
    write_csv_output(appendix_output_catalog, outputs["advanced_appendix_output_catalog"])
    write_csv_output(dim_year, outputs["dim_year"])
    write_csv_output(metric_catalog, outputs["dim_metric"])
    write_csv_output(scenario_dim, outputs["dim_scenario"])
    write_csv_output(scenario_kpi_catalog, outputs["appendix_kpi_catalog"])
    write_csv_output(fact_annual_metrics, outputs["fact_annual_metrics"])
    write_csv_output(fact_scenario_kpis, outputs["fact_scenario_kpis"])
    write_csv_output(simulation_distribution, outputs["fact_simulation_distribution"])
    write_csv_output(fact_tornado_sensitivity, outputs["fact_tornado_sensitivity"])
    write_csv_output(fact_heatmap_price_grade, outputs["fact_heatmap_price_grade"])
    return outputs
