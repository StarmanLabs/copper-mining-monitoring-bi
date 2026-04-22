let
    SourcePath = AdvancedAppendixOutputRoot & "\\dim_year.csv",
    Source = Csv.Document(
        File.Contents(SourcePath),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TypedColumns = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"year", Int64.Type},
            {"calendar_year", Int64.Type},
            {"phase", type text},
            {"year_label", type text}
        }
    )
in
    TypedColumns
