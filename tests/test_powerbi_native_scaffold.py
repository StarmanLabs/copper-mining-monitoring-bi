from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import yaml

from conftest import scratch_output_dir
from copper_risk_model.bi_export import build_bi_outputs
import copper_risk_model.powerbi_native_scaffold as powerbi_native_scaffold_module
from copper_risk_model.powerbi_native_scaffold import build_powerbi_native_scaffold


def _write_profile(profile_dir: Path, *, include_advanced_appendix: bool = True) -> Path:
    profile = {
        "version": 2,
        "profile_name": "native_powerbi_profile_test",
        "runner": {"default_scope": "all", "summary_output_dir": "outputs/private/run_summaries"},
        "monthly_monitoring": {
            "enabled": True,
            "raw_source_dir": "data/private/monthly_exports",
            "mapping_config": "config/mappings/local/monthly_private_mapping.yaml",
            "output_dir": "outputs/private/monthly_work_core",
        },
        "annual_appendix": {
            "enabled": True,
            "raw_source_dir": "data/private/annual_appendix_exports",
            "mapping_config": "config/mappings/local/annual_appendix_private_mapping.yaml",
            "canonical_output_dir": "outputs/private/annual_appendix_canonical",
            "advanced_appendix": {
                "enabled": include_advanced_appendix,
                "config_path": "config/project.yaml",
                "input_mode": "canonical",
                "benchmark_mode": "canonical",
                "output_dir": "outputs/private/annual_appendix_report",
            },
        },
    }
    profile_path = profile_dir / "native_powerbi_profile_test.yaml"
    profile_path.write_text(yaml.safe_dump(profile, sort_keys=False), encoding="utf-8")
    return profile_path


def test_build_powerbi_native_scaffold():
    with scratch_output_dir("test-native-bi") as bi_dir:
        build_bi_outputs(output_dir=bi_dir)

        with scratch_output_dir("test-native-scaffold") as scaffold_dir:
            outputs = build_powerbi_native_scaffold(bi_output_dir=bi_dir, scaffold_dir=scaffold_dir)

            assert outputs["scaffold_root"].exists()
            assert outputs["semantic_model_root"].exists()
            assert outputs["report_root"].exists()
            assert outputs["parameter_query"].exists()
            assert outputs["parameter_manifest"].exists()
            assert outputs["model_ordering_script"].exists()
            assert outputs["sort_visibility_script"].exists()
            assert outputs["core_measure_script"].exists()
            assert outputs["appendix_measure_script"].exists()
            assert outputs["relationship_script"].exists()
            assert outputs["desktop_finalization_manifest"].exists()

            model_ordering = outputs["model_ordering_script"].read_text(encoding="utf-8")
            assert "model Model" in model_ordering
            assert "ref table dim_site" in model_ordering
            assert "ref table fact_monthly_actual_vs_plan" in model_ordering

            sort_visibility = outputs["sort_visibility_script"].read_text(encoding="utf-8")
            assert "column month_label" in sort_visibility
            assert "sortByColumn: month_sort_order" in sort_visibility
            assert "column metric" in sort_visibility
            assert "isHidden" in sort_visibility

            core_measures = outputs["core_measure_script"].read_text(encoding="utf-8")
            assert "measure 'Monthly Throughput Actual' = SUM(kpi_monthly_summary[throughput_tonnes_actual])" in core_measures
            assert 'displayFolder: "01 Executive Overview"' in core_measures

            relationships = outputs["relationship_script"].read_text(encoding="utf-8")
            assert "fromColumn: kpi_monthly_summary.site_id" in relationships
            assert "toColumn: dim_site.site_id" in relationships
            assert "crossFilteringBehavior: oneDirection" in relationships

            monthly_output_query = (
                outputs["semantic_model_root"] / "PowerQuery" / "parameters" / "MonthlyOutputRoot.pq"
            ).read_text(encoding="utf-8")
            assert "MonthlyOutputRoot = ProjectRoot & " in monthly_output_query
            assert ".pytest_tmp\\test-native-bi-" in monthly_output_query

            fact_query = (
                outputs["semantic_model_root"]
                / "PowerQuery"
                / "queries"
                / "core_monthly_story"
                / "07_fact_monthly_actual_vs_plan.pq"
            ).read_text(encoding="utf-8")
            assert "MonthlyOutputRoot" in fact_query

            report_manifest = json.loads(outputs["report_manifest"].read_text(encoding="utf-8"))
            assert [page["page_name"] for page in report_manifest["pages"]] == [
                "Executive Overview",
                "Monthly Actual vs Plan",
                "Process Performance",
                "Cost and Margin",
                "Advanced Scenario / Risk Appendix",
            ]
            assert report_manifest["main_story"].startswith("Keep the first four pages")

            page_shell = json.loads(
                (outputs["report_root"] / "page_shells" / "03_process_performance.json").read_text(encoding="utf-8")
            )
            assert "dim_process_area[process_area]" in page_shell["page_specific_slicers"]
            assert page_shell["story_role"] == "Core Monthly Story"
            assert "required_measures" in page_shell

            scaffold_manifest = json.loads(outputs["scaffold_manifest"].read_text(encoding="utf-8"))
            assert scaffold_manifest["artifact_type"] == "PBIP finalization package"
            assert scaffold_manifest["artifact_strategy"] == "PBIP finalization package"
            assert "Power Query parameter roots aligned to starter-kit, monthly, and advanced-appendix output families" in scaffold_manifest["native_like_components"]

            desktop_manifest = json.loads(outputs["desktop_finalization_manifest"].read_text(encoding="utf-8"))
            assert desktop_manifest["artifact_strategy"] == "PBIP finalization package"
            assert desktop_manifest["page_sequence"][0] == "Executive Overview"
            assert any(
                check["check_name"] == "monthly_semantic_center" for check in desktop_manifest["verification_checks"]
            )

            semantic_catalogs_dir = outputs["semantic_model_root"] / "catalogs"
            measure_catalog = pd.read_csv(semantic_catalogs_dir / "powerbi_measure_catalog.csv")
            assert {"measure_order", "display_folder", "format_string"}.issubset(measure_catalog.columns)
            assert (semantic_catalogs_dir / "powerbi_sort_by_catalog.csv").exists()
            assert (semantic_catalogs_dir / "powerbi_field_visibility_catalog.csv").exists()


def test_build_powerbi_native_scaffold_can_follow_profile_output_roots():
    with scratch_output_dir("test-native-profile-bi") as bi_dir:
        build_bi_outputs(output_dir=bi_dir)

        with scratch_output_dir("test-native-profile") as profile_dir:
            profile_path = _write_profile(profile_dir)
            outputs = build_powerbi_native_scaffold(
                bi_output_dir=bi_dir,
                scaffold_dir=profile_dir / "scaffold",
                profile_path=profile_path,
            )

            monthly_output_query = (
                outputs["semantic_model_root"] / "PowerQuery" / "parameters" / "MonthlyOutputRoot.pq"
            ).read_text(encoding="utf-8")
            appendix_output_query = (
                outputs["semantic_model_root"] / "PowerQuery" / "parameters" / "AdvancedAppendixOutputRoot.pq"
            ).read_text(encoding="utf-8")

            assert "outputs\\private\\monthly_work_core" in monthly_output_query
            assert "outputs\\private\\annual_appendix_report" in appendix_output_query

            desktop_manifest = json.loads(outputs["desktop_finalization_manifest"].read_text(encoding="utf-8"))
            assert desktop_manifest["default_output_roots"]["monthly"] == "outputs/private/monthly_work_core"
            assert desktop_manifest["default_output_roots"]["advanced_appendix"] == "outputs/private/annual_appendix_report"


def test_build_powerbi_native_scaffold_marks_untracked_legacy_queries_obsolete(monkeypatch):
    with scratch_output_dir("test-native-legacy-bi") as bi_dir:
        build_bi_outputs(output_dir=bi_dir)

        with scratch_output_dir("test-native-legacy") as scaffold_dir:
            build_powerbi_native_scaffold(bi_output_dir=bi_dir, scaffold_dir=scaffold_dir)

            legacy_query = (
                scaffold_dir
                / "CopperMiningMonitoring.SemanticModel"
                / "PowerQuery"
                / "queries"
                / "01_dim_site.pq"
            )
            legacy_query.write_text("// legacy flat query\n", encoding="utf-8")

            def _preserve_directory(target: Path) -> None:
                target.mkdir(parents=True, exist_ok=True)

            monkeypatch.setattr(powerbi_native_scaffold_module, "_reset_directory", _preserve_directory)

            outputs = build_powerbi_native_scaffold(bi_output_dir=bi_dir, scaffold_dir=scaffold_dir)

            assert legacy_query.exists()
            assert "Obsolete scaffold file" in legacy_query.read_text(encoding="utf-8")

            build_inventory = json.loads(outputs["build_inventory"].read_text(encoding="utf-8"))
            assert (
                "CopperMiningMonitoring.SemanticModel/PowerQuery/queries/01_dim_site.pq"
                in build_inventory["obsolete_files"]
            )
            assert (
                outputs["semantic_model_root"]
                / "PowerQuery"
                / "queries"
                / "core_monthly_story"
                / "01_dim_site.pq"
            ).exists()


def test_build_powerbi_native_scaffold_omits_appendix_assets_when_profile_disables_it():
    with scratch_output_dir("test-native-profile-no-appendix-bi") as bi_dir:
        build_bi_outputs(output_dir=bi_dir)

        with scratch_output_dir("test-native-profile-no-appendix") as profile_dir:
            enabled_profile_path = _write_profile(profile_dir, include_advanced_appendix=True)
            scaffold_dir = profile_dir / "scaffold"
            build_powerbi_native_scaffold(
                bi_output_dir=bi_dir,
                scaffold_dir=scaffold_dir,
                profile_path=enabled_profile_path,
            )
            assert (scaffold_dir / "CopperMiningMonitoring.Report" / "page_shells" / "05_advanced_scenario_risk_appendix.json").exists()

            disabled_profile_path = _write_profile(profile_dir, include_advanced_appendix=False)
            outputs = build_powerbi_native_scaffold(
                bi_output_dir=bi_dir,
                scaffold_dir=scaffold_dir,
                profile_path=disabled_profile_path,
            )

            parameters_dir = outputs["semantic_model_root"] / "PowerQuery" / "parameters"
            appendix_parameter = parameters_dir / "AdvancedAppendixOutputRoot.pq"
            assert appendix_parameter.exists()
            assert "Obsolete scaffold file" in appendix_parameter.read_text(encoding="utf-8")

            appendix_query = (
                outputs["semantic_model_root"] / "PowerQuery" / "queries" / "advanced_appendix" / "20_fact_annual_metrics.pq"
            )
            assert appendix_query.exists()
            assert "Obsolete scaffold file" in appendix_query.read_text(encoding="utf-8")

            appendix_page_shell = outputs["report_root"] / "page_shells" / "05_advanced_scenario_risk_appendix.json"
            assert appendix_page_shell.exists()
            appendix_page_shell_payload = json.loads(appendix_page_shell.read_text(encoding="utf-8"))
            assert appendix_page_shell_payload["status"] == "obsolete"

            report_manifest = json.loads(outputs["report_manifest"].read_text(encoding="utf-8"))
            assert [page["page_name"] for page in report_manifest["pages"]] == [
                "Executive Overview",
                "Monthly Actual vs Plan",
                "Process Performance",
                "Cost and Margin",
            ]

            scaffold_manifest = json.loads(outputs["scaffold_manifest"].read_text(encoding="utf-8"))
            assert scaffold_manifest["appendix_enabled"] is False
            assert scaffold_manifest["page_count"] == 4
            assert scaffold_manifest["default_output_roots"] == {
                "starter_kit": str(bi_dir.relative_to(Path(__file__).resolve().parents[1])).replace("\\", "/"),
                "monthly": "outputs/private/monthly_work_core",
            }

            desktop_manifest = json.loads(outputs["desktop_finalization_manifest"].read_text(encoding="utf-8"))
            assert desktop_manifest["appendix_enabled"] is False
            assert desktop_manifest["page_sequence"] == [
                "Executive Overview",
                "Monthly Actual vs Plan",
                "Process Performance",
                "Cost and Margin",
            ]
            assert any(check["check_name"] == "appendix_omitted" for check in desktop_manifest["verification_checks"])

            parameter_manifest = json.loads(outputs["parameter_manifest"].read_text(encoding="utf-8"))
            assert {item["parameter_name"] for item in parameter_manifest["parameters"]} == {
                "ProjectRoot",
                "StarterKitOutputRoot",
                "MonthlyOutputRoot",
            }

            build_inventory = json.loads(outputs["build_inventory"].read_text(encoding="utf-8"))
            assert "CopperMiningMonitoring.SemanticModel/PowerQuery/parameters/AdvancedAppendixOutputRoot.pq" in build_inventory["obsolete_files"]
            assert "CopperMiningMonitoring.Report/page_shells/05_advanced_scenario_risk_appendix.json" in build_inventory["obsolete_files"]
