import sys
import time
import pandas as pd

# start timer
start_time = time.time()

try:
    df = pd.read_csv(sys.argv[1], sep=r"\s+")

    # stop timer after reading csv
    end_time = time.time() - start_time
    print(f"Wall-clock Time: {end_time:.2f} seconds")

    # sum total memory usage and convert from bytes to MB
    df_memory = df.memory_usage(deep=True).sum() / (1024**2)
    print(f"DataFrame Memory Usage: {df_memory:.2f} MB")

except Exception as e:
    print(f"\nError:\n{e}")