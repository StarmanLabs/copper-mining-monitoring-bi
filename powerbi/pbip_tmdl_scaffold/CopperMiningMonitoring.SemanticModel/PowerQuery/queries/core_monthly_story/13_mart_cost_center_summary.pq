let
    SourcePath = MonthlyOutputRoot & "\\mart_cost_center_summary.csv",
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
            {"cost_center", type text},
            {"cost_usd_plan", Int64.Type},
            {"cost_usd_actual", Int64.Type},
            {"cost_variance_usd", Int64.Type},
            {"cost_variance_pct", type number},
            {"planned_cost_per_tonne", type number},
            {"actual_cost_per_tonne", type number},
            {"positive_cost_variance_usd", Int64.Type},
            {"site_positive_cost_variance_usd", Int64.Type},
            {"cost_center_margin_pressure_share_pct", type number},
            {"overall_alert_level", type text},
            {"primary_alert_metric", type text},
            {"primary_alert_message", type text},
            {"data_classification", type text},
            {"sample_data_flag", type logical}
        }
    )
in
    TypedColumns
