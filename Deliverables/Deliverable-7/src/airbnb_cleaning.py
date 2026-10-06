import pandas as pd


def clean_airbnb(df):
    """
    Clean an Airbnb DataFrame for later area-code mapping.

    The function does not read or save files.
    It receives a DataFrame and returns a cleaned DataFrame,
    so it can be reused by the automated pipeline.
    """

    # Work on a copy so the original DataFrame is not modified
    df = df.copy()

    initial_rows = len(df)

    # ========================================================
    # 1. VALIDATE REQUIRED COLUMNS
    # ========================================================

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

    # ========================================================
    # 2. DROP UNNECESSARY COLUMNS
    # ========================================================

    # Keep month_year because it is needed to identify
    # different monthly datasets in Deliverable 7.
    columns_to_drop = [
        "neighbourhood_group",
    ]

    df = df.drop(
        columns=columns_to_drop,
        errors="ignore",
    )

    # ========================================================
    # 3. CONVERT DATA TYPES
    # ========================================================

    integer_columns = [
        "host_id",
        "calculated_host_listings_count",
        "minimum_nights",
    ]

    for col in integer_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce",
        ).astype("Int64")

    # Coordinates must be numeric for Koordinates API mapping
    df["latitude"] = pd.to_numeric(
        df["latitude"],
        errors="coerce",
    )

    df["longitude"] = pd.to_numeric(
        df["longitude"],
        errors="coerce",
    )

    # ========================================================
    # 4. DROP EXACT DUPLICATES
    # ========================================================

    rows_before_duplicates = len(df)

    df = df.drop_duplicates().copy()

    duplicate_rows_removed = (
        rows_before_duplicates - len(df)
    )

    # ========================================================
    # 5. CLEAN TEXT COLUMNS
    # ========================================================

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

    # ========================================================
    # 6. CLEAN DATE COLUMN
    # ========================================================

    df["last_review"] = pd.to_datetime(
        df["last_review"],
        errors="coerce",
    )

    # ========================================================
    # 7. SORT AND RESET INDEX
    # ========================================================

    df = (
        df.sort_values(
            ["id", "last_review"],
            na_position="last",
        )
        .reset_index(drop=True)
    )

    # ========================================================
    # 8. SANITY CHECK
    # ========================================================

    if df["latitude"].isna().any():
        raise ValueError(
            "Missing or invalid latitude values remain."
        )

    if df["longitude"].isna().any():
        raise ValueError(
            "Missing or invalid longitude values remain."
        )

    if not df["latitude"].between(-90, 90).all():
        raise ValueError(
            "Invalid latitude values found."
        )

    if not df["longitude"].between(-180, 180).all():
        raise ValueError(
            "Invalid longitude values found."
        )

    if df.duplicated().any():
        raise ValueError(
            "Exact duplicate rows remain."
        )

    # ========================================================
    # 9. CLEANING AUDIT
    # ========================================================

    print("\n--- Airbnb Data Cleaning Audit ---")
    print(f"Initial rows: {initial_rows}")
    print(
        f"Exact duplicate rows removed: "
        f"{duplicate_rows_removed}"
    )
    print(f"Final rows: {len(df)}")

    if "month_year" in df.columns:
        print("\nRows by month:")
        print(
            df["month_year"]
            .value_counts()
            .sort_index()
        )

    print("\nAirbnb cleaning sanity checks passed.")

    # ========================================================
    # 10. RETURN CLEANED DATAFRAME
    # ========================================================

    return df