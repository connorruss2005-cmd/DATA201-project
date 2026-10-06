from pathlib import Path
import pandas as pd

from airbnb_cleaning import clean_airbnb
from query_api import add_area_codes


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DELIVERABLES_DIR = BASE_DIR.parent.parent

INPUT_PATH = (
    DELIVERABLES_DIR
    / "combined_Christchurch_listings.csv"
)

# Reuse the mapping created in Deliverable 5
MAPPING_PATH = (
    DELIVERABLES_DIR
    / "Deliverable-5"
    / "area_code_mapping.csv"
)


# ============================================================
# 1. LOAD EXISTING AIRBNB DATA
# ============================================================

df = pd.read_csv(INPUT_PATH)

print("Original rows:", len(df))


# ============================================================
# 2. TEST CLEANING
# ============================================================

cleaned_df = clean_airbnb(df)

print("\nCleaning test")
print("-------------")
print("Cleaned rows:", len(cleaned_df))
print("Latitude missing:", cleaned_df["latitude"].isna().sum())
print("Longitude missing:", cleaned_df["longitude"].isna().sum())

assert cleaned_df["latitude"].notna().all()
assert cleaned_df["longitude"].notna().all()

print("Cleaning test passed.")


# ============================================================
# 3. TEST AREA-CODE MAPPING
# ============================================================

# Use a small sample first
test_df = cleaned_df.head(100).copy()

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

assert len(mapped_df) == len(test_df)
assert mapped_df["area_code"].notna().all()

print("API mapping test passed.")


# ============================================================
# 4. FINAL CHECK
# ============================================================

print("\nMember 2 integration test passed.")