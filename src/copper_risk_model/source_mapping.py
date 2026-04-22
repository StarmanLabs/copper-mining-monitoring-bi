"""Config-driven source mapping for canonical monthly monitoring datasets."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from .monthly_validation import DatasetSchema


def load_mapping_config(path: str | Path) -> dict:
    """Load a YAML source-mapping configuration."""

    path = Path(path)
    with path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict) or "datasets" not in config:
        raise ValueError(f"Mapping config '{path}' must contain a top-level 'datasets' section.")
    return config


def normalize_period_series(series: pd.Series) -> pd.Series:
    """Normalize monthly period values to YYYY-MM when possible."""

    text_series = series.astype("string").str.strip()
    already_monthly = text_series.str.fullmatch(r"\d{4}-\d{2}")
    normalized = text_series.where(already_monthly, text_series.str.replace("/", "-", regex=False))
    parsed = pd.to_datetime(normalized, errors="coerce")
    fallback = pd.to_datetime(normalized + "-01", format="%Y-%m-%d", errors="coerce")
    parsed = parsed.fillna(fallback)
    return parsed.dt.strftime("%Y-%m").where(parsed.notna(), series)


def map_source_dataframe(
    source_frame: pd.DataFrame,
    dataset_name: str,
    dataset_mapping: dict,
    target_schema: DatasetSchema,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Map a source DataFrame into the repository's canonical monthly schema."""

    column_map = dataset_mapping.get("column_map", {})
    defaults = dataset_mapping.get("defaults", {})
    value_multipliers = dataset_mapping.get("value_multipliers", {})
    normalize_period = bool(dataset_mapping.get("normalize_period", True))

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

    if normalize_period and "period" in renamed.columns:
        renamed["period"] = normalize_period_series(renamed["period"])

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
        "normalize_period_flag": normalize_period and "period" in mapped.columns,
        "status": status,
        "mapping_note": dataset_mapping.get("mapping_note", ""),
    }
    return mapped, audit_row


def map_source_directory(
    data_dir: str | Path,
    mapping_config_path: str | Path,
    target_schemas: dict[str, DatasetSchema],
) -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    """Load raw source files from a directory and map them to canonical datasets."""

    data_dir = Path(data_dir)
    mapping_config = load_mapping_config(mapping_config_path)
    dataset_mappings = mapping_config.get("datasets", {})

    mapped_frames: dict[str, pd.DataFrame] = {}
    audit_rows: list[dict[str, object]] = []

    for dataset_name, target_schema in target_schemas.items():
        if dataset_name not in dataset_mappings:
            raise ValueError(f"Mapping config is missing a dataset section for '{dataset_name}'.")
        dataset_mapping = dataset_mappings[dataset_name]
        source_path = data_dir / dataset_mapping["source_file"]
        if not source_path.exists():
            raise FileNotFoundError(f"Mapped source file not found for '{dataset_name}': {source_path}")
        source_frame = pd.read_csv(source_path)
        mapped_frame, audit_row = map_source_dataframe(
            source_frame=source_frame,
            dataset_name=dataset_name,
            dataset_mapping=dataset_mapping,
            target_schema=target_schema,
        )
        mapped_frames[dataset_name] = mapped_frame
        audit_rows.append(audit_row)

    audit = pd.DataFrame(audit_rows).sort_values("dataset_name").reset_index(drop=True)
    return mapped_frames, audit
