# runtime_summary.csv: array_index, yaml_file, runtime_s
import pandas as pd

df = pd.read_csv("logs/array/runtime_summary.csv", header=None,
                 names=["idx","yaml","time_s"])

print(f"Average runtime: {df.time_s.mean()/60:.1f} min")
print(f"Longest: {df.time_s.max()/60:.1f} min")
print(f"Shortest: {df.time_s.min()/60:.1f} min")
