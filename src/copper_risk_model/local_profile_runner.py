"""Unified local runner for profile-driven monthly and annual work packages."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any

import yaml

from .advanced_appendix import build_advanced_appendix_outputs
from .annual_appendix_work_adaptation import (
    ANNUAL_APPENDIX_SOURCE_DATASETS,
    build_annual_appendix_work_outputs,
    load_annual_appendix_mapping_config,
)
from .monthly_monitoring import MONTHLY_SOURCE_DATASETS, build_monthly_monitoring_outputs
from .source_mapping import load_mapping_config

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER_SCOPE_CHOICES = ("monthly", "annual_appendix", "all")
RUNNER_SUCCESS_STATUSES = {"success", "dry_run", "validated"}


@dataclass(frozen=True)
class RunnerSettings:
    """Execution preferences for the unified local runner."""

    default_scope: str
    summary_output_dir: Path


@dataclass(frozen=True)
class MonthlyProfileSection:
    """Profile contract for the monthly monitoring work package."""

    enabled: bool
    raw_source_dir: Path
    mapping_config: Path | None
    output_dir: Path


@dataclass(frozen=True)
class AdvancedAppendixSection:
    """Optional downstream advanced appendix continuation for annual work."""

    enabled: bool
    config_path: Path
    input_mode: str | None
    benchmark_mode: str | None
    data_dir: Path | None
    output_dir: Path


@dataclass(frozen=True)
class AnnualAppendixSection:
    """Profile contract for annual appendix canonicalization."""

    enabled: bool
    raw_source_dir: Path
    mapping_config: Path | None
    canonical_output_dir: Path
    advanced_appendix: AdvancedAppendixSection | None


@dataclass(frozen=True)
class LocalSourceProfile:
    """Typed source profile used by the unified local runner."""

    path: Path
    profile_name: str
    description: str
    public_repo_boundary: dict[str, Any]
    runner: RunnerSettings
    monthly_monitoring: MonthlyProfileSection | None
    annual_appendix: AnnualAppendixSection | None


def _load_yaml_dict(path: str | Path) -> dict[str, Any]:
    candidate = Path(path)
    with candidate.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected a YAML mapping in '{candidate}'.")
    return loaded


def _resolve_path(value: str | Path | None) -> Path | None:
    if value is None:
        return None
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    return REPO_ROOT / candidate


def _bool_value(value: Any, *, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "1", "on"}:
            return True
        if lowered in {"false", "no", "0", "off"}:
            return False
    return bool(value)


def _safe_path(path: str | Path | None) -> str | None:
    if path is None:
        return None
    candidate = Path(path)
    try:
        return candidate.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return candidate.name


def _slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    return slug or "profile"


def _parse_monthly_section(raw_section: dict[str, Any] | None) -> MonthlyProfileSection | None:
    if raw_section is None:
        return None

    output_dir = raw_section.get("output_dir") or raw_section.get("canonical_or_bi_output_dir") or "outputs/bi"
    return MonthlyProfileSection(
        enabled=_bool_value(raw_section.get("enabled"), default=True),
        raw_source_dir=_resolve_path(raw_section.get("raw_source_dir", "data/sample_data/monthly_monitoring")),
        mapping_config=_resolve_path(raw_section.get("mapping_config")),
        output_dir=_resolve_path(output_dir),
    )


def _parse_advanced_appendix_section(
    raw_section: dict[str, Any] | None,
    *,
    fallback_data_dir: Path | None,
) -> AdvancedAppendixSection | None:
    if raw_section is None:
        return None

    return AdvancedAppendixSection(
        enabled=_bool_value(raw_section.get("enabled"), default=False),
        config_path=_resolve_path(raw_section.get("config_path", "config/project.yaml")),
        input_mode=raw_section.get("input_mode"),
        benchmark_mode=raw_section.get("benchmark_mode"),
        data_dir=_resolve_path(raw_section.get("data_dir")) or fallback_data_dir,
        output_dir=_resolve_path(raw_section.get("output_dir", "outputs/bi")),
    )


def _parse_annual_section(raw_section: dict[str, Any] | None) -> AnnualAppendixSection | None:
    if raw_section is None:
        return None

    canonical_output_dir = _resolve_path(raw_section.get("canonical_output_dir", "outputs/bi"))
    advanced_section = _parse_advanced_appendix_section(
        raw_section.get("advanced_appendix"),
        fallback_data_dir=canonical_output_dir,
    )
    return AnnualAppendixSection(
        enabled=_bool_value(raw_section.get("enabled"), default=True),
        raw_source_dir=_resolve_path(raw_section.get("raw_source_dir", "data/sample_data/annual_appendix")),
        mapping_config=_resolve_path(raw_section.get("mapping_config")),
        canonical_output_dir=canonical_output_dir,
        advanced_appendix=advanced_section,
    )


def load_local_source_profile(path: str | Path) -> LocalSourceProfile:
    """Load and validate the profile contract for a local execution flow."""

    profile_path = Path(path)
    raw_profile = _load_yaml_dict(profile_path)

    monthly_section = _parse_monthly_section(raw_profile.get("monthly_monitoring"))
    annual_section = _parse_annual_section(raw_profile.get("annual_appendix"))
    runner_section = raw_profile.get("runner") or {}
    default_scope = str(runner_section.get("default_scope", "all"))
    if default_scope not in RUNNER_SCOPE_CHOICES:
        raise ValueError(
            f"Unsupported runner default_scope '{default_scope}'. Choose from {', '.join(RUNNER_SCOPE_CHOICES)}."
        )

    summary_output_dir = _resolve_path(runner_section.get("summary_output_dir", "outputs/bi"))
    return LocalSourceProfile(
        path=profile_path.resolve(),
        profile_name=str(raw_profile.get("profile_name", profile_path.stem)),
        description=str(raw_profile.get("description", "")),
        public_repo_boundary=raw_profile.get("public_repo_boundary", {}),
        runner=RunnerSettings(
            default_scope=default_scope,
            summary_output_dir=summary_output_dir,
        ),
        monthly_monitoring=monthly_section,
        annual_appendix=annual_section,
    )


def _summary_output_path(profile: LocalSourceProfile, scope: str) -> Path:
    filename = f"{_slugify(profile.profile_name)}_{scope}_local_run_summary.json"
    return profile.runner.summary_output_dir / filename


def _check_row(
    *,
    package_name: str,
    check_name: str,
    status: str,
    detail: str,
    target_path: str | Path | None = None,
) -> dict[str, Any]:
    return {
        "package_name": package_name,
        "check_name": check_name,
        "status": status,
        "detail": detail,
        "target_path": _safe_path(target_path),
    }


def _load_project_config(config_path: Path) -> dict[str, Any]:
    return _load_yaml_dict(config_path)


def _validate_mapping_sources(
    *,
    package_name: str,
    data_dir: Path,
    mapping_config_path: Path | None,
    mapping_loader,
    expected_datasets: tuple[str, ...],
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    checks.append(
        _check_row(
            package_name=package_name,
            check_name="data_dir_exists",
            status="pass" if data_dir.exists() and data_dir.is_dir() else "fail",
            detail="Input source directory is available." if data_dir.exists() and data_dir.is_dir() else "Input source directory is missing.",
            target_path=data_dir,
        )
    )

    if mapping_config_path is None:
        checks.append(
            _check_row(
                package_name=package_name,
                check_name="mapping_config_present",
                status="pass",
                detail="No mapping config was provided because inputs are expected to be canonical already.",
            )
        )
        return checks

    mapping_exists = mapping_config_path.exists() and mapping_config_path.is_file()
    checks.append(
        _check_row(
            package_name=package_name,
            check_name="mapping_config_exists",
            status="pass" if mapping_exists else "fail",
            detail="Mapping config is available." if mapping_exists else "Mapping config is missing.",
            target_path=mapping_config_path,
        )
    )
    if not mapping_exists:
        return checks

    try:
        mapping_config = mapping_loader(mapping_config_path)
    except Exception as error:  # pragma: no cover - defensive branch
        checks.append(
            _check_row(
                package_name=package_name,
                check_name="mapping_config_parseable",
                status="fail",
                detail=f"Mapping config could not be parsed: {error}",
                target_path=mapping_config_path,
            )
        )
        return checks

    dataset_mappings = mapping_config.get("datasets", {})
    missing_dataset_sections = [dataset_name for dataset_name in expected_datasets if dataset_name not in dataset_mappings]
    checks.append(
        _check_row(
            package_name=package_name,
            check_name="mapping_datasets_complete",
            status="pass" if not missing_dataset_sections else "fail",
            detail=(
                "Mapping config includes all required dataset sections."
                if not missing_dataset_sections
                else f"Missing dataset sections: {', '.join(missing_dataset_sections)}."
            ),
            target_path=mapping_config_path,
        )
    )

    missing_files: list[str] = []
    for dataset_name in expected_datasets:
        dataset_mapping = dataset_mappings.get(dataset_name)
        if not isinstance(dataset_mapping, dict):
            continue
        source_file = dataset_mapping.get("source_file")
        if source_file is None:
            missing_files.append(f"{dataset_name}: source_file missing in mapping config")
            continue
        source_path = data_dir / str(source_file)
        if not source_path.exists():
            missing_files.append(f"{dataset_name}: {source_file}")

    checks.append(
        _check_row(
            package_name=package_name,
            check_name="mapped_source_files_present",
            status="pass" if not missing_files else "fail",
            detail=(
                "All mapped source files are present."
                if not missing_files
                else f"Missing mapped source files: {', '.join(missing_files)}."
            ),
            target_path=data_dir,
        )
    )
    return checks


def _validate_monthly_section(section: MonthlyProfileSection | None, *, requested: bool) -> list[dict[str, Any]]:
    if not requested:
        return []
    if section is None:
        return [
            _check_row(
                package_name="monthly_monitoring",
                check_name="profile_section_present",
                status="fail",
                detail="The profile does not include a monthly_monitoring section.",
            )
        ]
    if not section.enabled:
        return [
            _check_row(
                package_name="monthly_monitoring",
                check_name="profile_section_enabled",
                status="fail",
                detail="The monthly_monitoring section is disabled in the profile.",
            )
        ]
    return _validate_mapping_sources(
        package_name="monthly_monitoring",
        data_dir=section.raw_source_dir,
        mapping_config_path=section.mapping_config,
        mapping_loader=load_mapping_config,
        expected_datasets=MONTHLY_SOURCE_DATASETS,
    )


def _validate_annual_section(section: AnnualAppendixSection | None, *, requested: bool) -> list[dict[str, Any]]:
    if not requested:
        return []
    if section is None:
        return [
            _check_row(
                package_name="annual_appendix_work",
                check_name="profile_section_present",
                status="fail",
                detail="The profile does not include an annual_appendix section.",
            )
        ]
    if not section.enabled:
        return [
            _check_row(
                package_name="annual_appendix_work",
                check_name="profile_section_enabled",
                status="fail",
                detail="The annual_appendix section is disabled in the profile.",
            )
        ]
    return _validate_mapping_sources(
        package_name="annual_appendix_work",
        data_dir=section.raw_source_dir,
        mapping_config_path=section.mapping_config,
        mapping_loader=load_annual_appendix_mapping_config,
        expected_datasets=ANNUAL_APPENDIX_SOURCE_DATASETS,
    )


def _validate_advanced_appendix_section(
    section: AdvancedAppendixSection | None,
    *,
    requested: bool,
    upstream_canonical_build_planned: bool,
) -> list[dict[str, Any]]:
    if not requested:
        return []
    if section is None:
        return []
    if not section.enabled:
        return [
            _check_row(
                package_name="advanced_appendix",
                check_name="profile_section_enabled",
                status="fail",
                detail="The advanced_appendix continuation is disabled in the profile.",
            )
        ]
    checks: list[dict[str, Any]] = []
    config_exists = section.config_path.exists() and section.config_path.is_file()
    checks.append(
        _check_row(
            package_name="advanced_appendix",
            check_name="config_path_exists",
            status="pass" if config_exists else "fail",
            detail="Appendix project config is available." if config_exists else "Appendix project config is missing.",
            target_path=section.config_path,
        )
    )
    if not config_exists:
        return checks

    project_config = _load_project_config(section.config_path)
    workbook_path = _resolve_path(project_config.get("project", {}).get("workbook_path"))
    resolved_data_dir = section.data_dir
    if resolved_data_dir is not None and upstream_canonical_build_planned:
        checks.append(
            _check_row(
                package_name="advanced_appendix",
                check_name="canonical_input_handoff",
                status="pass",
                detail="Advanced appendix will consume the canonical annual outputs generated by the annual_appendix_work step.",
                target_path=resolved_data_dir,
            )
        )
    elif resolved_data_dir is not None:
        checks.append(
            _check_row(
                package_name="advanced_appendix",
                check_name="data_dir_exists",
                status="pass" if resolved_data_dir.exists() and resolved_data_dir.is_dir() else "fail",
                detail=(
                    "Appendix canonical data directory is available."
                    if resolved_data_dir.exists() and resolved_data_dir.is_dir()
                    else "Appendix canonical data directory is missing."
                ),
                target_path=resolved_data_dir,
            )
        )

    required_canonical_files = ["appendix_scenarios.csv"]
    if (section.input_mode or "canonical") == "canonical":
        required_canonical_files.extend(["annual_appendix_inputs.csv", "appendix_parameters.csv"])
    if (section.benchmark_mode or "canonical") == "canonical":
        required_canonical_files.append("appendix_benchmark_metrics.csv")

    if (
        resolved_data_dir is not None
        and resolved_data_dir.exists()
        and not upstream_canonical_build_planned
    ):
        missing_files = [
            filename for filename in required_canonical_files if not (resolved_data_dir / filename).exists()
        ]
        checks.append(
            _check_row(
                package_name="advanced_appendix",
                check_name="canonical_appendix_files_present",
                status="pass" if not missing_files else "fail",
                detail=(
                    "Required canonical appendix files are present."
                    if not missing_files
                    else f"Missing canonical appendix files: {', '.join(missing_files)}."
                ),
                target_path=resolved_data_dir,
            )
        )

    needs_workbook = (section.input_mode == "legacy_workbook") or (section.benchmark_mode == "legacy_workbook")
    if needs_workbook:
        workbook_exists = workbook_path is not None and workbook_path.exists()
        checks.append(
            _check_row(
                package_name="advanced_appendix",
                check_name="legacy_workbook_available",
                status="pass" if workbook_exists else "fail",
                detail=(
                    "Legacy workbook benchmark path is available."
                    if workbook_exists
                    else "Legacy workbook benchmark path is missing."
                ),
                target_path=workbook_path,
            )
        )
    return checks


def _requested_packages(profile: LocalSourceProfile, scope: str) -> dict[str, bool]:
    annual_requested = scope in {"annual_appendix", "all"}
    advanced_requested = (
        annual_requested
        and profile.annual_appendix is not None
        and profile.annual_appendix.advanced_appendix is not None
        and profile.annual_appendix.advanced_appendix.enabled
    )
    return {
        "monthly_monitoring": scope in {"monthly", "all"},
        "annual_appendix_work": annual_requested,
        "advanced_appendix": advanced_requested,
    }


def validate_local_source_profile(profile: LocalSourceProfile, scope: str) -> list[dict[str, Any]]:
    """Run preflight checks for the requested profile scope."""

    requested = _requested_packages(profile, scope)
    checks = []
    checks.extend(_validate_monthly_section(profile.monthly_monitoring, requested=requested["monthly_monitoring"]))
    checks.extend(_validate_annual_section(profile.annual_appendix, requested=requested["annual_appendix_work"]))
    annual_advanced_section = profile.annual_appendix.advanced_appendix if profile.annual_appendix is not None else None
    checks.extend(
        _validate_advanced_appendix_section(
            annual_advanced_section,
            requested=requested["advanced_appendix"],
            upstream_canonical_build_planned=requested["annual_appendix_work"],
        )
    )
    return checks


def _package_status(checks: list[dict[str, Any]]) -> str:
    return "pass" if all(check["status"] != "fail" for check in checks) else "fail"


def _read_json_summary(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _monthly_result(outputs: dict[str, Path], section: MonthlyProfileSection) -> dict[str, Any]:
    refresh_summary = _read_json_summary(outputs["refresh_summary"])
    validation_summary = refresh_summary.get("validation_summary", {})
    exception_summary = refresh_summary.get("kpi_exception_summary", {})
    return {
        "package_name": "monthly_monitoring",
        "status": refresh_summary.get("refresh_status", "success"),
        "package_role": "core_monthly_monitoring",
        "data_dir": _safe_path(section.raw_source_dir),
        "mapping_config_path": refresh_summary.get("mapping_config_path") or _safe_path(section.mapping_config),
        "output_dir": _safe_path(section.output_dir),
        "summary_file": _safe_path(outputs["refresh_summary"]),
        "checks_passed": int(validation_summary.get("checks_passed", 0)),
        "checks_failed": int(validation_summary.get("checks_failed", 0)),
        "key_exceptions": exception_summary.get("top_exceptions", [])[:5],
        "outputs_produced": {name: _safe_path(path) for name, path in outputs.items()},
    }


def _annual_result(outputs: dict[str, Path], section: AnnualAppendixSection) -> dict[str, Any]:
    refresh_summary = _read_json_summary(outputs["annual_appendix_refresh_summary"])
    validation_summary = refresh_summary.get("validation_summary", {})
    return {
        "package_name": "annual_appendix_work",
        "status": refresh_summary.get("refresh_status", "success"),
        "package_role": "secondary_annual_appendix_work",
        "data_dir": _safe_path(section.raw_source_dir),
        "mapping_config_path": refresh_summary.get("mapping_config_path") or _safe_path(section.mapping_config),
        "output_dir": _safe_path(section.canonical_output_dir),
        "summary_file": _safe_path(outputs["annual_appendix_refresh_summary"]),
        "checks_passed": int(validation_summary.get("checks_passed", 0)),
        "checks_failed": int(validation_summary.get("checks_failed", 0)),
        "key_exceptions": validation_summary.get("failed_check_examples", [])[:5],
        "outputs_produced": {name: _safe_path(path) for name, path in outputs.items()},
    }


def _advanced_result(outputs: dict[str, Path], section: AdvancedAppendixSection) -> dict[str, Any]:
    return {
        "package_name": "advanced_appendix",
        "status": "success",
        "package_role": "secondary_valuation_risk_appendix",
        "data_dir": _safe_path(section.data_dir),
        "mapping_config_path": None,
        "output_dir": _safe_path(section.output_dir),
        "summary_file": None,
        "input_mode": section.input_mode or "canonical",
        "benchmark_mode": section.benchmark_mode or "canonical",
        "checks_passed": None,
        "checks_failed": None,
        "key_exceptions": [],
        "outputs_produced": {name: _safe_path(path) for name, path in outputs.items()},
    }


def _failed_result(
    *,
    package_name: str,
    package_role: str,
    error: Exception,
    output_dir: Path | None,
    data_dir: Path | None,
    mapping_config_path: Path | None,
) -> dict[str, Any]:
    return {
        "package_name": package_name,
        "status": "failed",
        "package_role": package_role,
        "data_dir": _safe_path(data_dir),
        "mapping_config_path": _safe_path(mapping_config_path),
        "output_dir": _safe_path(output_dir),
        "summary_file": None,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "outputs_produced": {},
    }


def _skipped_result(
    *,
    package_name: str,
    package_role: str,
    reason: str,
    output_dir: Path | None,
    data_dir: Path | None,
) -> dict[str, Any]:
    return {
        "package_name": package_name,
        "status": "skipped",
        "package_role": package_role,
        "data_dir": _safe_path(data_dir),
        "mapping_config_path": None,
        "output_dir": _safe_path(output_dir),
        "summary_file": None,
        "skip_reason": reason,
        "outputs_produced": {},
    }


def _write_summary(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def _planned_package_names(requested: dict[str, bool]) -> list[str]:
    order = ["monthly_monitoring", "annual_appendix_work", "advanced_appendix"]
    return [package_name for package_name in order if requested.get(package_name)]


def run_local_source_profile(
    profile_path: str | Path,
    *,
    scope: str | None = None,
    dry_run: bool = False,
    validate_only: bool = False,
) -> dict[str, Any]:
    """Run the requested local profile scope and write a unified execution summary."""

    if dry_run and validate_only:
        raise ValueError("Choose either dry_run or validate_only, not both.")

    profile = load_local_source_profile(profile_path)
    resolved_scope = scope or profile.runner.default_scope
    if resolved_scope not in RUNNER_SCOPE_CHOICES:
        raise ValueError(f"Unsupported scope '{resolved_scope}'. Choose from {', '.join(RUNNER_SCOPE_CHOICES)}.")

    requested = _requested_packages(profile, resolved_scope)
    preflight_checks = validate_local_source_profile(profile, resolved_scope)
    preflight_failed = any(check["status"] == "fail" for check in preflight_checks)
    summary_path = _summary_output_path(profile, resolved_scope)

    summary: dict[str, Any] = {
        "run_timestamp_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "runner_status": "failed",
        "execution_mode": "dry_run" if dry_run else "validate_only" if validate_only else "run",
        "profile_name": profile.profile_name,
        "profile_path": _safe_path(profile.path),
        "profile_description": profile.description,
        "requested_scope": resolved_scope,
        "planned_packages": _planned_package_names(requested),
        "public_repo_boundary": profile.public_repo_boundary,
        "preflight_status": "fail" if preflight_failed else "pass",
        "preflight_checks": preflight_checks,
        "package_results": [],
        "summary_file": _safe_path(summary_path),
    }

    if dry_run:
        summary["runner_status"] = "failed" if preflight_failed else "dry_run"
        _write_summary(summary_path, summary)
        return summary

    if validate_only:
        summary["package_results"] = [
            {
                "package_name": package_name,
                "status": "ready" if _package_status([check for check in preflight_checks if check["package_name"] == package_name]) == "pass" else "validation_failed",
            }
            for package_name in _planned_package_names(requested)
        ]
        summary["runner_status"] = "validation_failed" if preflight_failed else "validated"
        _write_summary(summary_path, summary)
        return summary

    if preflight_failed:
        summary["runner_status"] = "failed"
        _write_summary(summary_path, summary)
        return summary

    monthly_succeeded = True
    annual_succeeded = True

    if requested["monthly_monitoring"]:
        monthly_section = profile.monthly_monitoring
        assert monthly_section is not None  # validated above
        try:
            outputs = build_monthly_monitoring_outputs(
                data_dir=monthly_section.raw_source_dir,
                mapping_config_path=monthly_section.mapping_config,
                output_dir=monthly_section.output_dir,
            )
            summary["package_results"].append(_monthly_result(outputs, monthly_section))
        except Exception as error:
            monthly_succeeded = False
            summary["package_results"].append(
                _failed_result(
                    package_name="monthly_monitoring",
                    package_role="core_monthly_monitoring",
                    error=error,
                    output_dir=monthly_section.output_dir,
                    data_dir=monthly_section.raw_source_dir,
                    mapping_config_path=monthly_section.mapping_config,
                )
            )

    if requested["annual_appendix_work"]:
        annual_section = profile.annual_appendix
        assert annual_section is not None  # validated above
        try:
            outputs = build_annual_appendix_work_outputs(
                data_dir=annual_section.raw_source_dir,
                mapping_config_path=annual_section.mapping_config,
                output_dir=annual_section.canonical_output_dir,
            )
            summary["package_results"].append(_annual_result(outputs, annual_section))
        except Exception as error:
            annual_succeeded = False
            summary["package_results"].append(
                _failed_result(
                    package_name="annual_appendix_work",
                    package_role="secondary_annual_appendix_work",
                    error=error,
                    output_dir=annual_section.canonical_output_dir,
                    data_dir=annual_section.raw_source_dir,
                    mapping_config_path=annual_section.mapping_config,
                )
            )

    if requested["advanced_appendix"]:
        annual_section = profile.annual_appendix
        assert annual_section is not None
        advanced_section = annual_section.advanced_appendix
        assert advanced_section is not None

        canonical_dependency = (advanced_section.input_mode or "canonical") == "canonical"
        if canonical_dependency and not annual_succeeded:
            summary["package_results"].append(
                _skipped_result(
                    package_name="advanced_appendix",
                    package_role="secondary_valuation_risk_appendix",
                    reason="Skipped because annual appendix canonicalization did not complete successfully.",
                    output_dir=advanced_section.output_dir,
                    data_dir=advanced_section.data_dir,
                )
            )
        else:
            try:
                outputs = build_advanced_appendix_outputs(
                    config_path=advanced_section.config_path,
                    output_dir=advanced_section.output_dir,
                    input_mode=advanced_section.input_mode,
                    benchmark_mode=advanced_section.benchmark_mode,
                    data_dir=advanced_section.data_dir,
                )
                summary["package_results"].append(_advanced_result(outputs, advanced_section))
            except Exception as error:
                summary["package_results"].append(
                    _failed_result(
                        package_name="advanced_appendix",
                        package_role="secondary_valuation_risk_appendix",
                        error=error,
                        output_dir=advanced_section.output_dir,
                        data_dir=advanced_section.data_dir,
                        mapping_config_path=None,
                    )
                )

    execution_failed = any(result.get("status") == "failed" for result in summary["package_results"])
    summary["runner_status"] = "failed" if execution_failed else "success"
    _write_summary(summary_path, summary)
    return summary


def render_local_profile_console_summary(summary: dict[str, Any]) -> str:
    """Render a concise human-readable summary for terminal output."""

    lines = [
        f"Local profile run: {summary['profile_name']}",
        f"- scope: {summary['requested_scope']}",
        f"- mode: {summary['execution_mode']}",
        f"- status: {summary['runner_status']}",
        f"- preflight: {summary['preflight_status']}",
    ]

    if summary.get("package_results"):
        lines.append("Package results:")
        for package in summary["package_results"]:
            package_name = package.get("package_name", "unknown_package")
            package_status = package.get("status", "unknown")
            package_bits = [f"- {package_name}: {package_status}"]
            if package.get("checks_failed") is not None:
                package_bits.append(f"checks_failed={package['checks_failed']}")
            if package.get("mapping_config_path"):
                package_bits.append(f"mapping={package['mapping_config_path']}")
            if package.get("benchmark_mode"):
                package_bits.append(f"benchmark_mode={package['benchmark_mode']}")
            if package.get("skip_reason"):
                package_bits.append(package["skip_reason"])
            if package.get("error_message"):
                package_bits.append(package["error_message"])
            lines.append(" | ".join(package_bits))
    else:
        lines.append("Package results:")
        lines.append("- no packages executed")

    if summary.get("summary_file"):
        lines.append(f"Summary JSON: {summary['summary_file']}")
    return "\n".join(lines)
