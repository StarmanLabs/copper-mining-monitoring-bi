"""Build BI-ready datasets with a monthly core and a secondary appendix."""

from __future__ import annotations

from pathlib import Path

from .annual_appendix_work_adaptation import build_annual_appendix_work_outputs
from .advanced_appendix import build_advanced_appendix_outputs
from .bi_semantic import (
    build_dashboard_page_catalog,
    build_powerbi_field_visibility_catalog,
    build_powerbi_measure_catalog,
    build_powerbi_relationship_catalog,
    build_powerbi_sort_by_catalog,
    build_powerbi_table_catalog,
    build_powerbi_visual_binding_catalog,
)
from .monthly_monitoring import build_monthly_monitoring_outputs
from .powerbi_template import build_powerbi_query_catalog


def build_bi_outputs(
    config_path: str | Path = "config/project.yaml",
    output_dir: str | Path = "outputs/bi",
) -> dict[str, Path]:
    """Build the public BI core plus the clearly secondary appendix outputs."""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    dashboard_page_catalog = build_dashboard_page_catalog()
    powerbi_table_catalog = build_powerbi_table_catalog()
    powerbi_query_catalog = build_powerbi_query_catalog(powerbi_table_catalog)
    powerbi_relationship_catalog = build_powerbi_relationship_catalog()
    powerbi_visual_binding_catalog = build_powerbi_visual_binding_catalog()
    powerbi_measure_catalog = build_powerbi_measure_catalog()
    powerbi_sort_by_catalog = build_powerbi_sort_by_catalog()
    powerbi_field_visibility_catalog = build_powerbi_field_visibility_catalog()

    outputs = {
        "dashboard_page_catalog": output_dir / "dashboard_page_catalog.csv",
        "powerbi_table_catalog": output_dir / "powerbi_table_catalog.csv",
        "powerbi_query_catalog": output_dir / "powerbi_query_catalog.csv",
        "powerbi_relationship_catalog": output_dir / "powerbi_relationship_catalog.csv",
        "powerbi_visual_binding_catalog": output_dir / "powerbi_visual_binding_catalog.csv",
        "powerbi_measure_catalog": output_dir / "powerbi_measure_catalog.csv",
        "powerbi_sort_by_catalog": output_dir / "powerbi_sort_by_catalog.csv",
        "powerbi_field_visibility_catalog": output_dir / "powerbi_field_visibility_catalog.csv",
    }

    dashboard_page_catalog.to_csv(outputs["dashboard_page_catalog"], index=False)
    powerbi_table_catalog.to_csv(outputs["powerbi_table_catalog"], index=False)
    powerbi_query_catalog.to_csv(outputs["powerbi_query_catalog"], index=False)
    powerbi_relationship_catalog.to_csv(outputs["powerbi_relationship_catalog"], index=False)
    powerbi_visual_binding_catalog.to_csv(outputs["powerbi_visual_binding_catalog"], index=False)
    powerbi_measure_catalog.to_csv(outputs["powerbi_measure_catalog"], index=False)
    powerbi_sort_by_catalog.to_csv(outputs["powerbi_sort_by_catalog"], index=False)
    powerbi_field_visibility_catalog.to_csv(outputs["powerbi_field_visibility_catalog"], index=False)

    outputs.update(build_annual_appendix_work_outputs(output_dir=output_dir))
    outputs.update(build_advanced_appendix_outputs(config_path=config_path, output_dir=output_dir))
    outputs.update(build_monthly_monitoring_outputs(output_dir=output_dir))
    return outputs
