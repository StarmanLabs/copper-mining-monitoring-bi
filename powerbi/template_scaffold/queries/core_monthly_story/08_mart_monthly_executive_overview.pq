let
    SourcePath = MonthlyOutputRoot & "\\mart_monthly_executive_overview.csv",
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
            {"throughput_tonnes_actual", Int64.Type},
            {"copper_production_tonnes_actual", Int64.Type},
            {"copper_price_usd_per_lb_actual", type number},
            {"unit_cost_usd_per_tonne_actual", type number},
            {"revenue_proxy_usd_actual", type number},
            {"ebitda_proxy_usd_actual", type number},
            {"operating_cash_flow_proxy_usd_actual", type number},
            {"free_cash_flow_proxy_usd_actual", type number},
            {"critical_alert_count", Int64.Type},
            {"warning_alert_count", Int64.Type},
            {"overall_alert_level", type text},
            {"primary_alert_metric", type text},
            {"primary_alert_message", type text},
            {"throughput_tonnes_variance_pct", type number},
            {"copper_production_tonnes_variance_pct", type number},
            {"unit_cost_usd_per_tonne_variance_pct", type number},
            {"revenue_proxy_usd_variance_pct", type number},
            {"ebitda_proxy_usd_variance_pct", type number},
            {"downtime_hours_actual", Int64.Type},
            {"stockpile_feed_pct_actual", type number},
            {"site_production_gap_share_pct", type number},
            {"top_cost_center", type text},
            {"data_classification", type text},
            {"sample_data_flag", type logical}
        }
    )
in
    TypedColumns
