"""Monthly actual-vs-plan monitoring layer for planning, control, and BI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .data_quality import build_data_quality_report, summarize_data_quality_report
from .file_outputs import write_csv_output, write_json_output
from .monthly_validation import ColumnRule, DatasetSchema, validate_dataframe
from .refresh_reporting import build_kpi_exceptions, build_refresh_summary, summarize_kpi_exceptions
from .source_mapping import map_source_directory

POUNDS_PER_METRIC_TONNE = 2204.62262185
MIN_NET_REALIZED_PRICE_USD_PER_LB = 0.10
MAX_NET_REALIZED_PRICE_USD_PER_LB = 15.0
MIN_REVENUE_PROXY_USD_PER_COPPER_TONNE = 500.0
MAX_REVENUE_PROXY_USD_PER_COPPER_TONNE = 100_000.0
SAMPLE_DATA_CLASSIFICATION = "sample_demo_monthly_monitoring"
REPO_ROOT = Path(__file__).resolve().parents[2]
PRIMARY_ALERT_PRIORITY = {
    "throughput_tonnes": 0,
    "head_grade_pct": 0,
    "recovery_pct": 0,
    "copper_production_tonnes": 0,
    "unit_cost_usd_per_tonne": 0,
    "operating_cost_usd": 0,
    "revenue_proxy_usd": 1,
    "ebitda_proxy_usd": 1,
    "operating_cash_flow_proxy_usd": 2,
    "free_cash_flow_proxy_usd": 2,
    "sustaining_capex_usd": 2,
    "working_capital_change_usd": 2,
    "copper_price_usd_per_lb": 1,
    "net_realized_price_usd_per_lb": 1,
}


@dataclass(frozen=True)
class MonthlyMetricSpec:
    """Metric metadata for the long-form actual-vs-plan fact table."""

    key: str
    display_name: str
    metric_group: str
    unit: str
    dashboard_page: str
    alert_direction: str
    warning_threshold_pct: float
    critical_threshold_pct: float
    display_order: int

    @property
    def plan_column(self) -> str:
        return f"{self.key}_plan"

    @property
    def actual_column(self) -> str:
        return f"{self.key}_actual"

    @property
    def variance_column(self) -> str:
        return f"{self.key}_variance"

    @property
    def variance_pct_column(self) -> str:
        return f"{self.key}_variance_pct"


MONTHLY_METRIC_SPECS = (
    MonthlyMetricSpec(
        key="throughput_tonnes",
        display_name="Throughput",
        metric_group="Operations",
        unit="tonnes",
        dashboard_page="Monthly Actual vs Plan",
        alert_direction="lower_is_bad",
        warning_threshold_pct=0.03,
        critical_threshold_pct=0.06,
        display_order=1,
    ),
    MonthlyMetricSpec(
        key="head_grade_pct",
        display_name="Head Grade",
        metric_group="Process Performance",
        unit="percent",
        dashboard_page="Process Performance",
        alert_direction="lower_is_bad",
        warning_threshold_pct=0.02,
        critical_threshold_pct=0.04,
        display_order=2,
    ),
    MonthlyMetricSpec(
        key="recovery_pct",
        display_name="Recovery",
        metric_group="Process Performance",
        unit="percent",
        dashboard_page="Process Performance",
        alert_direction="lower_is_bad",
        warning_threshold_pct=0.015,
        critical_threshold_pct=0.03,
        display_order=3,
    ),
    MonthlyMetricSpec(
        key="copper_production_tonnes",
        display_name="Copper Production",
        metric_group="Production",
        unit="tonnes",
        dashboard_page="Monthly Actual vs Plan",
        alert_direction="lower_is_bad",
        warning_threshold_pct=0.03,
        critical_threshold_pct=0.05,
        display_order=4,
    ),
    MonthlyMetricSpec(
        key="copper_price_usd_per_lb",
        display_name="Copper Price",
        metric_group="Market",
        unit="USD/lb",
        dashboard_page="Executive Overview",
        alert_direction="lower_is_bad",
        warning_threshold_pct=0.03,
        critical_threshold_pct=0.06,
        display_order=5,
    ),
    MonthlyMetricSpec(
        key="net_realized_price_usd_per_lb",
        display_name="Net Realized Price",
        metric_group="Market",
        unit="USD/lb",
        dashboard_page="Executive Overview",
        alert_direction="lower_is_bad",
        warning_threshold_pct=0.03,
        critical_threshold_pct=0.06,
        display_order=6,
    ),
    MonthlyMetricSpec(
        key="unit_cost_usd_per_tonne",
        display_name="Unit Cost",
        metric_group="Cost",
        unit="USD/t",
        dashboard_page="Cost and Margin",
        alert_direction="higher_is_bad",
        warning_threshold_pct=0.05,
        critical_threshold_pct=0.10,
        display_order=7,
    ),
    MonthlyMetricSpec(
        key="operating_cost_usd",
        display_name="Operating Cost",
        metric_group="Cost",
        unit="USD",
        dashboard_page="Cost and Margin",
        alert_direction="higher_is_bad",
        warning_threshold_pct=0.05,
        critical_threshold_pct=0.10,
        display_order=8,
    ),
    MonthlyMetricSpec(
        key="revenue_proxy_usd",
        display_name="Revenue Proxy",
        metric_group="Economics",
        unit="USD",
        dashboard_page="Executive Overview",
        alert_direction="lower_is_bad",
        warning_threshold_pct=0.03,
        critical_threshold_pct=0.08,
        display_order=9,
    ),
    MonthlyMetricSpec(
        key="ebitda_proxy_usd",
        display_name="EBITDA Proxy",
        metric_group="Economics",
        unit="USD",
        dashboard_page="Cost and Margin",
        alert_direction="lower_is_bad",
        warning_threshold_pct=0.05,
        critical_threshold_pct=0.10,
        display_order=10,
    ),
    MonthlyMetricSpec(
        key="operating_cash_flow_proxy_usd",
        display_name="Operating Cash Flow Proxy",
        metric_group="Economics",
        unit="USD",
        dashboard_page="Executive Overview",
        alert_direction="lower_is_bad",
        warning_threshold_pct=0.05,
        critical_threshold_pct=0.10,
        display_order=11,
    ),
    MonthlyMetricSpec(
        key="free_cash_flow_proxy_usd",
        display_name="Free Cash Flow Proxy",
        metric_group="Economics",
        unit="USD",
        dashboard_page="Executive Overview",
        alert_direction="lower_is_bad",
        warning_threshold_pct=0.08,
        critical_threshold_pct=0.15,
        display_order=12,
    ),
    MonthlyMetricSpec(
        key="sustaining_capex_usd",
        display_name="Sustaining Capex",
        metric_group="Investment",
        unit="USD",
        dashboard_page="Cost and Margin",
        alert_direction="higher_is_bad",
        warning_threshold_pct=0.08,
        critical_threshold_pct=0.15,
        display_order=13,
    ),
    MonthlyMetricSpec(
        key="working_capital_change_usd",
        display_name="Working Capital Change",
        metric_group="Working Capital",
        unit="USD",
        dashboard_page="Cost and Margin",
        alert_direction="higher_is_bad",
        warning_threshold_pct=0.10,
        critical_threshold_pct=0.20,
        display_order=14,
    ),
)


MONTHLY_KPI_METADATA = {
    "throughput_tonnes": {
        "business_meaning": "Processed plant tonnes for the month and the main physical volume KPI for plan control.",
        "proxy_flag": False,
        "metric_role": "Operational actual-vs-plan KPI",
        "page_usage_note": "Use on Executive Overview and Monthly Actual vs Plan.",
    },
    "head_grade_pct": {
        "business_meaning": "Average copper grade in plant feed for the month, used to explain production outcomes.",
        "proxy_flag": False,
        "metric_role": "Process driver KPI",
        "page_usage_note": "Use on Monthly Actual vs Plan and Process Performance.",
    },
    "recovery_pct": {
        "business_meaning": "Metallurgical recovery achieved during the month.",
        "proxy_flag": False,
        "metric_role": "Process driver KPI",
        "page_usage_note": "Use on Monthly Actual vs Plan and Process Performance.",
    },
    "copper_production_tonnes": {
        "business_meaning": "Recovered copper production for the month after grade and recovery effects.",
        "proxy_flag": False,
        "metric_role": "Production KPI",
        "page_usage_note": "Use on Executive Overview and Monthly Actual vs Plan.",
    },
    "copper_price_usd_per_lb": {
        "business_meaning": "Monthly copper market price assumption used in the revenue proxy logic.",
        "proxy_flag": False,
        "metric_role": "Market input KPI",
        "page_usage_note": "Use sparingly on Executive Overview or support visuals where price explains revenue movement.",
    },
    "net_realized_price_usd_per_lb": {
        "business_meaning": "Copper price net of treatment and refining charges used in the revenue proxy logic.",
        "proxy_flag": True,
        "metric_role": "Commercial proxy KPI",
        "page_usage_note": "Use as supporting context for revenue proxy interpretation.",
    },
    "unit_cost_usd_per_tonne": {
        "business_meaning": "Operating cost per processed tonne for the month.",
        "proxy_flag": False,
        "metric_role": "Cost efficiency KPI",
        "page_usage_note": "Use on Monthly Actual vs Plan and Cost and Margin.",
    },
    "operating_cost_usd": {
        "business_meaning": "Total monthly operating cost across the modeled cost buckets.",
        "proxy_flag": False,
        "metric_role": "Cost burden KPI",
        "page_usage_note": "Use on Cost and Margin.",
    },
    "revenue_proxy_usd": {
        "business_meaning": "Management-control proxy for monthly payable copper revenue. It is not accounting revenue.",
        "proxy_flag": True,
        "metric_role": "Economic proxy KPI",
        "page_usage_note": "Use on Executive Overview and Cost and Margin.",
    },
    "ebitda_proxy_usd": {
        "business_meaning": "Management-control proxy for monthly EBITDA. It is not statutory EBITDA.",
        "proxy_flag": True,
        "metric_role": "Economic proxy KPI",
        "page_usage_note": "Use on Executive Overview and Cost and Margin.",
    },
    "operating_cash_flow_proxy_usd": {
        "business_meaning": "Monthly operating cash generation proxy after working-capital movement.",
        "proxy_flag": True,
        "metric_role": "Cash proxy KPI",
        "page_usage_note": "Use on Executive Overview and Cost and Margin.",
    },
    "free_cash_flow_proxy_usd": {
        "business_meaning": "Monthly free cash flow proxy after sustaining capex and working-capital movement.",
        "proxy_flag": True,
        "metric_role": "Cash proxy KPI",
        "page_usage_note": "Use on Executive Overview and Cost and Margin.",
    },
    "sustaining_capex_usd": {
        "business_meaning": "Monthly sustaining capital burden included in the cash proxy logic.",
        "proxy_flag": False,
        "metric_role": "Investment burden KPI",
        "page_usage_note": "Use on Cost and Margin as supporting cash interpretation.",
    },
    "working_capital_change_usd": {
        "business_meaning": "Monthly working-capital build or release assumption included in the cash proxy logic.",
        "proxy_flag": False,
        "metric_role": "Working capital KPI",
        "page_usage_note": "Use on Cost and Margin as supporting cash interpretation.",
    },
}


def _build_canonical_schemas() -> dict[str, DatasetSchema]:
    base_schemas = {
        "plan_monthly": DatasetSchema(
            name="plan_monthly",
            description="Monthly planning targets used as the baseline for actual-vs-plan monitoring.",
            grain="One row per site_id and period (YYYY-MM).",
            key_columns=("site_id", "period"),
            required_columns=(
                "site_id",
                "period",
                "throughput_tonnes_plan",
                "head_grade_pct_plan",
                "recovery_pct_plan",
                "unit_cost_usd_per_tonne_plan",
                "copper_price_usd_per_lb_plan",
                "tc_rc_usd_per_lb_plan",
                "payable_percent_plan",
                "sustaining_capex_usd_plan",
                "working_capital_change_usd_plan",
            ),
            optional_columns=("plan_version", "commentary"),
            layer="canonical_source",
            dashboard_use="Plan baseline for executive overview, actual-vs-plan, and cost/margin review.",
            key_logic="Unique key = site_id + period. Period must be monthly and consistently formatted as YYYY-MM.",
            limitation_note="Sample/demo planning targets only. Not a live planning system export.",
            field_rules={
                "period": ColumnRule("Monthly reporting period.", is_period=True),
                "throughput_tonnes_plan": ColumnRule("Planned plant throughput.", unit="tonnes", numeric=True, min_value=0.0),
                "head_grade_pct_plan": ColumnRule("Planned head grade.", unit="percent", numeric=True, min_value=0.0, max_value=5.0),
                "recovery_pct_plan": ColumnRule("Planned recovery.", unit="percent", numeric=True, min_value=0.0, max_value=100.0),
                "unit_cost_usd_per_tonne_plan": ColumnRule(
                    "Planned unit operating cost.", unit="USD/t", numeric=True, min_value=0.0
                ),
                "copper_price_usd_per_lb_plan": ColumnRule(
                    "Planned copper price assumption.", unit="USD/lb", numeric=True, min_value=0.0
                ),
                "tc_rc_usd_per_lb_plan": ColumnRule(
                    "Planned treatment and refining charge assumption.", unit="USD/lb", numeric=True, min_value=0.0
                ),
                "payable_percent_plan": ColumnRule(
                    "Planned payable factor.", unit="percent", numeric=True, min_value=0.0, max_value=100.0
                ),
                "sustaining_capex_usd_plan": ColumnRule(
                    "Planned sustaining capex.", unit="USD", numeric=True, min_value=0.0
                ),
                "working_capital_change_usd_plan": ColumnRule(
                    "Planned working-capital movement.", unit="USD", numeric=True, min_value=-25000000.0, max_value=25000000.0
                ),
            },
        ),
        "actual_production_monthly": DatasetSchema(
            name="actual_production_monthly",
            description="Monthly actual plant throughput and copper production outcomes.",
            grain="One row per site_id and period (YYYY-MM).",
            key_columns=("site_id", "period"),
            required_columns=("site_id", "period", "throughput_tonnes_actual", "copper_production_tonnes_actual"),
            optional_columns=("shipment_tonnes_actual",),
            layer="canonical_source",
            dashboard_use="Monthly actual-vs-plan and executive overview pages.",
            key_logic="Unique key = site_id + period.",
            limitation_note="Sample/demo actual outcomes. Not a plant historian or telemetry feed.",
            field_rules={
                "period": ColumnRule("Monthly reporting period.", is_period=True),
                "throughput_tonnes_actual": ColumnRule("Actual processed tonnes.", unit="tonnes", numeric=True, min_value=0.0),
                "copper_production_tonnes_actual": ColumnRule(
                    "Actual copper production.", unit="tonnes", numeric=True, min_value=0.0
                ),
            },
        ),
        "plant_performance_monthly": DatasetSchema(
            name="plant_performance_monthly",
            description="Monthly process performance indicators used to explain production deviations.",
            grain="One row per site_id and period (YYYY-MM).",
            key_columns=("site_id", "period"),
            required_columns=("site_id", "period", "head_grade_pct_actual", "recovery_pct_actual"),
            optional_columns=("availability_pct_actual", "utilization_pct_actual", "downtime_hours_actual"),
            layer="canonical_source",
            dashboard_use="Process performance page and driver diagnostics.",
            key_logic="Unique key = site_id + period.",
            limitation_note="Sample/demo process indicators. Not an engineering-grade metallurgical system.",
            field_rules={
                "period": ColumnRule("Monthly reporting period.", is_period=True),
                "head_grade_pct_actual": ColumnRule("Actual head grade.", unit="percent", numeric=True, min_value=0.0, max_value=5.0),
                "recovery_pct_actual": ColumnRule(
                    "Actual metallurgical recovery.", unit="percent", numeric=True, min_value=0.0, max_value=100.0
                ),
                "availability_pct_actual": ColumnRule(
                    "Plant availability.", unit="percent", numeric=True, min_value=0.0, max_value=100.0
                ),
                "utilization_pct_actual": ColumnRule(
                    "Plant utilization.", unit="percent", numeric=True, min_value=0.0, max_value=100.0
                ),
                "downtime_hours_actual": ColumnRule(
                    "Monthly downtime hours used as management-control context rather than engineering telemetry.",
                    unit="hours",
                    numeric=True,
                    min_value=0.0,
                    max_value=744.0,
                ),
            },
        ),
        "cost_actuals_monthly": DatasetSchema(
            name="cost_actuals_monthly",
            description="Monthly operating cost actuals and cash burden proxies.",
            grain="One row per site_id and period (YYYY-MM).",
            key_columns=("site_id", "period"),
            required_columns=(
                "site_id",
                "period",
                "mining_cost_usd_actual",
                "processing_cost_usd_actual",
                "ga_cost_usd_actual",
                "sustaining_capex_usd_actual",
                "working_capital_change_usd_actual",
            ),
            optional_columns=("maintenance_cost_usd_actual", "logistics_cost_usd_actual"),
            layer="canonical_source",
            dashboard_use="Cost and margin review plus executive oversight.",
            key_logic="Unique key = site_id + period.",
            limitation_note="Sample/demo cost actuals only. Not ERP or management-accounting extracts.",
            field_rules={
                "period": ColumnRule("Monthly reporting period.", is_period=True),
                "mining_cost_usd_actual": ColumnRule("Actual mining cost.", unit="USD", numeric=True, min_value=0.0),
                "processing_cost_usd_actual": ColumnRule("Actual processing cost.", unit="USD", numeric=True, min_value=0.0),
                "ga_cost_usd_actual": ColumnRule("Actual G&A cost.", unit="USD", numeric=True, min_value=0.0),
                "maintenance_cost_usd_actual": ColumnRule("Actual maintenance cost.", unit="USD", numeric=True, min_value=0.0),
                "logistics_cost_usd_actual": ColumnRule("Actual logistics cost.", unit="USD", numeric=True, min_value=0.0),
                "sustaining_capex_usd_actual": ColumnRule(
                    "Actual sustaining capex.", unit="USD", numeric=True, min_value=0.0
                ),
                "working_capital_change_usd_actual": ColumnRule(
                    "Actual working-capital movement.", unit="USD", numeric=True, min_value=-25000000.0, max_value=25000000.0
                ),
            },
        ),
        "market_prices_monthly": DatasetSchema(
            name="market_prices_monthly",
            description="Monthly market price and commercial assumption layer used in revenue proxies.",
            grain="One row per site_id and period (YYYY-MM).",
            key_columns=("site_id", "period"),
            required_columns=(
                "site_id",
                "period",
                "copper_price_usd_per_lb_actual",
                "tc_rc_usd_per_lb_actual",
                "payable_percent_actual",
            ),
            optional_columns=("benchmark_price_name",),
            layer="canonical_source",
            dashboard_use="Executive overview and cost/margin review.",
            key_logic="Unique key = site_id + period.",
            limitation_note="Sample/demo market assumptions. Not a market data vendor feed.",
            field_rules={
                "period": ColumnRule("Monthly reporting period.", is_period=True),
                "copper_price_usd_per_lb_actual": ColumnRule(
                    "Actual or realized copper price proxy.", unit="USD/lb", numeric=True, min_value=0.0
                ),
                "tc_rc_usd_per_lb_actual": ColumnRule(
                    "Actual treatment and refining charge proxy.", unit="USD/lb", numeric=True, min_value=0.0
                ),
                "payable_percent_actual": ColumnRule(
                    "Actual payable factor.", unit="percent", numeric=True, min_value=0.0, max_value=100.0
                ),
            },
        ),
        "process_driver_monthly": DatasetSchema(
            name="process_driver_monthly",
            description="Monthly process-area driver detail used to explain downtime, feed mix, and production gap concentration.",
            grain="One row per site_id, period, and process_area.",
            key_columns=("site_id", "period", "process_area"),
            required_columns=(
                "site_id",
                "period",
                "process_area",
                "ore_source",
                "stockpile_flag",
                "ore_mix_pct",
                "throughput_tonnes_plan",
                "throughput_tonnes_actual",
                "copper_production_tonnes_plan",
                "copper_production_tonnes_actual",
                "availability_pct",
                "downtime_hours",
            ),
            optional_columns=("commentary",),
            layer="canonical_source",
            dashboard_use="Process Performance drill-through and operational driver diagnostics.",
            key_logic="Unique key = site_id + period + process_area.",
            limitation_note="Public-safe operational driver detail for BI drill-down. It is not plant telemetry or root-cause analytics.",
            field_rules={
                "period": ColumnRule("Monthly reporting period.", is_period=True),
                "ore_mix_pct": ColumnRule(
                    "Share of monthly site feed represented by the process-area operating mode.",
                    unit="percent",
                    numeric=True,
                    min_value=0.0,
                    max_value=100.0,
                ),
                "throughput_tonnes_plan": ColumnRule("Planned throughput for the process area.", unit="tonnes", numeric=True, min_value=0.0),
                "throughput_tonnes_actual": ColumnRule("Actual throughput for the process area.", unit="tonnes", numeric=True, min_value=0.0),
                "copper_production_tonnes_plan": ColumnRule(
                    "Planned copper production contribution for the process area.",
                    unit="tonnes",
                    numeric=True,
                    min_value=0.0,
                ),
                "copper_production_tonnes_actual": ColumnRule(
                    "Actual copper production contribution for the process area.",
                    unit="tonnes",
                    numeric=True,
                    min_value=0.0,
                ),
                "availability_pct": ColumnRule(
                    "Public-safe availability context for the process area.",
                    unit="percent",
                    numeric=True,
                    min_value=0.0,
                    max_value=100.0,
                ),
                "downtime_hours": ColumnRule(
                    "Downtime hours attributed to the process area during the month.",
                    unit="hours",
                    numeric=True,
                    min_value=0.0,
                    max_value=744.0,
                ),
            },
        ),
        "cost_center_monthly": DatasetSchema(
            name="cost_center_monthly",
            description="Monthly cost-center detail used to explain unit-cost and margin pressure.",
            grain="One row per site_id, period, and cost_center.",
            key_columns=("site_id", "period", "cost_center"),
            required_columns=("site_id", "period", "cost_center", "cost_usd_plan", "cost_usd_actual"),
            optional_columns=("commentary",),
            layer="canonical_source",
            dashboard_use="Cost and Margin drill-through and cost-pressure diagnostics.",
            key_logic="Unique key = site_id + period + cost_center.",
            limitation_note="Public-safe management-control cost detail. It is not ERP cost-center governance.",
            field_rules={
                "period": ColumnRule("Monthly reporting period.", is_period=True),
                "cost_usd_plan": ColumnRule("Planned cost-center cost.", unit="USD", numeric=True, min_value=0.0),
                "cost_usd_actual": ColumnRule("Actual cost-center cost.", unit="USD", numeric=True, min_value=0.0),
            },
        ),
    }

    output_field_rules: dict[str, ColumnRule] = {
        "period": ColumnRule("Monthly reporting period.", is_period=True),
        "month_start_date": ColumnRule("Month start date used for BI time intelligence."),
        "calendar_year": ColumnRule("Calendar year.", numeric=True),
        "calendar_month": ColumnRule("Calendar month number.", numeric=True, min_value=1.0, max_value=12.0),
        "calendar_quarter": ColumnRule("Calendar quarter number.", numeric=True, min_value=1.0, max_value=4.0),
        "site_name": ColumnRule("Human-readable site label derived from site_id."),
        "plan_version": ColumnRule("Plan version or planning baseline label."),
        "data_classification": ColumnRule("Explicit data classification tag for the monitoring layer."),
        "sample_data_flag": ColumnRule("Boolean flag showing the layer is sample/demo data."),
        "overall_alert_level": ColumnRule("Overall alert status for the month."),
        "critical_alert_count": ColumnRule("Count of critical KPI alerts.", numeric=True, min_value=0.0),
        "warning_alert_count": ColumnRule("Count of warning KPI alerts.", numeric=True, min_value=0.0),
        "primary_alert_metric": ColumnRule("Main KPI requiring management attention."),
        "primary_alert_message": ColumnRule("Human-readable monitoring message."),
        "downtime_hours_actual": ColumnRule(
            "Monthly downtime hours used as management-control context.",
            unit="hours",
            numeric=True,
            min_value=0.0,
            max_value=744.0,
        ),
        "stockpile_feed_pct_actual": ColumnRule(
            "Share of monthly feed linked to stockpile or reclaim blend.",
            unit="percent",
            numeric=True,
            min_value=0.0,
            max_value=100.0,
        ),
        "primary_ore_source": ColumnRule("Dominant ore source or blend in the selected month."),
        "primary_process_area": ColumnRule("Process area contributing the largest downtime or production gap signal."),
        "primary_process_area_downtime_hours": ColumnRule(
            "Downtime hours tied to the primary constrained process area.",
            unit="hours",
            numeric=True,
            min_value=0.0,
            max_value=744.0,
        ),
        "site_production_gap_tonnes": ColumnRule(
            "Positive copper production shortfall versus plan for the site.",
            unit="tonnes",
            numeric=True,
            min_value=0.0,
        ),
        "site_production_gap_share_pct": ColumnRule(
            "Share of period production shortfall attributable to the site.",
            unit="ratio",
            numeric=True,
            min_value=0.0,
            max_value=1.0,
        ),
        "site_positive_cost_variance_usd": ColumnRule(
            "Positive operating-cost variance contributing to margin pressure.",
            unit="USD",
            numeric=True,
            min_value=0.0,
        ),
        "site_cost_pressure_share_pct": ColumnRule(
            "Share of positive period operating-cost variance attributable to the site.",
            unit="ratio",
            numeric=True,
            min_value=0.0,
            max_value=1.0,
        ),
        "top_cost_center": ColumnRule("Cost center contributing the largest positive cost variance in the month."),
        "top_cost_center_variance_usd": ColumnRule(
            "Positive cost variance for the most material cost center.",
            unit="USD",
            numeric=True,
            min_value=0.0,
        ),
        "top_cost_center_margin_pressure_share_pct": ColumnRule(
            "Share of site-level positive cost variance attributable to the top cost center.",
            unit="ratio",
            numeric=True,
            min_value=0.0,
            max_value=1.0,
        ),
    }

    for spec in MONTHLY_METRIC_SPECS:
        output_field_rules[spec.plan_column] = ColumnRule(
            f"Planned {spec.display_name.lower()} for the month.", unit=spec.unit, numeric=True
        )
        output_field_rules[spec.actual_column] = ColumnRule(
            f"Actual {spec.display_name.lower()} for the month.", unit=spec.unit, numeric=True
        )
        output_field_rules[spec.variance_column] = ColumnRule(
            f"Actual minus plan for {spec.display_name.lower()}.", unit=spec.unit, numeric=True
        )
        output_field_rules[spec.variance_pct_column] = ColumnRule(
            f"Percentage variance for {spec.display_name.lower()}.", unit="ratio", numeric=True
        )

    base_schemas["kpi_monthly_summary"] = DatasetSchema(
        name="kpi_monthly_summary",
        description="Wide monthly monitoring summary with plan, actual, variance, and alert fields.",
        grain="One row per site_id and period (YYYY-MM).",
        key_columns=("site_id", "period"),
        required_columns=(
            "site_id",
            "period",
            "month_start_date",
            "calendar_year",
            "calendar_month",
            "calendar_quarter",
            "plan_version",
            "data_classification",
            "sample_data_flag",
            "overall_alert_level",
            "critical_alert_count",
            "warning_alert_count",
            "primary_alert_metric",
            "primary_alert_message",
            *(column for spec in MONTHLY_METRIC_SPECS for column in (spec.plan_column, spec.actual_column, spec.variance_column, spec.variance_pct_column)),
        ),
        optional_columns=(
            "month_label",
            "site_name",
            "availability_pct_actual",
            "utilization_pct_actual",
            "downtime_hours_actual",
            "stockpile_feed_pct_actual",
            "primary_ore_source",
            "primary_process_area",
            "primary_process_area_downtime_hours",
            "site_production_gap_tonnes",
            "site_production_gap_share_pct",
            "site_positive_cost_variance_usd",
            "site_cost_pressure_share_pct",
            "top_cost_center",
            "top_cost_center_variance_usd",
            "top_cost_center_margin_pressure_share_pct",
        ),
        layer="canonical_output",
        dashboard_use="Primary wide KPI summary for monthly executive overview and monitoring dashboards.",
        key_logic="One monthly row per site_id + period with explicit plan, actual, variance, and alert outputs.",
        limitation_note="Built from sample/demo source tables. Suitable for portfolio BI, not for live mine control.",
        field_rules=output_field_rules,
    )

    base_schemas["dim_site"] = DatasetSchema(
        name="dim_site",
        description="Shared site dimension used to filter the monthly monitoring marts coherently.",
        grain="One row per site_id.",
        key_columns=("site_id",),
        required_columns=("site_id", "site_name", "site_sort_order"),
        optional_columns=(),
        layer="semantic_dimension",
        dashboard_use="Shared site slicer for the monthly Power BI model.",
        key_logic="Unique key = site_id.",
        limitation_note="Built from sample/demo site labels derived from the monthly monitoring layer.",
        field_rules={
            "site_id": ColumnRule("Stable site identifier used across the monthly model."),
            "site_name": ColumnRule("Business-readable site label."),
            "site_sort_order": ColumnRule("Recommended sort order for multi-site visuals.", numeric=True, min_value=1.0),
        },
    )
    base_schemas["dim_month"] = DatasetSchema(
        name="dim_month",
        description="Shared month dimension used to filter the monthly monitoring marts coherently.",
        grain="One row per monthly reporting period.",
        key_columns=("period",),
        required_columns=(
            "period",
            "month_start_date",
            "calendar_year",
            "calendar_month",
            "calendar_quarter",
            "month_label",
            "quarter_label",
            "month_sort_order",
        ),
        optional_columns=(),
        layer="semantic_dimension",
        dashboard_use="Shared month slicer and sort layer for the monthly Power BI model.",
        key_logic="Unique key = period (YYYY-MM).",
        limitation_note="Built from the monthly monitoring layer and intended for business-facing calendar filtering rather than accounting calendars.",
        field_rules={
            "period": ColumnRule("Monthly reporting period.", is_period=True),
            "month_start_date": ColumnRule("Month start date used for sorting and labeling."),
            "calendar_year": ColumnRule("Calendar year for the reporting month.", numeric=True),
            "calendar_month": ColumnRule(
                "Calendar month number for the reporting month.", numeric=True, min_value=1.0, max_value=12.0
            ),
            "calendar_quarter": ColumnRule(
                "Calendar quarter number for the reporting month.", numeric=True, min_value=1.0, max_value=4.0
            ),
            "month_label": ColumnRule("Business-readable month label for slicers and axes."),
            "quarter_label": ColumnRule("Business-readable quarter label for grouped visuals."),
            "month_sort_order": ColumnRule(
                "Numeric YYYYMM sort key for month ordering in BI visuals.", numeric=True, min_value=190001.0
            ),
        },
    )
    base_schemas["dim_process_area"] = DatasetSchema(
        name="dim_process_area",
        description="Shared process-area dimension for process-driver drill visuals.",
        grain="One row per process_area.",
        key_columns=("process_area",),
        required_columns=("process_area", "process_area_sort_order"),
        optional_columns=(),
        layer="semantic_dimension",
        dashboard_use="Optional shared process-area slicer for process-driver visuals.",
        key_logic="Unique key = process_area.",
        limitation_note="Built from public-safe process-driver labels rather than plant control-system hierarchies.",
        field_rules={
            "process_area": ColumnRule("Business-readable process-area label."),
            "process_area_sort_order": ColumnRule(
                "Recommended sort order for process-area visuals.", numeric=True, min_value=1.0
            ),
        },
    )
    base_schemas["dim_cost_center"] = DatasetSchema(
        name="dim_cost_center",
        description="Shared cost-center dimension for cost-pressure drill visuals.",
        grain="One row per cost_center.",
        key_columns=("cost_center",),
        required_columns=("cost_center", "cost_center_sort_order"),
        optional_columns=(),
        layer="semantic_dimension",
        dashboard_use="Optional shared cost-center slicer for cost and margin drill visuals.",
        key_logic="Unique key = cost_center.",
        limitation_note="Built from public-safe management-control cost labels rather than ERP governance structures.",
        field_rules={
            "cost_center": ColumnRule("Business-readable cost-center label."),
            "cost_center_sort_order": ColumnRule(
                "Recommended sort order for cost-center visuals.", numeric=True, min_value=1.0
            ),
        },
    )

    return base_schemas


MONTHLY_CANONICAL_SCHEMAS = _build_canonical_schemas()
MONTHLY_SUMMARY_SOURCE_DATASETS = (
    "plan_monthly",
    "actual_production_monthly",
    "plant_performance_monthly",
    "cost_actuals_monthly",
    "market_prices_monthly",
)
MONTHLY_DETAIL_SOURCE_DATASETS = ("process_driver_monthly", "cost_center_monthly")
MONTHLY_SOURCE_DATASETS = MONTHLY_SUMMARY_SOURCE_DATASETS + MONTHLY_DETAIL_SOURCE_DATASETS


def _sample_data_dir() -> Path:
    return Path("data") / "sample_data" / "monthly_monitoring"


def _default_mapping_config() -> Path:
    return Path("config") / "mappings" / "public_demo_identity_mapping.yaml"


def _public_safe_path(path: str | Path | None) -> str | None:
    if path is None:
        return None
    candidate = Path(path)
    if not candidate.is_absolute():
        return candidate.as_posix()
    try:
        return candidate.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return candidate.name


def _site_display_name(site_id: str) -> str:
    return str(site_id).replace("_", " ").title()


def load_monthly_monitoring_inputs(data_dir: str | Path = _sample_data_dir()) -> dict[str, pd.DataFrame]:
    """Load canonical monthly monitoring source datasets from CSV files."""

    data_dir = Path(data_dir)
    frames: dict[str, pd.DataFrame] = {}
    for dataset_name in MONTHLY_SOURCE_DATASETS:
        frames[dataset_name] = pd.read_csv(data_dir / f"{dataset_name}.csv")
    return frames


def _identity_source_mapping_audit(
    dataset_frames: dict[str, pd.DataFrame],
    data_dir: str | Path,
) -> pd.DataFrame:
    """Build a simple audit table when inputs are already canonical."""

    data_dir = Path(data_dir)
    rows = []
    for dataset_name, frame in dataset_frames.items():
        rows.append(
            {
                "dataset_name": dataset_name,
                "source_dataset_label": dataset_name,
                "source_file": f"{dataset_name}.csv",
                "source_rows": int(len(frame)),
                "mapped_rows": int(len(frame)),
                "source_column_count": int(len(frame.columns)),
                "mapped_column_count": int(len(frame.columns)),
                "mapped_columns": "; ".join(frame.columns),
                "mapped_source_columns": "; ".join(frame.columns),
                "unmapped_source_columns": "",
                "default_columns_applied": "",
                "missing_required_columns_after_mapping": "",
                "normalize_period_flag": "period" in frame.columns,
                "status": "ready_for_validation",
                "mapping_note": f"Canonical input loaded directly from {data_dir.as_posix()}.",
            }
        )
    return pd.DataFrame(rows).sort_values("dataset_name").reset_index(drop=True)


def load_mapped_monthly_monitoring_inputs(
    data_dir: str | Path = _sample_data_dir(),
    mapping_config_path: str | Path = _default_mapping_config(),
) -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    """Load and map monthly monitoring source datasets using a YAML mapping config."""

    source_schemas = {dataset_name: MONTHLY_CANONICAL_SCHEMAS[dataset_name] for dataset_name in MONTHLY_SOURCE_DATASETS}
    return map_source_directory(
        data_dir=data_dir,
        mapping_config_path=mapping_config_path,
        target_schemas=source_schemas,
    )


def validate_monthly_inputs(dataset_frames: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Validate each canonical monthly monitoring dataset."""

    validated: dict[str, pd.DataFrame] = {}
    for dataset_name in MONTHLY_SOURCE_DATASETS:
        schema = MONTHLY_CANONICAL_SCHEMAS[dataset_name]
        validated_frame = validate_dataframe(dataset_frames[dataset_name], schema)
        validated[dataset_name] = validated_frame.sort_values(list(schema.key_columns)).reset_index(drop=True)
    return validated


def build_monthly_dataset_catalog() -> pd.DataFrame:
    """Return a catalog describing the canonical monthly datasets."""

    rows = []
    for schema in MONTHLY_CANONICAL_SCHEMAS.values():
        rows.append(
            {
                "dataset_name": schema.name,
                "layer": schema.layer,
                "description": schema.description,
                "grain": schema.grain,
                "key_columns": ", ".join(schema.key_columns),
                "required_columns": ", ".join(schema.required_columns),
                "optional_columns": ", ".join(schema.optional_columns),
                "dashboard_use": schema.dashboard_use,
                "key_logic": schema.key_logic,
                "limitation_note": schema.limitation_note,
            }
        )
    return pd.DataFrame(rows)


def build_monthly_field_catalog() -> pd.DataFrame:
    """Return a field-level catalog for the canonical monthly datasets."""

    rows = []
    for schema in MONTHLY_CANONICAL_SCHEMAS.values():
        for field_name, rule in schema.field_rules.items():
            rows.append(
                {
                    "dataset_name": schema.name,
                    "field_name": field_name,
                    "description": rule.description,
                    "unit": rule.unit,
                    "required_flag": field_name in schema.required_columns,
                    "numeric_flag": rule.numeric,
                    "period_flag": rule.is_period,
                    "min_value": rule.min_value,
                    "max_value": rule.max_value,
                }
            )
    return pd.DataFrame(rows)


def build_monthly_metric_dimension() -> pd.DataFrame:
    """Return a metric dimension for the monthly actual-vs-plan fact table."""

    return pd.DataFrame(
        [
            {
                "metric": spec.key,
                "display_name": spec.display_name,
                "metric_group": spec.metric_group,
                "metric_role": MONTHLY_KPI_METADATA[spec.key]["metric_role"],
                "business_meaning": MONTHLY_KPI_METADATA[spec.key]["business_meaning"],
                "unit": spec.unit,
                "proxy_flag": MONTHLY_KPI_METADATA[spec.key]["proxy_flag"],
                "dashboard_page": spec.dashboard_page,
                "page_usage_note": MONTHLY_KPI_METADATA[spec.key]["page_usage_note"],
                "alert_direction": spec.alert_direction,
                "warning_threshold_pct": spec.warning_threshold_pct,
                "critical_threshold_pct": spec.critical_threshold_pct,
                "plan_column": spec.plan_column,
                "actual_column": spec.actual_column,
                "variance_column": spec.variance_column,
                "variance_pct_column": spec.variance_pct_column,
                "display_order": spec.display_order,
            }
            for spec in MONTHLY_METRIC_SPECS
        ]
    )


def build_site_dimension(kpi_monthly_summary: pd.DataFrame) -> pd.DataFrame:
    """Return a shared site dimension for the monthly BI model."""

    dim_site = (
        kpi_monthly_summary.loc[:, ["site_id", "site_name"]]
        .drop_duplicates()
        .sort_values(["site_name", "site_id"])
        .reset_index(drop=True)
    )
    dim_site["site_sort_order"] = range(1, len(dim_site) + 1)
    return dim_site.loc[:, ["site_id", "site_name", "site_sort_order"]]


def build_month_dimension(kpi_monthly_summary: pd.DataFrame) -> pd.DataFrame:
    """Return a shared month dimension for the monthly BI model."""

    dim_month = (
        kpi_monthly_summary.loc[
            :,
            [
                "period",
                "month_start_date",
                "calendar_year",
                "calendar_month",
                "calendar_quarter",
                "month_label",
            ],
        ]
        .drop_duplicates()
        .sort_values(["calendar_year", "calendar_month"])
        .reset_index(drop=True)
    )
    dim_month["quarter_label"] = "Q" + dim_month["calendar_quarter"].astype(int).astype(str) + " " + dim_month[
        "calendar_year"
    ].astype(int).astype(str)
    dim_month["month_sort_order"] = (dim_month["calendar_year"].astype(int) * 100) + dim_month["calendar_month"].astype(int)
    return dim_month.loc[
        :,
        [
            "period",
            "month_start_date",
            "calendar_year",
            "calendar_month",
            "calendar_quarter",
            "month_label",
            "quarter_label",
            "month_sort_order",
        ],
    ]


def build_process_area_dimension(mart_process_driver_summary: pd.DataFrame) -> pd.DataFrame:
    """Return a shared process-area dimension for process-driver drill visuals."""

    dim_process_area = (
        mart_process_driver_summary.loc[:, ["process_area"]]
        .drop_duplicates()
        .sort_values(["process_area"])
        .reset_index(drop=True)
    )
    dim_process_area["process_area_sort_order"] = range(1, len(dim_process_area) + 1)
    return dim_process_area.loc[:, ["process_area", "process_area_sort_order"]]


def build_cost_center_dimension(mart_cost_center_summary: pd.DataFrame) -> pd.DataFrame:
    """Return a shared cost-center dimension for cost-pressure drill visuals."""

    dim_cost_center = (
        mart_cost_center_summary.loc[:, ["cost_center"]]
        .drop_duplicates()
        .sort_values(["cost_center"])
        .reset_index(drop=True)
    )
    dim_cost_center["cost_center_sort_order"] = range(1, len(dim_cost_center) + 1)
    return dim_cost_center.loc[:, ["cost_center", "cost_center_sort_order"]]


def build_monthly_kpi_dictionary() -> pd.DataFrame:
    """Return a KPI dictionary for the monitored monthly metrics."""

    rows: list[dict[str, object]] = []
    for spec in MONTHLY_METRIC_SPECS:
        metadata = MONTHLY_KPI_METADATA[spec.key]
        rows.append(
            {
                "metric": spec.key,
                "display_name": spec.display_name,
                "metric_group": spec.metric_group,
                "metric_role": metadata["metric_role"],
                "business_meaning": metadata["business_meaning"],
                "unit": spec.unit,
                "proxy_flag": metadata["proxy_flag"],
                "plan_actual_variance_support": "plan, actual, variance, variance_pct",
                "plan_field": spec.plan_column,
                "actual_field": spec.actual_column,
                "variance_field": spec.variance_column,
                "variance_pct_field": spec.variance_pct_column,
                "wide_source_table": "kpi_monthly_summary",
                "long_source_table": "fact_monthly_actual_vs_plan",
                "primary_dashboard_page": spec.dashboard_page,
                "page_usage_note": metadata["page_usage_note"],
                "alert_direction": spec.alert_direction,
                "warning_threshold_pct": spec.warning_threshold_pct,
                "critical_threshold_pct": spec.critical_threshold_pct,
                "display_order": spec.display_order,
            }
        )
    return pd.DataFrame(rows)


def _safe_pct_variance(actual: pd.Series, plan: pd.Series) -> pd.Series:
    denominator = plan.where(plan.abs() > 1e-9)
    return (actual - plan) / denominator


def _build_month_key_fields(summary: pd.DataFrame) -> pd.DataFrame:
    month_index = pd.PeriodIndex(summary["period"], freq="M").to_timestamp()
    summary["month_start_date"] = month_index.strftime("%Y-%m-%d")
    summary["calendar_year"] = month_index.year
    summary["calendar_month"] = month_index.month
    summary["calendar_quarter"] = month_index.quarter
    summary["month_label"] = month_index.strftime("%b %Y")
    return summary


def _merge_monitoring_inputs(validated_inputs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    merged = validated_inputs["plan_monthly"].copy()

    for dataset_name in MONTHLY_SUMMARY_SOURCE_DATASETS[1:]:
        incoming = validated_inputs[dataset_name]
        new_columns = [column for column in incoming.columns if column not in {"site_id", "period"}]
        merged = merged.merge(incoming, on=["site_id", "period"], how="left", validate="one_to_one")
        missing_matches = merged[new_columns].isna().all(axis=1)
        if bool(missing_matches.any()):
            sample_keys = merged.loc[missing_matches, ["site_id", "period"]].head(5).to_dict("records")
            raise ValueError(
                f"Dataset '{dataset_name}' is missing rows for plan keys. Example missing monthly keys: {sample_keys}"
            )

    return merged.sort_values(["site_id", "period"]).reset_index(drop=True)


def _add_derived_monitoring_metrics(summary: pd.DataFrame) -> pd.DataFrame:
    """Add unit-consistent monthly planning/control proxy metrics.

    Revenue stays anchored to recovered copper tonnes, converted to pounds,
    then multiplied by net realized USD/lb and the payable fraction.
    EBITDA, operating cash flow, and free cash flow remain simple management-
    control proxies rather than audited accounting measures.
    """

    operating_cost_components_actual = [
        column
        for column in (
            "mining_cost_usd_actual",
            "processing_cost_usd_actual",
            "ga_cost_usd_actual",
            "maintenance_cost_usd_actual",
            "logistics_cost_usd_actual",
        )
        if column in summary.columns
    ]

    summary["operating_cost_usd_plan"] = summary["unit_cost_usd_per_tonne_plan"] * summary["throughput_tonnes_plan"]
    summary["operating_cost_usd_actual"] = summary[operating_cost_components_actual].sum(axis=1)
    summary["unit_cost_usd_per_tonne_actual"] = (
        summary["operating_cost_usd_actual"] / summary["throughput_tonnes_actual"].replace(0.0, np.nan)
    )

    summary["copper_production_tonnes_plan"] = (
        summary["throughput_tonnes_plan"]
        * (summary["head_grade_pct_plan"] / 100.0)
        * (summary["recovery_pct_plan"] / 100.0)
    )
    payable_fraction_plan = summary["payable_percent_plan"] / 100.0
    payable_fraction_actual = summary["payable_percent_actual"] / 100.0
    summary["net_realized_price_usd_per_lb_plan"] = summary["copper_price_usd_per_lb_plan"] - summary["tc_rc_usd_per_lb_plan"]
    summary["net_realized_price_usd_per_lb_actual"] = (
        summary["copper_price_usd_per_lb_actual"] - summary["tc_rc_usd_per_lb_actual"]
    )

    summary["revenue_proxy_usd_plan"] = (
        summary["copper_production_tonnes_plan"]
        * POUNDS_PER_METRIC_TONNE
        * payable_fraction_plan
        * summary["net_realized_price_usd_per_lb_plan"]
    )
    summary["revenue_proxy_usd_actual"] = (
        summary["copper_production_tonnes_actual"]
        * POUNDS_PER_METRIC_TONNE
        * payable_fraction_actual
        * summary["net_realized_price_usd_per_lb_actual"]
    )
    summary["ebitda_proxy_usd_plan"] = summary["revenue_proxy_usd_plan"] - summary["operating_cost_usd_plan"]
    summary["ebitda_proxy_usd_actual"] = summary["revenue_proxy_usd_actual"] - summary["operating_cost_usd_actual"]
    summary["operating_cash_flow_proxy_usd_plan"] = summary["ebitda_proxy_usd_plan"] - summary["working_capital_change_usd_plan"]
    summary["operating_cash_flow_proxy_usd_actual"] = (
        summary["ebitda_proxy_usd_actual"] - summary["working_capital_change_usd_actual"]
    )
    summary["free_cash_flow_proxy_usd_plan"] = (
        summary["operating_cash_flow_proxy_usd_plan"] - summary["sustaining_capex_usd_plan"]
    )
    summary["free_cash_flow_proxy_usd_actual"] = (
        summary["operating_cash_flow_proxy_usd_actual"] - summary["sustaining_capex_usd_actual"]
    )
    return summary


def _validate_financial_proxy_scales(summary: pd.DataFrame) -> pd.DataFrame:
    """Fail fast if unit regressions make the monthly financial proxies implausible."""

    violations: list[str] = []
    price_columns = (
        "net_realized_price_usd_per_lb_plan",
        "net_realized_price_usd_per_lb_actual",
    )
    for column in price_columns:
        invalid_price_mask = summary[column].notna() & (
            (summary[column] < MIN_NET_REALIZED_PRICE_USD_PER_LB)
            | (summary[column] > MAX_NET_REALIZED_PRICE_USD_PER_LB)
        )
        if invalid_price_mask.any():
            invalid_periods = ", ".join(summary.loc[invalid_price_mask, "period"].astype(str).head(3))
            violations.append(
                f"{column} fell outside the plausible copper price range "
                f"[{MIN_NET_REALIZED_PRICE_USD_PER_LB}, {MAX_NET_REALIZED_PRICE_USD_PER_LB}] USD/lb "
                f"for periods such as {invalid_periods}."
            )

    for suffix in ("plan", "actual"):
        copper_column = f"copper_production_tonnes_{suffix}"
        revenue_column = f"revenue_proxy_usd_{suffix}"
        positive_copper_mask = summary[copper_column] > 0.0
        if not positive_copper_mask.any():
            continue
        implied_revenue_per_tonne = summary.loc[positive_copper_mask, revenue_column] / summary.loc[
            positive_copper_mask, copper_column
        ]
        invalid_scale_mask = (
            (implied_revenue_per_tonne < MIN_REVENUE_PROXY_USD_PER_COPPER_TONNE)
            | (implied_revenue_per_tonne > MAX_REVENUE_PROXY_USD_PER_COPPER_TONNE)
            | ~np.isfinite(implied_revenue_per_tonne)
        )
        if invalid_scale_mask.any():
            flagged_rows = summary.loc[positive_copper_mask].loc[invalid_scale_mask, ["site_id", "period"]].head(3)
            examples = ", ".join(
                f"{row.site_id}/{row.period}"
                for row in flagged_rows.itertuples(index=False)
            )
            violations.append(
                f"{revenue_column} implies {suffix} copper values outside the plausible range "
                f"[{MIN_REVENUE_PROXY_USD_PER_COPPER_TONNE}, {MAX_REVENUE_PROXY_USD_PER_COPPER_TONNE}] USD per copper tonne "
                f"for rows such as {examples}."
            )

    if violations:
        raise ValueError("Monthly financial proxy unit guardrails failed: " + " ".join(violations))
    return summary


def _add_variance_columns(summary: pd.DataFrame) -> pd.DataFrame:
    for spec in MONTHLY_METRIC_SPECS:
        summary[spec.variance_column] = summary[spec.actual_column] - summary[spec.plan_column]
        summary[spec.variance_pct_column] = _safe_pct_variance(summary[spec.actual_column], summary[spec.plan_column])
    return summary


def _badness_score(variance_pct: float | None, alert_direction: str) -> float:
    if variance_pct is None or pd.isna(variance_pct):
        return 0.0
    if alert_direction == "lower_is_bad":
        return max(float(-variance_pct), 0.0)
    return max(float(variance_pct), 0.0)


def _alert_level(badness_score: float, warning_threshold: float, critical_threshold: float) -> str:
    if badness_score >= critical_threshold:
        return "critical"
    if badness_score >= warning_threshold:
        return "warning"
    return "on_track"


def _alert_message(spec: MonthlyMetricSpec, variance_pct: float | None, alert_level: str) -> str:
    if variance_pct is None or pd.isna(variance_pct):
        return f"{spec.display_name} has no valid plan baseline for variance interpretation."
    if alert_level == "on_track":
        return f"{spec.display_name} remains within the monthly tolerance band."
    direction = "below plan" if spec.alert_direction == "lower_is_bad" else "above plan"
    return f"{spec.display_name} is {abs(float(variance_pct)) * 100:.1f}% {direction}."


def build_kpi_monthly_summary(dataset_frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Build the wide monthly KPI summary from canonical source datasets."""

    validated_inputs = validate_monthly_inputs(dataset_frames)
    summary = _merge_monitoring_inputs(validated_inputs)
    summary = _build_month_key_fields(summary)
    summary = _add_derived_monitoring_metrics(summary)
    summary = _validate_financial_proxy_scales(summary)
    summary = _add_variance_columns(summary)
    summary["site_name"] = summary["site_id"].map(_site_display_name)
    if "plan_version" not in summary.columns:
        summary["plan_version"] = "sample_demo_budget"
    summary["plan_version"] = summary["plan_version"].fillna("sample_demo_budget")
    summary["data_classification"] = SAMPLE_DATA_CLASSIFICATION
    summary["sample_data_flag"] = True
    return summary


def build_monthly_actual_vs_plan_fact(kpi_monthly_summary: pd.DataFrame) -> pd.DataFrame:
    """Build a long-form actual-vs-plan fact table for BI dashboards."""

    rows: list[dict[str, object]] = []
    for row in kpi_monthly_summary.itertuples(index=False):
        for spec in MONTHLY_METRIC_SPECS:
            variance_pct = getattr(row, spec.variance_pct_column)
            badness_score = _badness_score(variance_pct, spec.alert_direction)
            alert_level = _alert_level(badness_score, spec.warning_threshold_pct, spec.critical_threshold_pct)
            rows.append(
                {
                    "site_id": row.site_id,
                    "period": row.period,
                    "month_start_date": row.month_start_date,
                    "calendar_year": row.calendar_year,
                    "calendar_month": row.calendar_month,
                    "calendar_quarter": row.calendar_quarter,
                    "month_label": row.month_label,
                    "metric": spec.key,
                    "metric_display_name": spec.display_name,
                    "metric_group": spec.metric_group,
                    "unit": spec.unit,
                    "dashboard_page": spec.dashboard_page,
                    "display_order": spec.display_order,
                    "plan_value": getattr(row, spec.plan_column),
                    "actual_value": getattr(row, spec.actual_column),
                    "variance_value": getattr(row, spec.variance_column),
                    "variance_pct": variance_pct,
                    "alert_direction": spec.alert_direction,
                    "alert_level": alert_level,
                    "alert_flag": alert_level != "on_track",
                    "badness_score": badness_score,
                    "alert_message": _alert_message(spec, variance_pct, alert_level),
                    "plan_version": row.plan_version,
                    "data_classification": row.data_classification,
                    "sample_data_flag": row.sample_data_flag,
                }
            )

    fact = pd.DataFrame(rows).sort_values(["site_id", "period", "display_order"]).reset_index(drop=True)
    return fact


def _merge_alert_rollup(kpi_monthly_summary: pd.DataFrame, fact_monthly_actual_vs_plan: pd.DataFrame) -> pd.DataFrame:
    top_alert = (
        fact_monthly_actual_vs_plan.assign(
            has_material_alert=lambda frame: frame["alert_level"] != "on_track",
            primary_alert_priority=lambda frame: frame["metric"].map(PRIMARY_ALERT_PRIORITY).fillna(9),
        ).sort_values(
            ["site_id", "period", "has_material_alert", "primary_alert_priority", "badness_score", "display_order"],
            ascending=[True, True, False, True, False, True],
        )
        .drop_duplicates(["site_id", "period"])
        .loc[:, ["site_id", "period", "metric_display_name", "alert_message", "badness_score"]]
        .rename(
            columns={
                "metric_display_name": "primary_alert_metric",
                "alert_message": "primary_alert_message",
            }
        )
    )

    alert_rollup = (
        fact_monthly_actual_vs_plan.groupby(["site_id", "period"], as_index=False)
        .agg(
            critical_alert_count=("alert_level", lambda values: int((values == "critical").sum())),
            warning_alert_count=("alert_level", lambda values: int((values == "warning").sum())),
        )
        .merge(top_alert, on=["site_id", "period"], how="left")
    )
    alert_rollup["primary_alert_metric"] = np.where(
        alert_rollup["badness_score"] > 0.0,
        alert_rollup["primary_alert_metric"],
        "No material deviation",
    )
    alert_rollup["primary_alert_message"] = np.where(
        alert_rollup["badness_score"] > 0.0,
        alert_rollup["primary_alert_message"],
        "All monitored KPIs remain within tolerance.",
    )
    alert_rollup["overall_alert_level"] = np.select(
        [alert_rollup["critical_alert_count"] > 0, alert_rollup["warning_alert_count"] > 0],
        ["critical", "warning"],
        default="on_track",
    )

    summary_subset = alert_rollup.loc[
        :,
        [
            "site_id",
            "period",
            "critical_alert_count",
            "warning_alert_count",
            "primary_alert_metric",
            "primary_alert_message",
            "overall_alert_level",
        ],
    ]
    return kpi_monthly_summary.merge(summary_subset, on=["site_id", "period"], how="left")


def build_process_driver_summary_mart(
    process_driver_monthly: pd.DataFrame,
    kpi_monthly_summary: pd.DataFrame,
) -> pd.DataFrame:
    """Build a process-area operational mart for process diagnostics."""

    month_context = kpi_monthly_summary.loc[
        :,
        [
            "site_id",
            "period",
            "site_name",
            "month_start_date",
            "calendar_year",
            "calendar_month",
            "calendar_quarter",
            "month_label",
            "overall_alert_level",
            "primary_alert_metric",
            "primary_alert_message",
            "data_classification",
            "sample_data_flag",
        ],
    ]
    mart = process_driver_monthly.merge(month_context, on=["site_id", "period"], how="left", validate="many_to_one")
    mart["throughput_tonnes_variance"] = mart["throughput_tonnes_actual"] - mart["throughput_tonnes_plan"]
    mart["throughput_tonnes_variance_pct"] = _safe_pct_variance(mart["throughput_tonnes_actual"], mart["throughput_tonnes_plan"])
    mart["copper_production_tonnes_variance"] = (
        mart["copper_production_tonnes_actual"] - mart["copper_production_tonnes_plan"]
    )
    mart["copper_production_tonnes_variance_pct"] = _safe_pct_variance(
        mart["copper_production_tonnes_actual"],
        mart["copper_production_tonnes_plan"],
    )
    mart["negative_production_gap_tonnes"] = (-mart["copper_production_tonnes_variance"]).clip(lower=0.0)
    mart["site_total_downtime_hours"] = mart.groupby(["site_id", "period"])["downtime_hours"].transform("sum")
    mart["downtime_share_pct"] = np.where(
        mart["site_total_downtime_hours"] > 0.0,
        mart["downtime_hours"] / mart["site_total_downtime_hours"],
        0.0,
    )
    mart["site_negative_production_gap_tonnes"] = mart.groupby(["site_id", "period"])["negative_production_gap_tonnes"].transform("sum")
    mart["process_area_production_gap_share_pct"] = np.where(
        mart["site_negative_production_gap_tonnes"] > 0.0,
        mart["negative_production_gap_tonnes"] / mart["site_negative_production_gap_tonnes"],
        0.0,
    )

    columns = [
        "site_id",
        "site_name",
        "period",
        "month_start_date",
        "calendar_year",
        "calendar_month",
        "calendar_quarter",
        "month_label",
        "process_area",
        "ore_source",
        "stockpile_flag",
        "ore_mix_pct",
        "throughput_tonnes_plan",
        "throughput_tonnes_actual",
        "throughput_tonnes_variance",
        "throughput_tonnes_variance_pct",
        "copper_production_tonnes_plan",
        "copper_production_tonnes_actual",
        "copper_production_tonnes_variance",
        "copper_production_tonnes_variance_pct",
        "negative_production_gap_tonnes",
        "process_area_production_gap_share_pct",
        "availability_pct",
        "downtime_hours",
        "site_total_downtime_hours",
        "downtime_share_pct",
        "overall_alert_level",
        "primary_alert_metric",
        "primary_alert_message",
        "data_classification",
        "sample_data_flag",
    ]
    return mart.loc[:, columns].sort_values(["site_id", "period", "process_area"]).reset_index(drop=True)


def build_cost_center_summary_mart(
    cost_center_monthly: pd.DataFrame,
    kpi_monthly_summary: pd.DataFrame,
) -> pd.DataFrame:
    """Build a cost-center mart for unit-cost and margin-pressure diagnostics."""

    month_context = kpi_monthly_summary.loc[
        :,
        [
            "site_id",
            "period",
            "site_name",
            "month_start_date",
            "calendar_year",
            "calendar_month",
            "calendar_quarter",
            "month_label",
            "throughput_tonnes_plan",
            "throughput_tonnes_actual",
            "overall_alert_level",
            "primary_alert_metric",
            "primary_alert_message",
            "data_classification",
            "sample_data_flag",
        ],
    ]
    mart = cost_center_monthly.merge(month_context, on=["site_id", "period"], how="left", validate="many_to_one")
    mart["cost_variance_usd"] = mart["cost_usd_actual"] - mart["cost_usd_plan"]
    mart["cost_variance_pct"] = _safe_pct_variance(mart["cost_usd_actual"], mart["cost_usd_plan"])
    mart["planned_cost_per_tonne"] = mart["cost_usd_plan"] / mart["throughput_tonnes_plan"].replace(0.0, np.nan)
    mart["actual_cost_per_tonne"] = mart["cost_usd_actual"] / mart["throughput_tonnes_actual"].replace(0.0, np.nan)
    mart["positive_cost_variance_usd"] = mart["cost_variance_usd"].clip(lower=0.0)
    mart["site_positive_cost_variance_usd"] = mart.groupby(["site_id", "period"])["positive_cost_variance_usd"].transform("sum")
    mart["cost_center_margin_pressure_share_pct"] = np.where(
        mart["site_positive_cost_variance_usd"] > 0.0,
        mart["positive_cost_variance_usd"] / mart["site_positive_cost_variance_usd"],
        0.0,
    )

    columns = [
        "site_id",
        "site_name",
        "period",
        "month_start_date",
        "calendar_year",
        "calendar_month",
        "calendar_quarter",
        "month_label",
        "cost_center",
        "cost_usd_plan",
        "cost_usd_actual",
        "cost_variance_usd",
        "cost_variance_pct",
        "planned_cost_per_tonne",
        "actual_cost_per_tonne",
        "positive_cost_variance_usd",
        "site_positive_cost_variance_usd",
        "cost_center_margin_pressure_share_pct",
        "overall_alert_level",
        "primary_alert_metric",
        "primary_alert_message",
        "data_classification",
        "sample_data_flag",
    ]
    return mart.loc[:, columns].sort_values(["site_id", "period", "cost_center"]).reset_index(drop=True)


def _merge_operational_context(
    kpi_monthly_summary: pd.DataFrame,
    mart_process_driver_summary: pd.DataFrame,
    mart_cost_center_summary: pd.DataFrame,
) -> pd.DataFrame:
    process_context = (
        mart_process_driver_summary.groupby(["site_id", "period"], as_index=False)
        .agg(
            process_driver_downtime_hours_actual=("downtime_hours", "sum"),
            stockpile_feed_pct_actual=(
                "ore_mix_pct",
                lambda values: float(
                    mart_process_driver_summary.loc[values.index, "ore_mix_pct"]
                    .where(mart_process_driver_summary.loc[values.index, "stockpile_flag"], 0.0)
                    .sum()
                ),
            ),
        )
    )
    top_process_area = (
        mart_process_driver_summary.sort_values(
            ["site_id", "period", "negative_production_gap_tonnes", "downtime_hours", "ore_mix_pct"],
            ascending=[True, True, False, False, False],
        )
        .drop_duplicates(["site_id", "period"])
        .loc[:, ["site_id", "period", "process_area", "ore_source", "downtime_hours"]]
        .rename(
            columns={
                "process_area": "primary_process_area",
                "ore_source": "primary_ore_source",
                "downtime_hours": "primary_process_area_downtime_hours",
            }
        )
    )

    cost_context = (
        mart_cost_center_summary.sort_values(
            ["site_id", "period", "positive_cost_variance_usd", "cost_usd_actual"],
            ascending=[True, True, False, False],
        )
        .drop_duplicates(["site_id", "period"])
        .loc[
            :,
            [
                "site_id",
                "period",
                "cost_center",
                "positive_cost_variance_usd",
                "cost_center_margin_pressure_share_pct",
                "site_positive_cost_variance_usd",
            ],
        ]
        .rename(
            columns={
                "cost_center": "top_cost_center",
                "positive_cost_variance_usd": "top_cost_center_variance_usd",
                "cost_center_margin_pressure_share_pct": "top_cost_center_margin_pressure_share_pct",
            }
        )
    )

    enriched = (
        kpi_monthly_summary.merge(process_context, on=["site_id", "period"], how="left")
        .merge(top_process_area, on=["site_id", "period"], how="left")
        .merge(cost_context, on=["site_id", "period"], how="left")
    )
    if "process_driver_downtime_hours_actual" in enriched.columns:
        enriched["downtime_hours_actual"] = enriched["downtime_hours_actual"].fillna(
            enriched["process_driver_downtime_hours_actual"]
        )
        enriched = enriched.drop(columns=["process_driver_downtime_hours_actual"])
    enriched["downtime_hours_actual"] = enriched["downtime_hours_actual"].fillna(0.0)
    enriched["stockpile_feed_pct_actual"] = enriched["stockpile_feed_pct_actual"].fillna(0.0)
    enriched["site_production_gap_tonnes"] = (-enriched["copper_production_tonnes_variance"]).clip(lower=0.0)
    period_total_shortfall = enriched.groupby("period")["site_production_gap_tonnes"].transform("sum")
    enriched["site_production_gap_share_pct"] = np.where(
        period_total_shortfall > 0.0,
        enriched["site_production_gap_tonnes"] / period_total_shortfall,
        0.0,
    )
    enriched["site_positive_cost_variance_usd"] = enriched["site_positive_cost_variance_usd"].fillna(
        enriched["operating_cost_usd_variance"].clip(lower=0.0)
    )
    period_total_cost_pressure = enriched.groupby("period")["site_positive_cost_variance_usd"].transform("sum")
    enriched["site_cost_pressure_share_pct"] = np.where(
        period_total_cost_pressure > 0.0,
        enriched["site_positive_cost_variance_usd"] / period_total_cost_pressure,
        0.0,
    )
    enriched["top_cost_center_variance_usd"] = enriched["top_cost_center_variance_usd"].fillna(0.0)
    enriched["top_cost_center_margin_pressure_share_pct"] = enriched["top_cost_center_margin_pressure_share_pct"].fillna(0.0)
    return enriched


def build_monthly_by_site_mart(kpi_monthly_summary: pd.DataFrame) -> pd.DataFrame:
    """Build a site-level mart highlighting contribution to production and cost deviation."""

    columns = [
        "site_id",
        "site_name",
        "period",
        "month_start_date",
        "calendar_year",
        "calendar_month",
        "calendar_quarter",
        "month_label",
        "throughput_tonnes_plan",
        "throughput_tonnes_actual",
        "throughput_tonnes_variance",
        "throughput_tonnes_variance_pct",
        "copper_production_tonnes_plan",
        "copper_production_tonnes_actual",
        "copper_production_tonnes_variance",
        "copper_production_tonnes_variance_pct",
        "unit_cost_usd_per_tonne_plan",
        "unit_cost_usd_per_tonne_actual",
        "unit_cost_usd_per_tonne_variance",
        "unit_cost_usd_per_tonne_variance_pct",
        "revenue_proxy_usd_actual",
        "ebitda_proxy_usd_actual",
        "availability_pct_actual",
        "utilization_pct_actual",
        "downtime_hours_actual",
        "stockpile_feed_pct_actual",
        "primary_ore_source",
        "primary_process_area",
        "site_production_gap_tonnes",
        "site_production_gap_share_pct",
        "site_positive_cost_variance_usd",
        "site_cost_pressure_share_pct",
        "top_cost_center",
        "top_cost_center_variance_usd",
        "top_cost_center_margin_pressure_share_pct",
        "overall_alert_level",
        "primary_alert_metric",
        "primary_alert_message",
        "data_classification",
        "sample_data_flag",
    ]
    available_columns = [column for column in columns if column in kpi_monthly_summary.columns]
    return kpi_monthly_summary.loc[:, available_columns].copy()


def build_monthly_process_performance_mart(kpi_monthly_summary: pd.DataFrame) -> pd.DataFrame:
    """Build a process-performance mart for BI dashboards."""

    columns = [
        "site_id",
        "site_name",
        "period",
        "month_start_date",
        "calendar_year",
        "calendar_month",
        "calendar_quarter",
        "month_label",
        "throughput_tonnes_plan",
        "throughput_tonnes_actual",
        "throughput_tonnes_variance",
        "throughput_tonnes_variance_pct",
        "head_grade_pct_plan",
        "head_grade_pct_actual",
        "head_grade_pct_variance",
        "head_grade_pct_variance_pct",
        "recovery_pct_plan",
        "recovery_pct_actual",
        "recovery_pct_variance",
        "recovery_pct_variance_pct",
        "copper_production_tonnes_plan",
        "copper_production_tonnes_actual",
        "copper_production_tonnes_variance",
        "copper_production_tonnes_variance_pct",
        "availability_pct_actual",
        "utilization_pct_actual",
        "downtime_hours_actual",
        "stockpile_feed_pct_actual",
        "primary_ore_source",
        "primary_process_area",
        "primary_process_area_downtime_hours",
        "site_production_gap_share_pct",
        "overall_alert_level",
        "primary_alert_metric",
        "primary_alert_message",
        "data_classification",
        "sample_data_flag",
    ]
    available_columns = [column for column in columns if column in kpi_monthly_summary.columns]
    return kpi_monthly_summary.loc[:, available_columns].copy()


def build_monthly_cost_margin_mart(kpi_monthly_summary: pd.DataFrame) -> pd.DataFrame:
    """Build a cost and margin mart for BI dashboards."""

    columns = [
        "site_id",
        "site_name",
        "period",
        "month_start_date",
        "calendar_year",
        "calendar_month",
        "calendar_quarter",
        "month_label",
        "copper_price_usd_per_lb_plan",
        "copper_price_usd_per_lb_actual",
        "copper_price_usd_per_lb_variance",
        "copper_price_usd_per_lb_variance_pct",
        "net_realized_price_usd_per_lb_plan",
        "net_realized_price_usd_per_lb_actual",
        "net_realized_price_usd_per_lb_variance",
        "net_realized_price_usd_per_lb_variance_pct",
        "unit_cost_usd_per_tonne_plan",
        "unit_cost_usd_per_tonne_actual",
        "unit_cost_usd_per_tonne_variance",
        "unit_cost_usd_per_tonne_variance_pct",
        "operating_cost_usd_plan",
        "operating_cost_usd_actual",
        "operating_cost_usd_variance",
        "operating_cost_usd_variance_pct",
        "revenue_proxy_usd_plan",
        "revenue_proxy_usd_actual",
        "revenue_proxy_usd_variance",
        "revenue_proxy_usd_variance_pct",
        "ebitda_proxy_usd_plan",
        "ebitda_proxy_usd_actual",
        "ebitda_proxy_usd_variance",
        "ebitda_proxy_usd_variance_pct",
        "operating_cash_flow_proxy_usd_plan",
        "operating_cash_flow_proxy_usd_actual",
        "operating_cash_flow_proxy_usd_variance",
        "operating_cash_flow_proxy_usd_variance_pct",
        "free_cash_flow_proxy_usd_plan",
        "free_cash_flow_proxy_usd_actual",
        "free_cash_flow_proxy_usd_variance",
        "free_cash_flow_proxy_usd_variance_pct",
        "sustaining_capex_usd_plan",
        "sustaining_capex_usd_actual",
        "sustaining_capex_usd_variance",
        "sustaining_capex_usd_variance_pct",
        "working_capital_change_usd_plan",
        "working_capital_change_usd_actual",
        "working_capital_change_usd_variance",
        "working_capital_change_usd_variance_pct",
        "mining_cost_usd_actual",
        "processing_cost_usd_actual",
        "ga_cost_usd_actual",
        "maintenance_cost_usd_actual",
        "logistics_cost_usd_actual",
        "site_positive_cost_variance_usd",
        "site_cost_pressure_share_pct",
        "top_cost_center",
        "top_cost_center_variance_usd",
        "top_cost_center_margin_pressure_share_pct",
        "overall_alert_level",
        "primary_alert_metric",
        "primary_alert_message",
        "data_classification",
        "sample_data_flag",
    ]
    available_columns = [column for column in columns if column in kpi_monthly_summary.columns]
    return kpi_monthly_summary.loc[:, available_columns].copy()


def build_monthly_executive_overview_mart(kpi_monthly_summary: pd.DataFrame) -> pd.DataFrame:
    """Build a headline executive monitoring mart."""

    columns = [
        "site_id",
        "site_name",
        "period",
        "month_start_date",
        "calendar_year",
        "calendar_month",
        "calendar_quarter",
        "month_label",
        "throughput_tonnes_actual",
        "copper_production_tonnes_actual",
        "copper_price_usd_per_lb_actual",
        "unit_cost_usd_per_tonne_actual",
        "revenue_proxy_usd_actual",
        "ebitda_proxy_usd_actual",
        "operating_cash_flow_proxy_usd_actual",
        "free_cash_flow_proxy_usd_actual",
        "critical_alert_count",
        "warning_alert_count",
        "overall_alert_level",
        "primary_alert_metric",
        "primary_alert_message",
        "throughput_tonnes_variance_pct",
        "copper_production_tonnes_variance_pct",
        "unit_cost_usd_per_tonne_variance_pct",
        "revenue_proxy_usd_variance_pct",
        "ebitda_proxy_usd_variance_pct",
        "downtime_hours_actual",
        "stockpile_feed_pct_actual",
        "site_production_gap_share_pct",
        "top_cost_center",
        "data_classification",
        "sample_data_flag",
    ]
    available_columns = [column for column in columns if column in kpi_monthly_summary.columns]
    return kpi_monthly_summary.loc[:, available_columns].copy()


def build_monthly_monitoring_outputs(
    data_dir: str | Path = _sample_data_dir(),
    mapping_config_path: str | Path | None = _default_mapping_config(),
    output_dir: str | Path = "outputs/bi",
) -> dict[str, Path]:
    """Build and export monthly monitoring datasets and BI marts."""

    if mapping_config_path is None:
        dataset_frames = load_monthly_monitoring_inputs(data_dir=data_dir)
        source_mapping_audit = _identity_source_mapping_audit(dataset_frames=dataset_frames, data_dir=data_dir)
        mapping_config_str = None
    else:
        dataset_frames, source_mapping_audit = load_mapped_monthly_monitoring_inputs(
            data_dir=data_dir,
            mapping_config_path=mapping_config_path,
        )
        mapping_config_str = _public_safe_path(mapping_config_path)

    validated_inputs = validate_monthly_inputs(dataset_frames)
    kpi_monthly_summary = build_kpi_monthly_summary(validated_inputs)
    fact_monthly_actual_vs_plan = build_monthly_actual_vs_plan_fact(kpi_monthly_summary)
    kpi_monthly_summary = _merge_alert_rollup(kpi_monthly_summary, fact_monthly_actual_vs_plan)
    mart_process_driver_summary = build_process_driver_summary_mart(
        validated_inputs["process_driver_monthly"],
        kpi_monthly_summary,
    )
    mart_cost_center_summary = build_cost_center_summary_mart(
        validated_inputs["cost_center_monthly"],
        kpi_monthly_summary,
    )
    kpi_monthly_summary = _merge_operational_context(
        kpi_monthly_summary,
        mart_process_driver_summary,
        mart_cost_center_summary,
    )
    kpi_monthly_summary = validate_dataframe(kpi_monthly_summary, MONTHLY_CANONICAL_SCHEMAS["kpi_monthly_summary"])

    monthly_dataset_catalog = build_monthly_dataset_catalog()
    monthly_field_catalog = build_monthly_field_catalog()
    dim_monthly_metric = build_monthly_metric_dimension()
    monthly_kpi_dictionary = build_monthly_kpi_dictionary()
    mart_monthly_by_site = build_monthly_by_site_mart(kpi_monthly_summary)
    mart_monthly_process_performance = build_monthly_process_performance_mart(kpi_monthly_summary)
    mart_monthly_cost_margin = build_monthly_cost_margin_mart(kpi_monthly_summary)
    mart_monthly_executive_overview = build_monthly_executive_overview_mart(kpi_monthly_summary)
    dim_site = validate_dataframe(build_site_dimension(kpi_monthly_summary), MONTHLY_CANONICAL_SCHEMAS["dim_site"])
    dim_month = validate_dataframe(build_month_dimension(kpi_monthly_summary), MONTHLY_CANONICAL_SCHEMAS["dim_month"])
    dim_process_area = validate_dataframe(
        build_process_area_dimension(mart_process_driver_summary),
        MONTHLY_CANONICAL_SCHEMAS["dim_process_area"],
    )
    dim_cost_center = validate_dataframe(
        build_cost_center_dimension(mart_cost_center_summary),
        MONTHLY_CANONICAL_SCHEMAS["dim_cost_center"],
    )
    data_quality_report = build_data_quality_report(
        dataset_frames={
            **validated_inputs,
            "kpi_monthly_summary": kpi_monthly_summary,
            "dim_site": dim_site,
            "dim_month": dim_month,
            "dim_process_area": dim_process_area,
            "dim_cost_center": dim_cost_center,
        },
        schemas=MONTHLY_CANONICAL_SCHEMAS,
    )
    kpi_exceptions = build_kpi_exceptions(fact_monthly_actual_vs_plan)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    outputs = {
        "monthly_dataset_catalog": output_dir / "monthly_dataset_catalog.csv",
        "monthly_field_catalog": output_dir / "monthly_field_catalog.csv",
        "dim_site": output_dir / "dim_site.csv",
        "dim_month": output_dir / "dim_month.csv",
        "dim_monthly_metric": output_dir / "dim_monthly_metric.csv",
        "dim_process_area": output_dir / "dim_process_area.csv",
        "dim_cost_center": output_dir / "dim_cost_center.csv",
        "monthly_kpi_dictionary": output_dir / "monthly_kpi_dictionary.csv",
        "kpi_monthly_summary": output_dir / "kpi_monthly_summary.csv",
        "fact_monthly_actual_vs_plan": output_dir / "fact_monthly_actual_vs_plan.csv",
        "mart_monthly_process_performance": output_dir / "mart_monthly_process_performance.csv",
        "mart_monthly_cost_margin": output_dir / "mart_monthly_cost_margin.csv",
        "mart_monthly_executive_overview": output_dir / "mart_monthly_executive_overview.csv",
        "mart_monthly_by_site": output_dir / "mart_monthly_by_site.csv",
        "mart_process_driver_summary": output_dir / "mart_process_driver_summary.csv",
        "mart_cost_center_summary": output_dir / "mart_cost_center_summary.csv",
        "data_quality_report": output_dir / "data_quality_report.csv",
        "kpi_exceptions": output_dir / "kpi_exceptions.csv",
        "source_mapping_audit": output_dir / "source_mapping_audit.csv",
        "refresh_summary": output_dir / "refresh_summary.json",
    }

    refresh_summary = build_refresh_summary(
        source_mapping_audit=source_mapping_audit,
        data_quality_summary=summarize_data_quality_report(data_quality_report),
        kpi_exception_summary={
            "monthly_exception_logic": [
                "major throughput shortfall",
                "major recovery underperformance",
                "major production shortfall",
                "unit cost deterioration",
            ],
            **summarize_kpi_exceptions(kpi_exceptions),
        },
        output_files={name: _public_safe_path(path) or "" for name, path in outputs.items()},
        mapping_config_path=mapping_config_str,
        data_dir=_public_safe_path(data_dir) or "",
    )

    write_csv_output(monthly_dataset_catalog, outputs["monthly_dataset_catalog"])
    write_csv_output(monthly_field_catalog, outputs["monthly_field_catalog"])
    write_csv_output(dim_site, outputs["dim_site"])
    write_csv_output(dim_month, outputs["dim_month"])
    write_csv_output(dim_monthly_metric, outputs["dim_monthly_metric"])
    write_csv_output(dim_process_area, outputs["dim_process_area"])
    write_csv_output(dim_cost_center, outputs["dim_cost_center"])
    write_csv_output(monthly_kpi_dictionary, outputs["monthly_kpi_dictionary"])
    write_csv_output(kpi_monthly_summary, outputs["kpi_monthly_summary"])
    write_csv_output(fact_monthly_actual_vs_plan, outputs["fact_monthly_actual_vs_plan"])
    write_csv_output(mart_monthly_process_performance, outputs["mart_monthly_process_performance"])
    write_csv_output(mart_monthly_cost_margin, outputs["mart_monthly_cost_margin"])
    write_csv_output(mart_monthly_executive_overview, outputs["mart_monthly_executive_overview"])
    write_csv_output(mart_monthly_by_site, outputs["mart_monthly_by_site"])
    write_csv_output(mart_process_driver_summary, outputs["mart_process_driver_summary"])
    write_csv_output(mart_cost_center_summary, outputs["mart_cost_center_summary"])
    write_csv_output(data_quality_report, outputs["data_quality_report"])
    write_csv_output(kpi_exceptions, outputs["kpi_exceptions"])
    write_csv_output(source_mapping_audit, outputs["source_mapping_audit"])
    write_json_output(outputs["refresh_summary"], refresh_summary)
    return outputs
