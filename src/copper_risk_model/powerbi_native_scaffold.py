"""Build a PBIP/TMDL-oriented Power BI scaffold from public-safe BI exports."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .powerbi_template import (
    ADVANCED_APPENDIX_OUTPUT_PARAMETER,
    BUILD_INVENTORY_FILENAME,
    MONTHLY_OUTPUT_PARAMETER,
    PROJECT_ROOT_PARAMETER,
    REPO_ROOT,
    STARTER_KIT_OUTPUT_PARAMETER,
    PowerBIHandoffContext,
    _display_repo_path,
    _filter_powerbi_measure_catalog,
    _filter_powerbi_page_catalog,
    _filter_powerbi_relationship_catalog,
    _filter_powerbi_table_catalog,
    _filter_powerbi_visual_catalog,
    _filter_table_named_catalog,
    _output_root_parameter_specs,
    _page_order_markdown,
    _page_sequence,
    _parameter_query_markdown,
    _profile_defaults_markdown,
    _inventory_entry,
    _neutralize_obsolete_files,
    _write_build_inventory,
    build_powerbi_parameter_manifest,
    build_powerbi_query_catalog,
    _reset_directory,
    _render_csv_query,
    _render_output_root_query,
    _render_parameter_query,
    _safe_slug,
    resolve_powerbi_handoff_context,
)
from .file_outputs import write_csv_output, write_json_output, write_text_output

DEFAULT_NATIVE_SCAFFOLD_DIR = REPO_ROOT / "powerbi" / "pbip_tmdl_scaffold"
PBIP_PROJECT_NAME = "CopperMiningMonitoring"


def _quote_tmdl_name(name: str) -> str:
    if any(character in name for character in " .:=/'-%") or name != name.strip():
        return "'" + name.replace("'", "''") + "'"
    return name


def _render_model_ordering_tmdl(table_catalog: pd.DataFrame) -> str:
    lines = [
        "createOrReplace",
        "",
        "model Model",
    ]
    for table_name in table_catalog.sort_values("import_order")["table_name"]:
        lines.append(f"    ref table {_quote_tmdl_name(str(table_name))}")
    return "\n".join(lines) + "\n"


def _render_sort_and_visibility_tmdl(
    sort_by_catalog: pd.DataFrame,
    field_visibility_catalog: pd.DataFrame,
) -> str:
    table_column_rules: dict[str, dict[str, dict[str, object]]] = {}
    table_order: list[str] = []

    def ensure_rule(table_name: str, column_name: str) -> dict[str, object]:
        if table_name not in table_column_rules:
            table_column_rules[table_name] = {}
            table_order.append(table_name)
        if column_name not in table_column_rules[table_name]:
            table_column_rules[table_name][column_name] = {}
        return table_column_rules[table_name][column_name]

    for row in sort_by_catalog.sort_values("sort_order").itertuples(index=False):
        display_rule = ensure_rule(str(row.table_name), str(row.display_column))
        display_rule["sort_by_column"] = str(row.sort_by_column)
        display_rule["summarize_by"] = "none"

    for row in field_visibility_catalog.sort_values("visibility_order").itertuples(index=False):
        visibility_rule = ensure_rule(str(row.table_name), str(row.column_name))
        if str(row.recommended_visibility) == "hide":
            visibility_rule["is_hidden"] = True
            visibility_rule["summarize_by"] = "none"

    lines = ["createOrReplace", ""]
    for table_name in table_order:
        lines.append(f"ref table {_quote_tmdl_name(table_name)}")
        for column_name, rule in table_column_rules[table_name].items():
            lines.append(f"    column {_quote_tmdl_name(column_name)}")
            if "sort_by_column" in rule:
                lines.append(f"        sortByColumn: {_quote_tmdl_name(str(rule['sort_by_column']))}")
            if rule.get("is_hidden"):
                lines.append("        isHidden")
            if rule.get("summarize_by"):
                lines.append(f"        summarizeBy: {rule['summarize_by']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _measure_expression(dax_template: str) -> str:
    _, _, expression = dax_template.partition(" = ")
    return expression.strip()


def _render_measure_tmdl(measures: pd.DataFrame) -> str:
    lines = ["createOrReplace", ""]
    for table_name, table_measures in measures.sort_values(["table_name", "measure_order"]).groupby("table_name", sort=False):
        lines.append(f"ref table {_quote_tmdl_name(str(table_name))}")
        for measure in table_measures.itertuples(index=False):
            lines.append(f"    /// {measure.description}")
            lines.append(
                f"    measure {_quote_tmdl_name(str(measure.measure_name))} = {_measure_expression(str(measure.dax_template))}"
            )
            if str(measure.format_string):
                lines.append(f"        formatString: {measure.format_string}")
            lines.append(f'        displayFolder: "{measure.display_folder}"')
            lines.append("")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _relationship_object_name(row: pd.Series) -> str:
    return _safe_slug(
        f"rel_{int(row['relationship_order']):02d}_{row['from_table']}_{row['from_column']}_{row['to_table']}_{row['to_column']}"
    )


def _render_relationships_tmdl(relationship_catalog: pd.DataFrame) -> str:
    lines = ["createOrReplace", ""]
    for row in relationship_catalog.sort_values("relationship_order").itertuples(index=False):
        relationship_name = _relationship_object_name(pd.Series(row._asdict()))
        lines.append(f"/// {row.modeling_note}")
        lines.append(f"relationship {relationship_name}")
        lines.append(f"    fromColumn: {row.tmdl_from_column_reference}")
        lines.append(f"    toColumn: {row.tmdl_to_column_reference}")
        lines.append(f"    fromCardinality: {row.from_cardinality}")
        lines.append(f"    toCardinality: {row.to_cardinality}")
        lines.append(f"    crossFilteringBehavior: {row.tmdl_cross_filtering_behavior}")
        if bool(row.active_flag):
            lines.append("    isActive")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _split_catalog_values(raw_value: object) -> list[str]:
    if pd.isna(raw_value):
        return []
    return [value.strip() for value in str(raw_value).split(";") if value and value.strip()]


def _page_completion_checks(page_name: str, page_group: str) -> list[str]:
    checks = [
        "Confirm page title and narrative match the intended business question.",
        "Confirm dim_site and dim_month slicers are present where the monthly core requires them.",
        "Confirm visuals use the recommended marts, dimensions, and measures from the shell.",
    ]
    if page_group == "Monthly Monitoring":
        checks.append("Confirm the page still reads as management control rather than exploratory appendix analysis.")
    if page_name == "Process Performance":
        checks.append("Confirm process-area drill visuals use dim_process_area consistently.")
    if page_name == "Cost and Margin":
        checks.append("Confirm cost-center drill visuals use dim_cost_center consistently.")
    if page_group == "Advanced Appendix":
        checks.append("Keep the appendix page secondary and do not move it ahead of the monthly pages.")
    return checks


def _build_page_shell(page_row: pd.Series, visual_catalog: pd.DataFrame) -> dict[str, object]:
    page_visuals = visual_catalog.loc[visual_catalog["page_name"] == page_row["page_name"]].sort_values("visual_order")
    shared_slicers = ["dim_site[site_name]", "dim_month[month_label]"]
    page_specific_slicers: list[str] = []
    if str(page_row["page_name"]) == "Process Performance":
        page_specific_slicers = ["dim_process_area[process_area]"]
    elif str(page_row["page_name"]) == "Cost and Margin":
        page_specific_slicers = ["dim_cost_center[cost_center]"]

    required_tables = sorted(set(page_visuals["source_table"].astype(str)))
    required_measures = sorted(
        {
            measure
            for measure_list in page_visuals["key_measures"]
            for measure in _split_catalog_values(measure_list)
        }
    )
    required_dimensions = sorted(
        {
            dimension
            for dimension_list in page_visuals["key_dimensions"]
            for dimension in _split_catalog_values(dimension_list)
        }
    )

    return {
        "page_order": int(page_row["page_order"]),
        "page_name": page_row["page_name"],
        "page_group": page_row["page_group"],
        "story_role": "Core Monthly Story" if page_row["page_group"] == "Monthly Monitoring" else "Secondary Appendix",
        "goal": page_row["goal"],
        "primary_dataset": page_row["primary_dataset"],
        "shared_slicers": shared_slicers if page_row["page_group"] == "Monthly Monitoring" else [],
        "page_specific_slicers": page_specific_slicers,
        "required_tables": required_tables,
        "required_dimensions": required_dimensions,
        "required_measures": required_measures,
        "desktop_completion_checks": _page_completion_checks(str(page_row["page_name"]), str(page_row["page_group"])),
        "visuals": page_visuals.loc[
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


def _build_report_shell_manifest(
    page_catalog: pd.DataFrame,
    visual_catalog: pd.DataFrame,
    handoff_context: PowerBIHandoffContext,
) -> dict[str, object]:
    return {
        "artifact_strategy": handoff_context.artifact_strategy,
        "artifact_type": "Report page shell manifest",
        "page_count": int(len(page_catalog)),
        "main_story": "Keep the first four pages focused on monthly monitoring, management control, and KPI review.",
        "secondary_appendix": (
            "Treat the appendix page as a continuation layer, not the lead report story."
            if handoff_context.appendix_enabled
            else "Appendix page shells are intentionally omitted because the selected profile disables the advanced appendix path."
        ),
        "pages": [
            {
                "page_order": int(page["page_order"]),
                "page_name": page["page_name"],
                "page_group": page["page_group"],
                "goal": page["goal"],
                "page_shell_file": f"page_shells/{int(page['page_order']):02d}_{_safe_slug(str(page['page_name']))}.json",
                "visual_count": int(len(visual_catalog.loc[visual_catalog["page_name"] == page["page_name"]])),
                "shared_slicers": (
                    ["dim_site[site_name]", "dim_month[month_label]"]
                    if page["page_group"] == "Monthly Monitoring"
                    else []
                ),
            }
            for page in page_catalog.sort_values("page_order").to_dict(orient="records")
        ],
    }


def _build_native_scaffold_manifest(
    query_catalog: pd.DataFrame,
    table_catalog: pd.DataFrame,
    relationship_catalog: pd.DataFrame,
    measure_catalog: pd.DataFrame,
    sort_by_catalog: pd.DataFrame,
    field_visibility_catalog: pd.DataFrame,
    page_catalog: pd.DataFrame,
    handoff_context: PowerBIHandoffContext,
) -> dict[str, object]:
    default_output_roots = {
        "starter_kit": _display_repo_path(handoff_context.starter_kit_output_dir),
        "monthly": _display_repo_path(handoff_context.monthly_output_dir),
    }
    if handoff_context.appendix_enabled:
        default_output_roots["advanced_appendix"] = _display_repo_path(handoff_context.advanced_appendix_output_dir)

    return {
        "artifact_name": "Copper Mining Monitoring PBIP Finalization Package",
        "artifact_type": "PBIP finalization package",
        "artifact_strategy": handoff_context.artifact_strategy,
        "public_safe": True,
        "profile_name": handoff_context.profile_name,
        "profile_path": handoff_context.profile_path,
        "appendix_enabled": handoff_context.appendix_enabled,
        "main_story": "Monthly actual-vs-plan monitoring remains the semantic center of the model.",
        "secondary_appendix": (
            "Scenario, valuation, benchmark, and risk outputs remain a secondary appendix."
            if handoff_context.appendix_enabled
            else "Secondary appendix assets are intentionally omitted because the selected profile disables that path."
        ),
        "native_like_components": [
            "PBIP-style SemanticModel and Report folders",
            (
                "Power Query parameter roots aligned to starter-kit, monthly, and advanced-appendix output families"
                if handoff_context.appendix_enabled
                else "Power Query parameter roots aligned to starter-kit and monthly output families"
            ),
            "TMDL apply scripts for model ordering, measures, relationships, sort-by, and hidden technical fields",
            "Source-control-friendly manifests and page shells",
        ],
        "manual_components": [
            "A real Desktop-saved PBIP still needs to be created or saved from Power BI Desktop",
            "Power Query assets still need to be pasted or imported in Desktop",
            "TMDL scripts still need to be applied from TMDL view",
            "Report canvas visuals still need to be laid out manually from the page shells",
        ],
        "default_output_roots": default_output_roots,
        "query_count": int(len(query_catalog)),
        "table_count": int(len(table_catalog)),
        "relationship_count": int(len(relationship_catalog)),
        "measure_count": int(len(measure_catalog)),
        "sort_by_rule_count": int(len(sort_by_catalog)),
        "hidden_field_rule_count": int(len(field_visibility_catalog)),
        "page_count": int(len(page_catalog)),
    }


def _build_desktop_finalization_manifest(
    query_catalog: pd.DataFrame,
    relationship_catalog: pd.DataFrame,
    page_catalog: pd.DataFrame,
    handoff_context: PowerBIHandoffContext,
) -> dict[str, object]:
    default_output_roots = {
        "starter_kit": _display_repo_path(handoff_context.starter_kit_output_dir),
        "monthly": _display_repo_path(handoff_context.monthly_output_dir),
    }
    if handoff_context.appendix_enabled:
        default_output_roots["advanced_appendix"] = _display_repo_path(handoff_context.advanced_appendix_output_dir)

    verification_checks = [
        {
            "check_name": "monthly_semantic_center",
            "detail": "dim_site and dim_month should remain the shared filters across the monthly model.",
        },
        {
            "check_name": "core_relationship_count",
            "detail": f"Confirm {int((relationship_catalog['relationship_scope'] == 'Core Starter Kit').sum())} monthly-core relationships are active.",
        },
    ]
    if handoff_context.appendix_enabled:
        verification_checks.append(
            {
                "check_name": "appendix_relationship_count",
                "detail": f"Confirm {int((relationship_catalog['relationship_scope'] == 'Advanced Appendix').sum())} appendix relationships stay secondary.",
            }
        )
    else:
        verification_checks.append(
            {
                "check_name": "appendix_omitted",
                "detail": "Appendix relationships, queries, and page shells are intentionally omitted for this profile-driven scaffold.",
            }
        )
    verification_checks.extend(
        [
            {
                "check_name": "page_order",
                "detail": f"Report pages should remain ordered as {', '.join(_page_sequence(page_catalog))}.",
            },
            {
                "check_name": "query_grouping",
                "detail": f"Desktop import should preserve {int(query_catalog['query_group'].nunique())} grouped query families with separate output roots.",
            },
        ]
    )

    return {
        "artifact_strategy": handoff_context.artifact_strategy,
        "honest_limit": "This package is not a Power BI Desktop-saved PBIP. It is the strongest public-safe finalization package that can be produced here.",
        "profile_name": handoff_context.profile_name,
        "profile_path": handoff_context.profile_path,
        "appendix_enabled": handoff_context.appendix_enabled,
        "default_output_roots": default_output_roots,
        "desktop_required_steps": [
            "Create or open a blank PBIX or PBIP in Power BI Desktop.",
            "Import ProjectRoot plus the output-root parameter queries that ship with the scaffold.",
            "Import the grouped Power Query files and disable load for reference queries where appropriate.",
            "Apply the TMDL scripts in order to restore model ordering, visibility, measures, and relationships.",
            "Build report pages from the page-shell JSON files and keep the monthly pages first.",
            "Save the final local result as PBIP if source control continuity is needed.",
        ],
        "verification_checks": verification_checks,
        "page_sequence": _page_sequence(page_catalog),
    }


def _render_root_readme(handoff_context: PowerBIHandoffContext, page_catalog: pd.DataFrame) -> str:
    profile_line = (
        f"- this package was parameterized from `{handoff_context.profile_path}`\n"
        if handoff_context.profile_path
        else ""
    )
    return f"""# PBIP Finalization Package

This folder is the repository's strongest honest public-safe Power BI Desktop continuation package.

What it is:

- a PBIP-style folder structure with separate SemanticModel and Report folders
- reusable Power Query imports grouped by starter-kit references, monthly marts, and secondary appendix tables only when the selected profile keeps the appendix active
- output-root parameters that can follow either the public demo build or a unified local profile
- TMDL apply scripts for model ordering, measure bundles, relationships, sort-by rules, and hidden technical fields
- page-shell JSON files that preserve the intended report narrative and visual intent
- Desktop finalization manifests that explain what is already packaged and what still remains manual

What it is not:

- not a binary `.pbix`
- not a binary `.pbit`
- not a Power BI Desktop-authored PBIP already saved from a finished semantic model

Use this package when you want the repository handoff to feel as close as honestly possible to native PBIP continuation without pretending the final Desktop save already exists.

Recommended path:

1. Run `python scripts/build_bi_dataset.py` for the public-safe baseline.
2. If you want local-runner-aware defaults, rebuild with `python scripts/build_powerbi_native_scaffold.py --profile config/source_profiles/local/my_company_profile.yaml`.
3. Read `DESKTOP_FINALIZATION.md`.
4. Open `CopperMiningMonitoring.SemanticModel/README.md`.
5. Import the Power Query assets from `CopperMiningMonitoring.SemanticModel/PowerQuery/`.
6. Apply the TMDL scripts in `CopperMiningMonitoring.SemanticModel/TMDLScripts/`.
7. Build the report canvas from `CopperMiningMonitoring.Report/page_shells/`.
8. Save your local file as PBIP or PBIX from Power BI Desktop.

This scaffold keeps the monthly business story first:

{_page_order_markdown(page_catalog)}

Profile defaults:

{profile_line}{_profile_defaults_markdown(handoff_context)}
"""


def _render_semantic_model_readme(handoff_context: PowerBIHandoffContext) -> str:
    tmdl_steps = [
        "   - `00_model_ordering.tmdl`",
        "   - `01_sort_and_visibility.tmdl`",
        "   - `02_core_monthly_measures.tmdl`",
    ]
    if handoff_context.appendix_enabled:
        tmdl_steps.append("   - `03_advanced_appendix_measures.tmdl`")
    tmdl_steps.append("   - `04_relationships.tmdl`")
    return f"""# Semantic Model Scaffold

This folder is the semantic-model continuation layer for the public-safe Power BI handoff.

Recommended build sequence in Power BI Desktop:

1. Create a blank PBIX or PBIP.
2. Add these parameter queries from `PowerQuery/parameters/`:
{_parameter_query_markdown(handoff_context)}
3. Replace the placeholder in `ProjectRoot` and change only the output-root queries that need to follow your local runner folders.
4. Import the `.pq` queries from `PowerQuery/queries/` in query order.
5. Apply the TMDL scripts from `TMDLScripts/` in this order:
{chr(10).join(tmdl_steps)}
6. Check `catalogs/powerbi_sort_by_catalog.csv` and `catalogs/powerbi_field_visibility_catalog.csv` for any manual cleanup that still makes sense in your adapted model.
7. Verify that `dim_site` and `dim_month` remain the shared monthly filter center.
8. Save the result as PBIP if you want a fully source-control-friendly local continuation.

This scaffold is intentionally generic:

- no private connectors
- no internal company tables
- no proprietary mappings
- no hidden enterprise model claims

Current default output roots:

{_profile_defaults_markdown(handoff_context).replace("- starter-kit references default to", "- starter-kit references:").replace("- monthly queries default to", "- monthly model tables:").replace("- appendix queries default to", "- appendix tables:")}
"""


def _render_report_readme(handoff_context: PowerBIHandoffContext) -> str:
    appendix_line = (
        "5. Keep the appendix as secondary context only."
        if handoff_context.appendix_enabled
        else "5. If you later re-enable the appendix path, keep it secondary to the monthly pages."
    )
    return f"""# Report Scaffold

This folder packages the page shells for the intended monthly-first report story.

Use it after the semantic model is imported and the TMDL scripts are applied.

Recommended use:

1. Open `report_shell_manifest.json`.
2. Build pages in numeric order.
3. Use `page_shells/*.json` as the layout and visual-intent checklist.
4. Keep the first four pages as the main management-control story.
{appendix_line}
"""


def _render_desktop_finalization_readme(handoff_context: PowerBIHandoffContext) -> str:
    appendix_verification = (
        "3. confirm the appendix stays secondary"
        if handoff_context.appendix_enabled
        else "3. confirm the scaffold omits appendix assets cleanly for this monthly-first profile"
    )
    return f"""# Desktop Finalization

Artifact strategy:

- this repository does not claim to ship a real Desktop-saved PBIP
- this folder is the strongest honest PBIP finalization package that can be produced in a public-safe environment

What is already done:

- query grouping and output-root parameterization
- measure bundles and TMDL scripts
- relationship, sort-by, and hidden-field catalogs
- report page shells in monthly-first order

What still must be done in Desktop:

1. set `{PROJECT_ROOT_PARAMETER}` and the output-root queries included with this scaffold
2. import the Power Query files
3. apply the TMDL scripts
4. lay out the report canvas from the page shells
5. save the final local result as PBIP or PBIX

How to verify the model:

1. confirm `dim_site` and `dim_month` are the shared monthly filters
2. confirm the first four pages remain the operational story
{appendix_verification}
4. confirm the model points only to public-safe outputs or to ignored local runner outputs

Current defaults:

{_profile_defaults_markdown(handoff_context).replace("- starter-kit references default to", "- starter-kit references:").replace("- monthly queries default to", "- monthly model tables:").replace("- appendix queries default to", "- appendix tables:")}
"""


def _render_gitignore() -> str:
    return """# Local Power BI state that should not be committed if this scaffold is converted into a live PBIP
**/.pbi/localSettings.json
**/.pbi/cache.abf
**/.pbi/unappliedChanges.json
"""


def build_powerbi_native_scaffold(
    bi_output_dir: str | Path = REPO_ROOT / "outputs" / "bi",
    scaffold_dir: str | Path = DEFAULT_NATIVE_SCAFFOLD_DIR,
    profile_path: str | Path | None = None,
) -> dict[str, Path]:
    """Build a PBIP finalization package from current BI exports."""

    bi_output_dir = Path(bi_output_dir)
    scaffold_dir = Path(scaffold_dir)
    _reset_directory(scaffold_dir)

    table_catalog = pd.read_csv(bi_output_dir / "powerbi_table_catalog.csv")
    relationship_catalog = pd.read_csv(bi_output_dir / "powerbi_relationship_catalog.csv")
    measure_catalog = pd.read_csv(bi_output_dir / "powerbi_measure_catalog.csv")
    sort_by_catalog = pd.read_csv(bi_output_dir / "powerbi_sort_by_catalog.csv")
    field_visibility_catalog = pd.read_csv(bi_output_dir / "powerbi_field_visibility_catalog.csv")
    page_catalog = pd.read_csv(bi_output_dir / "dashboard_page_catalog.csv")
    visual_catalog = pd.read_csv(bi_output_dir / "powerbi_visual_binding_catalog.csv")
    monthly_dictionary = pd.read_csv(bi_output_dir / "monthly_kpi_dictionary.csv")
    monthly_dataset_catalog = pd.read_csv(bi_output_dir / "monthly_dataset_catalog.csv")
    monthly_field_catalog = pd.read_csv(bi_output_dir / "monthly_field_catalog.csv")
    handoff_context = resolve_powerbi_handoff_context(profile_path, bi_output_dir=bi_output_dir)
    table_catalog = _filter_powerbi_table_catalog(table_catalog, handoff_context)
    relationship_catalog = _filter_powerbi_relationship_catalog(relationship_catalog, handoff_context)
    measure_catalog = _filter_powerbi_measure_catalog(measure_catalog, handoff_context)
    sort_by_catalog = _filter_table_named_catalog(sort_by_catalog, table_catalog=table_catalog)
    field_visibility_catalog = _filter_table_named_catalog(field_visibility_catalog, table_catalog=table_catalog)
    page_catalog = _filter_powerbi_page_catalog(page_catalog, handoff_context)
    visual_catalog = _filter_powerbi_visual_catalog(visual_catalog, page_catalog)
    query_catalog = build_powerbi_query_catalog(table_catalog=table_catalog, handoff_context=handoff_context)
    parameter_manifest = build_powerbi_parameter_manifest(handoff_context)
    desktop_finalization_manifest = _build_desktop_finalization_manifest(
        query_catalog=query_catalog,
        relationship_catalog=relationship_catalog,
        page_catalog=page_catalog,
        handoff_context=handoff_context,
    )

    semantic_model_dir = scaffold_dir / f"{PBIP_PROJECT_NAME}.SemanticModel"
    report_dir = scaffold_dir / f"{PBIP_PROJECT_NAME}.Report"
    powerquery_dir = semantic_model_dir / "PowerQuery"
    parameters_dir = powerquery_dir / "parameters"
    queries_dir = powerquery_dir / "queries"
    tmdl_scripts_dir = semantic_model_dir / "TMDLScripts"
    semantic_catalogs_dir = semantic_model_dir / "catalogs"
    page_shells_dir = report_dir / "page_shells"
    report_assets_dir = report_dir / "assets"

    for path in [
        semantic_model_dir,
        report_dir,
        powerquery_dir,
        parameters_dir,
        queries_dir,
        tmdl_scripts_dir,
        semantic_catalogs_dir,
        page_shells_dir,
        report_assets_dir,
    ]:
        path.mkdir(parents=True, exist_ok=True)

    write_text_output(scaffold_dir / ".gitignore", _render_gitignore())
    write_text_output(scaffold_dir / "README.md", _render_root_readme(handoff_context, page_catalog))
    write_text_output(scaffold_dir / "DESKTOP_FINALIZATION.md", _render_desktop_finalization_readme(handoff_context))
    write_text_output(semantic_model_dir / "README.md", _render_semantic_model_readme(handoff_context))
    write_text_output(report_dir / "README.md", _render_report_readme(handoff_context))

    write_text_output(parameters_dir / f"{PROJECT_ROOT_PARAMETER}.pq", _render_parameter_query())
    for parameter_spec in _output_root_parameter_specs(handoff_context):
        write_text_output(
            parameters_dir / f"{parameter_spec['parameter_name']}.pq",
            _render_output_root_query(
                str(parameter_spec["parameter_name"]),
                str(parameter_spec["default_output_dir"]),
            ),
        )
    write_json_output(parameters_dir / "parameter_manifest.json", parameter_manifest)
    for query in query_catalog.sort_values("query_order").itertuples(index=False):
        source_df = pd.read_csv(bi_output_dir / query.source_file)
        query_path = queries_dir / query.power_query_relative_file
        query_path.parent.mkdir(parents=True, exist_ok=True)
        write_text_output(
            query_path,
            _render_csv_query(
                source_parameter_name=query.parameter_name,
                source_file=query.source_file,
                source_df=source_df,
            ),
        )
    write_csv_output(query_catalog, powerquery_dir / "powerbi_query_catalog.csv")

    write_text_output(tmdl_scripts_dir / "00_model_ordering.tmdl", _render_model_ordering_tmdl(table_catalog))
    write_text_output(
        tmdl_scripts_dir / "01_sort_and_visibility.tmdl",
        _render_sort_and_visibility_tmdl(sort_by_catalog, field_visibility_catalog),
    )
    write_text_output(
        tmdl_scripts_dir / "02_core_monthly_measures.tmdl",
        _render_measure_tmdl(measure_catalog.loc[measure_catalog["starter_kit_scope"] == "Core Monthly Story"]),
    )
    write_text_output(
        tmdl_scripts_dir / "03_advanced_appendix_measures.tmdl",
        _render_measure_tmdl(measure_catalog.loc[measure_catalog["starter_kit_scope"] == "Advanced Appendix"]),
    )
    write_text_output(tmdl_scripts_dir / "04_relationships.tmdl", _render_relationships_tmdl(relationship_catalog))

    write_csv_output(table_catalog, semantic_catalogs_dir / "powerbi_table_catalog.csv")
    write_csv_output(relationship_catalog, semantic_catalogs_dir / "powerbi_relationship_catalog.csv")
    write_csv_output(measure_catalog, semantic_catalogs_dir / "powerbi_measure_catalog.csv")
    write_csv_output(sort_by_catalog, semantic_catalogs_dir / "powerbi_sort_by_catalog.csv")
    write_csv_output(field_visibility_catalog, semantic_catalogs_dir / "powerbi_field_visibility_catalog.csv")
    write_csv_output(monthly_dictionary, semantic_catalogs_dir / "monthly_kpi_dictionary.csv")
    write_csv_output(monthly_dataset_catalog, semantic_catalogs_dir / "monthly_dataset_catalog.csv")
    write_csv_output(monthly_field_catalog, semantic_catalogs_dir / "monthly_field_catalog.csv")

    report_manifest = _build_report_shell_manifest(
        page_catalog=page_catalog,
        visual_catalog=visual_catalog,
        handoff_context=handoff_context,
    )
    write_json_output(report_dir / "report_shell_manifest.json", report_manifest)
    write_csv_output(page_catalog, report_dir / "dashboard_page_catalog.csv")
    write_csv_output(visual_catalog, report_dir / "powerbi_visual_binding_catalog.csv")
    for page in page_catalog.sort_values("page_order").to_dict(orient="records"):
        page_shell_path = page_shells_dir / f"{int(page['page_order']):02d}_{_safe_slug(str(page['page_name']))}.json"
        write_json_output(page_shell_path, _build_page_shell(pd.Series(page), visual_catalog))

    theme_source = REPO_ROOT / "powerbi" / "copper_risk_theme.json"
    write_text_output(report_assets_dir / "copper_risk_theme.json", theme_source.read_text(encoding="utf-8"))

    scaffold_manifest = _build_native_scaffold_manifest(
        query_catalog=query_catalog,
        table_catalog=table_catalog,
        relationship_catalog=relationship_catalog,
        measure_catalog=measure_catalog,
        sort_by_catalog=sort_by_catalog,
        field_visibility_catalog=field_visibility_catalog,
        page_catalog=page_catalog,
        handoff_context=handoff_context,
    )
    write_json_output(scaffold_dir / "scaffold_manifest.json", scaffold_manifest)
    write_json_output(scaffold_dir / "desktop_finalization_manifest.json", desktop_finalization_manifest)

    current_inventory = {
        _inventory_entry(scaffold_dir, scaffold_dir / ".gitignore"),
        _inventory_entry(scaffold_dir, scaffold_dir / "README.md"),
        _inventory_entry(scaffold_dir, scaffold_dir / "DESKTOP_FINALIZATION.md"),
        _inventory_entry(scaffold_dir, scaffold_dir / "scaffold_manifest.json"),
        _inventory_entry(scaffold_dir, scaffold_dir / "desktop_finalization_manifest.json"),
        _inventory_entry(scaffold_dir, semantic_model_dir / "README.md"),
        _inventory_entry(scaffold_dir, report_dir / "README.md"),
        _inventory_entry(scaffold_dir, parameters_dir / f"{PROJECT_ROOT_PARAMETER}.pq"),
        _inventory_entry(scaffold_dir, parameters_dir / "parameter_manifest.json"),
        *{
            _inventory_entry(scaffold_dir, parameters_dir / f"{parameter_spec['parameter_name']}.pq")
            for parameter_spec in _output_root_parameter_specs(handoff_context)
        },
        *{
            _inventory_entry(scaffold_dir, queries_dir / str(query.power_query_relative_file))
            for query in query_catalog.itertuples(index=False)
        },
        _inventory_entry(scaffold_dir, powerquery_dir / "powerbi_query_catalog.csv"),
        _inventory_entry(scaffold_dir, tmdl_scripts_dir / "00_model_ordering.tmdl"),
        _inventory_entry(scaffold_dir, tmdl_scripts_dir / "01_sort_and_visibility.tmdl"),
        _inventory_entry(scaffold_dir, tmdl_scripts_dir / "02_core_monthly_measures.tmdl"),
        _inventory_entry(scaffold_dir, tmdl_scripts_dir / "03_advanced_appendix_measures.tmdl"),
        _inventory_entry(scaffold_dir, tmdl_scripts_dir / "04_relationships.tmdl"),
        _inventory_entry(scaffold_dir, semantic_catalogs_dir / "powerbi_table_catalog.csv"),
        _inventory_entry(scaffold_dir, semantic_catalogs_dir / "powerbi_relationship_catalog.csv"),
        _inventory_entry(scaffold_dir, semantic_catalogs_dir / "powerbi_measure_catalog.csv"),
        _inventory_entry(scaffold_dir, semantic_catalogs_dir / "powerbi_sort_by_catalog.csv"),
        _inventory_entry(scaffold_dir, semantic_catalogs_dir / "powerbi_field_visibility_catalog.csv"),
        _inventory_entry(scaffold_dir, semantic_catalogs_dir / "monthly_kpi_dictionary.csv"),
        _inventory_entry(scaffold_dir, semantic_catalogs_dir / "monthly_dataset_catalog.csv"),
        _inventory_entry(scaffold_dir, semantic_catalogs_dir / "monthly_field_catalog.csv"),
        _inventory_entry(scaffold_dir, report_dir / "report_shell_manifest.json"),
        _inventory_entry(scaffold_dir, report_dir / "dashboard_page_catalog.csv"),
        _inventory_entry(scaffold_dir, report_dir / "powerbi_visual_binding_catalog.csv"),
        _inventory_entry(scaffold_dir, report_assets_dir / "copper_risk_theme.json"),
        *{
            _inventory_entry(
                scaffold_dir,
                page_shells_dir / f"{int(page['page_order']):02d}_{_safe_slug(str(page['page_name']))}.json",
            )
            for page in page_catalog.sort_values("page_order").to_dict(orient="records")
        },
        BUILD_INVENTORY_FILENAME,
    }
    obsolete_files = _neutralize_obsolete_files(scaffold_dir, current_inventory)
    build_inventory = _write_build_inventory(scaffold_dir, current_inventory, obsolete_files)

    return {
        "scaffold_root": scaffold_dir,
        "semantic_model_root": semantic_model_dir,
        "report_root": report_dir,
        "parameter_query": parameters_dir / f"{PROJECT_ROOT_PARAMETER}.pq",
        "parameter_manifest": parameters_dir / "parameter_manifest.json",
        "model_ordering_script": tmdl_scripts_dir / "00_model_ordering.tmdl",
        "sort_visibility_script": tmdl_scripts_dir / "01_sort_and_visibility.tmdl",
        "core_measure_script": tmdl_scripts_dir / "02_core_monthly_measures.tmdl",
        "appendix_measure_script": tmdl_scripts_dir / "03_advanced_appendix_measures.tmdl",
        "relationship_script": tmdl_scripts_dir / "04_relationships.tmdl",
        "report_manifest": report_dir / "report_shell_manifest.json",
        "scaffold_manifest": scaffold_dir / "scaffold_manifest.json",
        "desktop_finalization_manifest": scaffold_dir / "desktop_finalization_manifest.json",
        "build_inventory": build_inventory,
    }
