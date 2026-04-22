"""Canonical annual input contracts and loaders for the advanced appendix."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yaml

from .excel_loader import WorkbookData, load_workbook_data
from .simulation import SimulationConfig
from .valuation_model import ScenarioParameters


@dataclass(frozen=True)
class AppendixInputBundle:
    """Validated appendix inputs independent from the report layer."""

    annual_inputs: pd.DataFrame
    parameter_table: pd.DataFrame
    scenario_registry: list[dict]
    benchmark_metrics: pd.DataFrame | None
    params: ScenarioParameters
    simulation_config: SimulationConfig
    input_mode: str
    benchmark_mode: str
    input_source_label: str
    benchmark_source_label: str
    project_currency: str
    legacy_workbook_data: WorkbookData | None = None


ANNUAL_APPENDIX_INPUT_REQUIRED_COLUMNS = (
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
)

APPENDIX_PARAMETER_REQUIRED_COLUMNS = (
    "parameter_name",
    "value",
    "unit",
    "parameter_group",
    "used_by",
    "source_type",
    "source_reference",
    "note",
)

APPENDIX_SCENARIO_REQUIRED_COLUMNS = (
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
)

APPENDIX_BENCHMARK_REQUIRED_COLUMNS = (
    "metric",
    "value",
    "unit",
    "currency",
    "valuation_basis",
    "timing_basis",
    "benchmark_source",
    "note",
)

APPENDIX_PARAMETER_REQUIRED_NAMES = (
    "payable_rate",
    "tc_rc_usd_per_lb",
    "mine_cost_usd_per_tonne",
    "plant_cost_usd_per_tonne",
    "g_and_a_cost_usd_per_tonne",
    "income_tax_rate",
    "royalty_rate",
    "special_levy_rate",
    "wacc",
    "working_capital_ratio",
    "uplift_pct",
    "logistic_midpoint",
    "logistic_steepness",
    "initial_capex_year0_usd",
    "iterations",
    "random_seed",
    "var_alpha",
    "sigma_price_returns",
    "grade_cv",
    "recovery_cv",
    "price_path_autocorrelation",
)

APPENDIX_BENCHMARK_REQUIRED_METRICS = (
    "incremental_npv",
    "incremental_irr",
    "expected_npv",
    "var_5pct",
    "cvar_5pct",
)


def _load_yaml(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Required appendix input file not found: {path}")
    return pd.read_csv(path)


def _parameter_value(parameter_table: pd.DataFrame, parameter_name: str) -> float:
    return float(parameter_table.loc[parameter_table["parameter_name"] == parameter_name, "value"].iloc[0])


def _validate_required_columns(frame: pd.DataFrame, required_columns: tuple[str, ...], dataset_name: str) -> None:
    missing = [column for column in required_columns if column not in frame.columns]
    if missing:
        raise ValueError(f"Dataset '{dataset_name}' is missing required columns: {missing}")


def validate_annual_appendix_inputs(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate the canonical annual appendix driver table."""

    _validate_required_columns(frame, ANNUAL_APPENDIX_INPUT_REQUIRED_COLUMNS, "annual_appendix_inputs")
    validated = frame.copy()
    if validated["year"].duplicated().any():
        raise ValueError("annual_appendix_inputs contains duplicate project years.")
    years = validated["year"].astype(int).tolist()
    expected_years = list(range(1, len(years) + 1))
    if years != expected_years:
        raise ValueError(f"annual_appendix_inputs years must be consecutive starting at 1. Found {years}.")
    if (validated["copper_price_usd_per_lb"] <= 0).any():
        raise ValueError("annual_appendix_inputs contains non-positive copper prices.")
    if (validated["base_processed_tonnes"] <= 0).any():
        raise ValueError("annual_appendix_inputs contains non-positive processed tonnes.")
    if (~validated["base_head_grade"].between(0.0, 1.0)).any():
        raise ValueError("annual_appendix_inputs head grade must stay within [0, 1].")
    if (~validated["base_recovery"].between(0.0, 1.0)).any():
        raise ValueError("annual_appendix_inputs recovery must stay within [0, 1].")
    for column in (
        "base_unit_cost_usd_per_tonne",
        "expansion_unit_cost_usd_per_tonne",
        "initial_capex_usd",
        "sustaining_capex_usd",
    ):
        if (validated[column] < 0).any():
            raise ValueError(f"annual_appendix_inputs column '{column}' must be non-negative.")
    return validated.sort_values("year").reset_index(drop=True)


def validate_appendix_parameter_table(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate the scalar parameter contract for the appendix."""

    _validate_required_columns(frame, APPENDIX_PARAMETER_REQUIRED_COLUMNS, "appendix_parameters")
    validated = frame.copy()
    if validated["parameter_name"].duplicated().any():
        duplicates = validated.loc[validated["parameter_name"].duplicated(), "parameter_name"].tolist()
        raise ValueError(f"appendix_parameters contains duplicate parameter_name values: {duplicates}")
    missing = [name for name in APPENDIX_PARAMETER_REQUIRED_NAMES if name not in set(validated["parameter_name"])]
    if missing:
        raise ValueError(f"appendix_parameters is missing required parameters: {missing}")

    bounded_parameters = {
        "payable_rate": (0.0, 1.0),
        "income_tax_rate": (0.0, 1.0),
        "royalty_rate": (0.0, 1.0),
        "special_levy_rate": (0.0, 1.0),
        "wacc": (0.0, 1.0),
        "working_capital_ratio": (0.0, 1.0),
        "var_alpha": (0.0, 1.0),
        "price_path_autocorrelation": (0.0, 0.95),
    }
    for parameter_name, (lower, upper) in bounded_parameters.items():
        value = _parameter_value(validated, parameter_name)
        if not lower <= value <= upper:
            raise ValueError(f"appendix parameter '{parameter_name}' must stay in [{lower}, {upper}]. Found {value}.")

    for parameter_name in (
        "tc_rc_usd_per_lb",
        "mine_cost_usd_per_tonne",
        "plant_cost_usd_per_tonne",
        "g_and_a_cost_usd_per_tonne",
        "initial_capex_year0_usd",
        "iterations",
        "sigma_price_returns",
        "grade_cv",
        "recovery_cv",
    ):
        if _parameter_value(validated, parameter_name) < 0:
            raise ValueError(f"appendix parameter '{parameter_name}' must be non-negative.")
    return validated.reset_index(drop=True)


def validate_appendix_scenarios(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate the deterministic scenario registry used by the appendix."""

    _validate_required_columns(frame, APPENDIX_SCENARIO_REQUIRED_COLUMNS, "appendix_scenarios")
    validated = frame.copy()
    if validated["scenario_id"].duplicated().any():
        raise ValueError("appendix_scenarios contains duplicate scenario_id values.")
    for column in (
        "price_factor",
        "grade_factor",
        "recovery_factor",
        "throughput_factor",
        "opex_factor",
        "capex_factor",
    ):
        if (validated[column] <= 0).any():
            raise ValueError(f"appendix_scenarios column '{column}' must stay positive.")
    return validated.reset_index(drop=True)


def validate_appendix_benchmark_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate the benchmark reference table used by appendix comparisons."""

    _validate_required_columns(frame, APPENDIX_BENCHMARK_REQUIRED_COLUMNS, "appendix_benchmark_metrics")
    validated = frame.copy()
    if validated["metric"].duplicated().any():
        raise ValueError("appendix_benchmark_metrics contains duplicate metric values.")
    missing = [metric for metric in APPENDIX_BENCHMARK_REQUIRED_METRICS if metric not in set(validated["metric"])]
    if missing:
        raise ValueError(f"appendix_benchmark_metrics is missing required benchmark metrics: {missing}")
    return validated.reset_index(drop=True)


def build_annual_appendix_dataset_catalog() -> pd.DataFrame:
    """Return dataset-level documentation for the canonical annual appendix layer."""

    return pd.DataFrame(
        [
            {
                "dataset_name": "annual_appendix_inputs",
                "source_file": "annual_appendix_inputs.csv",
                "grain": "One row per project year.",
                "purpose": "Canonical annual operating and capex inputs used by valuation, scenario, and simulation logic.",
                "primary_use": "Default appendix driver table.",
                "limitation_note": "Planning-style annual inputs, not a mine-plan or corporate-finance system.",
            },
            {
                "dataset_name": "appendix_parameters",
                "source_file": "appendix_parameters.csv",
                "grain": "One row per scalar parameter.",
                "purpose": "Canonical scalar parameter table for commercial, fiscal-proxy, ramp, and simulation settings.",
                "primary_use": "Default appendix parameter contract.",
                "limitation_note": "Public-safe planning parameters remain simplified and explicit.",
            },
            {
                "dataset_name": "appendix_scenarios",
                "source_file": "appendix_scenarios.csv",
                "grain": "One row per deterministic scenario.",
                "purpose": "Scenario registry for the appendix page.",
                "primary_use": "Deterministic scenario comparison.",
                "limitation_note": "Scenario shocks are illustrative planning cases, not asset-grade committees or budgets.",
            },
            {
                "dataset_name": "appendix_benchmark_metrics",
                "source_file": "appendix_benchmark_metrics.csv",
                "grain": "One row per benchmark metric.",
                "purpose": "Canonical benchmark reference table used for transparency outputs.",
                "primary_use": "Benchmark comparison without direct workbook dependency.",
                "limitation_note": "The current canonical benchmark table remains legacy-derived reference content.",
            },
        ]
    )


def build_annual_appendix_field_catalog() -> pd.DataFrame:
    """Return field-level metadata for the canonical annual appendix layer."""

    rows = [
        ("annual_appendix_inputs", "year", "Project year starting at 1.", "year", True),
        ("annual_appendix_inputs", "calendar_year", "Calendar year label for reporting.", "year", True),
        ("annual_appendix_inputs", "copper_price_usd_per_lb", "Base copper price deck.", "USD/lb", True),
        ("annual_appendix_inputs", "base_processed_tonnes", "Base processed tonnes before expansion uplift.", "tonnes", True),
        ("annual_appendix_inputs", "base_head_grade", "Base head grade in decimal form.", "grade_decimal", True),
        ("annual_appendix_inputs", "base_recovery", "Base recovery in decimal form.", "recovery_decimal", True),
        ("annual_appendix_inputs", "base_unit_cost_usd_per_tonne", "Base-operation unit cost.", "USD/t", True),
        ("annual_appendix_inputs", "expansion_unit_cost_usd_per_tonne", "Expanded-operation unit cost.", "USD/t", True),
        ("annual_appendix_inputs", "initial_capex_usd", "Initial capex allocated to the project year.", "USD", True),
        ("annual_appendix_inputs", "sustaining_capex_usd", "Sustaining capex allocated to the project year.", "USD", True),
        ("appendix_parameters", "parameter_name", "Scalar parameter identifier.", None, True),
        ("appendix_parameters", "value", "Scalar parameter numeric value.", None, True),
        ("appendix_parameters", "unit", "Parameter unit or semantic type.", None, True),
        ("appendix_parameters", "parameter_group", "Business-readable grouping for the parameter.", None, True),
        ("appendix_parameters", "used_by", "Appendix module family that consumes the parameter.", None, True),
        ("appendix_parameters", "source_type", "Whether the parameter came from canonical tables or the legacy adapter.", None, True),
        ("appendix_parameters", "source_reference", "Public-safe source reference.", None, True),
        ("appendix_parameters", "note", "Limitation or interpretation note.", None, True),
        ("appendix_scenarios", "scenario_id", "Stable scenario identifier.", None, True),
        ("appendix_scenarios", "scenario_name", "Human-readable scenario name.", None, True),
        ("appendix_scenarios", "category", "Scenario grouping for review.", None, True),
        ("appendix_scenarios", "description", "Plain-language scenario description.", None, True),
        ("appendix_scenarios", "price_factor", "Scenario price multiplier.", "ratio", True),
        ("appendix_scenarios", "grade_factor", "Scenario grade multiplier.", "ratio", True),
        ("appendix_scenarios", "recovery_factor", "Scenario recovery multiplier.", "ratio", True),
        ("appendix_scenarios", "throughput_factor", "Scenario throughput multiplier.", "ratio", True),
        ("appendix_scenarios", "opex_factor", "Scenario unit-opex multiplier.", "ratio", True),
        ("appendix_scenarios", "capex_factor", "Scenario capex multiplier.", "ratio", True),
        ("appendix_scenarios", "wacc_shift_bps", "Discount-rate shift in basis points.", "bps", True),
        ("appendix_benchmark_metrics", "metric", "Benchmarked output name.", None, True),
        ("appendix_benchmark_metrics", "value", "Benchmark value.", None, True),
        ("appendix_benchmark_metrics", "unit", "Benchmark unit.", None, True),
        ("appendix_benchmark_metrics", "currency", "Benchmark currency where relevant.", None, True),
        ("appendix_benchmark_metrics", "valuation_basis", "Valuation basis used by the benchmark.", None, True),
        ("appendix_benchmark_metrics", "timing_basis", "Timing basis used by the benchmark.", None, True),
        ("appendix_benchmark_metrics", "benchmark_source", "Source label for benchmark traceability.", None, True),
        ("appendix_benchmark_metrics", "note", "Benchmark interpretation note.", None, True),
    ]
    return pd.DataFrame(
        rows,
        columns=["dataset_name", "column_name", "description", "unit", "required_flag"],
    )


def _annual_inputs_from_workbook(workbook_data: WorkbookData, config: dict) -> pd.DataFrame:
    assumptions = workbook_data.assumptions.set_index("parameter")["value"]
    annual_inputs = workbook_data.annual_inputs.copy()
    annual_inputs["calendar_year"] = annual_inputs["year"].astype(int) + int(config["project"]["project_start_calendar_year"]) - 1
    annual_inputs["base_unit_cost_usd_per_tonne"] = float(assumptions["base_unit_cost_usd_per_tonne"])
    annual_inputs["expansion_unit_cost_usd_per_tonne"] = float(assumptions["expansion_unit_cost_usd_per_tonne"])
    annual_inputs["initial_capex_usd"] = 0.0
    annual_inputs.loc[annual_inputs["year"] == 1, "initial_capex_usd"] = float(assumptions["initial_capex_year1_usd"])
    annual_inputs["sustaining_capex_usd"] = 0.0
    annual_inputs.loc[annual_inputs["year"] >= 2, "sustaining_capex_usd"] = float(assumptions["sustaining_capex_usd"])
    return annual_inputs.loc[:, ANNUAL_APPENDIX_INPUT_REQUIRED_COLUMNS]


def _parameter_table_from_workbook(workbook_data: WorkbookData, config: dict) -> pd.DataFrame:
    assumptions = workbook_data.assumptions.set_index("parameter")
    grade_cv = float(workbook_data.operational_history["head_grade"].std(ddof=1) / workbook_data.operational_history["head_grade"].mean())
    recovery_cv = float(workbook_data.operational_history["recovery"].std(ddof=1) / workbook_data.operational_history["recovery"].mean())

    rows = [
        ("payable_rate", assumptions.loc["payable_rate", "value"], "decimal", "Commercial", "valuation_model", "legacy_workbook_adapter", f"{assumptions.loc['payable_rate', 'source_sheet']}!{assumptions.loc['payable_rate', 'source_cell']}", "Legacy workbook payable-rate assumption."),
        ("tc_rc_usd_per_lb", assumptions.loc["tc_rc_usd_per_lb", "value"], "USD/lb", "Commercial", "valuation_model", "legacy_workbook_adapter", f"{assumptions.loc['tc_rc_usd_per_lb', 'source_sheet']}!{assumptions.loc['tc_rc_usd_per_lb', 'source_cell']}", "Legacy workbook treatment and refining charge assumption."),
        ("mine_cost_usd_per_tonne", assumptions.loc["mine_cost_usd_per_tonne", "value"], "USD/t", "Cost", "valuation_model", "legacy_workbook_adapter", f"{assumptions.loc['mine_cost_usd_per_tonne', 'source_sheet']}!{assumptions.loc['mine_cost_usd_per_tonne', 'source_cell']}", "Legacy workbook mine-cost input."),
        ("plant_cost_usd_per_tonne", assumptions.loc["plant_cost_usd_per_tonne", "value"], "USD/t", "Cost", "valuation_model", "legacy_workbook_adapter", f"{assumptions.loc['plant_cost_usd_per_tonne', 'source_sheet']}!{assumptions.loc['plant_cost_usd_per_tonne', 'source_cell']}", "Legacy workbook plant-cost input."),
        ("g_and_a_cost_usd_per_tonne", assumptions.loc["g_and_a_cost_usd_per_tonne", "value"], "USD/t", "Cost", "valuation_model", "legacy_workbook_adapter", f"{assumptions.loc['g_and_a_cost_usd_per_tonne', 'source_sheet']}!{assumptions.loc['g_and_a_cost_usd_per_tonne', 'source_cell']}", "Legacy workbook G&A cost input."),
        ("income_tax_rate", assumptions.loc["income_tax_rate", "value"], "decimal", "Fiscal Proxy", "valuation_model", "legacy_workbook_adapter", f"{assumptions.loc['income_tax_rate', 'source_sheet']}!{assumptions.loc['income_tax_rate', 'source_cell']}", "Legacy workbook cash-tax proxy input."),
        ("royalty_rate", assumptions.loc["royalty_rate", "value"], "decimal", "Fiscal Proxy", "valuation_model", "legacy_workbook_adapter", f"{assumptions.loc['royalty_rate', 'source_sheet']}!{assumptions.loc['royalty_rate', 'source_cell']}", "Tracked for transparency but not applied in the public cash-flow chain."),
        ("special_levy_rate", assumptions.loc["special_levy_rate", "value"], "decimal", "Fiscal Proxy", "valuation_model", "legacy_workbook_adapter", f"{assumptions.loc['special_levy_rate', 'source_sheet']}!{assumptions.loc['special_levy_rate', 'source_cell']}", "Tracked for transparency but not applied in the public cash-flow chain."),
        ("wacc", assumptions.loc["wacc", "value"], "decimal", "Finance", "valuation_model", "legacy_workbook_adapter", f"{assumptions.loc['wacc', 'source_sheet']}!{assumptions.loc['wacc', 'source_cell']}", "Legacy workbook discount-rate assumption."),
        ("working_capital_ratio", float(config["scenario"]["finance"]["working_capital_ratio"]), "decimal", "Finance", "valuation_model", "project_config", "config/project.yaml:scenario.finance.working_capital_ratio", "Repo-governed working-capital proxy."),
        ("uplift_pct", float(config["scenario"]["expansion"]["uplift_pct"]), "decimal", "Ramp", "valuation_model", "project_config", "config/project.yaml:scenario.expansion.uplift_pct", "Repo-governed throughput uplift for the public appendix."),
        ("logistic_midpoint", float(config["scenario"]["expansion"]["logistic_midpoint"]), "project_year", "Ramp", "valuation_model", "project_config", "config/project.yaml:scenario.expansion.logistic_midpoint", "Repo-governed ramp midpoint."),
        ("logistic_steepness", float(config["scenario"]["expansion"]["logistic_steepness"]), "decimal", "Ramp", "valuation_model", "project_config", "config/project.yaml:scenario.expansion.logistic_steepness", "Repo-governed ramp steepness."),
        ("initial_capex_year0_usd", assumptions.loc["initial_capex_year0_usd", "value"], "USD", "Capex", "valuation_model", "legacy_workbook_adapter", f"{assumptions.loc['initial_capex_year0_usd', 'source_sheet']}!{assumptions.loc['initial_capex_year0_usd', 'source_cell']}", "Legacy workbook year-0 capex reference."),
        ("iterations", float(config["simulation"]["iterations"]), "count", "Simulation", "simulation", "project_config", "config/project.yaml:simulation.iterations", "Repo-governed Monte Carlo iteration count."),
        ("random_seed", float(config["simulation"]["random_seed"]), "seed", "Simulation", "simulation", "project_config", "config/project.yaml:simulation.random_seed", "Repo-governed seed for reproducibility."),
        ("var_alpha", float(config["simulation"]["var_alpha"]), "decimal", "Simulation", "simulation", "project_config", "config/project.yaml:simulation.var_alpha", "Repo-governed downside percentile."),
        ("sigma_price_returns", assumptions.loc["sigma_price_returns", "value"], "decimal", "Simulation", "simulation", "legacy_workbook_adapter", f"{assumptions.loc['sigma_price_returns', 'source_sheet']}!{assumptions.loc['sigma_price_returns', 'source_cell']}", "Legacy workbook volatility input."),
        ("grade_cv", grade_cv, "ratio", "Simulation", "simulation", "legacy_workbook_adapter", "Workbook operational history: head_grade", "Derived from workbook operational history."),
        ("recovery_cv", recovery_cv, "ratio", "Simulation", "simulation", "legacy_workbook_adapter", "Workbook operational history: recovery", "Derived from workbook operational history."),
        ("price_path_autocorrelation", float(config["simulation"]["price_path_autocorrelation"]), "decimal", "Simulation", "simulation", "project_config", "config/project.yaml:simulation.price_path_autocorrelation", "Repo-governed price-path persistence."),
    ]
    return pd.DataFrame(
        rows,
        columns=APPENDIX_PARAMETER_REQUIRED_COLUMNS,
    )


def _benchmark_metrics_from_workbook(workbook_data: WorkbookData) -> pd.DataFrame:
    assumptions = workbook_data.assumptions.set_index("parameter")["value"]
    benchmark_metrics = workbook_data.benchmark_metrics.copy()
    rows = [
        {
            "metric": "incremental_npv",
            "value": float(assumptions["benchmark_npv_excel"]),
            "unit": "USD",
            "currency": "USD",
            "valuation_basis": "incremental_expansion",
            "timing_basis": "year0_initial_outlay_plus_discounted_year1_to_year15",
            "benchmark_source": "Legacy workbook reference",
            "note": "Legacy workbook deterministic NPV for the incremental expansion flow.",
        },
        {
            "metric": "incremental_irr",
            "value": float(assumptions["benchmark_irr_excel"]),
            "unit": "decimal",
            "currency": None,
            "valuation_basis": "incremental_expansion",
            "timing_basis": "year0_initial_outlay_plus_discounted_year1_to_year15",
            "benchmark_source": "Legacy workbook reference",
            "note": "Legacy workbook deterministic IRR for the incremental expansion flow.",
        },
    ]
    for metric in ("expected_npv", "var_5pct", "cvar_5pct"):
        benchmark_row = benchmark_metrics.loc[benchmark_metrics["metric"] == metric].iloc[0]
        rows.append(
            {
                "metric": metric,
                "value": float(benchmark_row["value"]),
                "unit": benchmark_row["unit"],
                "currency": benchmark_row["currency"],
                "valuation_basis": benchmark_row["valuation_basis"],
                "timing_basis": benchmark_row["timing_basis"],
                "benchmark_source": "Legacy workbook reference",
                "note": benchmark_row["note"],
            }
        )
    return pd.DataFrame(rows, columns=APPENDIX_BENCHMARK_REQUIRED_COLUMNS)


def _build_params_from_tables(annual_inputs: pd.DataFrame, parameter_table: pd.DataFrame) -> ScenarioParameters:
    sustaining_candidates = annual_inputs.loc[annual_inputs["sustaining_capex_usd"] > 0, "sustaining_capex_usd"]
    annual_sustaining_capex_usd = float(sustaining_candidates.iloc[0]) if not sustaining_candidates.empty else 0.0
    year1_capex = float(annual_inputs.loc[annual_inputs["year"] == 1, "initial_capex_usd"].iloc[0])
    return ScenarioParameters(
        payable_rate=_parameter_value(parameter_table, "payable_rate"),
        tc_rc_usd_per_lb=_parameter_value(parameter_table, "tc_rc_usd_per_lb"),
        mine_cost_usd_per_tonne=_parameter_value(parameter_table, "mine_cost_usd_per_tonne"),
        plant_cost_usd_per_tonne=_parameter_value(parameter_table, "plant_cost_usd_per_tonne"),
        g_and_a_cost_usd_per_tonne=_parameter_value(parameter_table, "g_and_a_cost_usd_per_tonne"),
        base_unit_cost_usd_per_tonne=float(annual_inputs["base_unit_cost_usd_per_tonne"].iloc[0]),
        expansion_unit_cost_usd_per_tonne=float(annual_inputs["expansion_unit_cost_usd_per_tonne"].iloc[0]),
        income_tax_rate=_parameter_value(parameter_table, "income_tax_rate"),
        royalty_rate=_parameter_value(parameter_table, "royalty_rate"),
        special_levy_rate=_parameter_value(parameter_table, "special_levy_rate"),
        wacc=_parameter_value(parameter_table, "wacc"),
        annual_sustaining_capex_usd=annual_sustaining_capex_usd,
        initial_capex_schedule_usd={
            0: _parameter_value(parameter_table, "initial_capex_year0_usd"),
            1: year1_capex,
        },
        working_capital_ratio=_parameter_value(parameter_table, "working_capital_ratio"),
        uplift_pct=_parameter_value(parameter_table, "uplift_pct"),
        logistic_midpoint=_parameter_value(parameter_table, "logistic_midpoint"),
        logistic_steepness=_parameter_value(parameter_table, "logistic_steepness"),
    )


def _build_simulation_config(parameter_table: pd.DataFrame) -> SimulationConfig:
    return SimulationConfig(
        iterations=int(_parameter_value(parameter_table, "iterations")),
        random_seed=int(_parameter_value(parameter_table, "random_seed")),
        var_alpha=_parameter_value(parameter_table, "var_alpha"),
        sigma_price_returns=_parameter_value(parameter_table, "sigma_price_returns"),
        grade_cv=_parameter_value(parameter_table, "grade_cv"),
        recovery_cv=_parameter_value(parameter_table, "recovery_cv"),
        price_path_autocorrelation=_parameter_value(parameter_table, "price_path_autocorrelation"),
    )


def load_appendix_input_bundle(
    config_path: str | Path = "config/project.yaml",
    input_mode: str | None = None,
    benchmark_mode: str | None = None,
    data_dir: str | Path | None = None,
) -> AppendixInputBundle:
    """Load appendix inputs from the canonical annual path or the legacy workbook adapter."""

    config = _load_yaml(config_path)
    appendix_config = config.get("appendix", {})
    resolved_input_mode = str(input_mode or appendix_config.get("default_input_mode", "canonical"))
    default_benchmark_mode = "canonical" if resolved_input_mode == "canonical" else "legacy_workbook"
    resolved_benchmark_mode = str(benchmark_mode or appendix_config.get("default_benchmark_mode", default_benchmark_mode))
    resolved_data_dir = Path(data_dir or appendix_config.get("data_dir", "data/sample_data/annual_appendix"))

    scenario_registry_frame = validate_appendix_scenarios(_load_csv(resolved_data_dir / "appendix_scenarios.csv"))
    scenario_registry = scenario_registry_frame.to_dict("records")

    legacy_workbook_data: WorkbookData | None = None
    if resolved_input_mode == "canonical":
        annual_inputs = validate_annual_appendix_inputs(_load_csv(resolved_data_dir / "annual_appendix_inputs.csv"))
        parameter_table = validate_appendix_parameter_table(_load_csv(resolved_data_dir / "appendix_parameters.csv"))
        input_source_label = "Canonical annual appendix tables"
    elif resolved_input_mode == "legacy_workbook":
        legacy_workbook_data = load_workbook_data(config["project"]["workbook_path"])
        annual_inputs = validate_annual_appendix_inputs(_annual_inputs_from_workbook(legacy_workbook_data, config))
        parameter_table = validate_appendix_parameter_table(_parameter_table_from_workbook(legacy_workbook_data, config))
        input_source_label = "Legacy workbook adapter"
    else:
        raise ValueError(f"Unsupported appendix input_mode '{resolved_input_mode}'.")

    if resolved_benchmark_mode == "canonical":
        benchmark_metrics = validate_appendix_benchmark_metrics(_load_csv(resolved_data_dir / "appendix_benchmark_metrics.csv"))
        benchmark_source_label = "Canonical appendix benchmark table"
    elif resolved_benchmark_mode == "legacy_workbook":
        if legacy_workbook_data is None:
            legacy_workbook_data = load_workbook_data(config["project"]["workbook_path"])
        benchmark_metrics = validate_appendix_benchmark_metrics(_benchmark_metrics_from_workbook(legacy_workbook_data))
        benchmark_source_label = "Legacy workbook reference"
    elif resolved_benchmark_mode == "none":
        benchmark_metrics = None
        benchmark_source_label = "No benchmark source"
    else:
        raise ValueError(f"Unsupported appendix benchmark_mode '{resolved_benchmark_mode}'.")

    params = _build_params_from_tables(annual_inputs, parameter_table)
    simulation_config = _build_simulation_config(parameter_table)
    return AppendixInputBundle(
        annual_inputs=annual_inputs,
        parameter_table=parameter_table,
        scenario_registry=scenario_registry,
        benchmark_metrics=benchmark_metrics,
        params=params,
        simulation_config=simulation_config,
        input_mode=resolved_input_mode,
        benchmark_mode=resolved_benchmark_mode,
        input_source_label=input_source_label,
        benchmark_source_label=benchmark_source_label,
        project_currency=str(config["project"]["currency"]),
        legacy_workbook_data=legacy_workbook_data,
    )
