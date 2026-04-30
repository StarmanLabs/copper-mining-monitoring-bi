import pandas as pd
import pytest

from conftest import scratch_output_dir
from copper_risk_model.monthly_monitoring import (
    POUNDS_PER_METRIC_TONNE,
    build_monthly_monitoring_outputs,
    load_monthly_monitoring_inputs,
    validate_monthly_inputs,
)
from copper_risk_model.monthly_validation import DatasetValidationError


def test_monthly_monitoring_outputs_smoke():
    with scratch_output_dir("test-monthly-monitoring") as output_dir:
        outputs = build_monthly_monitoring_outputs(output_dir=output_dir)

        assert outputs["kpi_monthly_summary"].exists()
        assert outputs["fact_monthly_actual_vs_plan"].exists()
        assert outputs["monthly_dataset_catalog"].exists()
        assert outputs["dim_site"].exists()
        assert outputs["dim_month"].exists()
        assert outputs["dim_monthly_metric"].exists()
        assert outputs["dim_process_area"].exists()
        assert outputs["dim_cost_center"].exists()
        assert outputs["monthly_kpi_dictionary"].exists()
        assert outputs["data_quality_report"].exists()
        assert outputs["kpi_exceptions"].exists()
        assert outputs["source_mapping_audit"].exists()
        assert outputs["refresh_summary"].exists()
        assert outputs["mart_monthly_by_site"].exists()
        assert outputs["mart_process_driver_summary"].exists()
        assert outputs["mart_cost_center_summary"].exists()

        summary = pd.read_csv(outputs["kpi_monthly_summary"])
        fact = pd.read_csv(outputs["fact_monthly_actual_vs_plan"])
        dim_site = pd.read_csv(outputs["dim_site"])
        dim_month = pd.read_csv(outputs["dim_month"])
        dim_process_area = pd.read_csv(outputs["dim_process_area"])
        dim_cost_center = pd.read_csv(outputs["dim_cost_center"])
        monthly_dictionary = pd.read_csv(outputs["monthly_kpi_dictionary"])
        data_quality_report = pd.read_csv(outputs["data_quality_report"])
        kpi_exceptions = pd.read_csv(outputs["kpi_exceptions"])
        source_mapping_audit = pd.read_csv(outputs["source_mapping_audit"])
        site_mart = pd.read_csv(outputs["mart_monthly_by_site"])
        process_driver_mart = pd.read_csv(outputs["mart_process_driver_summary"])
        cost_center_mart = pd.read_csv(outputs["mart_cost_center_summary"])

        assert len(summary) == 24
        assert len(fact) == 24 * 14
        assert len(dim_site) == 2
        assert len(dim_month) == 12
        assert len(dim_process_area) == 2
        assert len(dim_cost_center) == 3
        assert len(monthly_dictionary) == 14
        assert len(site_mart) == 24
        assert len(process_driver_mart) == 48
        assert len(cost_center_mart) == 72
        assert {"site_id", "site_name", "site_sort_order"}.issubset(dim_site.columns)
        assert {
            "period",
            "month_start_date",
            "calendar_year",
            "calendar_month",
            "calendar_quarter",
            "month_label",
            "quarter_label",
            "month_sort_order",
        }.issubset(dim_month.columns)
        assert {"process_area", "process_area_sort_order"}.issubset(dim_process_area.columns)
        assert {"cost_center", "cost_center_sort_order"}.issubset(dim_cost_center.columns)
        assert summary["data_classification"].eq("sample_demo_monthly_monitoring").all()
        assert summary["sample_data_flag"].all()
        assert {
            "throughput_tonnes_variance_pct",
            "revenue_proxy_usd_variance_pct",
            "ebitda_proxy_usd_variance_pct",
            "overall_alert_level",
            "primary_alert_metric",
            "site_name",
            "downtime_hours_actual",
            "primary_ore_source",
            "top_cost_center",
            "site_production_gap_share_pct",
        }.issubset(summary.columns)
        assert {
            "throughput_tonnes",
            "head_grade_pct",
            "recovery_pct",
            "copper_production_tonnes",
            "unit_cost_usd_per_tonne",
            "revenue_proxy_usd",
            "ebitda_proxy_usd",
        }.issubset(set(fact["metric"]))
        assert {
            "business_meaning",
            "proxy_flag",
            "plan_field",
            "actual_field",
            "variance_field",
            "variance_pct_field",
            "primary_dashboard_page",
        }.issubset(monthly_dictionary.columns)
        assert bool(monthly_dictionary.loc[monthly_dictionary["metric"] == "revenue_proxy_usd", "proxy_flag"].iloc[0])
        assert not bool(monthly_dictionary.loc[monthly_dictionary["metric"] == "throughput_tonnes", "proxy_flag"].iloc[0])
        assert {"dataset_name", "check_name", "status", "issue_count"}.issubset(data_quality_report.columns)
        assert data_quality_report.loc[data_quality_report["status"] == "fail"].empty
        assert {"process_driver_monthly", "cost_center_monthly", "dim_site", "dim_month"}.issubset(
            set(data_quality_report["dataset_name"])
        )
        month_field_checks = data_quality_report.loc[
            data_quality_report["check_name"] == "month_fields_consistent", ["dataset_name", "affected_columns"]
        ]
        assert month_field_checks.loc[month_field_checks["dataset_name"] == "dim_month", "affected_columns"].iloc[0] == (
            "period; month_start_date; calendar_year; calendar_month"
        )
        assert month_field_checks.loc[
            month_field_checks["dataset_name"] == "kpi_monthly_summary", "affected_columns"
        ].iloc[0] == "period; month_start_date; calendar_year; calendar_month"
        assert {"exception_code", "exception_title", "severity", "management_question"}.issubset(kpi_exceptions.columns)
        assert "major_production_shortfall" in set(kpi_exceptions["exception_code"])
        assert set(kpi_exceptions["exception_code"]).issubset(
            {
                "major_throughput_shortfall",
                "major_recovery_underperformance",
                "major_production_shortfall",
                "unit_cost_deterioration",
            }
        )
        assert {"dataset_name", "source_file", "status", "mapped_rows"}.issubset(source_mapping_audit.columns)
        assert source_mapping_audit["status"].eq("ready_for_validation").all()
        assert set(source_mapping_audit["dataset_name"]) == {
            "plan_monthly",
            "actual_production_monthly",
            "plant_performance_monthly",
            "cost_actuals_monthly",
            "market_prices_monthly",
            "process_driver_monthly",
            "cost_center_monthly",
        }
        assert {"site_name", "site_production_gap_share_pct", "top_cost_center"}.issubset(site_mart.columns)
        assert {"process_area", "downtime_share_pct", "process_area_production_gap_share_pct"}.issubset(
            process_driver_mart.columns
        )
        assert {"cost_center", "cost_variance_usd", "cost_center_margin_pressure_share_pct"}.issubset(
            cost_center_mart.columns
        )
        assert list(dim_month["period"]) == [f"2025-{month:02d}" for month in range(1, 13)]
        assert set(site_mart["site_id"]) == {"demo_north_concentrator", "demo_south_concentrator"}
        assert bool(site_mart.loc[site_mart["period"] == "2025-10", "stockpile_feed_pct_actual"].max() > 0.0)

        january = summary.loc[
            (summary["period"] == "2025-01") & (summary["site_id"] == "demo_north_concentrator")
        ].iloc[0]
        assert january["throughput_tonnes_actual"] < january["throughput_tonnes_plan"]
        assert january["unit_cost_usd_per_tonne_actual"] > january["unit_cost_usd_per_tonne_plan"]
        assert january["revenue_proxy_usd_actual"] < january["revenue_proxy_usd_plan"]
        assert january["overall_alert_level"] in {"warning", "critical"}


def test_monthly_validation_rejects_missing_required_columns():
    dataset_frames = load_monthly_monitoring_inputs()
    dataset_frames["plan_monthly"] = dataset_frames["plan_monthly"].drop(columns=["throughput_tonnes_plan"])

    with pytest.raises(DatasetValidationError, match="missing_required_columns"):
        validate_monthly_inputs(dataset_frames)


def test_monthly_validation_rejects_duplicate_keys():
    dataset_frames = load_monthly_monitoring_inputs()
    duplicated_row = dataset_frames["actual_production_monthly"].iloc[[0]].copy()
    dataset_frames["actual_production_monthly"] = pd.concat(
        [dataset_frames["actual_production_monthly"], duplicated_row],
        ignore_index=True,
    )

    with pytest.raises(DatasetValidationError, match="duplicate_keys"):
        validate_monthly_inputs(dataset_frames)


def test_monthly_validation_rejects_invalid_period_format():
    dataset_frames = load_monthly_monitoring_inputs()
    dataset_frames["market_prices_monthly"].loc[0, "period"] = "2025/01"

    with pytest.raises(DatasetValidationError, match="invalid_period_format"):
        validate_monthly_inputs(dataset_frames)


def test_monthly_validation_rejects_impossible_rates():
    dataset_frames = load_monthly_monitoring_inputs()
    dataset_frames["plant_performance_monthly"].loc[0, "recovery_pct_actual"] = 120.0

    with pytest.raises(DatasetValidationError, match="numeric_range_high"):
        validate_monthly_inputs(dataset_frames)


def test_monthly_financial_proxies_follow_unit_consistent_formula():
    with scratch_output_dir("test-monthly-monitoring-financial-proxies") as output_dir:
        outputs = build_monthly_monitoring_outputs(output_dir=output_dir)
        summary = pd.read_csv(outputs["kpi_monthly_summary"])

        january = summary.loc[
            (summary["period"] == "2025-01") & (summary["site_id"] == "demo_north_concentrator")
        ].iloc[0]

        expected_revenue_plan = (
            january["copper_production_tonnes_plan"]
            * POUNDS_PER_METRIC_TONNE
            * (january["payable_percent_plan"] / 100.0)
            * january["net_realized_price_usd_per_lb_plan"]
        )
        expected_revenue_actual = (
            january["copper_production_tonnes_actual"]
            * POUNDS_PER_METRIC_TONNE
            * (january["payable_percent_actual"] / 100.0)
            * january["net_realized_price_usd_per_lb_actual"]
        )

        assert january["revenue_proxy_usd_plan"] == pytest.approx(expected_revenue_plan)
        assert january["revenue_proxy_usd_actual"] == pytest.approx(expected_revenue_actual)
        assert january["ebitda_proxy_usd_plan"] == pytest.approx(
            january["revenue_proxy_usd_plan"] - january["operating_cost_usd_plan"]
        )
        assert january["ebitda_proxy_usd_actual"] == pytest.approx(
            january["revenue_proxy_usd_actual"] - january["operating_cost_usd_actual"]
        )
        assert january["operating_cash_flow_proxy_usd_plan"] == pytest.approx(
            january["ebitda_proxy_usd_plan"] - january["working_capital_change_usd_plan"]
        )
        assert january["operating_cash_flow_proxy_usd_actual"] == pytest.approx(
            january["ebitda_proxy_usd_actual"] - january["working_capital_change_usd_actual"]
        )
        assert january["free_cash_flow_proxy_usd_plan"] == pytest.approx(
            january["operating_cash_flow_proxy_usd_plan"] - january["sustaining_capex_usd_plan"]
        )
        assert january["free_cash_flow_proxy_usd_actual"] == pytest.approx(
            january["operating_cash_flow_proxy_usd_actual"] - january["sustaining_capex_usd_actual"]
        )


def test_demo_financial_proxy_guardrails_keep_monthly_scale_plausible():
    with scratch_output_dir("test-monthly-monitoring-financial-guardrails") as output_dir:
        outputs = build_monthly_monitoring_outputs(output_dir=output_dir)
        summary = pd.read_csv(outputs["kpi_monthly_summary"])

        financial_columns = [
            "revenue_proxy_usd_plan",
            "revenue_proxy_usd_actual",
            "ebitda_proxy_usd_plan",
            "ebitda_proxy_usd_actual",
            "operating_cash_flow_proxy_usd_plan",
            "operating_cash_flow_proxy_usd_actual",
            "free_cash_flow_proxy_usd_plan",
            "free_cash_flow_proxy_usd_actual",
        ]
        assert summary[financial_columns].abs().max().max() < 100_000_000.0

        implied_revenue_per_tonne_plan = summary["revenue_proxy_usd_plan"] / summary["copper_production_tonnes_plan"]
        implied_revenue_per_tonne_actual = summary["revenue_proxy_usd_actual"] / summary["copper_production_tonnes_actual"]
        assert implied_revenue_per_tonne_plan.between(500.0, 100_000.0).all()
        assert implied_revenue_per_tonne_actual.between(500.0, 100_000.0).all()

        variance_pct_columns = [
            "revenue_proxy_usd_variance_pct",
            "ebitda_proxy_usd_variance_pct",
            "operating_cash_flow_proxy_usd_variance_pct",
            "free_cash_flow_proxy_usd_variance_pct",
        ]
        for column in variance_pct_columns:
            assert summary[column].notna().all()
            assert summary[column].abs().max() < 5.0
