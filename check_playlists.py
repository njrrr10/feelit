import pandas as pd

df = pd.read_csv("big_dataset.csv")

print("\n=== UNIQUE PLAYLIST NAMES ===\n")
for name in df["source_playlist"].unique():
    print(name)