let
    SourcePath = AdvancedAppendixOutputRoot & "\\fact_scenario_kpis.csv",
    Source = Csv.Document(
        File.Contents(SourcePath),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TypedColumns = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"scenario_id", type text},
            {"scenario_name", type text},
            {"scenario_category", type text},
            {"metric", type text},
            {"value", type number}
        }
    )
in
    TypedColumns
