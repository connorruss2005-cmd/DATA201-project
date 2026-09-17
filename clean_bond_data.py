from pathlib import Path
import pandas as pd

# 1. SETUP & LOAD DATASET
BASE_DIR = Path(__file__).resolve().parent
file_path = BASE_DIR / "Detailed-Quarterly-Tenancy-Q1-2020-Q3-2026.csv"

raw_bond_df = pd.read_csv(file_path)
print(f"Initial row count: {len(raw_bond_df)}")

# 2. COLUMN SELECTION & STANDARDIZATION
raw_bond_df.columns = raw_bond_df.columns.str.strip()

raw_bond_df.rename(
    columns={"Location Id": "Location ID", "LocationID": "Location ID"},
    inplace=True,
)

columns_to_keep = [
    "TimeFrame",
    "Location ID",
    "Dwelling Type",
    "Number of Beds",
    "Total Bonds",
    "Active Bonds",
    "Closed Bonds",
    "Median Rent",
    "Geometric Mean Rent",
]

existing_columns = [
    col for col in columns_to_keep if col in raw_bond_df.columns
]
bond_df = raw_bond_df[existing_columns].copy()

# 3. STRING & CATEGORICAL CLEANING
string_cols = ["TimeFrame", "Location ID", "Dwelling Type"]
for col in string_cols:
    if col in bond_df.columns:
        bond_df[col] = bond_df[col].astype(str).str.strip()

# 4. TIMEFRAME FILTERING (Matches YYYY-MM-DD quarter-start dates for 2020-2026)
quarter_months = ["01", "04", "07", "10"]
target_timeframes = [
    f"{year}-{month}-01"
    for year in range(2020, 2027)
    for month in quarter_months
]

bond_df = bond_df[bond_df["TimeFrame"].isin(target_timeframes)].copy()

# 5. NUMERIC SANITIZATION
numeric_cols = [
    "Total Bonds",
    "Active Bonds",
    "Closed Bonds",
    "Median Rent",
    "Geometric Mean Rent",
]

for col in numeric_cols:
    if col in bond_df.columns:
        if bond_df[col].dtype == "object":
            bond_df[col] = (
                bond_df[col]
                .astype(str)
                .str.replace("$", "", regex=False)
                .str.replace(",", "", regex=False)
                .str.strip()
            )
        bond_df[col] = pd.to_numeric(bond_df[col], errors="coerce")

# 6. MISSING VALUE HANDLING & AUDIT
initial_count = len(bond_df)
bond_df = bond_df.dropna(subset=["TimeFrame", "Location ID"])
final_count = len(bond_df)

print("\n--- Data Cleaning Audit ---")
print(f"Rows retained after timeframe filter: {initial_count}")
print(f"Rows after dropping missing keys: {final_count}")
print(f"Rows removed during key cleaning: {initial_count - final_count}")
print("\nMissing values per column:")
print(bond_df.isnull().sum())

# 7. EXPORT CLEANED DATASET
output_path = BASE_DIR / "cleaned_rental_bond_data.csv"
bond_df.to_csv(output_path, index=False)
print(f"\nCleaned dataset saved locally as '{output_path.name}'.")