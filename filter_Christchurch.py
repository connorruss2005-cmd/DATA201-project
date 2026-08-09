import pandas as pd

# October 2025
# Read the CSV file and store it in a DataFrame called df.
oct_df = pd.read_csv("data/listings_2025_10.csv", encoding="latin1")


# Display all column names as a Python list.
# print(oct_df.columns.tolist())

# Display all values in the neighbourhood_group column.
# print(oct_df["neighbourhood_group"])

# Display unique values in the neighbourhood_group column.
# print(oct_df["neighbourhood_group"].unique())

# Display the number of raws and columns
# print(oct_df.shape)


## (process1) Filter all dataset to Christchurch City only.
filter_oct_df = oct_df[oct_df["neighbourhood_group"] == "Christchurch City"].copy()
# print(df.shape)
# print(filter_oct_df.shape)

# Add a column for the month + year.
filter_oct_df["month_year"] = "October 2025"
# Check the new column.
# print(filter_df["month_year"].head())
# Check all column names
# print(filter_df.columns.tolist())


# November 2025
nov_df = pd.read_csv("data/listings_2025_11.csv", encoding="latin1")
filter_nov_df = nov_df[nov_df["neighbourhood_group"] == "Christchurch City"].copy()
filter_nov_df["month_year"] = "November 2025"

# December 2025
dec_df = pd.read_csv("data/listings_2025_12.csv", encoding="latin1")
filter_dec_df = dec_df[dec_df["neighbourhood_group"] == "Christchurch City"].copy()
filter_dec_df["month_year"] = "December 2025"

# January 2026
jan_df = pd.read_csv("data/listings_2026_01.csv", encoding="latin1")
filter_jan_df = jan_df[jan_df["neighbourhood_group"] == "Christchurch City"].copy()
filter_jan_df["month_year"] = "January 2026"

# February 2026
feb_df = pd.read_csv("data/listings_2026_02.csv", encoding="latin1")
filter_feb_df = feb_df[feb_df["neighbourhood_group"] == "Christchurch City"].copy()
filter_feb_df["month_year"] = "February 2026"

# March 2026
mar_df = pd.read_csv("data/listings_2026_03.csv", encoding="latin1")
filter_mar_df = mar_df[mar_df["neighbourhood_group"] == "Christchurch City"].copy()
filter_mar_df["month_year"] = "March 2026"

# April 2026
apr_df = pd.read_csv("data/listings_2026_04.csv", encoding="latin1")
filter_apr_df = apr_df[apr_df["neighbourhood_group"] == "Christchurch City"].copy()
filter_apr_df["month_year"] = "April 2026"

# May 2026
may_df = pd.read_csv("data/listings_2026_05.csv", encoding="latin1")
filter_may_df = may_df[may_df["neighbourhood_group"] == "Christchurch City"].copy()
filter_may_df["month_year"] = "May 2026"

# June 2026
jun_df = pd.read_csv("data/listings_2026_06.csv", encoding="latin1")
filter_jun_df = jun_df[jun_df["neighbourhood_group"] == "Christchurch City"].copy()
filter_jun_df["month_year"] = "June 2026"


## (process2) Concatenate all filtered monthly datasets into a larger dataset spanning Oct 2025 to June 2026 for Christchurch.
combined_df = pd.concat(
    [
        filter_oct_df,
        filter_nov_df,
        filter_dec_df,
        filter_jan_df,
        filter_feb_df,
        filter_mar_df,
        filter_apr_df,
        filter_may_df,
        filter_jun_df
    ],
    ignore_index = True
)

# print(combined_df.shape)
# Display the number of listings for each month.
# print(combined_df["month_year"].value_counts())

# Remove the license column because all values are missing.
# The license column contained only missing values, so I removed it because it does not privide  useful information for the analysis.
combined_df = combined_df.drop(columns=["license"])

# Display summary statistics for numerical columns.
# print(combined_df.describe())

# Display summary statistics for categorical columns.
# print(combined_df.describe(include=["object"]))

# Display the number of missing values in each column.
# print(combined_df.isnull().sum())


## (process3) Store the concatenated dataset in a new file.
combined_df.to_csv("data/christchurch_listings_oct2025_jun2026.csv", index = False)

# Check the final dataset.
# print(combined_df.shape)
# print(combined_df.head())



import matplotlib.pyplot as plt

## Display a histgram of listing prices up to $1000 in Christchurch.
## I filtered listings with prices up to $1000, and selected the price column, and created a histgram with 50 bins.
combined_df[combined_df["price"] <= 1000]["price"].hist(bins = 50)

# Display a histgram of listing prices in Christchurch.
# combined_df["price"].hist()

# Check summary statistics for price.
# print(combined_df["price"].describe())

# Display the 20 highest prices. This result shows that the original histogram is distorted by a very small number of extremely expensive listings.
# print(combined_df["price"].nlargest(20))

plt.xlabel("Price (NZD)")
plt.ylabel("Frequency")
plt.title("Price Distribution of Christchurch Listings (<= $1000)")
plt.show()