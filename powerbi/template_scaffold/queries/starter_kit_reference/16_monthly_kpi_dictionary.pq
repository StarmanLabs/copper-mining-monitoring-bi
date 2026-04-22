let
    SourcePath = StarterKitOutputRoot & "\\monthly_kpi_dictionary.csv",
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
            {"plan_actual_variance_support", type text},
            {"plan_field", type text},
            {"actual_field", type text},
            {"variance_field", type text},
            {"variance_pct_field", type text},
            {"wide_source_table", type text},
            {"long_source_table", type text},
            {"primary_dashboard_page", type text},
            {"page_usage_note", type text},
            {"alert_direction", type text},
            {"warning_threshold_pct", type number},
            {"critical_threshold_pct", type number},
            {"display_order", Int64.Type}
        }
    )
in
    TypedColumns
