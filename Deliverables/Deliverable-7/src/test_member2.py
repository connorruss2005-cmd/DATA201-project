from pathlib import Path
import shutil
import time

import pandas as pd

from airbnb_cleaning import clean_airbnb
from query_api import add_area_codes


# ============================================================
# 1. PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DELIVERABLES_DIR = BASE_DIR.parent.parent

UPDATED_LISTINGS_DIR = (
    DELIVERABLES_DIR
    / "Deliverable-3"
    / "Output"
    / "Updated_listings"
)

JULY_PATH = (
    UPDATED_LISTINGS_DIR
    / "listings_july_2026_updated.csv"
)

AUGUST_PATH = (
    UPDATED_LISTINGS_DIR
    / "listings_august_2026_updated.csv"
)

# Existing full mapping from Deliverable 5
OLD_MAPPING_PATH = (
    DELIVERABLES_DIR
    / "Deliverable-5"
    / "area_code_mapping.csv"
)

# Deliverable 7 mapping
MAPPING_PATH = (
    DELIVERABLES_DIR
    / "Deliverable-7"
    / "area_code_mapping.csv"
)


# ============================================================
# 2. CHECK INPUT FILES
# ============================================================

if not JULY_PATH.exists():
    raise FileNotFoundError(
        f"July dataset not found: {JULY_PATH}"
    )

if not AUGUST_PATH.exists():
    raise FileNotFoundError(
        f"August dataset not found: {AUGUST_PATH}"
    )


# ============================================================
# 3. LOAD JULY / AUGUST DATA
# ============================================================

july_df = pd.read_csv(JULY_PATH)
august_df = pd.read_csv(AUGUST_PATH)

# Make sure each month can be identified
july_df["month_year"] = "July 2026"
august_df["month_year"] = "August 2026"

df = pd.concat(
    [
        july_df,
        august_df,
    ],
    ignore_index=True,
)

print("\nNew-month input test")
print("--------------------")
print("July rows:", len(july_df))
print("August rows:", len(august_df))
print("Combined rows:", len(df))

print("\nMonths included:")
print(
    df["month_year"]
    .value_counts()
    .sort_index()
)


# ============================================================
# 4. TEST CLEANING
# ============================================================

cleaned_df = clean_airbnb(df)

print("\nCleaning test")
print("-------------")
print("Cleaned rows:", len(cleaned_df))
print(
    "Latitude missing:",
    cleaned_df["latitude"].isna().sum()
)
print(
    "Longitude missing:",
    cleaned_df["longitude"].isna().sum()
)

assert cleaned_df["latitude"].notna().all()
assert cleaned_df["longitude"].notna().all()

expected_months = {
    "July 2026",
    "August 2026",
}

actual_months = set(
    cleaned_df["month_year"]
    .dropna()
    .unique()
)

assert expected_months.issubset(actual_months), (
    "July or August 2026 is missing after cleaning."
)

print("Cleaning test passed.")


# ============================================================
# 5. PREPARE EXISTING AREA-CODE MAPPING
# ============================================================

# Copy the Deliverable 5 mapping only if a Deliverable 7
# mapping has not already been created.
if not MAPPING_PATH.exists():

    if OLD_MAPPING_PATH.exists():

        shutil.copy2(
            OLD_MAPPING_PATH,
            MAPPING_PATH,
        )

        print(
            "\nExisting Deliverable 5 mapping copied "
            "to Deliverable 7."
        )

    else:
        print(
            "\nNo previous mapping found. "
            "New mappings will be created."
        )


# ============================================================
# 6. CREATE A SMALL JULY / AUGUST TEST SAMPLE
# ============================================================

# Use 50 rows from each month so BOTH months are tested.
july_test = (
    cleaned_df[
        cleaned_df["month_year"] == "July 2026"
    ]
    .head(50)
)

august_test = (
    cleaned_df[
        cleaned_df["month_year"] == "August 2026"
    ]
    .head(50)
)

test_df = pd.concat(
    [
        july_test,
        august_test,
    ],
    ignore_index=True,
)

print("\nAPI test sample")
print("---------------")
print(
    test_df["month_year"]
    .value_counts()
    .sort_index()
)


# ============================================================
# 7. TEST AREA-CODE MAPPING
# ============================================================

mapped_df = add_area_codes(
    test_df,
    mapping_path=MAPPING_PATH,
)

print("\nAPI mapping test")
print("----------------")
print("Rows before mapping:", len(test_df))
print("Rows after mapping:", len(mapped_df))

print(
    "Missing area codes:",
    mapped_df["area_code"].isna().sum()
)

assert len(mapped_df) == len(test_df), (
    "Row count changed during area-code mapping."
)

assert mapped_df["area_code"].notna().all(), (
    "Missing area codes remain after mapping."
)

mapped_months = set(
    mapped_df["month_year"]
    .dropna()
    .unique()
)

assert expected_months.issubset(mapped_months), (
    "July or August 2026 is missing after API mapping."
)


# ============================================================
# 8. SUCCESS MESSAGE
# ============================================================

print(
    "\nChecking July/August API mapping",
    end="",
    flush=True,
)

for _ in range(3):
    time.sleep(1.0)
    print(".", end="", flush=True)

print("\n✓ API mapping test passed!")
print("  July and August listings were mapped successfully.")


# ============================================================
# 9. FINAL CHECK
# ============================================================

print("\n" + "=" * 50)
print("✓ Member 2 final integration test passed!")
print("✓ July 2026 included")
print("✓ August 2026 included")
print("✓ No rows lost during API mapping")
print("✓ No missing area codes")
print("=" * 50)