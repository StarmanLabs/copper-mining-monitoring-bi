let
    SourcePath = MonthlyOutputRoot & "\\fact_monthly_actual_vs_plan.csv",
    Source = Csv.Document(
        File.Contents(SourcePath),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TypedColumns = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"site_id", type text},
            {"period", type text},
            {"month_start_date", type text},
            {"calendar_year", Int64.Type},
            {"calendar_month", Int64.Type},
            {"calendar_quarter", Int64.Type},
            {"month_label", type text},
            {"metric", type text},
            {"metric_display_name", type text},
            {"metric_group", type text},
            {"unit", type text},
            {"dashboard_page", type text},
            {"display_order", Int64.Type},
            {"plan_value", type number},
            {"actual_value", type number},
            {"variance_value", type number},
            {"variance_pct", type number},
            {"alert_direction", type text},
            {"alert_level", type text},
            {"alert_flag", type logical},
            {"badness_score", type number},
            {"alert_message", type text},
            {"plan_version", type text},
            {"data_classification", type text},
            {"sample_data_flag", type logical}
        }
    )
in
    TypedColumns
