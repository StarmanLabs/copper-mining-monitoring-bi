let
    SourcePath = AdvancedAppendixOutputRoot & "\\simulation_percentiles.csv",
    Source = Csv.Document(
        File.Contents(SourcePath),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TypedColumns = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"percentile", type number},
            {"npv_usd", type number}
        }
    )
in
    TypedColumns
