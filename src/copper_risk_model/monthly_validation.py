"""Validation helpers for canonical monthly monitoring datasets."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable

import pandas as pd

_PERIOD_PATTERN = re.compile(r"^\d{4}-\d{2}$")


@dataclass(frozen=True)
class ColumnRule:
    """Validation rule and field metadata for a dataset column."""

    description: str
    unit: str | None = None
    numeric: bool = False
    is_period: bool = False
    min_value: float | None = None
    max_value: float | None = None


@dataclass(frozen=True)
class DatasetSchema:
    """Canonical schema definition for a monthly dataset."""

    name: str
    description: str
    grain: str
    key_columns: tuple[str, ...]
    required_columns: tuple[str, ...]
    optional_columns: tuple[str, ...] = ()
    layer: str = "source"
    dashboard_use: str = ""
    key_logic: str = ""
    limitation_note: str = ""
    field_rules: dict[str, ColumnRule] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidationIssue:
    """Structured validation issue returned before raising."""

    dataset: str
    rule: str
    message: str
    column: str | None = None
    issue_count: int | None = None
    sample_values: tuple[str, ...] = ()


class DatasetValidationError(ValueError):
    """Raised when a canonical monthly dataset fails validation."""

    def __init__(self, dataset: str, issues: list[ValidationIssue]):
        self.dataset = dataset
        self.issues = issues
        details = "; ".join(f"[{issue.rule}] {issue.message}" for issue in issues)
        super().__init__(f"Dataset '{dataset}' failed validation: {details}")


def _format_group_key(group_columns: Iterable[str], group_key: object) -> str:
    columns = list(group_columns)
    if not columns:
        return "all_rows"
    if not isinstance(group_key, tuple):
        group_key = (group_key,)
    return ", ".join(f"{column}={value}" for column, value in zip(columns, group_key))


def collect_validation_issues(frame: pd.DataFrame, schema: DatasetSchema) -> list[ValidationIssue]:
    """Collect structured validation issues for a canonical monthly dataset."""

    issues: list[ValidationIssue] = []
    columns = set(frame.columns)

    missing_columns = [column for column in schema.required_columns if column not in columns]
    if missing_columns:
        issues.append(
            ValidationIssue(
                dataset=schema.name,
                rule="missing_required_columns",
                message="Missing columns: " + ", ".join(missing_columns),
                issue_count=len(missing_columns),
                sample_values=tuple(missing_columns[:5]),
            )
        )

    present_required = [column for column in schema.required_columns if column in columns]
    for column in present_required:
        missing_count = int(frame[column].isna().sum())
        if missing_count:
            issues.append(
                ValidationIssue(
                    dataset=schema.name,
                    rule="missing_required_values",
                    message=f"Column '{column}' has {missing_count} missing values.",
                    column=column,
                    issue_count=missing_count,
                )
            )

    if all(column in columns for column in schema.key_columns):
        duplicate_rows = frame.loc[frame.duplicated(list(schema.key_columns), keep=False), list(schema.key_columns)]
        if not duplicate_rows.empty:
            preview = duplicate_rows.astype(str).drop_duplicates().head(3).to_dict("records")
            issues.append(
                ValidationIssue(
                    dataset=schema.name,
                    rule="duplicate_keys",
                    message=f"Duplicate key rows detected for {schema.key_columns}: {preview}",
                    issue_count=int(len(duplicate_rows)),
                    sample_values=tuple(str(value) for value in preview[:3]),
                )
            )

    period_columns = [column for column, rule in schema.field_rules.items() if rule.is_period and column in columns]
    for column, rule in schema.field_rules.items():
        if column not in columns:
            continue

        series = frame[column]

        if rule.is_period:
            text_values = series.dropna().astype(str)
            invalid_format = text_values.loc[~text_values.str.match(_PERIOD_PATTERN)]
            if not invalid_format.empty:
                sample_values = invalid_format.head(5).tolist()
                issues.append(
                    ValidationIssue(
                        dataset=schema.name,
                        rule="invalid_period_format",
                        message=f"Column '{column}' contains invalid period values: {sample_values}",
                        column=column,
                        issue_count=int(len(invalid_format)),
                        sample_values=tuple(str(value) for value in sample_values),
                    )
                )
            else:
                parsed = pd.to_datetime(text_values + "-01", format="%Y-%m-%d", errors="coerce")
                if parsed.isna().any():
                    sample_values = text_values.loc[parsed.isna()].head(5).tolist()
                    issues.append(
                        ValidationIssue(
                            dataset=schema.name,
                            rule="invalid_period_value",
                            message=f"Column '{column}' contains non-parsable periods: {sample_values}",
                            column=column,
                            issue_count=int(parsed.isna().sum()),
                            sample_values=tuple(str(value) for value in sample_values),
                        )
                    )

        if rule.numeric:
            numeric_series = pd.to_numeric(series, errors="coerce")
            invalid_numeric = frame.loc[series.notna() & numeric_series.isna(), column]
            if not invalid_numeric.empty:
                sample_values = invalid_numeric.astype(str).head(5).tolist()
                issues.append(
                    ValidationIssue(
                        dataset=schema.name,
                        rule="invalid_numeric_value",
                        message=f"Column '{column}' contains non-numeric values: {sample_values}",
                        column=column,
                        issue_count=int(len(invalid_numeric)),
                        sample_values=tuple(str(value) for value in sample_values),
                    )
                )
                continue

            if rule.min_value is not None:
                below_min = numeric_series.dropna().loc[numeric_series.dropna() < rule.min_value]
                if not below_min.empty:
                    sample_values = below_min.head(5).tolist()
                    issues.append(
                        ValidationIssue(
                            dataset=schema.name,
                            rule="numeric_range_low",
                            message=(
                                f"Column '{column}' contains values below {rule.min_value}: "
                                f"{sample_values}"
                            ),
                            column=column,
                            issue_count=int(len(below_min)),
                            sample_values=tuple(str(value) for value in sample_values),
                        )
                    )

            if rule.max_value is not None:
                above_max = numeric_series.dropna().loc[numeric_series.dropna() > rule.max_value]
                if not above_max.empty:
                    sample_values = above_max.head(5).tolist()
                    issues.append(
                        ValidationIssue(
                            dataset=schema.name,
                            rule="numeric_range_high",
                            message=(
                                f"Column '{column}' contains values above {rule.max_value}: "
                                f"{sample_values}"
                            ),
                            column=column,
                            issue_count=int(len(above_max)),
                            sample_values=tuple(str(value) for value in sample_values),
                        )
                    )

    if period_columns:
        period_column = period_columns[0]
        text_values = frame[period_column].dropna().astype(str)
        if not text_values.empty and text_values.str.match(_PERIOD_PATTERN).all():
            parsed_periods = pd.PeriodIndex(text_values, freq="M")
            group_columns = [column for column in schema.key_columns if column != period_column and column in columns]
            if group_columns:
                grouped = frame.groupby(group_columns, dropna=False, sort=True)
            else:
                grouped = [((), frame)]

            missing_examples: list[str] = []
            missing_total = 0
            for group_key, group_frame in grouped:
                group_text = group_frame[period_column].dropna().astype(str)
                if group_text.empty or not group_text.str.match(_PERIOD_PATTERN).all():
                    continue
                group_periods = pd.PeriodIndex(group_text, freq="M")
                expected_periods = pd.period_range(group_periods.min(), group_periods.max(), freq="M")
                missing_periods = expected_periods.difference(group_periods.unique())
                if len(missing_periods) == 0:
                    continue
                missing_total += int(len(missing_periods))
                example_label = (
                    f"{_format_group_key(group_columns, group_key)} missing {', '.join(str(period) for period in missing_periods[:3])}"
                )
                missing_examples.append(example_label)

            if missing_total > 0:
                issues.append(
                    ValidationIssue(
                        dataset=schema.name,
                        rule="missing_period_sequence",
                        message="Missing monthly periods detected within the observed sequence: " + "; ".join(missing_examples[:5]),
                        column=period_column,
                        issue_count=missing_total,
                        sample_values=tuple(missing_examples[:5]),
                    )
                )

    return issues


def validate_dataframe(frame: pd.DataFrame, schema: DatasetSchema) -> pd.DataFrame:
    """Validate a DataFrame against a canonical monthly dataset schema."""

    issues = collect_validation_issues(frame, schema)
    if issues:
        raise DatasetValidationError(schema.name, issues)

    return frame.copy()
