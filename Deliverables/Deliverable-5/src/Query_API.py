from pathlib import Path
import os
import pandas as pd
import requests


# ============================================================
# 1. FILE PATHS AND SETTINGS
# ============================================================

# Location of this script:
# Deliverables/Deliverable-5/src/Query_API.py
BASE_DIR = Path(__file__).resolve().parent

# Go from:
# src -> Deliverable-5 -> Deliverables
DELIVERABLES_DIR = BASE_DIR.parent.parent

# Input dataset
AIRBNB_PATH = DELIVERABLES_DIR / "combined_Christchurch_listings_cleaned.csv"

# Mapping and final output
MAPPING_PATH = BASE_DIR.parent / "area_code_mapping.csv"
OUTPUT_PATH = (
    BASE_DIR.parent
    / "Output"
    / "Airbnb listings with area codes"
    / "combined_Christchurch_listings_with_area_codes.csv"
)

# Koordinates API settings
API_URL = "https://datafinder.stats.govt.nz/services/query/v1/vector.json"
LAYER_ID = 123515
AREA_CODE_FIELD = "SA22026_V1_00"


# ============================================================
# 2. LOAD CLEANED AIRBNB DATA
# ============================================================

if not AIRBNB_PATH.exists():
    raise FileNotFoundError(
        f"Airbnb input file not found:\n{AIRBNB_PATH}"
    )

df = pd.read_csv(AIRBNB_PATH)

print("Total Airbnb rows:", len(df))
print("Input dataset shape:", df.shape)


# ============================================================
# 3. PREPARE UNIQUE COORDINATES
# ============================================================

unique_coords = (
    df[["latitude", "longitude"]]
    .drop_duplicates()
    .reset_index(drop=True)
)

print("Unique coordinates:", len(unique_coords))


# ============================================================
# 4. GET API KEY
# ============================================================

API_KEY = os.getenv("KOORDINATES_API_KEY")

if not API_KEY:
    raise ValueError(
        "KOORDINATES_API_KEY is not set. "
        "Please set the environment variable before running the script."
    )

API_KEY = API_KEY.strip()


# ============================================================
# 5. FUNCTION TO GET SA2 AREA CODE
# ============================================================

def get_area_code(latitude, longitude, max_retries=3):
    """
    Query the Koordinates API using a latitude and longitude
    and return the corresponding SA2 area code.

    Parameters:
        latitude: Latitude of the Airbnb coordinate.
        longitude: Longitude of the Airbnb coordinate.
        max_retries: Maximum number of API attempts.

    Returns:
        SA2 area code if found, otherwise None.
    """

    params = {
        "key": API_KEY,
        "layer": LAYER_ID,
        "x": longitude,
        "y": latitude,
        "max_results": 1,
        "radius": 0,
        "geometry": "false",
        "with_field_names": "true",
    }

    for attempt in range(max_retries):
        try:
            response = requests.get(
                API_URL,
                params=params,
                timeout=30
            )

            response.raise_for_status()

            data = response.json()

            features = (
                data["vectorQuery"]["layers"][str(LAYER_ID)]["features"]
            )

            if not features:
                return None

            properties = features[0]["properties"]

            return properties.get(AREA_CODE_FIELD)

        except Exception as e:

            if attempt < max_retries - 1:
                print(
                    f"Retrying {latitude}, {longitude} "
                    f"(attempt {attempt + 2}/{max_retries})"
                )

            else:
                print(
                    f"Failed after {max_retries} attempts for "
                    f"{latitude}, {longitude}: {e}"
                )

    return None


# ============================================================
# 6. TEST THE API FUNCTION
# ============================================================

first_latitude = unique_coords.iloc[0]["latitude"]
first_longitude = unique_coords.iloc[0]["longitude"]

test_area_code = get_area_code(
    first_latitude,
    first_longitude
)

print("\nAPI function test")
print("-----------------")
print("Test latitude:", first_latitude)
print("Test longitude:", first_longitude)
print("Test area code:", test_area_code)

if test_area_code is None:
    raise ValueError(
        "API test failed: no area code was returned for the test coordinate."
    )


# ============================================================
# 7. LOAD OR CREATE AREA-CODE MAPPING
# ============================================================

if MAPPING_PATH.exists():

    print("\nLoading existing area-code mapping...")
    unique_coords = pd.read_csv(MAPPING_PATH)

    required_columns = {
        "latitude",
        "longitude",
        "area_code"
    }

    missing_columns = required_columns - set(unique_coords.columns)

    if missing_columns:
        raise ValueError(
            f"Mapping file is missing required columns: {missing_columns}"
        )

    print("Existing mapping loaded.")

else:

    print("\nNo existing area-code mapping found.")
    print("Starting API queries...")

    area_codes = []

    for i, row in unique_coords.iterrows():

        latitude = row["latitude"]
        longitude = row["longitude"]

        area_code = get_area_code(
            latitude,
            longitude
        )

        area_codes.append(area_code)

        # Save progress every 100 coordinates
        if (i + 1) % 100 == 0:

            mapping_progress = unique_coords.iloc[:i + 1].copy()
            mapping_progress["area_code"] = area_codes

            mapping_progress.to_csv(
                MAPPING_PATH,
                index=False
            )

            print(
                f"Processed {i + 1} / {len(unique_coords)} coordinates"
            )

    unique_coords["area_code"] = area_codes

    unique_coords.to_csv(
        MAPPING_PATH,
        index=False
    )

    print("Area-code mapping saved.")


# ============================================================
# 8. SANITY CHECK THE AREA-CODE MAPPING
# ============================================================

print("\nMapping sanity check")
print("--------------------")

print(
    "Unique coordinates in mapping:",
    len(unique_coords)
)

missing_area_codes = unique_coords["area_code"].isna().sum()

print(
    "Missing area codes:",
    missing_area_codes
)

if missing_area_codes > 0:
    raise ValueError(
        f"{missing_area_codes} coordinates do not have an area code."
    )

print("Mapping sanity check passed.")


# ============================================================
# 9. MERGE AREA CODES WITH AIRBNB DATA
# ============================================================

df = df.merge(
    unique_coords,
    on=["latitude", "longitude"],
    how="left",
    validate="many_to_one"
)


# ============================================================
# 10. SANITY CHECK FINAL DATASET
# ============================================================

print("\nFinal dataset sanity check")
print("--------------------------")

print("Airbnb rows after merge:", len(df))

missing_final_area_codes = df["area_code"].isna().sum()

print(
    "Missing area codes after merge:",
    missing_final_area_codes
)

if len(df) != 28390:
    raise ValueError(
        f"Unexpected row count after merge: {len(df)}. "
        "Expected 28,390 rows."
    )

if missing_final_area_codes > 0:
    raise ValueError(
        f"{missing_final_area_codes} Airbnb listings are missing area codes."
    )

print("Final dataset sanity check passed.")


# ============================================================
# 11. SAVE FINAL DATASET
# ============================================================

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\nFinal dataset saved to:")
print(OUTPUT_PATH)

print("\nFinal dataset shape:", df.shape)

print(
    "Area-code column added:",
    "area_code" in df.columns
)

print(
    "Missing area codes:",
    df["area_code"].isna().sum()
)