let
    SourcePath = AdvancedAppendixOutputRoot & "\\dim_scenario.csv",
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
            {"description", type text},
            {"sort_order", Int64.Type},
            {"price_factor", type number},
            {"grade_factor", type number},
            {"recovery_factor", type number},
            {"throughput_factor", type number},
            {"opex_factor", type number},
            {"capex_factor", type number},
            {"wacc_shift_bps", type number}
        }
    )
in
    TypedColumns
