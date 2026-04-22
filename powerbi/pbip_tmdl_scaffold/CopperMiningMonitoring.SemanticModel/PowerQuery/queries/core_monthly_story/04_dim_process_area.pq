let
    SourcePath = MonthlyOutputRoot & "\\dim_process_area.csv",
    Source = Csv.Document(
        File.Contents(SourcePath),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TypedColumns = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"process_area", type text},
            {"process_area_sort_order", Int64.Type}
        }
    )
in
    TypedColumns
