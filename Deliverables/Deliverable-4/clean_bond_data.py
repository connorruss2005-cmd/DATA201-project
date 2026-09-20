from pathlib import Path
import pandas as pd

#=====1. SETUP & LOAD DATASET=====
BASE_DIR = Path(__file__).resolve().parent
file_path = BASE_DIR.parent / "Detailed-Quarterly-Tenancy-Q1-2020-Q3-2026.csv"

raw_bond_df = pd.read_csv(file_path)

#=====CHECK FOR ORIGINAL DATASET=====
print(f"\n{'=' * 60}")
print("=" * 60)
print(file_path)
print(raw_bond_df.columns.tolist())
print(raw_bond_df["TimeFrame"].value_counts().sort_index())
print(f"Initial row count: {len(raw_bond_df)}")
print("=" * 60)
print("=" * 60)
#====================================


#=====2. COLUMN SELECTION & STANDARDIZATION=====
raw_bond_df.columns = raw_bond_df.columns.str.strip()

raw_bond_df.rename(
    columns={"Location Id": "Location ID", "LocationID": "Location ID"},
    inplace=True,
)


#=====3. KEEP COLUMNS NEEDED FOR ANALYSIS=====
columns_to_keep = [
    "TimeFrame",
    "Location ID",
    "Dwelling Type",
    "Number Of Beds",
    "Total Bonds",
    "Active Bonds",
    "Closed Bonds",
    "Median Rent",
    "Geometric Mean Rent",
    "Upper Quartile Rent",
    "Lower Quartile Rent"
]

bond_df = raw_bond_df[columns_to_keep].copy()


#=====4. CREAN CATEGORICAL COLUMNS=====
bond_df["Dwelling Type"] = (
    bond_df["Dwelling Type"]
    .astype("string")
    .str.strip()
)

bond_df["Number Of Beds"] = (
    bond_df["Number Of Beds"]
    .astype("string")
    .str.strip()
)


#=====5. CONVERT AND FILTER TIMEFRAME=====
bond_df["TimeFrame"] = pd.to_datetime(
    bond_df["TimeFrame"],
    errors="coerce"
)

target_timeframes = pd.to_datetime([
    "2025-10-01",
    "2026-01-01",
    "2026-04-01"
])

bond_df = bond_df[
    bond_df["TimeFrame"].isin(target_timeframes)
].copy()


#=====6. CLEAN NUMERIC COLUMNS=====
numeric_cols = [
    "Total Bonds",
    "Active Bonds",
    "Closed Bonds",
    "Median Rent",
    "Geometric Mean Rent",
    "Upper Quartile Rent",
    "Lower Quartile Rent"
]

for col in numeric_cols:
        bond_df[col] = pd.to_numeric(
            bond_df[col],
            errors="coerce"
        )


#=====7. HANDLE MISSING KEYS=====
initial_count = len(bond_df)
bond_df = bond_df.dropna(
        subset=["TimeFrame", "Location ID"]
)

#beds_df = bond_df.dropna(subset=["Number Of Beds"])
final_count = len(bond_df)


#=====8. CLEANING AUDIT=====
print("\n--- Data Cleaning Audit ---")
print(f"Rows retained after timeframe filter: {initial_count}")
print(f"Rows after dropping missing keys: {final_count}")
print(f"Rows removed during key cleaning: {initial_count - final_count}")
print("\nMissing values per column:")
print(bond_df.isnull().sum())
print(bond_df["TimeFrame"].value_counts().sort_index())


#======9. EXPORT CLEANED DATASET LOCALLY=====
output_path = BASE_DIR.parent / "cleaned_rental_bond_data.csv"
bond_df.to_csv(
        output_path,
        index=False
)

print(
    f"\nCleaned dataset saved locally as '{output_path.name}'."
)