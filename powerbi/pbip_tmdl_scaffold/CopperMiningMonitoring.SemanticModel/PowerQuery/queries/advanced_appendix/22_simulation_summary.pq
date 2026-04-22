let
    SourcePath = AdvancedAppendixOutputRoot & "\\simulation_summary.csv",
    Source = Csv.Document(
        File.Contents(SourcePath),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TypedColumns = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"metric", type text},
            {"value", type number}
        }
    )
in
    TypedColumns
