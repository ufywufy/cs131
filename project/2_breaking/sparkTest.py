import sys

from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("cs131-project").getOrCreate()

if len(sys.argv) < 2:
    print("Usage: sparkTest.py (path to csv)")
    sys.exit()

path = sys.argv[1]
df = spark.read.csv(path, header=False, inferSchema=True)

total_lines = df.count()

print(f"Total Lines: {total_lines}")
