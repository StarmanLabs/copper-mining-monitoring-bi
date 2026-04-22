let
    SourcePath = MonthlyOutputRoot & "\\mart_monthly_by_site.csv",
    Source = Csv.Document(
        File.Contents(SourcePath),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TypedColumns = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"site_id", type text},
            {"site_name", type text},
            {"period", type text},
            {"month_start_date", type text},
            {"calendar_year", Int64.Type},
            {"calendar_month", Int64.Type},
            {"calendar_quarter", Int64.Type},
            {"month_label", type text},
            {"throughput_tonnes_plan", Int64.Type},
            {"throughput_tonnes_actual", Int64.Type},
            {"throughput_tonnes_variance", Int64.Type},
            {"throughput_tonnes_variance_pct", type number},
            {"copper_production_tonnes_plan", type number},
            {"copper_production_tonnes_actual", Int64.Type},
            {"copper_production_tonnes_variance", type number},
            {"copper_production_tonnes_variance_pct", type number},
            {"unit_cost_usd_per_tonne_plan", type number},
            {"unit_cost_usd_per_tonne_actual", type number},
            {"unit_cost_usd_per_tonne_variance", type number},
            {"unit_cost_usd_per_tonne_variance_pct", type number},
            {"revenue_proxy_usd_actual", type number},
            {"ebitda_proxy_usd_actual", type number},
            {"availability_pct_actual", type number},
            {"utilization_pct_actual", type number},
            {"downtime_hours_actual", Int64.Type},
            {"stockpile_feed_pct_actual", type number},
            {"primary_ore_source", type text},
            {"primary_process_area", type text},
            {"site_production_gap_tonnes", type number},
            {"site_production_gap_share_pct", type number},
            {"site_positive_cost_variance_usd", Int64.Type},
            {"site_cost_pressure_share_pct", type number},
            {"top_cost_center", type text},
            {"top_cost_center_variance_usd", Int64.Type},
            {"top_cost_center_margin_pressure_share_pct", type number},
            {"overall_alert_level", type text},
            {"primary_alert_metric", type text},
            {"primary_alert_message", type text},
            {"data_classification", type text},
            {"sample_data_flag", type logical}
        }
    )
in
    TypedColumns
