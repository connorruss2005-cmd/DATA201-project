# Packages we are using, please install them if you don't have them yet.
# Also be sure you have all the listings.csv files downloaded.
import pandas as pd
import matplotlib.pyplot as plt

# Iterate through the 9 listings files
#for i in range(1, 10):
#    filename = f"listings{i}.csv"
#
#    df = pd.read_csv(filename, encoding='latin1')
#
#   # Filter for Christchurch City listings
#    df = df[df["neighbourhood_group"] == "Christchurch City"]
#
#    # Convert the last_review column to datetime format
#    df["last_review"] = pd.to_datetime(df["last_review"])
#    
#    # Add a new column for month/year of the last review
#    df["month/year"] = df["last_review"].dt.to_period("M")
#
#    df.to_csv(f"listings_{i}_updated.csv", index=False)


#data_sets = []
#
#for i in range(1, 10):
#    filename = f"listings_{i}_updated.csv"
#    df = pd.read_csv(filename)
#
#    # Add the dataframes to an empty list
#    data_sets.append(df)
#
## Concatenate all datasets
#combined = pd.concat(data_sets, ignore_index=True)
#
#combined.to_csv("combined_Christchurch_listings.csv", index=False)


# Categories: different/unique values in a column
# Counts: how many times each category appears in a column

df = pd.read_csv("combined_Christchurch_listings.csv")

# Show all columns when printing
pd.set_option("display.max_columns", None)

# -----------------------------
# NUMERIC COLUMN SUMMARY
# -----------------------------

# Get summary statistics for numeric columns
numeric_summary = df.select_dtypes(include="number").describe().T

# Add a column for the number of missing values in each numeric column
numeric_summary["missing"] = df[numeric_summary.index].isna().sum()

print("NUMERIC COLUMNS")
print(numeric_summary)


# -----------------------------
# CATEGORICAL COLUMN SUMMARY
# -----------------------------

categorical_columns = df.select_dtypes(include="str").columns

for column in categorical_columns:
    print(f"\n{column}")
    print("Missing:", df[column].isna().sum())
    print(df[column].value_counts(dropna=False))

    print("Number of missing values:", df[column].isna().sum())
    print("Number of unique values:", df[column].nunique())

    print("\nCategories and counts:")
    print(df[column].value_counts(dropna=False))
