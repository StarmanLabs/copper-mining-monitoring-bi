let
    SourcePath = AdvancedAppendixOutputRoot & "\\fact_simulation_distribution.csv",
    Source = Csv.Document(
        File.Contents(SourcePath),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TypedColumns = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"iteration", Int64.Type},
            {"average_price_usd_per_lb", type number},
            {"terminal_price_usd_per_lb", type number},
            {"price_path_std_usd_per_lb", type number},
            {"grade_factor", type number},
            {"average_recovery", type number},
            {"recovery_std", type number},
            {"npv_usd", type number},
            {"scenario_id", type text},
            {"scenario_name", type text},
            {"valuation_basis", type text}
        }
    )
in
    TypedColumns
