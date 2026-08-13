# Packages we are using, please install them if you don't have them yet.
# Also be sure you have all the listings.csv files downloaded.
import numpy as np
import matplotlib.pyplot as plt # Not sure if we need this
import pandas as pd

# Iterate through the 9 listings files
#for i in range(1, 10):
#    filename = f"listings{i}.csv"
#
#    df = pd.read_csv(filename)
#
#    # Filter for Christchurch City listings
#    df = df[df["neighbourhood_group"] == "Christchurch City"]
#
#    # Convert the last_review column to datetime format
#    df["last_review"] = pd.to_datetime(df["last_review"])
#    
#    # Add a new column for month/year of the last review
#    df["month/year"] = df["last_review"].dt.to_period("M")
#
#    df.to_csv(f"listings_{i}_updated.csv", index=False)


data_sets = []

for i in range(1, 10):
    filename = f"listings_{i}_updated.csv"
    df = pd.read_csv(filename)

    # Add the dataframes to an empty list
    data_sets.append(df)

# Concatenate all datasets
combined = pd.concat(data_sets, ignore_index=True)

combined.to_csv("combined_Christchurch_listings.csv", index=False)
