import pandas as pd

from conftest import scratch_output_dir
from copper_risk_model.bi_export import build_bi_outputs


def test_build_bi_outputs_smoke():
    with scratch_output_dir("test-smoke-bi") as bi_dir:
        outputs = build_bi_outputs(output_dir=bi_dir)
        assert outputs["fact_simulation_distribution"].exists()
        assert outputs["dim_metric"].exists()
        assert outputs["powerbi_table_catalog"].exists()
        assert outputs["powerbi_query_catalog"].exists()
        assert outputs["powerbi_relationship_catalog"].exists()
        assert outputs["powerbi_visual_binding_catalog"].exists()
        assert outputs["powerbi_sort_by_catalog"].exists()
        assert outputs["powerbi_field_visibility_catalog"].exists()
        assert outputs["simulation_summary"].exists()
        assert outputs["benchmark_comparison"].exists()
        assert outputs["benchmark_scope_catalog"].exists()
        assert outputs["annual_appendix_dataset_catalog"].exists()
        assert outputs["annual_appendix_field_catalog"].exists()
        assert outputs["annual_appendix_inputs"].exists()
        assert outputs["appendix_parameters"].exists()
        assert outputs["appendix_scenarios"].exists()
        assert outputs["appendix_benchmark_metrics"].exists()
        assert outputs["annual_appendix_source_mapping_audit"].exists()
        assert outputs["annual_appendix_data_quality_report"].exists()
        assert outputs["annual_appendix_refresh_summary"].exists()
        assert outputs["advanced_appendix_assumption_catalog"].exists()
        assert outputs["advanced_appendix_output_catalog"].exists()
        assert outputs["appendix_kpi_catalog"].exists()
        assert outputs["dim_scenario"].exists()
        assert outputs["fact_tornado_sensitivity"].exists()
        assert outputs["kpi_monthly_summary"].exists()
        assert outputs["fact_monthly_actual_vs_plan"].exists()
        assert outputs["dim_site"].exists()
        assert outputs["dim_month"].exists()
        assert outputs["dim_process_area"].exists()
        assert outputs["dim_cost_center"].exists()
        assert outputs["monthly_kpi_dictionary"].exists()
        assert outputs["data_quality_report"].exists()
        assert outputs["kpi_exceptions"].exists()
        assert outputs["source_mapping_audit"].exists()
        assert outputs["refresh_summary"].exists()
        assert outputs["mart_monthly_executive_overview"].exists()
        assert outputs["mart_monthly_by_site"].exists()
        assert outputs["mart_process_driver_summary"].exists()
        assert outputs["mart_cost_center_summary"].exists()
        assert outputs["dashboard_page_catalog"].exists()

        dim_scenario = pd.read_csv(outputs["dim_scenario"])
        assert {"base", "committee_downside"}.issubset(set(dim_scenario["scenario_id"]))

        benchmark = pd.read_csv(outputs["benchmark_comparison"])
        assert {
            "metric",
            "comparability_class",
            "comparable_flag",
            "reconciliation_status",
            "reconciliation_note",
            "gap",
            "pct_gap",
        }.issubset(benchmark.columns)
        assert {"incremental_npv", "incremental_irr", "expected_npv"}.issubset(set(benchmark["metric"]))

        benchmark_scope = pd.read_csv(outputs["benchmark_scope_catalog"])
        assert {"comparison_role", "when_to_use", "limitation_note", "secondary_role_note"}.issubset(
            benchmark_scope.columns
        )
        assert {"Direct comparison", "Reference only"}.issubset(set(benchmark_scope["comparison_role"]))

        appendix_outputs = pd.read_csv(outputs["advanced_appendix_output_catalog"])
        assert {"dataset_name", "appendix_submodule", "why_secondary", "generated_from"}.issubset(appendix_outputs.columns)
        assert "fact_scenario_kpis" in set(appendix_outputs["dataset_name"])
        assert appendix_outputs.loc[
            appendix_outputs["dataset_name"] == "benchmark_comparison", "generated_from"
        ].eq("Canonical appendix benchmark table").all()

        appendix_assumptions = pd.read_csv(outputs["advanced_appendix_assumption_catalog"])
        assert {"parameter_name", "source_type", "practical_use", "limitation_note"}.issubset(
            appendix_assumptions.columns
        )
        assert appendix_assumptions.loc[
            appendix_assumptions["parameter_name"] == "base_unit_cost_usd_per_tonne", "source_type"
        ].eq("canonical_annual_input_table").all()
        assert appendix_assumptions.loc[
            appendix_assumptions["parameter_name"] == "royalty_rate", "limitation_note"
        ].str.contains("not applied", case=False).all()

        annual_dataset_catalog = pd.read_csv(outputs["annual_appendix_dataset_catalog"])
        assert {"dataset_name", "source_file", "purpose", "primary_use", "limitation_note"}.issubset(
            annual_dataset_catalog.columns
        )

        annual_field_catalog = pd.read_csv(outputs["annual_appendix_field_catalog"])
        assert {"dataset_name", "column_name", "description", "unit", "required_flag"}.issubset(
            annual_field_catalog.columns
        )
        assert annual_field_catalog.loc[
            annual_field_catalog["dataset_name"] == "annual_appendix_inputs", "column_name"
        ].isin({"initial_capex_usd", "sustaining_capex_usd"}).any()

        annual_appendix_mapping_audit = pd.read_csv(outputs["annual_appendix_source_mapping_audit"])
        assert {"dataset_name", "source_dataset_label", "source_file", "status"}.issubset(
            annual_appendix_mapping_audit.columns
        )
        assert annual_appendix_mapping_audit["status"].eq("ready_for_validation").all()

        annual_appendix_quality_report = pd.read_csv(outputs["annual_appendix_data_quality_report"])
        assert {"required_columns_present", "canonical_contract_valid", "numeric_ranges_valid"}.issubset(
            set(annual_appendix_quality_report["check_name"])
        )

        annual_appendix_refresh_summary = pd.read_json(outputs["annual_appendix_refresh_summary"], typ="series")
        assert annual_appendix_refresh_summary["refresh_status"] == "success"
        assert annual_appendix_refresh_summary["work_core_scope"] == "annual_appendix"

        fact_heatmap = pd.read_csv(outputs["fact_heatmap_price_grade"])
        assert len(fact_heatmap) == 35

        monthly_summary = pd.read_csv(outputs["kpi_monthly_summary"])
        assert monthly_summary["data_classification"].eq("sample_demo_monthly_monitoring").all()
        assert {
            "throughput_tonnes_variance_pct",
            "overall_alert_level",
            "site_name",
            "downtime_hours_actual",
            "top_cost_center",
        }.issubset(monthly_summary.columns)

        page_catalog = pd.read_csv(outputs["dashboard_page_catalog"])
        assert list(page_catalog["page_name"]) == [
            "Executive Overview",
            "Monthly Actual vs Plan",
            "Process Performance",
            "Cost and Margin",
            "Advanced Scenario / Risk Appendix",
        ]

        relationship_catalog = pd.read_csv(outputs["powerbi_relationship_catalog"])
        assert {
            ("dim_site", "kpi_monthly_summary"),
            ("dim_month", "fact_monthly_actual_vs_plan"),
            ("dim_monthly_metric", "fact_monthly_actual_vs_plan"),
            ("dim_process_area", "mart_process_driver_summary"),
            ("dim_cost_center", "mart_cost_center_summary"),
        }.issubset(set(zip(relationship_catalog["from_table"], relationship_catalog["to_table"])))

        table_catalog = pd.read_csv(outputs["powerbi_table_catalog"])
        assert {"dim_site", "dim_month", "dim_process_area", "dim_cost_center", "mart_monthly_by_site", "mart_process_driver_summary", "mart_cost_center_summary"}.issubset(
            set(table_catalog["table_name"])
        )

        visual_catalog = pd.read_csv(outputs["powerbi_visual_binding_catalog"])
        assert {"Site Contribution To Production Gap", "Downtime By Process Area", "Cost Variance By Cost Center"}.issubset(
            set(visual_catalog["visual_title"])
        )

        query_catalog = pd.read_csv(outputs["powerbi_query_catalog"])
        assert "load_recommendation" in query_catalog.columns
        assert query_catalog.loc[query_catalog["query_name"] == "dim_site", "relative_source_path"].iloc[0] == "outputs/bi/dim_site.csv"
        assert query_catalog.loc[query_catalog["query_name"] == "kpi_monthly_summary", "relative_source_path"].iloc[0] == "outputs/bi/kpi_monthly_summary.csv"

        measure_catalog = pd.read_csv(outputs["powerbi_measure_catalog"])
        assert {"measure_order", "display_folder", "format_string"}.issubset(measure_catalog.columns)
        assert measure_catalog.loc[measure_catalog["measure_name"] == "Monthly Throughput Actual", "display_folder"].iloc[0] == "01 Executive Overview"

        sort_by_catalog = pd.read_csv(outputs["powerbi_sort_by_catalog"])
        assert {
            ("dim_site", "site_name", "site_sort_order"),
            ("dim_month", "month_label", "month_sort_order"),
            ("dim_monthly_metric", "display_name", "display_order"),
        }.issubset(
            set(zip(sort_by_catalog["table_name"], sort_by_catalog["display_column"], sort_by_catalog["sort_by_column"]))
        )

        visibility_catalog = pd.read_csv(outputs["powerbi_field_visibility_catalog"])
        assert {
            ("dim_site", "site_id"),
            ("dim_month", "month_sort_order"),
            ("fact_monthly_actual_vs_plan", "metric"),
        }.issubset(set(zip(visibility_catalog["table_name"], visibility_catalog["column_name"])))

        monthly_dictionary = pd.read_csv(outputs["monthly_kpi_dictionary"])
        assert {"throughput_tonnes", "revenue_proxy_usd", "free_cash_flow_proxy_usd"}.issubset(set(monthly_dictionary["metric"]))

        data_quality_report = pd.read_csv(outputs["data_quality_report"])
        assert {"required_columns_present", "period_sequence_complete", "numeric_ranges_valid"}.issubset(
            set(data_quality_report["check_name"])
        )
