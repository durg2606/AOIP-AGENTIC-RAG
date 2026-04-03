import pandas as pd

df = pd.read_parquet("./data/tickets_clean.parquet")

print(df.head(10))
print(df.shape)
print(df.columns)