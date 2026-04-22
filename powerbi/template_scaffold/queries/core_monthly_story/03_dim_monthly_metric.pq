let
    SourcePath = MonthlyOutputRoot & "\\dim_monthly_metric.csv",
    Source = Csv.Document(
        File.Contents(SourcePath),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TypedColumns = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"metric", type text},
            {"display_name", type text},
            {"metric_group", type text},
            {"metric_role", type text},
            {"business_meaning", type text},
            {"unit", type text},
            {"proxy_flag", type logical},
            {"dashboard_page", type text},
            {"page_usage_note", type text},
            {"alert_direction", type text},
            {"warning_threshold_pct", type number},
            {"critical_threshold_pct", type number},
            {"plan_column", type text},
            {"actual_column", type text},
            {"variance_column", type text},
            {"variance_pct_column", type text},
            {"display_order", Int64.Type}
        }
    )
in
    TypedColumns
