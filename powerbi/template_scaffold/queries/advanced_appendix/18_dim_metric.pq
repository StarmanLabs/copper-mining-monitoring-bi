let
    SourcePath = AdvancedAppendixOutputRoot & "\\dim_metric.csv",
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
            {"unit", type text},
            {"category", type text},
            {"dashboard_page", type text}
        }
    )
in
    TypedColumns
