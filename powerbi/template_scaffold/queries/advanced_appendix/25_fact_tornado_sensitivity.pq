let
    SourcePath = AdvancedAppendixOutputRoot & "\\fact_tornado_sensitivity.csv",
    Source = Csv.Document(
        File.Contents(SourcePath),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TypedColumns = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"driver", type text},
            {"driver_label", type text},
            {"direction", type text},
            {"shock", type number},
            {"scenario_value", type number},
            {"npv_usd", type number},
            {"impact_vs_base_usd", type number},
            {"abs_impact_vs_base_usd", type number},
            {"impact_rank", type number}
        }
    )
in
    TypedColumns
