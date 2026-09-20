from pathlib import Path
import pandas as pd


# ===== 1. SETUP & LOAD DATASET =====
BASE_DIR = Path(__file__).resolve().parent

file_path = (
    BASE_DIR
    / "Detailed-Quarterly-Tenancy-Q1-2020-Q3-2026.csv"
)

raw_bond_df = pd.read_csv(file_path)


# ===== CHECK ORIGINAL DATASET =====
print(f"\n{'=' * 60}")
print(file_path)
print(raw_bond_df.columns.tolist())
print(raw_bond_df["TimeFrame"].value_counts().sort_index())
print(f"Initial row count: {len(raw_bond_df)}")
print("=" * 60)


# ===== 2. COLUMN STANDARDIZATION =====
raw_bond_df.columns = raw_bond_df.columns.str.strip()

raw_bond_df.rename(
    columns={
        "Location Id": "Location ID",
        "LocationID": "Location ID",
    },
    inplace=True,
)


# ===== 3. KEEP COLUMNS NEEDED FOR ANALYSIS =====
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
    "Lower Quartile Rent",
]

bond_df = raw_bond_df[columns_to_keep].copy()


# ===== 4. CLEAN CATEGORICAL COLUMNS =====
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


# ===== 5. CLEAN LOCATION ID =====
# Location ID is an identifier, so convert values such as
# 320800.0 into integer 320800.
bond_df["Location ID"] = pd.to_numeric(
    bond_df["Location ID"],
    errors="coerce",
).astype("Int64")


# ===== 6. CONVERT AND FILTER TIMEFRAME =====
bond_df["TimeFrame"] = pd.to_datetime(
    bond_df["TimeFrame"],
    errors="coerce",
)

target_timeframes = pd.to_datetime([
    "2025-10-01",
    "2026-01-01",
    "2026-04-01",
])

bond_df = bond_df[
    bond_df["TimeFrame"].isin(target_timeframes)
].copy()


# ===== 7. CLEAN NUMERIC COLUMNS =====
numeric_cols = [
    "Total Bonds",
    "Active Bonds",
    "Closed Bonds",
    "Median Rent",
    "Geometric Mean Rent",
    "Upper Quartile Rent",
    "Lower Quartile Rent",
]

for col in numeric_cols:
    bond_df[col] = pd.to_numeric(
        bond_df[col],
        errors="coerce",
    )


# ===== 8. HANDLE MISSING KEYS =====
initial_count = len(bond_df)

bond_df = bond_df.dropna(
    subset=["TimeFrame", "Location ID"]
).copy()

final_count = len(bond_df)


# ===== 9. CLEANING AUDIT =====
print("\n--- Data Cleaning Audit ---")
print(f"Rows retained after timeframe filter: {initial_count}")
print(f"Rows after dropping missing keys: {final_count}")
print(
    f"Rows removed during key cleaning: "
    f"{initial_count - final_count}"
)

print("\nMissing values per column:")
print(bond_df.isnull().sum())

print("\nRows per timeframe:")
print(
    bond_df["TimeFrame"]
    .value_counts()
    .sort_index()
)

print("\nLocation ID dtype:")
print(bond_df["Location ID"].dtype)

print("\nExample Location IDs:")
print(bond_df["Location ID"].head())


# ===== 10. EXPORT CLEANED DATASET =====
output_path = (
    BASE_DIR.parent
    / "cleaned_rental_bond_data.csv"
)

bond_df.to_csv(
    output_path,
    index=False,
)

print(
    f"\nCleaned dataset saved locally as "
    f"'{output_path.name}'."
)