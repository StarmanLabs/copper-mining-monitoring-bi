"""Refresh reporting helpers for the monthly monitoring work-core layer."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd


EXCEPTION_RULES = {
    "throughput_tonnes": {
        "exception_code": "major_throughput_shortfall",
        "exception_title": "Major Throughput Shortfall",
        "business_area": "Operations",
        "management_question": "Is plant availability, feed quality, or scheduling constraining tonnes processed?",
    },
    "recovery_pct": {
        "exception_code": "major_recovery_underperformance",
        "exception_title": "Major Recovery Underperformance",
        "business_area": "Process Performance",
        "management_question": "Is metallurgical performance eroding concentrate output relative to plan?",
    },
    "copper_production_tonnes": {
        "exception_code": "major_production_shortfall",
        "exception_title": "Major Production Shortfall",
        "business_area": "Production",
        "management_question": "Is the production gap being driven by volume, grade, recovery, or a combination?",
    },
    "unit_cost_usd_per_tonne": {
        "exception_code": "unit_cost_deterioration",
        "exception_title": "Unit Cost Deterioration",
        "business_area": "Cost and Margin",
        "management_question": "Is cost pressure temporary, structural, or volume-related?",
    },
}


def build_kpi_exceptions(fact_monthly_actual_vs_plan: pd.DataFrame) -> pd.DataFrame:
    """Build a concise business-facing KPI exception table."""

    rows: list[dict[str, Any]] = []
    for row in fact_monthly_actual_vs_plan.itertuples(index=False):
        if row.metric not in EXCEPTION_RULES or row.alert_level == "on_track":
            continue
        rule = EXCEPTION_RULES[row.metric]
        rows.append(
            {
                "site_id": row.site_id,
                "period": row.period,
                "month_label": row.month_label,
                "dashboard_page": row.dashboard_page,
                "metric": row.metric,
                "metric_display_name": row.metric_display_name,
                "exception_code": rule["exception_code"],
                "exception_title": rule["exception_title"],
                "business_area": rule["business_area"],
                "severity": row.alert_level,
                "plan_value": row.plan_value,
                "actual_value": row.actual_value,
                "variance_value": row.variance_value,
                "variance_pct": row.variance_pct,
                "management_question": rule["management_question"],
                "exception_message": row.alert_message,
            }
        )

    if not rows:
        return pd.DataFrame(
            columns=[
                "site_id",
                "period",
                "month_label",
                "dashboard_page",
                "metric",
                "metric_display_name",
                "exception_code",
                "exception_title",
                "business_area",
                "severity",
                "plan_value",
                "actual_value",
                "variance_value",
                "variance_pct",
                "management_question",
                "exception_message",
            ]
        )

    exceptions = pd.DataFrame(rows)
    severity_rank = {"critical": 0, "warning": 1}
    exceptions["severity_rank"] = exceptions["severity"].map(severity_rank).fillna(9)
    exceptions["abs_variance_pct"] = exceptions["variance_pct"].abs()
    exceptions = exceptions.sort_values(
        ["severity_rank", "abs_variance_pct", "period", "metric_display_name"],
        ascending=[True, False, True, True],
    ).drop(columns=["severity_rank", "abs_variance_pct"])
    return exceptions.reset_index(drop=True)


def summarize_kpi_exceptions(kpi_exceptions: pd.DataFrame) -> dict[str, Any]:
    """Summarize KPI exceptions for the refresh summary."""

    return {
        "total_exceptions": int(len(kpi_exceptions)),
        "critical_exceptions": int((kpi_exceptions.get("severity", pd.Series(dtype=str)) == "critical").sum()),
        "warning_exceptions": int((kpi_exceptions.get("severity", pd.Series(dtype=str)) == "warning").sum()),
        "top_exceptions": kpi_exceptions.loc[
            :,
            ["period", "exception_title", "severity", "metric_display_name", "exception_message"],
        ].head(10).to_dict("records"),
    }


def build_refresh_summary(
    source_mapping_audit: pd.DataFrame,
    data_quality_summary: dict[str, Any],
    kpi_exception_summary: dict[str, Any],
    output_files: dict[str, str],
    mapping_config_path: str | None,
    data_dir: str,
) -> dict[str, Any]:
    """Build a concise JSON-friendly refresh summary."""

    return {
        "refresh_timestamp_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "refresh_status": "success",
        "public_safe": True,
        "work_core_scope": "monthly_monitoring",
        "data_dir": data_dir,
        "mapping_config_path": mapping_config_path,
        "sources_used": source_mapping_audit.loc[
            :, ["dataset_name", "source_dataset_label", "source_file", "status"]
        ].to_dict("records"),
        "mapping_summary": {
            "datasets_mapped": int(len(source_mapping_audit)),
            "mapping_rows_ready_for_validation": int((source_mapping_audit["status"] == "ready_for_validation").sum()),
            "mapping_rows_with_issues": int((source_mapping_audit["status"] != "ready_for_validation").sum()),
        },
        "validation_summary": data_quality_summary,
        "kpi_exception_summary": kpi_exception_summary,
        "output_files": output_files,
    }


def build_failed_refresh_summary(
    error: Exception,
    mapping_config_path: str | None,
    data_dir: str,
) -> dict[str, Any]:
    """Build a failure summary when a refresh does not complete."""

    return {
        "refresh_timestamp_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "refresh_status": "failed",
        "public_safe": True,
        "work_core_scope": "monthly_monitoring",
        "data_dir": data_dir,
        "mapping_config_path": mapping_config_path,
        "error_type": type(error).__name__,
        "error_message": str(error),
    }
