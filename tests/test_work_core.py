from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import yaml

from conftest import scratch_output_dir
from copper_risk_model.annual_appendix_work_adaptation import (
    ANNUAL_APPENDIX_CANONICAL_SCHEMAS,
    build_annual_appendix_data_quality_report,
    build_annual_appendix_work_outputs,
    load_annual_appendix_mapping_config,
    map_annual_appendix_source_dataframe,
)
from copper_risk_model.data_quality import build_data_quality_report
from copper_risk_model.monthly_monitoring import (
    MONTHLY_CANONICAL_SCHEMAS,
    build_monthly_monitoring_outputs,
    load_monthly_monitoring_inputs,
)
from copper_risk_model.source_mapping import load_mapping_config, map_source_dataframe


ROOT = Path(__file__).resolve().parents[1]


def test_source_mapping_can_map_company_style_plan_columns():
    mapping_config = load_mapping_config(ROOT / "config" / "mappings" / "templates" / "example_company_mapping.yaml")
    plan_mapping = mapping_config["datasets"]["plan_monthly"]
    source_frame = pd.DataFrame(
        [
            {
                "operation_code": "example_site",
                "fiscal_month": "2025/01",
                "milled_tonnes_budget": 400000,
                "copper_grade_budget_pct": 0.72,
                "recovery_budget_pct": 87.5,
                "unit_opex_budget_usdpt": 18.4,
                "copper_price_budget_usdlb": 3.95,
                "tcrc_budget_usdlb": 0.25,
                "payable_budget_pct": 96.5,
                "sustaining_capex_budget_usd": 3200000,
                "working_capital_budget_usd": 1500000,
            }
        ]
    )

    mapped, audit_row = map_source_dataframe(
        source_frame=source_frame,
        dataset_name="plan_monthly",
        dataset_mapping=plan_mapping,
        target_schema=MONTHLY_CANONICAL_SCHEMAS["plan_monthly"],
    )

    assert mapped.loc[0, "site_id"] == "example_site"
    assert mapped.loc[0, "period"] == "2025-01"
    assert mapped.loc[0, "plan_version"] == "private_monthly_budget"
    assert {
        "throughput_tonnes_plan",
        "head_grade_pct_plan",
        "recovery_pct_plan",
        "unit_cost_usd_per_tonne_plan",
    }.issubset(mapped.columns)
    assert audit_row["status"] == "ready_for_validation"


def test_data_quality_report_flags_missing_period_sequence():
    dataset_frames = load_monthly_monitoring_inputs()
    dataset_frames["actual_production_monthly"] = dataset_frames["actual_production_monthly"].loc[
        dataset_frames["actual_production_monthly"]["period"] != "2025-03"
    ].reset_index(drop=True)

    report = build_data_quality_report(
        dataset_frames={"actual_production_monthly": dataset_frames["actual_production_monthly"]},
        schemas={"actual_production_monthly": MONTHLY_CANONICAL_SCHEMAS["actual_production_monthly"]},
    )
    sequence_row = report.loc[report["check_name"] == "period_sequence_complete"].iloc[0]

    assert sequence_row["status"] == "fail"
    assert sequence_row["issue_count"] >= 1
    assert "Missing monthly periods" in sequence_row["detail"]


def test_refresh_summary_contains_work_core_sections():
    with scratch_output_dir("test-work-core-refresh") as output_dir:
        outputs = build_monthly_monitoring_outputs(output_dir=output_dir)
        refresh_summary = json.loads(outputs["refresh_summary"].read_text(encoding="utf-8"))

        assert refresh_summary["refresh_status"] == "success"
        assert refresh_summary["public_safe"] is True
        assert refresh_summary["mapping_summary"]["datasets_mapped"] == 7
        assert refresh_summary["validation_summary"]["checks_failed"] == 0
        assert refresh_summary["kpi_exception_summary"]["total_exceptions"] >= 1
        assert len(refresh_summary["sources_used"]) == 7
        assert {"dim_site", "dim_month", "mart_monthly_by_site", "mart_process_driver_summary", "mart_cost_center_summary"}.issubset(
            set(refresh_summary["output_files"])
        )


def test_annual_appendix_mapping_can_map_company_style_driver_columns():
    mapping_config = load_annual_appendix_mapping_config(
        ROOT / "config" / "mappings" / "templates" / "example_company_annual_appendix_mapping.yaml"
    )
    driver_mapping = mapping_config["datasets"]["annual_appendix_inputs"]
    source_frame = pd.DataFrame(
        [
            {
                "project_year": "1",
                "calendar_year_label": "2026",
                "copper_price_budget_usdlb": 4.05,
                "processed_tonnes_base": 405000,
                "head_grade_decimal": 0.0074,
                "recovery_decimal": 0.882,
                "base_unit_cost_usdpt": 18.6,
                "expansion_unit_cost_usdpt": 17.1,
                "initial_capex_year_usd": 165000000,
                "sustaining_capex_year_usd": 0,
            }
        ]
    )

    mapped, audit_row = map_annual_appendix_source_dataframe(
        source_frame=source_frame,
        dataset_name="annual_appendix_inputs",
        dataset_mapping=driver_mapping,
        target_schema=ANNUAL_APPENDIX_CANONICAL_SCHEMAS["annual_appendix_inputs"],
    )

    assert int(mapped.loc[0, "year"]) == 1
    assert int(mapped.loc[0, "calendar_year"]) == 2026
    assert mapped.loc[0, "base_processed_tonnes"] == 405000
    assert {
        "copper_price_usd_per_lb",
        "base_head_grade",
        "base_recovery",
        "initial_capex_usd",
    }.issubset(mapped.columns)
    assert audit_row["status"] == "ready_for_validation"


def test_annual_appendix_data_quality_report_flags_missing_year_sequence():
    annual_inputs = pd.read_csv(ROOT / "data" / "sample_data" / "annual_appendix" / "annual_appendix_inputs.csv")
    annual_inputs = annual_inputs.loc[annual_inputs["year"] != 3].reset_index(drop=True)

    report = build_annual_appendix_data_quality_report(
        dataset_frames={"annual_appendix_inputs": annual_inputs},
        schemas={"annual_appendix_inputs": ANNUAL_APPENDIX_CANONICAL_SCHEMAS["annual_appendix_inputs"]},
    )
    sequence_row = report.loc[report["check_name"] == "year_sequence_complete"].iloc[0]

    assert sequence_row["status"] == "fail"
    assert sequence_row["issue_count"] >= 1
    assert "Project years" in sequence_row["detail"]


def test_annual_appendix_work_package_contains_refresh_sections():
    with scratch_output_dir("test-annual-appendix-work") as output_dir:
        outputs = build_annual_appendix_work_outputs(output_dir=output_dir)
        refresh_summary = json.loads(outputs["annual_appendix_refresh_summary"].read_text(encoding="utf-8"))
        appendix_scenarios = pd.read_csv(outputs["appendix_scenarios"])

        assert refresh_summary["refresh_status"] == "success"
        assert refresh_summary["public_safe"] is True
        assert refresh_summary["work_core_scope"] == "annual_appendix"
        assert refresh_summary["mapping_summary"]["datasets_mapped"] == 4
        assert refresh_summary["validation_summary"]["checks_failed"] == 0
        assert len(refresh_summary["sources_used"]) == 4
        assert {
            "annual_appendix_inputs",
            "appendix_parameters",
            "appendix_scenarios",
            "appendix_benchmark_metrics",
        }.issubset(set(refresh_summary["output_files"]))
        assert list(appendix_scenarios["scenario_id"]) == [
            "base",
            "bull_market",
            "bear_market",
            "operational_stress",
            "capex_overrun",
            "committee_downside",
        ]


def test_private_source_profile_template_is_parseable():
    profile = yaml.safe_load(
        (ROOT / "config" / "source_profiles" / "templates" / "example_private_company_profile.yaml").read_text(
            encoding="utf-8"
        )
    )

    assert profile["profile_name"] == "example_private_company_profile"
    assert {"runner", "monthly_monitoring", "annual_appendix", "powerbi_local", "public_repo_boundary"}.issubset(profile)
    assert profile["runner"]["default_scope"] == "all"
    assert "config/mappings/local/" in profile["public_repo_boundary"]["do_not_commit"]
    assert profile["annual_appendix"]["advanced_appendix"]["benchmark_mode"] == "canonical"
    assert "python scripts/run_local_profile.py" in profile["local_run_examples"]["all"]
