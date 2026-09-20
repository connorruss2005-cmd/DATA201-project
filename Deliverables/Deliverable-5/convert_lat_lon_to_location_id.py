from pathlib import Path
import os
import pandas as pd
import requests


# ===== 1. LOAD CLEANED AIRBNB DATA =====
BASE_DIR = Path(__file__).resolve().parent

airbnb_path = BASE_DIR.parent / "combined_Christchurch_listings_cleaned.csv"
cleaned_airbnb_df = pd.read_csv(airbnb_path)


# ===== 2. SELECT ONE COORDINATE FOR TESTING =====
latitude = cleaned_airbnb_df.iloc[0]["latitude"]
longitude = cleaned_airbnb_df.iloc[0]["longitude"]

print("\n" + "=" * 60)
print("Test coordinate")
print("Latitude:", latitude)
print("Longitude:", longitude)
print("=" * 60)


# ===== 3. API REQUEST =====
API_KEY = os.getenv("KOORDINATES_API_KEY")

if not API_KEY:
    raise ValueError("KOORDINATES_API_KEY is not set.")

API_KEY = API_KEY.strip()

url = "https://datafinder.stats.govt.nz/services/query/v1/vector.json"

LAYER_ID = 123515

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
    url,
    params=params,
    timeout=30,
)

print("Status code:", response.status_code)

if response.status_code != 200:
    print("Error response:", response.text)

response.raise_for_status()

data = response.json()


# ===== 4. EXTRACT SA2 AREA CODE =====
layer_data = data["vectorQuery"]["layers"][str(LAYER_ID)]
features = layer_data["features"]

if not features:
    raise ValueError("No matching SA2 area found for this coordinate.")

properties = features[0]["properties"]

area_code = int(properties["SA22026_V1_00"])
area_name = properties["SA22026_V1_00_NAME"]

print("\nSA2 code:", area_code)
print("SA2 name:", area_name)


# ===== 5. VERIFY AGAINST RENTAL BOND DATA =====
bond_path = BASE_DIR.parent / "cleaned_rental_bond_data.csv"
bond_df = pd.read_csv(bond_path)

matched_bond = bond_df[
    bond_df["Location ID"] == area_code
]

print("\nMatching rental bond records:")
print(
    matched_bond[
        ["Location ID", "TimeFrame", "Median Rent"]
    ].head()
)

print("\nNumber of matching rental bond records:")
print(len(matched_bond))