let
    SourcePath = StarterKitOutputRoot & "\\dashboard_page_catalog.csv",
    Source = Csv.Document(
        File.Contents(SourcePath),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TypedColumns = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"page_order", Int64.Type},
            {"page_name", type text},
            {"page_group", type text},
            {"goal", type text},
            {"primary_dataset", type text}
        }
    )
in
    TypedColumns
