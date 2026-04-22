"""Benchmark transparency helpers for the advanced appendix."""

from __future__ import annotations

import pandas as pd

from .valuation_model import irr_from_profile, npv_from_profile


def _summary_value(summary: pd.DataFrame, metric: str) -> float:
    return float(summary.loc[summary["metric"] == metric, "value"].iloc[0])


def _benchmark_row(benchmark_metrics: pd.DataFrame, metric: str) -> pd.Series | None:
    matches = benchmark_metrics.loc[benchmark_metrics["metric"] == metric]
    if matches.empty:
        return None
    return matches.iloc[0]


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
    benchmark_source: str,
    benchmark_note: str,
    issues: list[str] | None = None,
) -> dict[str, object]:
    benchmark_unit = None if pd.isna(benchmark_unit) else benchmark_unit
    benchmark_currency = None if pd.isna(benchmark_currency) else benchmark_currency
    benchmark_basis = None if pd.isna(benchmark_basis) else benchmark_basis
    benchmark_timing = None if pd.isna(benchmark_timing) else benchmark_timing
    benchmark_note = "" if pd.isna(benchmark_note) else benchmark_note
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
    status = "reference_only"
    if comparable:
        material_gap = False
        if python_unit == "decimal" and gap is not pd.NA:
            material_gap = abs(float(gap)) > 0.01
        elif pct_gap is not pd.NA:
            material_gap = abs(float(pct_gap)) > 0.05
        status = "material_gap" if material_gap else "close_match"

    note_parts = []
    if benchmark_note:
        note_parts.append(benchmark_note)
    if comparable and status == "material_gap":
        note_parts.append("Direct comparison is valid, but the residual gap remains material.")
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
        "benchmark_source": benchmark_source,
        "comparability_class": "direct_comparison" if comparable else "reference_only",
        "comparable_flag": comparable,
        "reconciliation_status": status,
        "reconciliation_note": " ".join(note_parts).strip(),
        "gap": gap,
        "pct_gap": pct_gap,
    }


def build_benchmark_comparison(
    incremental_profile: pd.DataFrame,
    simulation_summary: pd.DataFrame,
    benchmark_metrics: pd.DataFrame | None,
    project_currency: str,
    benchmark_source_label: str,
    deterministic_issues: list[str] | None = None,
) -> pd.DataFrame:
    """Compare appendix outputs against explicit benchmark reference points."""

    deterministic_issues = [] if deterministic_issues is None else deterministic_issues
    benchmark_metrics = pd.DataFrame(columns=["metric"]) if benchmark_metrics is None else benchmark_metrics
    benchmark_npv = _benchmark_row(benchmark_metrics, "incremental_npv")
    benchmark_irr = _benchmark_row(benchmark_metrics, "incremental_irr")
    expected_npv_row = _benchmark_row(benchmark_metrics, "expected_npv")
    var_row = _benchmark_row(benchmark_metrics, "var_5pct")
    cvar_row = _benchmark_row(benchmark_metrics, "cvar_5pct")

    rows = [
        _reconciliation_row(
            metric="incremental_npv",
            python_value=npv_from_profile(incremental_profile),
            python_unit="USD",
            python_currency=project_currency,
            python_basis="incremental_expansion",
            python_timing="year0_initial_outlay_plus_discounted_year1_to_year15",
            benchmark_value=None if benchmark_npv is None else float(benchmark_npv["value"]),
            benchmark_unit=None if benchmark_npv is None else str(benchmark_npv["unit"]),
            benchmark_currency=None if benchmark_npv is None else benchmark_npv["currency"],
            benchmark_basis=None if benchmark_npv is None else str(benchmark_npv["valuation_basis"]),
            benchmark_timing=None if benchmark_npv is None else str(benchmark_npv["timing_basis"]),
            benchmark_source=benchmark_source_label,
            benchmark_note="No benchmark source enabled for this build." if benchmark_npv is None else str(benchmark_npv["note"] or ""),
            issues=deterministic_issues.copy(),
        ),
        _reconciliation_row(
            metric="incremental_irr",
            python_value=irr_from_profile(incremental_profile),
            python_unit="decimal",
            python_currency=None,
            python_basis="incremental_expansion",
            python_timing="year0_initial_outlay_plus_discounted_year1_to_year15",
            benchmark_value=None if benchmark_irr is None else float(benchmark_irr["value"]),
            benchmark_unit=None if benchmark_irr is None else str(benchmark_irr["unit"]),
            benchmark_currency=None if benchmark_irr is None else benchmark_irr["currency"],
            benchmark_basis=None if benchmark_irr is None else str(benchmark_irr["valuation_basis"]),
            benchmark_timing=None if benchmark_irr is None else str(benchmark_irr["timing_basis"]),
            benchmark_source=benchmark_source_label,
            benchmark_note="No benchmark source enabled for this build." if benchmark_irr is None else str(benchmark_irr["note"] or ""),
            issues=deterministic_issues.copy(),
        ),
        _reconciliation_row(
            metric="expected_npv",
            python_value=_summary_value(simulation_summary, "expected_npv_usd"),
            python_unit="USD",
            python_currency=project_currency,
            python_basis="total_project_expanded_operation",
            python_timing="year0_initial_outlay_plus_discounted_year1_to_year15",
            benchmark_value=None if expected_npv_row is None else float(expected_npv_row["value"]),
            benchmark_unit=None if expected_npv_row is None else str(expected_npv_row["unit"]),
            benchmark_currency=None if expected_npv_row is None else expected_npv_row["currency"],
            benchmark_basis=None if expected_npv_row is None else str(expected_npv_row["valuation_basis"]),
            benchmark_timing=None if expected_npv_row is None else str(expected_npv_row["timing_basis"]),
            benchmark_source=benchmark_source_label,
            benchmark_note="No benchmark source enabled for this build." if expected_npv_row is None else str(expected_npv_row["note"]),
            issues=[] if expected_npv_row is None else ["stochastic_design_mismatch"],
        ),
        _reconciliation_row(
            metric="var_5pct",
            python_value=_summary_value(simulation_summary, "var_usd"),
            python_unit="USD",
            python_currency=project_currency,
            python_basis="total_project_expanded_operation",
            python_timing="year0_initial_outlay_plus_discounted_year1_to_year15",
            benchmark_value=None if var_row is None else float(var_row["value"]),
            benchmark_unit=None if var_row is None else str(var_row["unit"]),
            benchmark_currency=None if var_row is None else var_row["currency"],
            benchmark_basis=None if var_row is None else str(var_row["valuation_basis"]),
            benchmark_timing=None if var_row is None else str(var_row["timing_basis"]),
            benchmark_source=benchmark_source_label,
            benchmark_note="No benchmark source enabled for this build." if var_row is None else str(var_row["note"]),
            issues=[] if var_row is None else ["stochastic_design_mismatch"],
        ),
        _reconciliation_row(
            metric="cvar_5pct",
            python_value=_summary_value(simulation_summary, "cvar_usd"),
            python_unit="USD",
            python_currency=project_currency,
            python_basis="total_project_expanded_operation",
            python_timing="year0_initial_outlay_plus_discounted_year1_to_year15",
            benchmark_value=None if cvar_row is None else float(cvar_row["value"]),
            benchmark_unit=None if cvar_row is None else str(cvar_row["unit"]),
            benchmark_currency=None if cvar_row is None else cvar_row["currency"],
            benchmark_basis=None if cvar_row is None else str(cvar_row["valuation_basis"]),
            benchmark_timing=None if cvar_row is None else str(cvar_row["timing_basis"]),
            benchmark_source=benchmark_source_label,
            benchmark_note="No benchmark source enabled for this build." if cvar_row is None else str(cvar_row["note"]),
            issues=[] if cvar_row is None else ["stochastic_design_mismatch"],
        ),
    ]
    return pd.DataFrame(rows)


def build_benchmark_scope_catalog(benchmark_comparison: pd.DataFrame) -> pd.DataFrame:
    """Return business-readable benchmark transparency metadata."""

    explicit_guidance = {
        "incremental_npv": {
            "appendix_submodule": "Benchmark Transparency",
            "comparison_role": "Direct comparison",
            "when_to_use": "Use when discussing deterministic incremental valuation against the workbook reference.",
            "limitation_note": "A material gap can still remain even when the deterministic basis and timing align.",
        },
        "incremental_irr": {
            "appendix_submodule": "Benchmark Transparency",
            "comparison_role": "Direct comparison",
            "when_to_use": "Use when discussing deterministic return sensitivity against the workbook reference.",
            "limitation_note": "IRR remains a simplified appendix output and should not be described as full investment-committee parity.",
        },
        "expected_npv": {
            "appendix_submodule": "Monte Carlo Downside",
            "comparison_role": "Reference only",
            "when_to_use": "Use as a directional downside reference after the monthly and deterministic story is understood.",
            "limitation_note": "The Python simulation uses total-project expanded-operation framing while the workbook Monte Carlo benchmark uses incremental expansion framing.",
        },
        "var_5pct": {
            "appendix_submodule": "Monte Carlo Downside",
            "comparison_role": "Reference only",
            "when_to_use": "Use for downside framing, not for strict parity claims.",
            "limitation_note": "Tail-risk metrics are not directly comparable when the stochastic design and valuation basis differ.",
        },
        "cvar_5pct": {
            "appendix_submodule": "Monte Carlo Downside",
            "comparison_role": "Reference only",
            "when_to_use": "Use for downside framing, not for strict parity claims.",
            "limitation_note": "Tail-risk metrics are not directly comparable when the stochastic design and valuation basis differ.",
        },
    }

    rows = []
    for order, row in enumerate(benchmark_comparison.sort_values("metric").itertuples(index=False), start=1):
        guidance = explicit_guidance[str(row.metric)]
        rows.append(
            {
                "benchmark_order": order,
                "metric": row.metric,
                "appendix_submodule": guidance["appendix_submodule"],
                "comparison_role": guidance["comparison_role"],
                "python_basis": row.python_basis,
                "benchmark_basis": row.benchmark_basis,
                "python_timing_basis": row.python_timing_basis,
                "benchmark_timing_basis": row.benchmark_timing_basis,
                "benchmark_source": row.benchmark_source,
                "when_to_use": guidance["when_to_use"],
                "limitation_note": guidance["limitation_note"],
                "reconciliation_note": row.reconciliation_note,
                "secondary_role_note": "Benchmark outputs are appendix audit artifacts, not the main repository product story.",
            }
        )
    return pd.DataFrame(rows)
