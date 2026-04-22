"""Build a public-safe Power BI template scaffold from BI exports."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
import stat
import shutil
from pathlib import Path

import pandas as pd

from .bi_semantic import build_powerbi_table_catalog

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TEMPLATE_DIR = REPO_ROOT / "powerbi" / "template_scaffold"
BUILD_INVENTORY_FILENAME = ".scaffold_inventory.json"
PROJECT_ROOT_PARAMETER = "ProjectRoot"
PROJECT_ROOT_PLACEHOLDER = "REPLACE_WITH_ABSOLUTE_REPO_PATH"
STARTER_KIT_OUTPUT_PARAMETER = "StarterKitOutputRoot"
MONTHLY_OUTPUT_PARAMETER = "MonthlyOutputRoot"
ADVANCED_APPENDIX_OUTPUT_PARAMETER = "AdvancedAppendixOutputRoot"
DEFAULT_OUTPUT_RELATIVE_DIR = "outputs/bi"

REFERENCE_TABLES = {
    "dashboard_page_catalog",
    "powerbi_measure_catalog",
    "powerbi_relationship_catalog",
    "powerbi_sort_by_catalog",
    "powerbi_field_visibility_catalog",
    "powerbi_visual_binding_catalog",
    "powerbi_query_catalog",
    "powerbi_table_catalog",
    "monthly_kpi_dictionary",
}

QUERY_FOLDER_MAP = {
    "Core Monthly Story": "core_monthly_story",
    "Starter Kit Reference": "starter_kit_reference",
    "Advanced Appendix": "advanced_appendix",
}


@dataclass(frozen=True)
class PowerBIHandoffContext:
    """Default output-root settings for the Power BI continuation package."""

    artifact_strategy: str
    profile_name: str | None
    profile_path: str | None
    starter_kit_output_dir: Path
    monthly_output_dir: Path
    advanced_appendix_output_dir: Path
    appendix_enabled: bool


def _output_root_parameter_specs(handoff_context: PowerBIHandoffContext) -> list[dict[str, str | None]]:
    specs: list[dict[str, str | None]] = [
        {
            "parameter_name": STARTER_KIT_OUTPUT_PARAMETER,
            "purpose": "Folder containing public-safe starter catalogs such as page and measure references.",
            "default_output_dir": _display_repo_path(handoff_context.starter_kit_output_dir),
            "change_when": "Usually leave this on outputs/bi unless you intentionally relocate the public-safe starter assets.",
        },
        {
            "parameter_name": MONTHLY_OUTPUT_PARAMETER,
            "purpose": "Folder containing monthly monitoring marts and shared monthly dimensions.",
            "default_output_dir": _display_repo_path(handoff_context.monthly_output_dir),
            "change_when": "Change this after running a unified local profile if monthly outputs land outside outputs/bi.",
        },
    ]
    if handoff_context.appendix_enabled:
        specs.append(
            {
                "parameter_name": ADVANCED_APPENDIX_OUTPUT_PARAMETER,
                "purpose": "Folder containing secondary appendix tables for scenario, benchmark, and risk visuals.",
                "default_output_dir": _display_repo_path(handoff_context.advanced_appendix_output_dir),
                "change_when": "Change this only if you want the secondary appendix page to point to local runner outputs.",
            }
        )
    return specs


def _parameter_query_names(handoff_context: PowerBIHandoffContext) -> list[str]:
    return [PROJECT_ROOT_PARAMETER, *[str(spec["parameter_name"]) for spec in _output_root_parameter_specs(handoff_context)]]


def _parameter_query_markdown(handoff_context: PowerBIHandoffContext) -> str:
    return "\n".join(f"   - `{parameter_name}.pq`" for parameter_name in _parameter_query_names(handoff_context))


def _profile_defaults_markdown(handoff_context: PowerBIHandoffContext) -> str:
    lines = [
        f"- starter-kit references default to `{_display_repo_path(handoff_context.starter_kit_output_dir)}`",
        f"- monthly queries default to `{_display_repo_path(handoff_context.monthly_output_dir)}`",
    ]
    if handoff_context.appendix_enabled:
        lines.append(f"- appendix queries default to `{_display_repo_path(handoff_context.advanced_appendix_output_dir)}`")
    else:
        lines.append("- appendix queries and page shells are omitted because this profile disables the advanced appendix path.")
    return "\n".join(lines)


def _page_sequence(page_catalog: pd.DataFrame) -> list[str]:
    return page_catalog.sort_values("page_order")["page_name"].astype(str).tolist()


def _page_order_markdown(page_catalog: pd.DataFrame) -> str:
    return "\n".join(f"{index}. {page_name}" for index, page_name in enumerate(_page_sequence(page_catalog), start=1))


def _filter_appendix_scope(
    catalog: pd.DataFrame,
    *,
    handoff_context: PowerBIHandoffContext,
    column_name: str,
    appendix_value: str = "Advanced Appendix",
) -> pd.DataFrame:
    if handoff_context.appendix_enabled:
        return catalog.copy()
    return catalog.loc[catalog[column_name].astype(str) != appendix_value].reset_index(drop=True).copy()


def _filter_table_named_catalog(
    catalog: pd.DataFrame,
    *,
    table_catalog: pd.DataFrame,
    table_column: str = "table_name",
) -> pd.DataFrame:
    allowed_tables = set(table_catalog["table_name"].astype(str))
    return catalog.loc[catalog[table_column].astype(str).isin(allowed_tables)].reset_index(drop=True).copy()


def _filter_powerbi_table_catalog(
    table_catalog: pd.DataFrame,
    handoff_context: PowerBIHandoffContext,
) -> pd.DataFrame:
    return _filter_appendix_scope(table_catalog, handoff_context=handoff_context, column_name="subject_area")


def _filter_powerbi_page_catalog(
    page_catalog: pd.DataFrame,
    handoff_context: PowerBIHandoffContext,
) -> pd.DataFrame:
    return _filter_appendix_scope(page_catalog, handoff_context=handoff_context, column_name="page_group")


def _filter_powerbi_measure_catalog(
    measure_catalog: pd.DataFrame,
    handoff_context: PowerBIHandoffContext,
) -> pd.DataFrame:
    return _filter_appendix_scope(measure_catalog, handoff_context=handoff_context, column_name="starter_kit_scope")


def _filter_powerbi_relationship_catalog(
    relationship_catalog: pd.DataFrame,
    handoff_context: PowerBIHandoffContext,
) -> pd.DataFrame:
    return _filter_appendix_scope(
        relationship_catalog,
        handoff_context=handoff_context,
        column_name="relationship_scope",
    )


def _filter_powerbi_visual_catalog(
    visual_catalog: pd.DataFrame,
    page_catalog: pd.DataFrame,
) -> pd.DataFrame:
    allowed_pages = set(page_catalog["page_name"].astype(str))
    return visual_catalog.loc[visual_catalog["page_name"].astype(str).isin(allowed_pages)].reset_index(drop=True).copy()


def _build_inventory_path(root_dir: Path) -> Path:
    return root_dir / BUILD_INVENTORY_FILENAME


def _inventory_entry(root_dir: Path, path: Path) -> str:
    return path.relative_to(root_dir).as_posix()


def _load_existing_inventory(root_dir: Path) -> set[str]:
    inventory_path = _build_inventory_path(root_dir)
    if not inventory_path.exists():
        return set()
    try:
        payload = json.loads(inventory_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return set()
    generated_files = payload.get("generated_files", [])
    return {str(item) for item in generated_files if isinstance(item, str)}


def _scan_existing_files(root_dir: Path) -> set[str]:
    if not root_dir.exists():
        return set()
    return {
        _inventory_entry(root_dir, path)
        for path in root_dir.rglob("*")
        if path.is_file()
    }


def _obsolete_placeholder_contents(path: Path) -> str:
    detail = "This file was generated by a previous scaffold build and is not part of the current profile-driven package. Use the current manifests instead."
    suffix = path.suffix.lower()
    if suffix == ".json":
        return json.dumps({"status": "obsolete", "detail": detail}, indent=2)
    if suffix == ".csv":
        return f"status,detail\nobsolete,\"{detail}\"\n"
    if suffix in {".pq", ".dax", ".tmdl"}:
        return f"// Obsolete scaffold file.\n// {detail}\n"
    if suffix == ".md":
        return f"# Obsolete Scaffold File\n\n{detail}\n"
    return f"Obsolete scaffold file.\n{detail}\n"


def _neutralize_obsolete_files(root_dir: Path, current_inventory: set[str]) -> list[str]:
    obsolete_files = sorted((_load_existing_inventory(root_dir) | _scan_existing_files(root_dir)) - current_inventory)
    for relative_path in obsolete_files:
        candidate = root_dir / relative_path
        if candidate.exists() and candidate.is_file():
            candidate.write_text(_obsolete_placeholder_contents(candidate), encoding="utf-8")
    return obsolete_files


def _write_build_inventory(root_dir: Path, current_inventory: set[str], obsolete_files: list[str]) -> Path:
    inventory_path = _build_inventory_path(root_dir)
    payload = {
        "generated_files": sorted(current_inventory),
        "obsolete_files": obsolete_files,
    }
    inventory_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return inventory_path


def _display_repo_path(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _windows_path(path: str) -> str:
    return path.replace("/", "\\")


def resolve_powerbi_handoff_context(
    profile_path: str | Path | None = None,
    *,
    bi_output_dir: str | Path = REPO_ROOT / DEFAULT_OUTPUT_RELATIVE_DIR,
) -> PowerBIHandoffContext:
    """Resolve output-root defaults for the Power BI handoff package."""

    default_output_dir = Path(bi_output_dir)
    if not default_output_dir.is_absolute():
        default_output_dir = REPO_ROOT / default_output_dir

    profile_name: str | None = None
    profile_path_text: str | None = None
    monthly_output_dir = default_output_dir
    advanced_appendix_output_dir = default_output_dir
    appendix_enabled = True

    if profile_path is not None:
        from .local_profile_runner import load_local_source_profile

        profile = load_local_source_profile(profile_path)
        profile_name = profile.profile_name
        profile_path_text = _display_repo_path(profile.path)

        if profile.monthly_monitoring is not None and profile.monthly_monitoring.enabled:
            monthly_output_dir = profile.monthly_monitoring.output_dir

        if (
            profile.annual_appendix is not None
            and profile.annual_appendix.enabled
            and profile.annual_appendix.advanced_appendix is not None
            and profile.annual_appendix.advanced_appendix.enabled
        ):
            advanced_appendix_output_dir = profile.annual_appendix.advanced_appendix.output_dir
        else:
            appendix_enabled = False

    return PowerBIHandoffContext(
        artifact_strategy="PBIP finalization package",
        profile_name=profile_name,
        profile_path=profile_path_text,
        starter_kit_output_dir=default_output_dir,
        monthly_output_dir=monthly_output_dir,
        advanced_appendix_output_dir=advanced_appendix_output_dir,
        appendix_enabled=appendix_enabled,
    )


def _query_source_settings(
    row: pd.Series,
    handoff_context: PowerBIHandoffContext,
) -> tuple[str, str, str]:
    table_name = str(row["table_name"])
    subject_area = str(row["subject_area"])
    if table_name in REFERENCE_TABLES:
        return (
            STARTER_KIT_OUTPUT_PARAMETER,
            _display_repo_path(handoff_context.starter_kit_output_dir) or DEFAULT_OUTPUT_RELATIVE_DIR,
            "Starter Kit Reference",
        )
    if subject_area == "Advanced Appendix":
        return (
            ADVANCED_APPENDIX_OUTPUT_PARAMETER,
            _display_repo_path(handoff_context.advanced_appendix_output_dir) or DEFAULT_OUTPUT_RELATIVE_DIR,
            "Advanced Appendix",
        )
    return (
        MONTHLY_OUTPUT_PARAMETER,
        _display_repo_path(handoff_context.monthly_output_dir) or DEFAULT_OUTPUT_RELATIVE_DIR,
        "Core Monthly Story",
    )


def build_powerbi_query_catalog(
    table_catalog: pd.DataFrame | None = None,
    handoff_context: PowerBIHandoffContext | None = None,
) -> pd.DataFrame:
    """Build a query catalog for the public-safe Power BI scaffold."""
    if table_catalog is None:
        table_catalog = build_powerbi_table_catalog()
    if handoff_context is None:
        handoff_context = resolve_powerbi_handoff_context()

    query_catalog = _filter_powerbi_table_catalog(table_catalog, handoff_context)
    query_catalog["query_order"] = query_catalog["import_order"]
    query_catalog["query_name"] = query_catalog["table_name"]
    query_catalog[["parameter_name", "default_output_dir", "query_group"]] = query_catalog.apply(
        lambda row: pd.Series(_query_source_settings(row, handoff_context)),
        axis=1,
    )
    query_catalog["relative_source_path"] = query_catalog.apply(
        lambda row: f"{row['default_output_dir']}/{row['source_file']}",
        axis=1,
    )
    query_catalog["query_folder"] = query_catalog["query_group"].map(QUERY_FOLDER_MAP)
    query_catalog["power_query_file"] = query_catalog.apply(
        lambda row: f"{int(row['query_order']):02d}_{row['query_name']}.pq",
        axis=1,
    )
    query_catalog["power_query_relative_file"] = query_catalog.apply(
        lambda row: f"{row['query_folder']}/{row['power_query_file']}",
        axis=1,
    )
    query_catalog["load_recommendation"] = query_catalog["table_name"].map(
        lambda table: "disable_load_after_import" if table in REFERENCE_TABLES else "enable_load"
    )
    query_catalog["query_purpose"] = query_catalog["modeling_note"]
    query_catalog["project_root_parameter_name"] = PROJECT_ROOT_PARAMETER
    query_catalog["desktop_finalize_note"] = query_catalog["query_group"].map(
        {
            "Core Monthly Story": "Point this query group to the monthly output folder produced by the public demo build or the unified local runner.",
            "Advanced Appendix": "Point this query group to the advanced appendix output folder only if you want the secondary appendix page active.",
            "Starter Kit Reference": "Keep these reference queries optional and disable load after import if you bring them into Desktop.",
        }
    )

    ordered_columns = [
        "query_order",
        "query_name",
        "source_file",
        "relative_source_path",
        "default_output_dir",
        "query_folder",
        "power_query_file",
        "power_query_relative_file",
        "parameter_name",
        "project_root_parameter_name",
        "query_group",
        "load_recommendation",
        "recommended_action",
        "query_purpose",
        "desktop_finalize_note",
    ]
    return query_catalog.loc[:, ordered_columns]


def _assert_safe_template_target(template_dir: Path) -> None:
    resolved = template_dir.resolve()
    repo_resolved = REPO_ROOT.resolve()
    try:
        resolved.relative_to(repo_resolved)
    except ValueError as exc:
        raise ValueError(f"Template target must stay inside the repository: {resolved}") from exc


def _reset_directory(target: Path) -> None:
    """Regenerate a directory safely inside the repository."""
    _assert_safe_template_target(target)
    if target.exists():
        def _onerror(func, failing_path, exc_info):
            try:
                os.chmod(failing_path, stat.S_IWRITE)
                func(failing_path)
            except OSError:
                # Some local and sandboxed environments block recursive deletes.
                # The build inventory neutralization pass handles obsolete files in place.
                pass

        try:
            shutil.rmtree(target, onerror=_onerror)
        except PermissionError:
            # Some Windows and sandboxed environments block recursive deletes.
            # Fall back to in-place regeneration plus obsolete-file neutralization.
            pass
    target.mkdir(parents=True, exist_ok=True)


def _power_query_type(series: pd.Series) -> str:
    if pd.api.types.is_bool_dtype(series):
        return "type logical"
    if pd.api.types.is_integer_dtype(series):
        return "Int64.Type"
    if pd.api.types.is_float_dtype(series):
        return "type number"
    return "type text"


def _render_parameter_query(default_value: str = PROJECT_ROOT_PLACEHOLDER) -> str:
    return (
        "// Replace the placeholder with the absolute path to the repository root.\n"
        "// Example: D:\\\\Repos\\\\copper_minning_risk_model\n"
        "let\n"
        f'    {PROJECT_ROOT_PARAMETER} = "{default_value}"\n'
        "in\n"
        f"    {PROJECT_ROOT_PARAMETER}\n"
    )


def _render_output_root_query(parameter_name: str, default_output_dir: str) -> str:
    windows_value = _windows_path(default_output_dir)
    if not Path(default_output_dir).is_absolute():
        expression = f'{PROJECT_ROOT_PARAMETER} & "\\\\{windows_value}"'
    else:
        expression = f'"{windows_value}"'
    return (
        f"// Change this output-root query only if your local runner writes the dataset family somewhere else.\n"
        "let\n"
        f"    {parameter_name} = {expression}\n"
        "in\n"
        f"    {parameter_name}\n"
    )


def _render_csv_query(source_parameter_name: str, source_file: str, source_df: pd.DataFrame) -> str:
    type_rows = []
    for column in source_df.columns:
        power_query_type = _power_query_type(source_df[column])
        type_rows.append(f'            {{"{column}", {power_query_type}}}')
    type_block = ",\n".join(type_rows)
    source_windows_path = _windows_path(source_file)
    return (
        "let\n"
        f'    SourcePath = {source_parameter_name} & "\\\\{source_windows_path}",\n'
        "    Source = Csv.Document(\n"
        "        File.Contents(SourcePath),\n"
        '        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]\n'
        "    ),\n"
        "    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),\n"
        "    TypedColumns = Table.TransformColumnTypes(\n"
        "        PromotedHeaders,\n"
        "        {\n"
        f"{type_block}\n"
        "        }\n"
        "    )\n"
        "in\n"
        "    TypedColumns\n"
    )


def build_powerbi_parameter_manifest(handoff_context: PowerBIHandoffContext) -> dict[str, object]:
    """Describe the editable Power Query parameters for the Desktop finalization step."""

    return {
        "artifact_strategy": handoff_context.artifact_strategy,
        "profile_name": handoff_context.profile_name,
        "profile_path": handoff_context.profile_path,
        "appendix_enabled": handoff_context.appendix_enabled,
        "parameters": [
            {
                "parameter_name": PROJECT_ROOT_PARAMETER,
                "purpose": "Absolute local path to the repository root.",
                "default_value": PROJECT_ROOT_PLACEHOLDER,
                "change_when": "Always replace the placeholder before importing CSV queries in Desktop.",
            },
            *_output_root_parameter_specs(handoff_context),
        ],
    }


def _safe_slug(value: str) -> str:
    return value.lower().replace(" / ", "_").replace(" ", "_").replace("-", "_")


def _render_measure_bundle(title: str, measures: pd.DataFrame) -> str:
    lines = [f"-- {title}", ""]
    current_table: str | None = None
    for measure in measures.sort_values(["table_name", "measure_name"]).itertuples(index=False):
        if measure.table_name != current_table:
            if current_table is not None:
                lines.append("")
            lines.append(f"-- Table: {measure.table_name}")
            current_table = measure.table_name
        lines.append(str(measure.dax_template))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _build_report_manifest(page_catalog: pd.DataFrame, visual_catalog: pd.DataFrame) -> dict[str, object]:
    pages = []
    for page in page_catalog.sort_values("page_order").itertuples(index=False):
        visuals = visual_catalog.loc[visual_catalog["page_name"] == page.page_name].sort_values("visual_order")
        pages.append(
            {
                "page_order": int(page.page_order),
                "page_name": page.page_name,
                "page_group": page.page_group,
                "goal": page.goal,
                "primary_dataset": page.primary_dataset,
                "story_role": "Core Monthly Story" if page.page_group == "Monthly Monitoring" else "Secondary Appendix",
                "visual_count": int(len(visuals)),
                "visuals": visuals.loc[
                    :,
                    [
                        "visual_order",
                        "visual_title",
                        "visual_type",
                        "source_table",
                        "key_dimensions",
                        "key_measures",
                        "business_question",
                    ],
                ].to_dict(orient="records"),
            }
        )
    return {"pages": pages}


def _build_template_manifest(
    query_catalog: pd.DataFrame,
    page_catalog: pd.DataFrame,
    measure_catalog: pd.DataFrame,
    handoff_context: PowerBIHandoffContext,
) -> dict[str, object]:
    output_root_parameters = {
        "starter_kit": STARTER_KIT_OUTPUT_PARAMETER,
        "monthly": MONTHLY_OUTPUT_PARAMETER,
    }
    default_output_roots = {
        "starter_kit": _display_repo_path(handoff_context.starter_kit_output_dir),
        "monthly": _display_repo_path(handoff_context.monthly_output_dir),
    }
    if handoff_context.appendix_enabled:
        output_root_parameters["advanced_appendix"] = ADVANCED_APPENDIX_OUTPUT_PARAMETER
        default_output_roots["advanced_appendix"] = _display_repo_path(handoff_context.advanced_appendix_output_dir)

    return {
        "artifact_name": "Copper Mining Monitoring Power BI Scaffold",
        "artifact_type": "Power BI Desktop finalization package with executable Power Query imports and reusable DAX bundles",
        "artifact_strategy": handoff_context.artifact_strategy,
        "public_safe": True,
        "main_story": "Monthly actual-vs-plan monitoring remains the first-class report narrative.",
        "secondary_appendix": (
            "Valuation, scenario, benchmark, Monte Carlo, tornado, and heatmap outputs remain in the appendix only."
            if handoff_context.appendix_enabled
            else "Appendix assets are intentionally omitted because the selected profile disables the advanced appendix path."
        ),
        "profile_name": handoff_context.profile_name,
        "profile_path": handoff_context.profile_path,
        "appendix_enabled": handoff_context.appendix_enabled,
        "project_root_parameter_name": PROJECT_ROOT_PARAMETER,
        "output_root_parameters": output_root_parameters,
        "default_output_roots": default_output_roots,
        "query_count": int(len(query_catalog)),
        "page_count": int(len(page_catalog)),
        "measure_count": int(len(measure_catalog)),
        "core_pages": page_catalog.loc[page_catalog["page_group"] == "Monthly Monitoring", "page_name"].tolist(),
        "appendix_page": page_catalog.loc[page_catalog["page_group"] == "Advanced Appendix", "page_name"].tolist(),
        "desktop_required_steps": [
            "Set ProjectRoot and the output-root queries in parameters/.",
            "Import the Power Query files in query order.",
            "Disable load for reference queries when they are only used as build aids.",
            "Create relationships from the relationship catalog with dim_site and dim_month as the monthly semantic center.",
            "Paste the DAX measure bundles and complete sort-by plus hidden-field cleanup.",
            "Lay out pages in the monthly-first order from the report manifest.",
        ],
    }


def _render_template_readme(handoff_context: PowerBIHandoffContext, page_catalog: pd.DataFrame) -> str:
    profile_note = (
        f"- profile-aware defaults were resolved from `{handoff_context.profile_path}`\n"
        if handoff_context.profile_path
        else ""
    )
    return f"""# Power BI Template Scaffold

This folder is the repository's fastest honest Power BI Desktop finalization package.

What this scaffold gives you:

- ready-to-paste Power Query imports for each exported mart, fact, and dimension
- separate output-root parameters for starter-kit references, monthly marts, and the secondary appendix
- shared monthly dimensions for site, month, process area, and cost center
- DAX measure bundles grouped by the report page order
- copied model and report catalogs for relationships, page order, visual intent, sort-by, and technical-field visibility
- a portable theme file for the starter report
- a parameter manifest that tells you exactly what still must be changed in Desktop

Use it like this:

1. Run `python scripts/build_bi_dataset.py` for the public demo baseline.
2. If you want local-runner-compatible defaults, rebuild with `python scripts/build_powerbi_template_layer.py --profile config/source_profiles/local/my_company_profile.yaml`.
3. In Power BI Desktop create a blank report.
4. Add the queries from `parameters/`:
{_parameter_query_markdown(handoff_context)}
5. Replace the placeholder in `ProjectRoot` and change only the output-root queries that need to follow your local runner outputs.
6. Import the `.pq` files from `queries/` in query order.
7. Disable load for any query marked `disable_load_after_import` in `model/powerbi_query_catalog.csv`.
8. Create relationships from `model/powerbi_relationship_catalog.csv`, starting with `dim_site` and `dim_month` as the monthly semantic center.
9. Paste the DAX bundles from `measures/`.
10. Apply sort-by and hidden-column cleanup from `model/powerbi_sort_by_catalog.csv` and `model/powerbi_field_visibility_catalog.csv`.
11. Build pages in the order described in `report/dashboard_page_catalog.csv` and `report/report_manifest.json`.

This scaffold is intentionally public-safe:

- it uses only repository exports
- it does not contain company connections
- it does not claim live ERP, plant, or telemetry integration
- it is a finalization package, not a fake Desktop-saved `.pbip`

Profile defaults:

{profile_note}{_profile_defaults_markdown(handoff_context)}

Current report order:

{_page_order_markdown(page_catalog)}

It is near plug-and-play rather than a binary `.pbit`.

If you want the more native-feeling continuation path, use `powerbi/pbip_tmdl_scaffold/` after running the BI build.
"""


def build_powerbi_template_layer(
    bi_output_dir: str | Path = REPO_ROOT / "outputs" / "bi",
    template_dir: str | Path = DEFAULT_TEMPLATE_DIR,
    profile_path: str | Path | None = None,
) -> dict[str, Path]:
    """Build a near-executable Power BI scaffold package from current BI exports."""
    bi_output_dir = Path(bi_output_dir)
    template_dir = Path(template_dir)
    _reset_directory(template_dir)

    page_catalog = pd.read_csv(bi_output_dir / "dashboard_page_catalog.csv")
    relationship_catalog = pd.read_csv(bi_output_dir / "powerbi_relationship_catalog.csv")
    measure_catalog = pd.read_csv(bi_output_dir / "powerbi_measure_catalog.csv")
    sort_by_catalog = pd.read_csv(bi_output_dir / "powerbi_sort_by_catalog.csv")
    field_visibility_catalog = pd.read_csv(bi_output_dir / "powerbi_field_visibility_catalog.csv")
    visual_catalog = pd.read_csv(bi_output_dir / "powerbi_visual_binding_catalog.csv")
    table_catalog = pd.read_csv(bi_output_dir / "powerbi_table_catalog.csv")
    monthly_dictionary = pd.read_csv(bi_output_dir / "monthly_kpi_dictionary.csv")
    handoff_context = resolve_powerbi_handoff_context(profile_path, bi_output_dir=bi_output_dir)
    page_catalog = _filter_powerbi_page_catalog(page_catalog, handoff_context)
    relationship_catalog = _filter_powerbi_relationship_catalog(relationship_catalog, handoff_context)
    measure_catalog = _filter_powerbi_measure_catalog(measure_catalog, handoff_context)
    table_catalog = _filter_powerbi_table_catalog(table_catalog, handoff_context)
    sort_by_catalog = _filter_table_named_catalog(sort_by_catalog, table_catalog=table_catalog)
    field_visibility_catalog = _filter_table_named_catalog(field_visibility_catalog, table_catalog=table_catalog)
    visual_catalog = _filter_powerbi_visual_catalog(visual_catalog, page_catalog)
    query_catalog = build_powerbi_query_catalog(table_catalog=table_catalog, handoff_context=handoff_context)
    parameter_manifest = build_powerbi_parameter_manifest(handoff_context)

    parameters_dir = template_dir / "parameters"
    queries_dir = template_dir / "queries"
    measures_dir = template_dir / "measures"
    model_dir = template_dir / "model"
    report_dir = template_dir / "report"
    theme_dir = template_dir / "theme"

    for path in [parameters_dir, queries_dir, measures_dir, model_dir, report_dir, theme_dir]:
        path.mkdir(parents=True, exist_ok=True)

    (parameters_dir / f"{PROJECT_ROOT_PARAMETER}.pq").write_text(_render_parameter_query(), encoding="utf-8")
    for parameter_spec in _output_root_parameter_specs(handoff_context):
        (parameters_dir / f"{parameter_spec['parameter_name']}.pq").write_text(
            _render_output_root_query(
                str(parameter_spec["parameter_name"]),
                str(parameter_spec["default_output_dir"]),
            ),
            encoding="utf-8",
        )
    (parameters_dir / "parameter_manifest.json").write_text(json.dumps(parameter_manifest, indent=2), encoding="utf-8")

    for query in query_catalog.sort_values("query_order").itertuples(index=False):
        source_df = pd.read_csv(bi_output_dir / query.source_file)
        query_path = queries_dir / query.power_query_relative_file
        query_path.parent.mkdir(parents=True, exist_ok=True)
        query_path.write_text(
            _render_csv_query(
                source_parameter_name=query.parameter_name,
                source_file=query.source_file,
                source_df=source_df,
            ),
            encoding="utf-8",
        )

    all_measure_path = measures_dir / "00_all_measures.dax"
    all_measure_path.write_text(_render_measure_bundle("All Recommended Measures", measure_catalog), encoding="utf-8")

    for page in page_catalog.sort_values("page_order").itertuples(index=False):
        page_measures = measure_catalog.loc[measure_catalog["dashboard_page"] == page.page_name]
        page_bundle_path = measures_dir / f"{int(page.page_order):02d}_{_safe_slug(page.page_name)}.dax"
        page_bundle_path.write_text(
            _render_measure_bundle(f"{page.page_name} Measures", page_measures),
            encoding="utf-8",
        )

    query_catalog.to_csv(model_dir / "powerbi_query_catalog.csv", index=False)
    table_catalog.to_csv(model_dir / "powerbi_table_catalog.csv", index=False)
    relationship_catalog.to_csv(model_dir / "powerbi_relationship_catalog.csv", index=False)
    measure_catalog.to_csv(model_dir / "powerbi_measure_catalog.csv", index=False)
    sort_by_catalog.to_csv(model_dir / "powerbi_sort_by_catalog.csv", index=False)
    field_visibility_catalog.to_csv(model_dir / "powerbi_field_visibility_catalog.csv", index=False)
    monthly_dictionary.to_csv(model_dir / "monthly_kpi_dictionary.csv", index=False)

    page_catalog.to_csv(report_dir / "dashboard_page_catalog.csv", index=False)
    visual_catalog.to_csv(report_dir / "powerbi_visual_binding_catalog.csv", index=False)

    report_manifest = _build_report_manifest(page_catalog=page_catalog, visual_catalog=visual_catalog)
    (report_dir / "report_manifest.json").write_text(
        json.dumps(report_manifest, indent=2),
        encoding="utf-8",
    )

    template_manifest = _build_template_manifest(
        query_catalog=query_catalog,
        page_catalog=page_catalog,
        measure_catalog=measure_catalog,
        handoff_context=handoff_context,
    )
    (template_dir / "template_manifest.json").write_text(
        json.dumps(template_manifest, indent=2),
        encoding="utf-8",
    )
    (template_dir / "README.md").write_text(
        _render_template_readme(handoff_context, page_catalog),
        encoding="utf-8",
    )

    theme_source = REPO_ROOT / "powerbi" / "copper_risk_theme.json"
    shutil.copy2(theme_source, theme_dir / "copper_risk_theme.json")

    current_inventory = {
        _inventory_entry(template_dir, template_dir / "README.md"),
        _inventory_entry(template_dir, template_dir / "template_manifest.json"),
        _inventory_entry(template_dir, parameters_dir / f"{PROJECT_ROOT_PARAMETER}.pq"),
        _inventory_entry(template_dir, parameters_dir / "parameter_manifest.json"),
        *{
            _inventory_entry(template_dir, parameters_dir / f"{parameter_spec['parameter_name']}.pq")
            for parameter_spec in _output_root_parameter_specs(handoff_context)
        },
        *{
            _inventory_entry(template_dir, queries_dir / str(query.power_query_relative_file))
            for query in query_catalog.itertuples(index=False)
        },
        _inventory_entry(template_dir, measures_dir / "00_all_measures.dax"),
        *{
            _inventory_entry(
                template_dir,
                measures_dir / f"{int(page.page_order):02d}_{_safe_slug(page.page_name)}.dax",
            )
            for page in page_catalog.itertuples(index=False)
        },
        _inventory_entry(template_dir, model_dir / "powerbi_query_catalog.csv"),
        _inventory_entry(template_dir, model_dir / "powerbi_table_catalog.csv"),
        _inventory_entry(template_dir, model_dir / "powerbi_relationship_catalog.csv"),
        _inventory_entry(template_dir, model_dir / "powerbi_measure_catalog.csv"),
        _inventory_entry(template_dir, model_dir / "powerbi_sort_by_catalog.csv"),
        _inventory_entry(template_dir, model_dir / "powerbi_field_visibility_catalog.csv"),
        _inventory_entry(template_dir, model_dir / "monthly_kpi_dictionary.csv"),
        _inventory_entry(template_dir, report_dir / "dashboard_page_catalog.csv"),
        _inventory_entry(template_dir, report_dir / "powerbi_visual_binding_catalog.csv"),
        _inventory_entry(template_dir, report_dir / "report_manifest.json"),
        _inventory_entry(template_dir, theme_dir / "copper_risk_theme.json"),
        BUILD_INVENTORY_FILENAME,
    }
    obsolete_files = _neutralize_obsolete_files(template_dir, current_inventory)
    build_inventory = _write_build_inventory(template_dir, current_inventory, obsolete_files)

    return {
        "template_root": template_dir,
        "parameter_query": parameters_dir / f"{PROJECT_ROOT_PARAMETER}.pq",
        "parameter_manifest": parameters_dir / "parameter_manifest.json",
        "query_catalog": model_dir / "powerbi_query_catalog.csv",
        "all_measures": all_measure_path,
        "report_manifest": report_dir / "report_manifest.json",
        "template_manifest": template_dir / "template_manifest.json",
        "template_readme": template_dir / "README.md",
        "build_inventory": build_inventory,
    }
