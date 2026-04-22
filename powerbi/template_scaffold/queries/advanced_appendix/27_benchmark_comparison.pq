let
    SourcePath = AdvancedAppendixOutputRoot & "\\benchmark_comparison.csv",
    Source = Csv.Document(
        File.Contents(SourcePath),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TypedColumns = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"metric", type text},
            {"python_value", type number},
            {"python_unit", type text},
            {"python_currency", type text},
            {"python_basis", type text},
            {"python_timing_basis", type text},
            {"benchmark_value", type number},
            {"benchmark_unit", type text},
            {"benchmark_currency", type text},
            {"benchmark_basis", type text},
            {"benchmark_timing_basis", type text},
            {"benchmark_source", type text},
            {"comparability_class", type text},
            {"comparable_flag", type logical},
            {"reconciliation_status", type text},
            {"reconciliation_note", type text},
            {"gap", type number},
            {"pct_gap", type number}
        }
    )
in
    TypedColumns
