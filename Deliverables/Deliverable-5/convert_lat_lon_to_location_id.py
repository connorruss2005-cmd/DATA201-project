import pandas as pd

cleaned_airbnb_df = pd.read_csv(
    'Deliverables/combined_Christchurch_listings_cleaned.csv'
)

print(
    cleaned_airbnb_df[["latitude", "longitude"]].head()
)

