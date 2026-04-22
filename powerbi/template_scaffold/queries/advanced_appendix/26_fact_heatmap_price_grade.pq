let
    SourcePath = AdvancedAppendixOutputRoot & "\\fact_heatmap_price_grade.csv",
    Source = Csv.Document(
        File.Contents(SourcePath),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TypedColumns = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"price_factor", type number},
            {"grade_factor", type number},
            {"recovery_factor", type number},
            {"throughput_factor", type number},
            {"opex_factor", type number},
            {"capex_factor", type number},
            {"wacc_shift_bps", type number},
            {"npv_usd", type number},
            {"npv_sign", type text}
        }
    )
in
    TypedColumns
