import pandas as pd
import sqlite3


# ===== 1. Load modified Airbnb data and rental bond data and load an output path =====

LISTINGS_PATH = "Deliverables/Deliverable-5/combined_Christchurch_listings_with_area_codes.csv"
BONDS_PATH = "Deliverables/cleaned_rental_bond_data.csv"
OUTPUT_PATH = "Deliverables/Deliverable-5/christchurch_listings_with_rental_bonds_area_only.csv"

listings = pd.read_csv(LISTINGS_PATH)
bonds = pd.read_csv(BONDS_PATH)

# ===== 2. Performing a left join, area_code on Location ID between the two datasets using SQL =====

# When I did it the first time with pandas merge, I got a lot of rows with no bond data. I realized that the rental bond data has multiple rows per area_code (one for each dwelling type and bed count), 
# so I need to filter it down to just one row per area_code before joining. I got claude to help me with this.

conn = sqlite3.connect(":memory:") # create an in-memory SQLite database
listings.to_sql("listings", conn, index=False, if_exists="replace") # create a table for the Airbnb data
bonds.to_sql("bonds", conn, index=False, if_exists="replace") # create a table for the rental bond data

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

# ===== 3. Save the joined dataset to a CSV file =====
result = pd.read_sql_query(JOIN_SQL, conn)
conn.close() # close the database connection
 
result.to_csv(OUTPUT_PATH, index=False)

# ===== 4. Print some summary statistics =====
matched = result["median_rent"].notna().sum()
print(f"Listings in            : {len(listings)}") # Number of rows in the original listings dataset
print(f"Rows out               : {len(result)}  (should equal listings in)") # Number of rows in the joined dataset (should equal listings in)
print(f"Rows WITH a bond match : {matched} ({matched/len(result):.1%})") # Number of rows with a matching bond record
print(f"Rows with NO bond match: {len(result)-matched} ({1-matched/len(result):.1%})  <- area not in bond data at all") # Number of rows without a matching bond record
print(f"Saved to               : {OUTPUT_PATH}")
