from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import yaml

from conftest import scratch_output_dir
from copper_risk_model.bi_export import build_bi_outputs
import copper_risk_model.powerbi_template as powerbi_template_module
from copper_risk_model.powerbi_template import build_powerbi_template_layer


def _write_profile(profile_dir: Path, *, include_advanced_appendix: bool = True) -> Path:
    profile = {
        "version": 2,
        "profile_name": "powerbi_profile_test",
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
    profile_path = profile_dir / "powerbi_profile_test.yaml"
    profile_path.write_text(yaml.safe_dump(profile, sort_keys=False), encoding="utf-8")
    return profile_path


def test_build_powerbi_template_layer_scaffold():
    with scratch_output_dir("test-bi-template-bi") as bi_dir:
        build_bi_outputs(output_dir=bi_dir)

        with scratch_output_dir("test-bi-template-scaffold") as template_dir:
            outputs = build_powerbi_template_layer(bi_output_dir=bi_dir, template_dir=template_dir)

            assert outputs["template_root"].exists()
            assert outputs["parameter_query"].exists()
            assert outputs["parameter_manifest"].exists()
            assert outputs["query_catalog"].exists()
            assert outputs["all_measures"].exists()
            assert outputs["report_manifest"].exists()
            assert outputs["template_manifest"].exists()

            parameter_query = outputs["parameter_query"].read_text(encoding="utf-8")
            assert "REPLACE_WITH_ABSOLUTE_REPO_PATH" in parameter_query
            assert "ProjectRoot" in parameter_query

            monthly_output_query = (template_dir / "parameters" / "MonthlyOutputRoot.pq").read_text(encoding="utf-8")
            assert "MonthlyOutputRoot = ProjectRoot & " in monthly_output_query
            assert ".pytest_tmp\\test-bi-template-bi-" in monthly_output_query

            dim_site_query = (
                template_dir / "queries" / "core_monthly_story" / "01_dim_site.pq"
            ).read_text(encoding="utf-8")
            assert "MonthlyOutputRoot" in dim_site_query
            assert "\\dim_site.csv" in dim_site_query

            query_text = (
                template_dir / "queries" / "core_monthly_story" / "07_fact_monthly_actual_vs_plan.pq"
            ).read_text(encoding="utf-8")
            assert "File.Contents(SourcePath)" in query_text
            assert "MonthlyOutputRoot" in query_text
            assert "\\fact_monthly_actual_vs_plan.csv" in query_text

            measure_text = (template_dir / "measures" / "01_executive_overview.dax").read_text(encoding="utf-8")
            assert "Monthly Throughput Actual = SUM(kpi_monthly_summary[throughput_tonnes_actual])" in measure_text

            report_manifest = json.loads(outputs["report_manifest"].read_text(encoding="utf-8"))
            assert [page["page_name"] for page in report_manifest["pages"]] == [
                "Executive Overview",
                "Monthly Actual vs Plan",
                "Process Performance",
                "Cost and Margin",
                "Advanced Scenario / Risk Appendix",
            ]
            assert report_manifest["pages"][0]["story_role"] == "Core Monthly Story"

            query_catalog = pd.read_csv(outputs["query_catalog"])
            reference_query = query_catalog.loc[query_catalog["query_name"] == "powerbi_measure_catalog"].iloc[0]
            assert reference_query["load_recommendation"] == "disable_load_after_import"
            assert reference_query["parameter_name"] == "StarterKitOutputRoot"
            assert (template_dir / "model" / "powerbi_sort_by_catalog.csv").exists()
            assert (template_dir / "model" / "powerbi_field_visibility_catalog.csv").exists()

            template_manifest = json.loads(outputs["template_manifest"].read_text(encoding="utf-8"))
            assert template_manifest["artifact_strategy"] == "PBIP finalization package"
            assert template_manifest["measure_count"] >= 1
            assert ".pytest_tmp/test-bi-template-bi-" in template_manifest["default_output_roots"]["monthly"]

            parameter_manifest = json.loads(outputs["parameter_manifest"].read_text(encoding="utf-8"))
            assert {item["parameter_name"] for item in parameter_manifest["parameters"]} == {
                "ProjectRoot",
                "StarterKitOutputRoot",
                "MonthlyOutputRoot",
                "AdvancedAppendixOutputRoot",
            }

            outputs = build_powerbi_template_layer(bi_output_dir=bi_dir, template_dir=template_dir)
            regenerated_queries = list((template_dir / "queries").rglob("*.pq"))
            expected_query_count = len(pd.read_csv(outputs["query_catalog"]))
            assert len(regenerated_queries) == expected_query_count
            assert (template_dir / "queries" / "core_monthly_story" / "07_fact_monthly_actual_vs_plan.pq").exists()
            for generated_file in outputs["template_root"].rglob("*"):
                if generated_file.is_file():
                    assert b"\r\n" not in generated_file.read_bytes(), f"{generated_file.name} should use LF newlines"


def test_build_powerbi_template_layer_can_follow_profile_output_roots():
    with scratch_output_dir("test-bi-template-profile-bi") as bi_dir:
        build_bi_outputs(output_dir=bi_dir)

        with scratch_output_dir("test-bi-template-profile") as profile_dir:
            profile_path = _write_profile(profile_dir)
            outputs = build_powerbi_template_layer(
                bi_output_dir=bi_dir,
                template_dir=profile_dir / "scaffold",
                profile_path=profile_path,
            )

            monthly_output_query = (outputs["template_root"] / "parameters" / "MonthlyOutputRoot.pq").read_text(
                encoding="utf-8"
            )
            appendix_output_query = (
                outputs["template_root"] / "parameters" / "AdvancedAppendixOutputRoot.pq"
            ).read_text(encoding="utf-8")

            assert "outputs\\private\\monthly_work_core" in monthly_output_query
            assert "outputs\\private\\annual_appendix_report" in appendix_output_query

            appendix_query = (
                outputs["template_root"] / "queries" / "advanced_appendix" / "20_fact_annual_metrics.pq"
            ).read_text(encoding="utf-8")
            assert "AdvancedAppendixOutputRoot" in appendix_query


def test_build_powerbi_template_layer_marks_untracked_legacy_queries_obsolete(monkeypatch):
    with scratch_output_dir("test-bi-template-legacy-bi") as bi_dir:
        build_bi_outputs(output_dir=bi_dir)

        with scratch_output_dir("test-bi-template-legacy") as template_dir:
            build_powerbi_template_layer(bi_output_dir=bi_dir, template_dir=template_dir)

            legacy_query = template_dir / "queries" / "01_dim_site.pq"
            legacy_query.write_text("// legacy flat query\n", encoding="utf-8")

            def _preserve_directory(target: Path) -> None:
                target.mkdir(parents=True, exist_ok=True)

            monkeypatch.setattr(powerbi_template_module, "_reset_directory", _preserve_directory)

            outputs = build_powerbi_template_layer(bi_output_dir=bi_dir, template_dir=template_dir)

            assert legacy_query.exists()
            assert "Obsolete scaffold file" in legacy_query.read_text(encoding="utf-8")

            build_inventory = json.loads(outputs["build_inventory"].read_text(encoding="utf-8"))
            assert "queries/01_dim_site.pq" in build_inventory["obsolete_files"]
            assert (
                template_dir / "queries" / "core_monthly_story" / "01_dim_site.pq"
            ).exists()


def test_build_powerbi_template_layer_omits_appendix_assets_when_profile_disables_it():
    with scratch_output_dir("test-bi-template-no-appendix-bi") as bi_dir:
        build_bi_outputs(output_dir=bi_dir)

        with scratch_output_dir("test-bi-template-no-appendix") as profile_dir:
            enabled_profile_path = _write_profile(profile_dir, include_advanced_appendix=True)
            scaffold_dir = profile_dir / "scaffold"
            build_powerbi_template_layer(
                bi_output_dir=bi_dir,
                template_dir=scaffold_dir,
                profile_path=enabled_profile_path,
            )
            assert (scaffold_dir / "queries" / "advanced_appendix").exists()

            disabled_profile_path = _write_profile(profile_dir, include_advanced_appendix=False)
            outputs = build_powerbi_template_layer(
                bi_output_dir=bi_dir,
                template_dir=scaffold_dir,
                profile_path=disabled_profile_path,
            )

            appendix_parameter = outputs["template_root"] / "parameters" / "AdvancedAppendixOutputRoot.pq"
            assert appendix_parameter.exists()
            assert "Obsolete scaffold file" in appendix_parameter.read_text(encoding="utf-8")

            appendix_query = outputs["template_root"] / "queries" / "advanced_appendix" / "20_fact_annual_metrics.pq"
            assert appendix_query.exists()
            assert "Obsolete scaffold file" in appendix_query.read_text(encoding="utf-8")

            query_catalog = pd.read_csv(outputs["query_catalog"])
            assert "Advanced Appendix" not in set(query_catalog["query_group"])

            report_manifest = json.loads(outputs["report_manifest"].read_text(encoding="utf-8"))
            assert [page["page_name"] for page in report_manifest["pages"]] == [
                "Executive Overview",
                "Monthly Actual vs Plan",
                "Process Performance",
                "Cost and Margin",
            ]

            template_manifest = json.loads(outputs["template_manifest"].read_text(encoding="utf-8"))
            assert template_manifest["appendix_enabled"] is False
            assert "advanced_appendix" not in template_manifest["output_root_parameters"]

            parameter_manifest = json.loads(outputs["parameter_manifest"].read_text(encoding="utf-8"))
            assert parameter_manifest["appendix_enabled"] is False
            assert {item["parameter_name"] for item in parameter_manifest["parameters"]} == {
                "ProjectRoot",
                "StarterKitOutputRoot",
                "MonthlyOutputRoot",
            }
            build_inventory = json.loads(outputs["build_inventory"].read_text(encoding="utf-8"))
            assert "parameters/AdvancedAppendixOutputRoot.pq" in build_inventory["obsolete_files"]
            assert "queries/advanced_appendix/20_fact_annual_metrics.pq" in build_inventory["obsolete_files"]
