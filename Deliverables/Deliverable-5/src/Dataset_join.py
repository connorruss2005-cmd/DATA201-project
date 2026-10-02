import pandas as pd
import sqlite3


# ===== 1. Load modified Airbnb data and rental bond data and load an output path =====

LISTINGS_PATH = "Deliverables/Deliverable-5/Data/Airbnb listings with area codes/combined_Christchurch_listings_with_area_codes.csv"
BONDS_PATH = "Deliverables/Deliverable-5/Data/cleaned input data/cleaned_rental_bond_data.csv"
OUTPUT_PATH = "Deliverables/Deliverable-5/Output/Merged dataset/christchurch_listings_with_rental_bonds_area_only.csv"

VALID_BOND_QUARTERS = {"2025-10-01", "2026-01-01", "2026-04-01"} # The most recent three quarters of bond data available in the dataset. 

# ===== 2. Performing a left join, area_code on Location ID between the two datasets using SQL =====

# When I did it the first time with pandas merge, I got a lot of rows with no bond data. Becuase some area_codes dont have a match in the bond dataset. So I decided to use SQL to do a left join, 
# and it turned out to be better than pandas, keeping all rows from the listings dataset and adding the median_rent from the bond dataset where available. I got claude to touch up on the code and
# make it a lot cleaner and more readable. I also added some summary statistics at the end to show how many rows were matched and unmatched.

listings = pd.read_csv(LISTINGS_PATH)
bonds = pd.read_csv(BONDS_PATH)

connection = sqlite3.connect(":memory:") # create an in-memory SQLite database
listings.to_sql("listings", connection, index=False, if_exists="replace") # table for the Airbnb data
bonds.to_sql("bonds", connection, index=False, if_exists="replace") # table for the rental bond data

JOIN_SQL = """
WITH bond_all_rows AS (
    -- Area-wide overall market stats only (drop the dwelling-type / bed-
    -- count breakdown rows so each area+quarter is a single row).
    SELECT
        "Location ID"          AS area_code,
        TimeFrame              AS quarter,
        "Total Bonds"          AS total_bonds,
        "Active Bonds"         AS active_bonds,
        "Closed Bonds"         AS closed_bonds,
        "Median Rent"          AS median_rent,
        "Geometric Mean Rent"  AS geometric_mean_rent,
        "Upper Quartile Rent"  AS upper_quartile_rent,
        "Lower Quartile Rent"  AS lower_quartile_rent
    FROM bonds
    WHERE "Dwelling Type" = 'ALL'
      AND "Number Of Beds" = 'ALL'
),
bond_latest_per_area AS (
    -- Keep only each area's most recent available quarter -- a "current
    -- market snapshot" per area. (Falls back to an earlier quarter for the
    -- handful of areas missing the very latest one.)
    SELECT b1.*
    FROM bond_all_rows b1
    WHERE b1.quarter = (
        SELECT MAX(b2.quarter)
        FROM bond_all_rows b2
        WHERE b2.area_code = b1.area_code
    )
)
SELECT
    l.*,
    b.quarter AS bond_data_quarter,
    b.total_bonds,
    b.active_bonds,
    b.closed_bonds,
    b.median_rent,
    b.geometric_mean_rent,
    b.upper_quartile_rent,
    b.lower_quartile_rent
FROM listings AS l
LEFT JOIN bond_latest_per_area AS b
    ON l.area_code = b.area_code;
"""
 
result = pd.read_sql_query(JOIN_SQL, connection)
connection.close()

#----------------------------------------------------------------------------------------------------------------------------
# Sanity checks -> verify the join actually did what we expected it to do. (This is a good idea when doing any kind of join.)
# rather than just assumuing it did becuase it ran without errors.
#----------------------------------------------------------------------------------------------------------------------------
print("Running sanity checks on the joined dataset...")

# 1. No fan-out: A left join against a duplicated per-area lookup should never create extra rows.
assert len(result) == len(listings), ( 
    f"Row count changed by the join ({len(listings)} -> {len(result)}): "
    "the bond side is not uniquely keyed by area_code, so rows fanned out."
)

# 2. Primary/key columns must never be null -- a null here would mean the
#    join silently corrupted or dropped identifying information.
for col in ["id", "area_code"]:
    n_nulls = result[col].isna().sum()
    assert n_nulls == 0, f"Found {n_nulls} unexpected nulls in the primary/key column '{col}'."

# 3. Match rate should land around about 70 - 85 percent (Which was 78%, and null values was 22%)
#    a big deviation signals a key mismatch. The reason it isnt 100% is because some area_codes in the listings 
#    dataset dont have a match in the bond dataset, which is expected.
match_rate = result["median_rent"].notna().mean()
assert 0.70 <= match_rate <= 0.85, (
    f"Match rate {match_rate:.1%} is outside the expected range of 70-85%."
    "check that area_code and Location ID are being compared correctly."
)

# 4. Every non-null bond_data_quarter must be one of the kown valid quarters
#    -- catches silent corruption/mis-parsing of the quarter column.
bad_quarters = set(result["bond_data_quarter"].dropna().unique()) - VALID_BOND_QUARTERS
assert not bad_quarters, f"Unexpected bond_data_quarter value(s) found: {bad_quarters}"

# 5. Rent columns should be non-negative, and finite (negative values would be nonsensical)
for col in ["median_rent", "geometric_mean_rent", "upper_quartile_rent", "lower_quartile_rent"]:
    non_null_values = result[col].dropna()
    assert (non_null_values > 0).all(), f"'{col}' has non-positive values -- investigate before using this data."

print("All sanity checks passed.")

result.to_csv(OUTPUT_PATH, index=False)


# ===== 3. Print some summary statistics =====
matched = result["median_rent"].notna().sum()
print(f"Listings in            : {len(listings)}") # Number of rows in the original listings dataset
print(f"Rows out               : {len(result)}  (should equal listings in)") # Number of rows in the joined dataset (should equal listings in)
print(f"Rows WITH a bond match : {matched} ({matched/len(result):.1%})") # Number of rows with a matching bond record
print(f"Rows with NO bond match: {len(result)-matched} ({1-matched/len(result):.1%})  <- area not in bond data at all") # Number of rows without a matching bond record
print(f"Saved to               : {OUTPUT_PATH}")
