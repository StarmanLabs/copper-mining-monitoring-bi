let
    SourcePath = AdvancedAppendixOutputRoot & "\\fact_annual_metrics.csv",
    Source = Csv.Document(
        File.Contents(SourcePath),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TypedColumns = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"year", Int64.Type},
            {"metric", type text},
            {"value", type number},
            {"scenario_id", type text},
            {"scenario_name", type text},
            {"scenario_category", type text},
            {"category", type text}
        }
    )
in
    TypedColumns
