import pandas as pd
from pathlib import Path


# Clean the Christchurch listing dataset created in Deliverable 3.
# Keep latitude and longitude because they are required later for area-code mapping.
# Document cleaning decisions, reasons, and consequences such as row loss.


# ===== 1. SETUP & LOAD DATASET =====
BASE_DIR = Path(__file__).resolve().parent
PROJECT_DELIVERABLES = BASE_DIR.parent

input_path = (
    PROJECT_DELIVERABLES
    / "combined_Christchurch_listings.csv"
)

df = pd.read_csv(input_path)

initial_rows = len(df)


# ===== 2. VALIDATE REQUIRED COLUMNS =====
required_columns = [
    "id",
    "host_id",
    "latitude",
    "longitude",
    "minimum_nights",
    "name",
    "host_name",
    "neighbourhood",
    "room_type",
    "last_review",
    "calculated_host_listings_count",
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )


# ===== 3. DROP UNNECESSARY COLUMNS =====
columns_to_drop = [
    "neighbourhood_group",
    "month_year",
]

df = df.drop(
    columns=columns_to_drop,
    errors="ignore",
)


# ===== 4. CONVERT DATA TYPES =====
df["host_id"] = pd.to_numeric(
    df["host_id"],
    errors="coerce",
).astype("Int64")

df["calculated_host_listings_count"] = pd.to_numeric(
    df["calculated_host_listings_count"],
    errors="coerce",
).astype("Int64")

df["minimum_nights"] = pd.to_numeric(
    df["minimum_nights"],
    errors="coerce",
).astype("Int64")


# ===== 5. DROP EXACT DUPLICATES =====
rows_before_duplicates = len(df)

df = df.drop_duplicates().copy()

duplicate_rows_removed = (
    rows_before_duplicates - len(df)
)


# ===== 6. CLEAN TEXT COLUMNS =====
text_columns = [
    "name",
    "host_name",
    "neighbourhood",
    "room_type",
]

for col in text_columns:
    df[col] = (
        df[col]
        .astype("string")
        .str.strip()
    )


# ===== 7. CLEAN DATE COLUMN =====
df["last_review"] = pd.to_datetime(
    df["last_review"],
    errors="coerce",
)


# ===== 8. SORT AND RESET INDEX =====
df = (
    df.sort_values(
        ["id", "last_review"],
        na_position="last",
    )
    .reset_index(drop=True)
)


# ===== 9. SANITY CHECK =====
assert df["latitude"].notna().all(), (
    "Missing latitude values remain."
)

assert df["longitude"].notna().all(), (
    "Missing longitude values remain."
)

assert df["latitude"].between(-90, 90).all(), (
    "Invalid latitude values found."
)

assert df["longitude"].between(-180, 180).all(), (
    "Invalid longitude values found."
)

assert df.duplicated().sum() == 0, (
    "Exact duplicate rows remain."
)

print("\nAirbnb sanity checks passed.")


# ===== 10. CLEANING AUDIT =====
print("\n--- Airbnb Data Cleaning Audit ---")

print(f"Initial row count: {initial_rows}")

print(
    f"Exact duplicate rows removed: "
    f"{duplicate_rows_removed}"
)

print(f"Final row count: {len(df)}")

print("\nMissing values per column:")
print(df.isnull().sum())

print("\nData types:")
print(df.dtypes)

print("\nExample coordinates:")
print(
    df[
        ["latitude", "longitude"]
    ].head()
)


# ===== 11. EXPORT CLEANED DATASET =====
output_path = (
    PROJECT_DELIVERABLES
    / "combined_Christchurch_listings_cleaned.csv"
)

df.to_csv(
    output_path,
    index=False,
)

print(
    f"\nCleaned dataset saved locally as "
    f"'{output_path.name}'."
)