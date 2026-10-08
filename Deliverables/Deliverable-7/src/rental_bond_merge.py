import sqlite3
from pathlib import Path

import pandas as pd


def merge_airbnb_bonds(listings_df, bonds_df):
    """
    Merge Airbnb listings with the latest available rental-bond
    information for each area.

    Parameters
    ----------
    listings_df : pandas.DataFrame
        Airbnb data containing an 'area_code' column.

    bonds_df : pandas.DataFrame
        Cleaned rental-bond data containing 'Location ID',
        'TimeFrame', and rental statistics.

    Returns
    -------
    pandas.DataFrame
        Airbnb listings with the latest available rental-bond
        information added.
    """

    # --------------------------------------------------------
    # 1. Validate required columns
    # --------------------------------------------------------

    required_listing_columns = {
        "id",
        "area_code",
    }

    required_bond_columns = {
        "Location ID",
        "TimeFrame",
        "Dwelling Type",
        "Number Of Beds",
        "Total Bonds",
        "Active Bonds",
        "Closed Bonds",
        "Median Rent",
        "Geometric Mean Rent",
        "Upper Quartile Rent",
        "Lower Quartile Rent",
    }

    missing_listing_columns = (
        required_listing_columns - set(listings_df.columns)
    )

    if missing_listing_columns:
        raise ValueError(
            "Airbnb data is missing required columns: "
            f"{missing_listing_columns}"
        )

    missing_bond_columns = (
        required_bond_columns - set(bonds_df.columns)
    )

    if missing_bond_columns:
        raise ValueError(
            "Rental-bond data is missing required columns: "
            f"{missing_bond_columns}"
        )

    # Work on copies so the input DataFrames are not modified.
    listings = listings_df.copy()
    bonds = bonds_df.copy()

    original_row_count = len(listings)

    # --------------------------------------------------------
    # 2. Prepare bond data
    # --------------------------------------------------------

    bond_all_rows = bonds[
        (bonds["Dwelling Type"] == "ALL")
        & (bonds["Number Of Beds"] == "ALL")
    ].copy()

    if bond_all_rows.empty:
        raise ValueError(
            "No area-wide rental-bond records were found."
        )

    # Make sure TimeFrame can be compared correctly.
    bond_all_rows["TimeFrame"] = pd.to_datetime(
        bond_all_rows["TimeFrame"],
        errors="coerce",
    )

    if bond_all_rows["TimeFrame"].isna().any():
        raise ValueError(
            "Invalid TimeFrame values found in rental-bond data."
        )

    # --------------------------------------------------------
    # 3. Keep the latest bond quarter for each area
    # --------------------------------------------------------

    latest_quarter = bond_all_rows["TimeFrame"].max()

    bond_latest_per_area = bond_all_rows[
        bond_all_rows["TimeFrame"] == latest_quarter
    ].copy()

    # Check that there is only one bond row per area.
    duplicate_area_codes = (
        bond_latest_per_area["Location ID"]
        .duplicated()
    )

    if duplicate_area_codes.any():
        raise ValueError(
            "Multiple latest rental-bond rows exist for the "
            "same Location ID."
        )

    # --------------------------------------------------------
    # 4. Prepare the columns used in the merge
    # --------------------------------------------------------

    bond_latest_per_area = bond_latest_per_area[
        [
            "Location ID",
            "TimeFrame",
            "Total Bonds",
            "Active Bonds",
            "Closed Bonds",
            "Median Rent",
            "Geometric Mean Rent",
            "Upper Quartile Rent",
            "Lower Quartile Rent",
        ]
    ].copy()

    bond_latest_per_area = bond_latest_per_area.rename(
        columns={
            "Location ID": "area_code",
            "TimeFrame": "bond_data_quarter",
            "Total Bonds": "total_bonds",
            "Active Bonds": "active_bonds",
            "Closed Bonds": "closed_bonds",
            "Median Rent": "median_rent",
            "Geometric Mean Rent": "geometric_mean_rent",
            "Upper Quartile Rent": "upper_quartile_rent",
            "Lower Quartile Rent": "lower_quartile_rent",
        }
    )

    # Make both merge keys numeric.
    listings["area_code"] = pd.to_numeric(
        listings["area_code"],
        errors="coerce",
    )

    bond_latest_per_area["area_code"] = pd.to_numeric(
        bond_latest_per_area["area_code"],
        errors="coerce",
    )

    # --------------------------------------------------------
    # 5. Perform the left join
    # --------------------------------------------------------

    result = listings.merge(
        bond_latest_per_area,
        on="area_code",
        how="left",
        validate="many_to_one",
    )

    # --------------------------------------------------------
    # 6. Sanity checks
    # --------------------------------------------------------

    print("\nRental-bond merge sanity checks")
    print("--------------------------------")

    # No fan-out.
    if len(result) != original_row_count:
        raise ValueError(
            "Row count changed during rental-bond merge. "
            f"Before: {original_row_count}, "
            f"After: {len(result)}"
        )

    # Primary identifiers must exist.
    if result["id"].isna().any():
        raise ValueError(
            "Missing Airbnb listing IDs after merge."
        )

    if result["area_code"].isna().any():
        raise ValueError(
            "Missing area codes before rental-bond merge."
        )

    # Match rate is reported rather than hard-coded to an old range.
    match_rate = result["median_rent"].notna().mean()

    # Rental values should be positive when present.
    rent_columns = [
        "median_rent",
        "geometric_mean_rent",
        "upper_quartile_rent",
        "lower_quartile_rent",
    ]

    for column in rent_columns:
        values = result[column].dropna()

        if (values <= 0).any():
            raise ValueError(
                f"Non-positive values found in '{column}'."
            )

    print(f"Airbnb rows: {len(listings)}")
    print(f"Rows after merge: {len(result)}")
    print(f"Bond match rate: {match_rate:.1%}")
    print(
        "Latest bond quarter used: "
        f"{latest_quarter.strftime('%Y-%m-%d')}"
    )

    print("Rental-bond merge sanity checks passed.")

    return result