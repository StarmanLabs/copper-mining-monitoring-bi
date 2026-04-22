let
    SourcePath = StarterKitOutputRoot & "\\powerbi_measure_catalog.csv",
    Source = Csv.Document(
        File.Contents(SourcePath),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TypedColumns = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"measure_order", Int64.Type},
            {"measure_name", type text},
            {"measure_group", type text},
            {"display_folder", type text},
            {"table_name", type text},
            {"dashboard_page", type text},
            {"page_order", Int64.Type},
            {"starter_kit_scope", type text},
            {"format_hint", type text},
            {"format_string", type text},
            {"preferred_visual_type", type text},
            {"context_requirement", type text},
            {"business_question", type text},
            {"description", type text},
            {"dax_template", type text}
        }
    )
in
    TypedColumns
