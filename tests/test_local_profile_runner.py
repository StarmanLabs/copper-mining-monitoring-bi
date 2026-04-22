from __future__ import annotations

from pathlib import Path

import yaml

from conftest import scratch_output_dir
from copper_risk_model.local_profile_runner import run_local_source_profile


ROOT = Path(__file__).resolve().parents[1]


def _repo_relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _write_profile(profile_dir: Path, *, include_advanced_appendix: bool = True) -> Path:
    summary_dir = profile_dir / "run_summaries"
    monthly_output_dir = profile_dir / "monthly_work_core"
    annual_output_dir = profile_dir / "annual_appendix_canonical"
    appendix_report_dir = profile_dir / "annual_appendix_report"

    profile = {
        "version": 2,
        "profile_name": "test_local_profile",
        "description": "Scratch profile used for runner tests.",
        "runner": {
            "default_scope": "all",
            "summary_output_dir": _repo_relative(summary_dir),
        },
        "monthly_monitoring": {
            "enabled": True,
            "raw_source_dir": "data/sample_data/monthly_monitoring",
            "mapping_config": "config/mappings/public_demo_identity_mapping.yaml",
            "output_dir": _repo_relative(monthly_output_dir),
        },
        "annual_appendix": {
            "enabled": True,
            "raw_source_dir": "data/sample_data/annual_appendix",
            "mapping_config": "config/mappings/public_demo_annual_appendix_identity_mapping.yaml",
            "canonical_output_dir": _repo_relative(annual_output_dir),
            "advanced_appendix": {
                "enabled": include_advanced_appendix,
                "config_path": "config/project.yaml",
                "input_mode": "canonical",
                "benchmark_mode": "canonical",
                "output_dir": _repo_relative(appendix_report_dir),
            },
        },
    }
    profile_path = profile_dir / "test_local_profile.yaml"
    profile_path.write_text(yaml.safe_dump(profile, sort_keys=False), encoding="utf-8")
    return profile_path


def test_run_local_source_profile_monthly_scope_executes_only_monthly_package():
    with scratch_output_dir("test-local-profile-monthly") as output_dir:
        profile_path = _write_profile(output_dir)

        summary = run_local_source_profile(profile_path, scope="monthly")

        assert summary["runner_status"] == "success"
        assert summary["planned_packages"] == ["monthly_monitoring"]
        assert [package["package_name"] for package in summary["package_results"]] == ["monthly_monitoring"]
        assert (output_dir / "monthly_work_core" / "kpi_monthly_summary.csv").exists()
        assert not (output_dir / "annual_appendix_canonical" / "annual_appendix_inputs.csv").exists()


def test_run_local_source_profile_all_scope_executes_monthly_then_annual_then_advanced():
    with scratch_output_dir("test-local-profile-all") as output_dir:
        profile_path = _write_profile(output_dir)

        summary = run_local_source_profile(profile_path, scope="all")

        assert summary["runner_status"] == "success"
        assert summary["planned_packages"] == ["monthly_monitoring", "annual_appendix_work", "advanced_appendix"]
        assert [package["package_name"] for package in summary["package_results"]] == [
            "monthly_monitoring",
            "annual_appendix_work",
            "advanced_appendix",
        ]

        monthly_result = summary["package_results"][0]
        annual_result = summary["package_results"][1]
        advanced_result = summary["package_results"][2]

        assert monthly_result["checks_failed"] == 0
        assert annual_result["checks_failed"] == 0
        assert advanced_result["benchmark_mode"] == "canonical"
        assert (output_dir / "monthly_work_core" / "refresh_summary.json").exists()
        assert (output_dir / "annual_appendix_canonical" / "annual_appendix_refresh_summary.json").exists()
        assert (output_dir / "annual_appendix_report" / "fact_scenario_kpis.csv").exists()
        assert len(list((output_dir / "run_summaries").glob("*.json"))) == 1


def test_run_local_source_profile_validate_only_checks_contract_without_building_outputs():
    with scratch_output_dir("test-local-profile-validate") as output_dir:
        profile_path = _write_profile(output_dir)

        summary = run_local_source_profile(profile_path, scope="all", validate_only=True)

        assert summary["runner_status"] == "validated"
        assert summary["preflight_status"] == "pass"
        assert {package["status"] for package in summary["package_results"]} == {"ready"}
        assert not (output_dir / "monthly_work_core" / "kpi_monthly_summary.csv").exists()
        assert len(list((output_dir / "run_summaries").glob("*.json"))) == 1
