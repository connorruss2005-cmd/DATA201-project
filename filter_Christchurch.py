import pandas as pd

# Read the CSV file and store it in a DataFrame called df.
df = pd.read_csv("data/listings.csv", encoding="latin1")

# Display all column names as a Python list.
print(df.columns.tolist())

# Display all values in the neighbourhood_group column.
print(df["neighbourhood_group"])