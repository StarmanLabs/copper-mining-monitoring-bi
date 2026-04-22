let
    SourcePath = MonthlyOutputRoot & "\\mart_process_driver_summary.csv",
    Source = Csv.Document(
        File.Contents(SourcePath),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TypedColumns = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"site_id", type text},
            {"site_name", type text},
            {"period", type text},
            {"month_start_date", type text},
            {"calendar_year", Int64.Type},
            {"calendar_month", Int64.Type},
            {"calendar_quarter", Int64.Type},
            {"month_label", type text},
            {"process_area", type text},
            {"ore_source", type text},
            {"stockpile_flag", type logical},
            {"ore_mix_pct", type number},
            {"throughput_tonnes_plan", Int64.Type},
            {"throughput_tonnes_actual", Int64.Type},
            {"throughput_tonnes_variance", Int64.Type},
            {"throughput_tonnes_variance_pct", type number},
            {"copper_production_tonnes_plan", Int64.Type},
            {"copper_production_tonnes_actual", Int64.Type},
            {"copper_production_tonnes_variance", Int64.Type},
            {"copper_production_tonnes_variance_pct", type number},
            {"negative_production_gap_tonnes", Int64.Type},
            {"process_area_production_gap_share_pct", type number},
            {"availability_pct", type number},
            {"downtime_hours", Int64.Type},
            {"site_total_downtime_hours", Int64.Type},
            {"downtime_share_pct", type number},
            {"overall_alert_level", type text},
            {"primary_alert_metric", type text},
            {"primary_alert_message", type text},
            {"data_classification", type text},
            {"sample_data_flag", type logical}
        }
    )
in
    TypedColumns
