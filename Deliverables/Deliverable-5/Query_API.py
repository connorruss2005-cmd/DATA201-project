from pathlib import Path
import os
import pandas as pd
import requests


# ===== 1. LOAD CLEANED AIRBNB DATA =====

BASE_DIR = Path(__file__).resolve().parent

airbnb_path = BASE_DIR.parent / "combined_Christchurch_listings_cleaned.csv"

df = pd.read_csv(airbnb_path)

print("Total Airbnb rows:", len(df))


# ===== 2. GET UNIQUE COORDINATES =====

unique_coords = df[["latitude", "longitude"]].drop_duplicates().reset_index(drop=True)

print("Unique coordinates:", len(unique_coords))


# ===== 3. GET API KEY =====

API_KEY = os.getenv("KOORDINATES_API_KEY")

if not API_KEY:
    raise ValueError("KOORDINATES_API_KEY is not set.")

API_KEY = API_KEY.strip()


# ===== 4. KOORDINATES API SETTINGS =====

URL = "https://datafinder.stats.govt.nz/services/query/v1/vector.json"

LAYER_ID = 123515


# ===== 5. TEST ONE COORDINATE =====

latitude = unique_coords.iloc[0]["latitude"]
longitude = unique_coords.iloc[0]["longitude"]

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

response = requests.get(
    URL,
    params=params,
    timeout=30,
)

print("Test status:", response.status_code)

response.raise_for_status()

data = response.json()

features = data["vectorQuery"]["layers"][str(LAYER_ID)]["features"]

if features:
    properties = features[0]["properties"]

    area_code = properties["SA22026_V1_00"]
    area_name = properties["SA22026_V1_00_NAME"]

    print("Test area code:", area_code)
    print("Test area name:", area_name)

else:
    print("No area found.")


#==== 6. ADDING API FUNCTION =====

def get_area_code(latitude, longitude, max_retries=3):

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
                URL,
                params=params,
                timeout=30,
            )

            response.raise_for_status()

            data = response.json()

            features = data["vectorQuery"]["layers"][str(LAYER_ID)]["features"]

            if not features:
                return None

            properties = features[0]["properties"]

            return properties["SA22026_V1_00"]

        except Exception as e:

            if attempt < max_retries - 1:
                print(
                    f"Retrying {latitude}, {longitude} "
                    f"(attempt {attempt + 2}/{max_retries})"
                )
            else:
                print(
                    f"Failed after {max_retries} attempts "
                    f"for {latitude}, {longitude}: {e}"
                )

    return None

# ===== TEST THE FUNCTION =====

test_area_code = get_area_code(
    unique_coords.iloc[0]["latitude"],
    unique_coords.iloc[0]["longitude"]
)

print("Function test area code:", test_area_code)

# ===== 7. QUERY ALL UNIQUE COORDINATES =====

mapping_path = BASE_DIR / "area_code_mapping.csv"

# Load existing mapping if available
if mapping_path.exists():

    print("Loading existing area-code mapping...")

    unique_coords = pd.read_csv(mapping_path)

    print("Existing mapping loaded.")

else:

    print("No existing mapping found. Starting API queries...")

    area_codes = []

    for i, row in unique_coords.iterrows():

        latitude = row["latitude"]
        longitude = row["longitude"]

        area_code = get_area_code(latitude, longitude)

        area_codes.append(area_code)

        # Save progress every 100 coordinates
        if (i + 1) % 100 == 0:

            unique_coords_temp = unique_coords.iloc[:i + 1].copy()
            unique_coords_temp["area_code"] = area_codes

            unique_coords_temp.to_csv(mapping_path, index=False)

            print(
                f"Processed {i + 1} / {len(unique_coords)} coordinates"
            )

    unique_coords["area_code"] = area_codes

    unique_coords.to_csv(mapping_path, index=False)

    print("Area-code mapping saved.")


print("Finished querying coordinates.")
print("Unique coordinates:", len(unique_coords))
print("Missing area codes:", unique_coords["area_code"].isna().sum())

print("\nFirst 10 results:")
print(unique_coords.head(10))

# ===== 8. ADD AREA CODE TO AIRBNB DATA =====

df = df.merge(
    unique_coords,
    on=["latitude", "longitude"],
    how="left"
)

print("\nAfter adding area codes:")
print("Airbnb rows:", len(df))
print("Missing area codes:", df["area_code"].isna().sum())

print("\nFirst 10 Airbnb rows with area codes:")
print(df[["latitude", "longitude", "area_code"]].head(10))

# ===== 9. SAVE FINAL AIRBNB DATASET =====

output_path = BASE_DIR / "combined_Christchurch_listings_with_area_codes.csv"

df.to_csv(output_path, index=False)

print("\nFinal dataset saved to:", output_path)
print("Final dataset shape:", df.shape)
print("Area-code column added:", "area_code" in df.columns)
print("Missing area codes:", df["area_code"].isna().sum())