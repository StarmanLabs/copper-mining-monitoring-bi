"""Public-safe data quality reporting for the monthly monitoring flow."""

from __future__ import annotations

from typing import Iterable

import pandas as pd

from .monthly_validation import DatasetSchema


def _result_row(
    dataset_name: str,
    schema: DatasetSchema,
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


def _check_required_columns(frame: pd.DataFrame, schema: DatasetSchema) -> dict[str, object]:
    missing_columns = [column for column in schema.required_columns if column not in frame.columns]
    if missing_columns:
        return _result_row(
            dataset_name=schema.name,
            schema=schema,
            check_name="required_columns_present",
            status="fail",
            issue_count=len(missing_columns),
            affected_columns=missing_columns,
            detail="Missing required columns after source mapping.",
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


def _check_required_values(frame: pd.DataFrame, schema: DatasetSchema) -> dict[str, object]:
    missing_counts = {
        column: int(frame[column].isna().sum()) for column in schema.required_columns if column in frame.columns and frame[column].isna().any()
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
            detail="Required columns contain missing values.",
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


def _check_duplicate_keys(frame: pd.DataFrame, schema: DatasetSchema) -> dict[str, object]:
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


def _period_columns(schema: DatasetSchema, frame: pd.DataFrame) -> list[str]:
    return [column for column, rule in schema.field_rules.items() if rule.is_period and column in frame.columns]


def _check_period_values(frame: pd.DataFrame, schema: DatasetSchema) -> dict[str, object]:
    period_columns = _period_columns(schema, frame)
    if not period_columns:
        return _result_row(
            dataset_name=schema.name,
            schema=schema,
            check_name="period_values_valid",
            status="not_applicable",
            issue_count=0,
            detail="No period columns defined for this dataset.",
        )

    issues: list[str] = []
    issue_count = 0
    for column in period_columns:
        text_values = frame[column].dropna().astype(str).str.strip()
        invalid_format = text_values.loc[~text_values.str.fullmatch(r"\d{4}-\d{2}")]
        if not invalid_format.empty:
            issue_count += int(len(invalid_format))
            issues.append(f"{column} invalid format: {invalid_format.head(3).tolist()}")
            continue
        parsed = pd.to_datetime(text_values + "-01", format="%Y-%m-%d", errors="coerce")
        if parsed.isna().any():
            invalid_values = text_values.loc[parsed.isna()].head(3).tolist()
            issue_count += int(parsed.isna().sum())
            issues.append(f"{column} non-parsable: {invalid_values}")

    if issues:
        return _result_row(
            dataset_name=schema.name,
            schema=schema,
            check_name="period_values_valid",
            status="fail",
            issue_count=issue_count,
            affected_columns=period_columns,
            detail="Invalid or inconsistent monthly period values detected.",
            sample_values=issues[:5],
        )

    return _result_row(
        dataset_name=schema.name,
        schema=schema,
        check_name="period_values_valid",
        status="pass",
        issue_count=0,
        affected_columns=period_columns,
        detail="Monthly period values are valid and parseable.",
    )


def _check_period_sequence(frame: pd.DataFrame, schema: DatasetSchema) -> dict[str, object]:
    period_columns = _period_columns(schema, frame)
    if "period" not in period_columns:
        return _result_row(
            dataset_name=schema.name,
            schema=schema,
            check_name="period_sequence_complete",
            status="not_applicable",
            issue_count=0,
            detail="Period-sequence checks require a canonical period column.",
        )

    text_values = frame["period"].dropna().astype(str).str.strip()
    if text_values.empty or not text_values.str.fullmatch(r"\d{4}-\d{2}").all():
        return _result_row(
            dataset_name=schema.name,
            schema=schema,
            check_name="period_sequence_complete",
            status="not_applicable",
            issue_count=0,
            affected_columns=("period",),
            detail="Period values must be valid before sequence checks can run.",
        )

    grouping_columns = [column for column in schema.key_columns if column != "period" and column in frame.columns]
    if grouping_columns:
        grouped_frames = frame.groupby(grouping_columns, sort=True, dropna=False)
    else:
        grouped_frames = [((), frame)]

    missing_examples: list[str] = []
    missing_total = 0
    for group_key, group_frame in grouped_frames:
        group_periods = pd.PeriodIndex(group_frame["period"].dropna().astype(str), freq="M")
        if group_periods.empty:
            continue
        expected = pd.period_range(group_periods.min(), group_periods.max(), freq="M")
        missing = expected.difference(group_periods.unique())
        if len(missing) == 0:
            continue
        missing_total += int(len(missing))
        if not isinstance(group_key, tuple):
            group_key = (group_key,)
        group_label = ", ".join(f"{column}={value}" for column, value in zip(grouping_columns, group_key)) or "all_rows"
        missing_examples.append(f"{group_label}: {', '.join(str(value) for value in missing[:4])}")

    if missing_examples:
        return _result_row(
            dataset_name=schema.name,
            schema=schema,
            check_name="period_sequence_complete",
            status="fail",
            issue_count=missing_total,
            affected_columns=(*grouping_columns, "period"),
            detail="Missing monthly periods were detected within the observed sequence.",
            sample_values=missing_examples[:5],
        )

    return _result_row(
        dataset_name=schema.name,
        schema=schema,
        check_name="period_sequence_complete",
        status="pass",
        issue_count=0,
        affected_columns=(*grouping_columns, "period"),
        detail="Monthly periods are contiguous within each observed key sequence.",
    )


def _check_month_fields(frame: pd.DataFrame, schema: DatasetSchema) -> dict[str, object]:
    required_columns = ("period", "month_start_date", "calendar_year", "calendar_month")
    if not set(required_columns).issubset(frame.columns):
        return _result_row(
            dataset_name=schema.name,
            schema=schema,
            check_name="month_fields_consistent",
            status="not_applicable",
            issue_count=0,
            detail="Derived month-field checks require period, month_start_date, calendar_year, and calendar_month.",
        )

    parsed = pd.to_datetime(frame["period"].astype(str) + "-01", format="%Y-%m-%d", errors="coerce")
    expected_month_start = parsed.dt.strftime("%Y-%m-%d")
    mismatch_mask = (
        frame["month_start_date"].astype(str).ne(expected_month_start)
        | pd.to_numeric(frame["calendar_year"], errors="coerce").ne(parsed.dt.year)
        | pd.to_numeric(frame["calendar_month"], errors="coerce").ne(parsed.dt.month)
    )
    if "month_label" in frame.columns:
        expected_labels = parsed.dt.strftime("%b %Y")
        mismatch_mask = mismatch_mask | frame["month_label"].astype(str).ne(expected_labels)

    mismatches = frame.loc[mismatch_mask, ["period"]].astype(str)
    if not mismatches.empty:
        return _result_row(
            dataset_name=schema.name,
            schema=schema,
            check_name="month_fields_consistent",
            status="fail",
            issue_count=int(len(mismatches)),
            affected_columns=required_columns,
            detail="Derived month fields do not align with the reporting period.",
            sample_values=mismatches["period"].head(5).tolist(),
        )

    return _result_row(
        dataset_name=schema.name,
        schema=schema,
        check_name="month_fields_consistent",
        status="pass",
        issue_count=0,
        affected_columns=required_columns,
        detail="Derived month fields align with the reporting period.",
    )


def _check_numeric_ranges(frame: pd.DataFrame, schema: DatasetSchema) -> dict[str, object]:
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
            detail="Numeric range checks detected invalid values, impossible percentages, or invalid negatives.",
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


def build_data_quality_report(
    dataset_frames: dict[str, pd.DataFrame],
    schemas: dict[str, DatasetSchema],
) -> pd.DataFrame:
    """Build a public-safe data quality report for monthly monitoring datasets."""

    rows: list[dict[str, object]] = []
    for dataset_name, schema in schemas.items():
        if dataset_name not in dataset_frames:
            continue
        frame = dataset_frames[dataset_name]
        rows.append(_check_required_columns(frame, schema))
        rows.append(_check_required_values(frame, schema))
        rows.append(_check_duplicate_keys(frame, schema))
        rows.append(_check_period_values(frame, schema))
        rows.append(_check_period_sequence(frame, schema))
        rows.append(_check_month_fields(frame, schema))
        rows.append(_check_numeric_ranges(frame, schema))

    return pd.DataFrame(rows)


def summarize_data_quality_report(report: pd.DataFrame) -> dict[str, object]:
    """Summarize data quality results for refresh reporting."""

    effective_report = report.loc[report["status"].isin(["pass", "fail"])].copy()
    failed_checks = effective_report.loc[effective_report["status"] == "fail"]
    return {
        "checks_passed": int((effective_report["status"] == "pass").sum()),
        "checks_failed": int((effective_report["status"] == "fail").sum()),
        "datasets_with_failures": sorted(failed_checks["dataset_name"].unique().tolist()),
        "failed_check_examples": failed_checks.loc[:, ["dataset_name", "check_name", "detail"]].head(10).to_dict("records"),
    }
