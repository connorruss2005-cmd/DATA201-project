from pathlib import Path
import os

import pandas as pd
import requests


# ============================================================
# SETTINGS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

API_URL = (
    "https://datafinder.stats.govt.nz/"
    "services/query/v1/vector.json"
)

LAYER_ID = 123515
AREA_CODE_FIELD = "SA22026_V1_00"

MAPPING_PATH = (
    BASE_DIR.parent
    / "area_code_mapping.csv"
)

# ============================================================
# GET ONE SA2 AREA CODE
# ============================================================

def get_area_code(latitude, longitude, api_key, max_retries=3):
    """
    Query the Koordinates API and return the SA2 area code
    for one latitude/longitude pair.
    """

    params = {
        "key": api_key,
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
                timeout=30,
            )

            response.raise_for_status()

            data = response.json()

            features = (
                data["vectorQuery"]
                ["layers"]
                [str(LAYER_ID)]
                ["features"]
            )

            if not features:
                return None

            properties = features[0]["properties"]

            return properties.get(AREA_CODE_FIELD)

        except requests.RequestException as e:

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
# ADD AREA CODES TO AIRBNB DATA
# ============================================================

def add_area_codes(df, mapping_path=MAPPING_PATH):
    """
    Add SA2 area codes to an Airbnb DataFrame.

    Existing mappings are reused.
    Only previously unseen coordinates are queried.
    """

    mapping_path = Path(mapping_path)

    required_columns = {
        "latitude",
        "longitude",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    api_key = os.getenv("KOORDINATES_API_KEY")

    if not api_key:
        raise ValueError(
            "KOORDINATES_API_KEY is not set."
        )

    api_key = api_key.strip()

    original_row_count = len(df)

    # --------------------------------------------------------
    # Get unique coordinates from the current Airbnb data
    # --------------------------------------------------------

    unique_coords = (
        df[
            ["latitude", "longitude"]
        ]
        .dropna()
        .drop_duplicates()
        .reset_index(drop=True)
    )

    print(
        "\nUnique coordinates in current dataset:",
        len(unique_coords)
    )

    # --------------------------------------------------------
    # Load existing mapping if available
    # --------------------------------------------------------

    if mapping_path.exists():

        print("Loading existing area-code mapping...")

        existing_mapping = pd.read_csv(mapping_path)

        required_mapping_columns = {
            "latitude",
            "longitude",
            "area_code",
        }

        missing_mapping_columns = (
            required_mapping_columns
            - set(existing_mapping.columns)
        )

        if missing_mapping_columns:
            raise ValueError(
                "Mapping file is missing required columns: "
                f"{missing_mapping_columns}"
            )

    else:

        print("No existing mapping found.")

        existing_mapping = pd.DataFrame(
            columns=[
                "latitude",
                "longitude",
                "area_code",
            ]
        )

    # --------------------------------------------------------
    # Find coordinates that have not been mapped before
    # --------------------------------------------------------
    valid_existing_mapping = (
        existing_mapping[
            existing_mapping["area_code"].notna()
        ]
        .drop_duplicates(
            subset=["latitude", "longitude"]
        )
    )

    coords_with_mapping = unique_coords.merge(
        valid_existing_mapping[
            ["latitude", "longitude"]
        ],
        on=["latitude", "longitude"],
        how="left",
        indicator=True,
    )

    new_coords = (
        coords_with_mapping[
            coords_with_mapping["_merge"] == "left_only"
        ][["latitude", "longitude"]]
        .reset_index(drop=True)
    )

    print(
        "New coordinates requiring API queries:",
        len(new_coords)
    )

    # --------------------------------------------------------
    # Query only new coordinates
    # --------------------------------------------------------

    new_mapping_rows = []

    for i, row in new_coords.iterrows():

        latitude = row["latitude"]
        longitude = row["longitude"]

        area_code = get_area_code(
            latitude,
            longitude,
            api_key,
        )

        new_mapping_rows.append(
            {
                "latitude": latitude,
                "longitude": longitude,
                "area_code": area_code,
            }
        )

        if (i + 1) % 100 == 0:
            print(
                f"Processed {i + 1} / "
                f"{len(new_coords)} new coordinates"
            )

    new_mapping = pd.DataFrame(new_mapping_rows)

    # --------------------------------------------------------
    # Combine old and new mappings
    # --------------------------------------------------------

    if not new_mapping.empty:

        full_mapping = pd.concat(
            [
                existing_mapping,
                new_mapping,
            ],
            ignore_index=True,
        )

    else:
        full_mapping = existing_mapping.copy()

    full_mapping = (
        full_mapping
        .drop_duplicates(
            subset=["latitude", "longitude"],
            keep="last",
        )
        .reset_index(drop=True)
    )

    full_mapping["area_code"] = pd.to_numeric(
        full_mapping["area_code"],
        errors="coerce",
    ).astype("Int64")

    mapping_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    full_mapping.to_csv(
        mapping_path,
        index=False,
    )

    # --------------------------------------------------------
    # Merge area codes back into Airbnb data
    # --------------------------------------------------------

    mapped_df = df.merge(
        full_mapping,
        on=["latitude", "longitude"],
        how="left",
        validate="many_to_one",
    )

    # --------------------------------------------------------
    # SANITY CHECK
    # --------------------------------------------------------

    if len(mapped_df) != original_row_count:
        raise ValueError(
            "Row count changed during area-code merge. "
            f"Before: {original_row_count}, "
            f"After: {len(mapped_df)}"
        )

    missing_area_codes = (
        mapped_df["area_code"]
        .isna()
        .sum()
    )

    print("\nArea-code mapping summary")
    print("-------------------------")
    print("Rows:", len(mapped_df))
    print("New coordinates queried:", len(new_coords))
    print("Missing area codes:", missing_area_codes)

    if missing_area_codes > 0:
        raise ValueError(
            f"{missing_area_codes} listings are missing area codes."
        )

    print("Area-code mapping sanity check passed.")

    return mapped_df