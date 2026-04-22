let
    SourcePath = MonthlyOutputRoot & "\\dim_cost_center.csv",
    Source = Csv.Document(
        File.Contents(SourcePath),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TypedColumns = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"cost_center", type text},
            {"cost_center_sort_order", Int64.Type}
        }
    )
in
    TypedColumns
