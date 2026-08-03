from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, sum as spark_sum, when, lit, regexp_extract, input_file_name

def main():
    spark = SparkSession.builder \
        .appName("WikipediaChatGPTImpactAnalysis") \
        .getOrCreate()

    # 1. Load target articles
    csv_gcs_path = "gs://emily-cs131/phase3/target_pages.csv"
    mapping_df = spark.read.text(csv_gcs_path)
    target_articles = [row.value for row in mapping_df.collect()]
    broadcast_articles = spark.sparkContext.broadcast(target_articles)

    # 2. Load pageviews
    gcs_pageviews_path = "gs://emily-cs131/project_data/pageviews-2022*.gz"
    raw_df = spark.read.text(gcs_pageviews_path)

    # 3. Parse and extract date from filename
    parsed_df = raw_df.selectExpr("split(value, ' ') as col") \
        .select(
            col("col")[0].alias("domain_code"),
            col("col")[1].alias("article_title"),
            col("col")[2].cast("long").alias("view_count"),
            input_file_name().alias("source_file")
        )

    clean_df = parsed_df.withColumn(
        "date_str", 
        regexp_extract(col("source_file"), r"(2022\d{4})", 1)
    )

    # 4. Filter for English Wikipedia and target articles
    filtered_df = clean_df.filter(
        col("domain_code").isin("en", "en.m") & 
        col("article_title").isin(broadcast_articles.value)
    )

    # 5. Get daily total views per article
    daily_article_views = filtered_df.groupBy("article_title", "date_str") \
        .agg({"view_count": "sum"}).withColumnRenamed("sum(view_count)", "daily_views")

    # 6. Categorize dates into Before vs After periods
    categorized_df = daily_article_views.withColumn(
        "period",
        when(col("date_str").isin("20221128", "20221129"), "Before_ChatGPT")
        .when(col("date_str").isin("20221201", "20221202"), "After_ChatGPT")
        .otherwise("Release_Day")
    )

    # 7. Calculate daily average for each period per article
    period_avg_df = categorized_df.groupBy("article_title", "period") \
        .agg(avg("daily_views").alias("avg_daily_views"))

    # 8. Pivot to put Before and After averages side-by-side
    pivoted_df = period_avg_df.groupBy("article_title") \
        .pivot("period", ["Before_ChatGPT", "Release_Day", "After_ChatGPT"]) \
        .sum("avg_daily_views") \
        .na.fill(0)

    # 9. Compute difference of averages and sort
    comparison_df = pivoted_df.withColumn(
        "avg_view_difference", col("After_ChatGPT") - col("Before_ChatGPT")
    ).withColumn(
        "pct_change", 
        when(col("Before_ChatGPT") > 0, 
             ((col("After_ChatGPT") - col("Before_ChatGPT")) / col("Before_ChatGPT")) * 100
        ).otherwise(lit(0.0))
    ).orderBy(col("avg_view_difference").desc())

    # 10. Print the top 5 directly to the console logs
    print("\n" + "="*80)
    print("TOP 5 MOST AFFECTED AI ARTICLES (Based on Average Daily View Difference)")
    print("="*80)
    
    comparison_df.select(
        col("article_title").alias("Article"),
        col("Before_ChatGPT").alias("Before_Avg"),
        col("After_ChatGPT").alias("After_Avg"),
        col("avg_view_difference").alias("Difference"),
        col("pct_change").alias("Pct_Change")
    ).show(5, truncate=False)

    # 11. Calculate and Print Overall Aggregate Traffic Stats
    # (i.e. total count before ChatGPT --> average over the 2 day window --> compare to average after ChatGPT's release)
    totals = comparison_df.agg(
        spark_sum("Before_ChatGPT").alias("total_before"),
        spark_sum("After_ChatGPT").alias("total_after"),
        avg("pct_change").alias("mean_pct_change")
    ).collect()[0]

    tot_before = totals["total_before"]
    tot_after = totals["total_after"]
    mean_change = totals["mean_pct_change"]
    overall_net_change_pct = ((tot_after - tot_before) / tot_before * 100) if tot_before > 0 else 0

    print("="*80)
    print("OVERALL MARKET / AGGREGATE SUMMARY ACROSS ALL TARGET ARTICLES")
    print("="*80)
    print(f"Total Daily Average Views Before ChatGPT: {tot_before:,.2f}")
    print(f"Total Daily Average Views After ChatGPT:  {tot_after:,.2f}")
    print(f"Overall Net Volume Percentage Change:     {overall_net_change_pct:+.2f}%")
    print(f"Mean Percentage Change Across Articles:   {mean_change:+.2f}%")
    print("="*80 + "\n")

    # 12. Save as CSV in GCS
    output_gcs_csv = "gs://emily-cs131/phase3/chatgpt_impact_csv"
    comparison_df.coalesce(1).write \
        .mode("overwrite") \
        .option("header", "true") \
        .csv(output_gcs_csv)
        
    print(f"Results successfully saved as CSV to {output_gcs_csv}")

    spark.stop()

if __name__ == "__main__":
    main()
