"""Private-adaptable mapping and validation helpers for annual appendix inputs."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable

import pandas as pd
import yaml

from .annual_appendix_inputs import (
    build_annual_appendix_dataset_catalog,
    build_annual_appendix_field_catalog,
    validate_annual_appendix_inputs,
    validate_appendix_benchmark_metrics,
    validate_appendix_parameter_table,
    validate_appendix_scenarios,
)
from .file_outputs import write_csv_output, write_json_output
from .refresh_reporting import reproducible_refresh_metadata


@dataclass(frozen=True)
class AnnualColumnRule:
    """Validation metadata for annual appendix work-adaptation fields."""

    description: str
    unit: str | None = None
    numeric: bool = False
    min_value: float | None = None
    max_value: float | None = None


@dataclass(frozen=True)
class AnnualDatasetSchema:
    """Canonical schema definition for annual appendix adaptation datasets."""

    name: str
    description: str
    grain: str
    key_columns: tuple[str, ...]
    required_columns: tuple[str, ...]
    optional_columns: tuple[str, ...] = ()
    nullable_required_columns: tuple[str, ...] = ()
    layer: str = "appendix_source"
    key_logic: str = ""
    limitation_note: str = ""
    field_rules: dict[str, AnnualColumnRule] = field(default_factory=dict)


ANNUAL_APPENDIX_SOURCE_DATASETS = (
    "annual_appendix_inputs",
    "appendix_parameters",
    "appendix_scenarios",
    "appendix_benchmark_metrics",
)


def _sample_data_dir() -> Path:
    return Path("data") / "sample_data" / "annual_appendix"


def _default_mapping_config() -> Path:
    return Path("config") / "mappings" / "public_demo_annual_appendix_identity_mapping.yaml"


def _public_safe_path(path: str | Path | None) -> str | None:
    if path is None:
        return None
    path_obj = Path(path)
    try:
        return path_obj.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path_obj.name


def _build_canonical_schemas() -> dict[str, AnnualDatasetSchema]:
    return {
        "annual_appendix_inputs": AnnualDatasetSchema(
            name="annual_appendix_inputs",
            description="Canonical annual appendix driver table for valuation, scenario comparison, and simulation.",
            grain="One row per project year.",
            key_columns=("year",),
            required_columns=(
                "year",
                "calendar_year",
                "copper_price_usd_per_lb",
                "base_processed_tonnes",
                "base_head_grade",
                "base_recovery",
                "base_unit_cost_usd_per_tonne",
                "expansion_unit_cost_usd_per_tonne",
                "initial_capex_usd",
                "sustaining_capex_usd",
            ),
            key_logic="Each project year should appear once with the base annual commercial, operating, and capex drivers used by the appendix.",
            limitation_note="Planning-style annual drivers, not a detailed mine-plan or corporate-finance model.",
            field_rules={
                "year": AnnualColumnRule("Project year starting at 1.", unit="year", numeric=True, min_value=1),
                "calendar_year": AnnualColumnRule("Calendar year used for reporting.", unit="year", numeric=True, min_value=2000, max_value=2100),
                "copper_price_usd_per_lb": AnnualColumnRule("Base copper price deck.", unit="USD/lb", numeric=True, min_value=0.01),
                "base_processed_tonnes": AnnualColumnRule("Base processed tonnes.", unit="tonnes", numeric=True, min_value=1),
                "base_head_grade": AnnualColumnRule("Base head grade in decimal form.", unit="grade_decimal", numeric=True, min_value=0.0, max_value=1.0),
                "base_recovery": AnnualColumnRule("Base recovery in decimal form.", unit="recovery_decimal", numeric=True, min_value=0.0, max_value=1.0),
                "base_unit_cost_usd_per_tonne": AnnualColumnRule("Base-operation unit cost.", unit="USD/t", numeric=True, min_value=0.0),
                "expansion_unit_cost_usd_per_tonne": AnnualColumnRule("Expanded-operation unit cost.", unit="USD/t", numeric=True, min_value=0.0),
                "initial_capex_usd": AnnualColumnRule("Initial capex by project year.", unit="USD", numeric=True, min_value=0.0),
                "sustaining_capex_usd": AnnualColumnRule("Sustaining capex by project year.", unit="USD", numeric=True, min_value=0.0),
            },
        ),
        "appendix_parameters": AnnualDatasetSchema(
            name="appendix_parameters",
            description="Canonical scalar parameter table for the annual appendix.",
            grain="One row per parameter_name.",
            key_columns=("parameter_name",),
            required_columns=(
                "parameter_name",
                "value",
                "unit",
                "parameter_group",
                "used_by",
                "source_type",
                "source_reference",
                "note",
            ),
            key_logic="Each parameter should appear once with value, semantic grouping, and source traceability.",
            limitation_note="Scalar parameter values remain simplified and public-safe.",
            field_rules={
                "value": AnnualColumnRule("Numeric parameter value.", numeric=True),
            },
        ),
        "appendix_scenarios": AnnualDatasetSchema(
            name="appendix_scenarios",
            description="Canonical deterministic scenario registry for the annual appendix.",
            grain="One row per scenario_id.",
            key_columns=("scenario_id",),
            required_columns=(
                "scenario_id",
                "scenario_name",
                "category",
                "description",
                "price_factor",
                "grade_factor",
                "recovery_factor",
                "throughput_factor",
                "opex_factor",
                "capex_factor",
                "wacc_shift_bps",
            ),
            key_logic="Each scenario must define one set of public-safe planning multipliers.",
            limitation_note="Scenario shocks are illustrative planning cases rather than committee-grade budgets or investment cases.",
            field_rules={
                "price_factor": AnnualColumnRule("Scenario price multiplier.", unit="ratio", numeric=True, min_value=0.01),
                "grade_factor": AnnualColumnRule("Scenario grade multiplier.", unit="ratio", numeric=True, min_value=0.01),
                "recovery_factor": AnnualColumnRule("Scenario recovery multiplier.", unit="ratio", numeric=True, min_value=0.01),
                "throughput_factor": AnnualColumnRule("Scenario throughput multiplier.", unit="ratio", numeric=True, min_value=0.01),
                "opex_factor": AnnualColumnRule("Scenario opex multiplier.", unit="ratio", numeric=True, min_value=0.01),
                "capex_factor": AnnualColumnRule("Scenario capex multiplier.", unit="ratio", numeric=True, min_value=0.01),
                "wacc_shift_bps": AnnualColumnRule("Discount-rate shift in basis points.", unit="bps", numeric=True, min_value=-5000, max_value=5000),
            },
        ),
        "appendix_benchmark_metrics": AnnualDatasetSchema(
            name="appendix_benchmark_metrics",
            description="Canonical benchmark metric table for appendix transparency.",
            grain="One row per metric.",
            key_columns=("metric",),
            required_columns=(
                "metric",
                "value",
                "unit",
                "currency",
                "valuation_basis",
                "timing_basis",
                "benchmark_source",
                "note",
            ),
            nullable_required_columns=("currency",),
            key_logic="Each benchmark metric should appear once with source and comparability metadata.",
            limitation_note="Benchmark values can remain legacy-derived reference points even when the appendix input path is canonical.",
            field_rules={
                "value": AnnualColumnRule("Benchmark metric value.", numeric=True),
            },
        ),
    }


ANNUAL_APPENDIX_CANONICAL_SCHEMAS = _build_canonical_schemas()


CANONICAL_APPENDIX_VALIDATORS: dict[str, Callable[[pd.DataFrame], pd.DataFrame]] = {
    "annual_appendix_inputs": validate_annual_appendix_inputs,
    "appendix_parameters": validate_appendix_parameter_table,
    "appendix_scenarios": validate_appendix_scenarios,
    "appendix_benchmark_metrics": validate_appendix_benchmark_metrics,
}


def load_annual_appendix_mapping_config(path: str | Path) -> dict:
    """Load a YAML annual appendix source-mapping configuration."""

    path = Path(path)
    with path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict) or "datasets" not in config:
        raise ValueError(f"Annual appendix mapping config '{path}' must contain a top-level 'datasets' section.")
    return config


def normalize_year_series(series: pd.Series) -> pd.Series:
    """Normalize year-like values to integer years where possible."""

    text_series = series.astype("string").str.strip()
    numeric = pd.to_numeric(text_series, errors="coerce")
    extracted = pd.to_numeric(text_series.str.extract(r"((?:19|20)\d{2})")[0], errors="coerce")
    parsed = numeric.fillna(extracted)
    normalized = parsed.round().astype("Int64")
    return normalized.where(parsed.notna(), series)


def map_annual_appendix_source_dataframe(
    source_frame: pd.DataFrame,
    dataset_name: str,
    dataset_mapping: dict,
    target_schema: AnnualDatasetSchema,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Map a source DataFrame into the repository's canonical annual appendix schema."""

    column_map = dataset_mapping.get("column_map", {})
    defaults = dataset_mapping.get("defaults", {})
    value_multipliers = dataset_mapping.get("value_multipliers", {})
    normalize_year = bool(dataset_mapping.get("normalize_year", True))

    renamed = source_frame.rename(columns=column_map).copy()
    default_columns_applied: list[str] = []
    for column, value in defaults.items():
        if column not in renamed.columns:
            renamed[column] = value
            default_columns_applied.append(column)
        elif renamed[column].isna().any():
            renamed[column] = renamed[column].fillna(value)
            default_columns_applied.append(column)

    for column, multiplier in value_multipliers.items():
        if column in renamed.columns:
            renamed[column] = pd.to_numeric(renamed[column], errors="coerce") * float(multiplier)

    if normalize_year:
        for column in ("year", "calendar_year"):
            if column in renamed.columns:
                renamed[column] = normalize_year_series(renamed[column])

    canonical_column_order = [
        column
        for column in list(target_schema.required_columns) + list(target_schema.optional_columns)
        if column in renamed.columns
    ]
    mapped = renamed.loc[:, canonical_column_order].copy()

    missing_required = [column for column in target_schema.required_columns if column not in mapped.columns]
    mapped_source_columns = [source_column for source_column in column_map if source_column in source_frame.columns]
    unmapped_source_columns = [column for column in source_frame.columns if column not in column_map]
    status = "ready_for_validation" if not missing_required else "missing_required_columns"

    audit_row = {
        "dataset_name": dataset_name,
        "source_dataset_label": dataset_mapping.get("source_dataset_label", dataset_name),
        "source_file": dataset_mapping["source_file"],
        "source_rows": int(len(source_frame)),
        "mapped_rows": int(len(mapped)),
        "source_column_count": int(len(source_frame.columns)),
        "mapped_column_count": int(len(mapped.columns)),
        "mapped_columns": "; ".join(mapped.columns),
        "mapped_source_columns": "; ".join(mapped_source_columns),
        "unmapped_source_columns": "; ".join(unmapped_source_columns),
        "default_columns_applied": "; ".join(default_columns_applied),
        "missing_required_columns_after_mapping": "; ".join(missing_required),
        "normalize_year_flag": normalize_year and any(column in mapped.columns for column in ("year", "calendar_year")),
        "status": status,
        "mapping_note": dataset_mapping.get("mapping_note", ""),
    }
    return mapped, audit_row


def map_annual_appendix_source_directory(
    data_dir: str | Path,
    mapping_config_path: str | Path,
    target_schemas: dict[str, AnnualDatasetSchema],
) -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    """Load raw annual appendix files from a directory and map them to canonical datasets."""

    data_dir = Path(data_dir)
    mapping_config = load_annual_appendix_mapping_config(mapping_config_path)
    dataset_mappings = mapping_config.get("datasets", {})

    mapped_frames: dict[str, pd.DataFrame] = {}
    audit_rows: list[dict[str, object]] = []

    for dataset_name, target_schema in target_schemas.items():
        if dataset_name not in dataset_mappings:
            raise ValueError(f"Annual appendix mapping config is missing a dataset section for '{dataset_name}'.")
        dataset_mapping = dataset_mappings[dataset_name]
        source_path = data_dir / dataset_mapping["source_file"]
        if not source_path.exists():
            raise FileNotFoundError(f"Mapped annual appendix source file not found for '{dataset_name}': {source_path}")
        source_frame = pd.read_csv(source_path)
        mapped_frame, audit_row = map_annual_appendix_source_dataframe(
            source_frame=source_frame,
            dataset_name=dataset_name,
            dataset_mapping=dataset_mapping,
            target_schema=target_schema,
        )
        mapped_frames[dataset_name] = mapped_frame
        audit_rows.append(audit_row)

    audit = pd.DataFrame(audit_rows).sort_values("dataset_name").reset_index(drop=True)
    return mapped_frames, audit


def _load_canonical_appendix_inputs(data_dir: str | Path) -> dict[str, pd.DataFrame]:
    data_dir = Path(data_dir)
    return {
        dataset_name: pd.read_csv(data_dir / f"{dataset_name}.csv")
        for dataset_name in ANNUAL_APPENDIX_SOURCE_DATASETS
    }


def _identity_source_mapping_audit(dataset_frames: dict[str, pd.DataFrame], data_dir: str | Path) -> pd.DataFrame:
    """Build a simple audit table when appendix inputs are already canonical."""

    data_dir = Path(data_dir)
    rows = []
    for dataset_name, frame in dataset_frames.items():
        rows.append(
            {
                "dataset_name": dataset_name,
                "source_dataset_label": f"canonical_{dataset_name}",
                "source_file": str((data_dir / f"{dataset_name}.csv").as_posix()),
                "source_rows": int(len(frame)),
                "mapped_rows": int(len(frame)),
                "source_column_count": int(len(frame.columns)),
                "mapped_column_count": int(len(frame.columns)),
                "mapped_columns": "; ".join(frame.columns),
                "mapped_source_columns": "; ".join(frame.columns),
                "unmapped_source_columns": "",
                "default_columns_applied": "",
                "missing_required_columns_after_mapping": "",
                "normalize_year_flag": any(column in frame.columns for column in ("year", "calendar_year")),
                "status": "ready_for_validation",
                "mapping_note": "Inputs were already in canonical annual appendix form.",
            }
        )
    return pd.DataFrame(rows).sort_values("dataset_name").reset_index(drop=True)


def validate_annual_appendix_work_inputs(dataset_frames: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Validate each canonical annual appendix dataset."""

    validated: dict[str, pd.DataFrame] = {}
    for dataset_name in ANNUAL_APPENDIX_SOURCE_DATASETS:
        validator = CANONICAL_APPENDIX_VALIDATORS[dataset_name]
        frame = validator(dataset_frames[dataset_name]).copy()
        key_columns = [column for column in ANNUAL_APPENDIX_CANONICAL_SCHEMAS[dataset_name].key_columns if column in frame.columns]
        # Scenario order is intentionally business-defined in the source table and should
        # remain stable across canonicalization, runner handoff, and Power BI appendix pages.
        if key_columns and dataset_name != "appendix_scenarios":
            frame = frame.sort_values(key_columns).reset_index(drop=True)
        validated[dataset_name] = frame
    return validated


def _result_row(
    dataset_name: str,
    schema: AnnualDatasetSchema,
    check_name: str,
    status: str,
    issue_count: int,
    affected_columns: Iterable[str] = (),
    detail: str = "",
    sample_values: Iterable[str] = (),
) -> dict[str, object]:
    return {
        "dataset_name": dataset_name,
        "dataset_layer": schema.layer,
        "check_name": check_name,
        "status": status,
        "issue_count": int(issue_count),
        "affected_columns": "; ".join(str(value) for value in affected_columns if value),
        "detail": detail,
        "sample_values": " | ".join(str(value) for value in sample_values if value),
    }


def _check_required_columns(frame: pd.DataFrame, schema: AnnualDatasetSchema) -> dict[str, object]:
    missing_columns = [column for column in schema.required_columns if column not in frame.columns]
    if missing_columns:
        return _result_row(
            dataset_name=schema.name,
            schema=schema,
            check_name="required_columns_present",
            status="fail",
            issue_count=len(missing_columns),
            affected_columns=missing_columns,
            detail="Missing required columns after annual appendix source mapping.",
            sample_values=missing_columns[:5],
        )
    return _result_row(
        dataset_name=schema.name,
        schema=schema,
        check_name="required_columns_present",
        status="pass",
        issue_count=0,
        affected_columns=schema.required_columns,
        detail="All required columns are present.",
    )


def _check_required_values(frame: pd.DataFrame, schema: AnnualDatasetSchema) -> dict[str, object]:
    missing_counts = {
        column: int(frame[column].isna().sum())
        for column in schema.required_columns
        if column not in set(schema.nullable_required_columns) and column in frame.columns and frame[column].isna().any()
    }
    if missing_counts:
        sample_values = [f"{column}={count}" for column, count in list(missing_counts.items())[:5]]
        return _result_row(
            dataset_name=schema.name,
            schema=schema,
            check_name="required_values_complete",
            status="fail",
            issue_count=sum(missing_counts.values()),
            affected_columns=missing_counts.keys(),
            detail="Required annual appendix columns contain missing values.",
            sample_values=sample_values,
        )
    return _result_row(
        dataset_name=schema.name,
        schema=schema,
        check_name="required_values_complete",
        status="pass",
        issue_count=0,
        affected_columns=schema.required_columns,
        detail="Required columns have no missing values.",
    )


def _check_duplicate_keys(frame: pd.DataFrame, schema: AnnualDatasetSchema) -> dict[str, object]:
    if not all(column in frame.columns for column in schema.key_columns):
        return _result_row(
            dataset_name=schema.name,
            schema=schema,
            check_name="duplicate_keys_absent",
            status="not_applicable",
            issue_count=0,
            affected_columns=schema.key_columns,
            detail="Key columns are not fully present, so duplicate-key checks are not applicable.",
        )
    duplicate_rows = frame.loc[frame.duplicated(list(schema.key_columns), keep=False), list(schema.key_columns)]
    if not duplicate_rows.empty:
        preview = duplicate_rows.astype(str).drop_duplicates().head(5).to_dict("records")
        return _result_row(
            dataset_name=schema.name,
            schema=schema,
            check_name="duplicate_keys_absent",
            status="fail",
            issue_count=int(len(duplicate_rows)),
            affected_columns=schema.key_columns,
            detail="Duplicate grain rows detected.",
            sample_values=preview,
        )
    return _result_row(
        dataset_name=schema.name,
        schema=schema,
        check_name="duplicate_keys_absent",
        status="pass",
        issue_count=0,
        affected_columns=schema.key_columns,
        detail="No duplicate grain rows detected.",
    )


def _check_year_sequence(frame: pd.DataFrame, schema: AnnualDatasetSchema) -> dict[str, object]:
    if "year" not in frame.columns:
        return _result_row(
            dataset_name=schema.name,
            schema=schema,
            check_name="year_sequence_complete",
            status="not_applicable",
            issue_count=0,
            detail="This dataset has no project-year field.",
        )

    numeric_years = pd.to_numeric(frame["year"], errors="coerce").dropna().astype(int).tolist()
    if not numeric_years:
        return _result_row(
            dataset_name=schema.name,
            schema=schema,
            check_name="year_sequence_complete",
            status="fail",
            issue_count=1,
            affected_columns=("year",),
            detail="Project-year values could not be interpreted as integers.",
        )

    expected_years = list(range(1, len(numeric_years) + 1))
    if numeric_years != expected_years:
        missing_years = sorted(set(expected_years).difference(numeric_years))
        return _result_row(
            dataset_name=schema.name,
            schema=schema,
            check_name="year_sequence_complete",
            status="fail",
            issue_count=max(len(missing_years), 1),
            affected_columns=("year",),
            detail="Project years must be contiguous starting at 1.",
            sample_values=[str(value) for value in missing_years[:5]] or [str(value) for value in numeric_years[:5]],
        )
    return _result_row(
        dataset_name=schema.name,
        schema=schema,
        check_name="year_sequence_complete",
        status="pass",
        issue_count=0,
        affected_columns=("year",),
        detail="Project years are contiguous and start at 1.",
    )


def _check_numeric_ranges(frame: pd.DataFrame, schema: AnnualDatasetSchema) -> dict[str, object]:
    issues: list[str] = []
    issue_count = 0
    affected_columns: list[str] = []
    for column, rule in schema.field_rules.items():
        if not rule.numeric or column not in frame.columns:
            continue

        numeric_series = pd.to_numeric(frame[column], errors="coerce")
        invalid_numeric = frame.loc[frame[column].notna() & numeric_series.isna(), column]
        if not invalid_numeric.empty:
            issue_count += int(len(invalid_numeric))
            affected_columns.append(column)
            issues.append(f"{column} non-numeric: {invalid_numeric.astype(str).head(3).tolist()}")
            continue

        if rule.min_value is not None:
            below_min = numeric_series.dropna().loc[numeric_series.dropna() < rule.min_value]
            if not below_min.empty:
                issue_count += int(len(below_min))
                affected_columns.append(column)
                issues.append(f"{column} below {rule.min_value}: {below_min.head(3).tolist()}")

        if rule.max_value is not None:
            above_max = numeric_series.dropna().loc[numeric_series.dropna() > rule.max_value]
            if not above_max.empty:
                issue_count += int(len(above_max))
                affected_columns.append(column)
                issues.append(f"{column} above {rule.max_value}: {above_max.head(3).tolist()}")

    if issues:
        return _result_row(
            dataset_name=schema.name,
            schema=schema,
            check_name="numeric_ranges_valid",
            status="fail",
            issue_count=issue_count,
            affected_columns=sorted(set(affected_columns)),
            detail="Numeric range checks detected invalid values or impossible annual appendix rates.",
            sample_values=issues[:5],
        )

    numeric_columns = [column for column, rule in schema.field_rules.items() if rule.numeric]
    return _result_row(
        dataset_name=schema.name,
        schema=schema,
        check_name="numeric_ranges_valid",
        status="pass",
        issue_count=0,
        affected_columns=numeric_columns,
        detail="Numeric values remain inside expected public-safe bounds.",
    )


def _check_canonical_contract(frame: pd.DataFrame, schema: AnnualDatasetSchema) -> dict[str, object]:
    validator = CANONICAL_APPENDIX_VALIDATORS[schema.name]
    try:
        validator(frame.copy())
    except Exception as error:
        return _result_row(
            dataset_name=schema.name,
            schema=schema,
            check_name="canonical_contract_valid",
            status="fail",
            issue_count=1,
            affected_columns=schema.required_columns,
            detail=str(error),
        )
    return _result_row(
        dataset_name=schema.name,
        schema=schema,
        check_name="canonical_contract_valid",
        status="pass",
        issue_count=0,
        affected_columns=schema.required_columns,
        detail="Dataset passes the canonical annual appendix validator.",
    )


def build_annual_appendix_data_quality_report(
    dataset_frames: dict[str, pd.DataFrame],
    schemas: dict[str, AnnualDatasetSchema],
) -> pd.DataFrame:
    """Build a public-safe data quality report for annual appendix source datasets."""

    rows: list[dict[str, object]] = []
    for dataset_name, schema in schemas.items():
        if dataset_name not in dataset_frames:
            continue
        frame = dataset_frames[dataset_name]
        rows.append(_check_required_columns(frame, schema))
        rows.append(_check_required_values(frame, schema))
        rows.append(_check_duplicate_keys(frame, schema))
        rows.append(_check_year_sequence(frame, schema))
        rows.append(_check_numeric_ranges(frame, schema))
        rows.append(_check_canonical_contract(frame, schema))
    return pd.DataFrame(rows)


def summarize_annual_appendix_data_quality_report(report: pd.DataFrame) -> dict[str, object]:
    """Summarize annual appendix data quality results for refresh reporting."""

    effective_report = report.loc[report["status"].isin(["pass", "fail"])].copy()
    failed_checks = effective_report.loc[effective_report["status"] == "fail"]
    return {
        "checks_passed": int((effective_report["status"] == "pass").sum()),
        "checks_failed": int((effective_report["status"] == "fail").sum()),
        "datasets_with_failures": sorted(failed_checks["dataset_name"].unique().tolist()),
        "failed_check_examples": failed_checks.loc[:, ["dataset_name", "check_name", "detail"]].head(10).to_dict("records"),
    }


def build_annual_appendix_refresh_summary(
    source_mapping_audit: pd.DataFrame,
    data_quality_summary: dict[str, object],
    output_files: dict[str, str],
    mapping_config_path: str | None,
    data_dir: str,
) -> dict[str, object]:
    """Build a concise JSON-friendly refresh summary for the annual appendix adaptation layer."""

    return {
        **reproducible_refresh_metadata(),
        "refresh_status": "success",
        "public_safe": True,
        "work_core_scope": "annual_appendix",
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
        "output_files": output_files,
    }


def build_failed_annual_appendix_refresh_summary(
    error: Exception,
    mapping_config_path: str | None,
    data_dir: str,
) -> dict[str, object]:
    """Build a failure summary when the annual appendix work package does not complete."""

    return {
        **reproducible_refresh_metadata(),
        "refresh_status": "failed",
        "public_safe": True,
        "work_core_scope": "annual_appendix",
        "data_dir": data_dir,
        "mapping_config_path": mapping_config_path,
        "error_type": type(error).__name__,
        "error_message": str(error),
    }


def build_annual_appendix_work_outputs(
    data_dir: str | Path = _sample_data_dir(),
    mapping_config_path: str | Path | None = _default_mapping_config(),
    output_dir: str | Path = "outputs/bi",
) -> dict[str, Path]:
    """Build canonical annual appendix inputs plus audit and validation outputs."""

    if mapping_config_path is None:
        dataset_frames = _load_canonical_appendix_inputs(data_dir=data_dir)
        source_mapping_audit = _identity_source_mapping_audit(dataset_frames=dataset_frames, data_dir=data_dir)
        mapping_config_str = None
    else:
        dataset_frames, source_mapping_audit = map_annual_appendix_source_directory(
            data_dir=data_dir,
            mapping_config_path=mapping_config_path,
            target_schemas=ANNUAL_APPENDIX_CANONICAL_SCHEMAS,
        )
        mapping_config_str = _public_safe_path(mapping_config_path)

    validated_inputs = validate_annual_appendix_work_inputs(dataset_frames)
    data_quality_report = build_annual_appendix_data_quality_report(
        dataset_frames=validated_inputs,
        schemas=ANNUAL_APPENDIX_CANONICAL_SCHEMAS,
    )
    dataset_catalog = build_annual_appendix_dataset_catalog()
    field_catalog = build_annual_appendix_field_catalog()

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    outputs = {
        "annual_appendix_dataset_catalog": output_dir / "annual_appendix_dataset_catalog.csv",
        "annual_appendix_field_catalog": output_dir / "annual_appendix_field_catalog.csv",
        "annual_appendix_inputs": output_dir / "annual_appendix_inputs.csv",
        "appendix_parameters": output_dir / "appendix_parameters.csv",
        "appendix_scenarios": output_dir / "appendix_scenarios.csv",
        "appendix_benchmark_metrics": output_dir / "appendix_benchmark_metrics.csv",
        "annual_appendix_source_mapping_audit": output_dir / "annual_appendix_source_mapping_audit.csv",
        "annual_appendix_data_quality_report": output_dir / "annual_appendix_data_quality_report.csv",
        "annual_appendix_refresh_summary": output_dir / "annual_appendix_refresh_summary.json",
    }

    write_csv_output(dataset_catalog, outputs["annual_appendix_dataset_catalog"])
    write_csv_output(field_catalog, outputs["annual_appendix_field_catalog"])
    write_csv_output(validated_inputs["annual_appendix_inputs"], outputs["annual_appendix_inputs"])
    write_csv_output(validated_inputs["appendix_parameters"], outputs["appendix_parameters"])
    write_csv_output(validated_inputs["appendix_scenarios"], outputs["appendix_scenarios"])
    write_csv_output(validated_inputs["appendix_benchmark_metrics"], outputs["appendix_benchmark_metrics"])
    write_csv_output(source_mapping_audit, outputs["annual_appendix_source_mapping_audit"])
    write_csv_output(data_quality_report, outputs["annual_appendix_data_quality_report"])

    refresh_summary = build_annual_appendix_refresh_summary(
        source_mapping_audit=source_mapping_audit,
        data_quality_summary=summarize_annual_appendix_data_quality_report(data_quality_report),
        output_files={name: _public_safe_path(path) or str(path) for name, path in outputs.items() if name != "annual_appendix_refresh_summary"},
        mapping_config_path=mapping_config_str,
        data_dir=_public_safe_path(data_dir) or str(data_dir),
    )
    write_json_output(outputs["annual_appendix_refresh_summary"], refresh_summary)
    return outputs
