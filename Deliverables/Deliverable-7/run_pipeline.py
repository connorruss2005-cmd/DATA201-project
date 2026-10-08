from pathlib import Path
import sys
import pandas as pd


# ============================================================
# PATHS
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]

SRC_DIR = SCRIPT_DIR / "src"
D5_ANALYSIS_DIR = REPO_ROOT / "Deliverables/Deliverable-5/src"

# Allow Python to find the reusable modules
sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(D5_ANALYSIS_DIR))


# ============================================================
# INPUT FILES
# ============================================================

AIRBNB_FILES = [
    REPO_ROOT
    / "Deliverables/Deliverable-3/Output/Updated_listings/listings_july_2026_updated.csv",

    REPO_ROOT
    / "Deliverables/Deliverable-3/Output/Updated_listings/listings_august_2026_updated.csv",
]

BOND_FILE = (
    REPO_ROOT
    / "Deliverables/Deliverable-4/Output/cleaned_rental_bond_data.csv"
)


# ============================================================
# OUTPUT FILES
# ============================================================

OUTPUT_DIR = SCRIPT_DIR / "Output"

MERGED_OUTPUT = (
    OUTPUT_DIR
    / "july_august_2026_airbnb_with_rental_bonds.csv"
)


# ============================================================
# IMPORT REUSABLE FUNCTIONS
# ============================================================

from airbnb_cleaning import clean_airbnb
from query_api import add_area_codes
from rental_bond_merge import merge_airbnb_bonds

from deliverable_5_analysis import (
    load_and_validate_data,
    plot_price_gap,
    plot_listing_volumes,
)


# ============================================================
# LOAD AIRBNB DATA
# ============================================================

def load_airbnb_months():
    """
    Load the July and August 2026 Airbnb datasets
    and combine them into one DataFrame.
    """

    frames = []

    for file_path in AIRBNB_FILES:

        if not file_path.exists():
            raise FileNotFoundError(
                f"Airbnb input file not found: {file_path}"
            )

        print(f"Loading: {file_path.name}")

        df = pd.read_csv(file_path)

        print(f"  Rows loaded: {len(df)}")

        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)

    print(f"\nCombined Airbnb rows: {len(combined)}")

    return combined


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_pipeline():

    print("=" * 60)
    print("D7 AUTOMATED AIRBNB + RENTAL BOND PIPELINE")
    print("=" * 60)


    # Create output folder if it does not already exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


    # --------------------------------------------------------
    # STEP 1 — LOAD JULY + AUGUST AIRBNB DATA
    # --------------------------------------------------------

    print("\n[1/5] Loading Airbnb data...")

    airbnb = load_airbnb_months()


    # --------------------------------------------------------
    # STEP 2 — CLEAN AIRBNB DATA
    # --------------------------------------------------------

    print("\n[2/5] Cleaning Airbnb data...")

    cleaned = clean_airbnb(airbnb)


    # --------------------------------------------------------
    # STEP 3 — ADD AREA CODES
    # --------------------------------------------------------

    print("\n[3/5] Adding Koordinates area codes...")

    mapped = add_area_codes(cleaned)


    # --------------------------------------------------------
    # STEP 4 — MERGE RENTAL BOND DATA
    # --------------------------------------------------------

    print("\n[4/5] Merging rental bond data...")

    if not BOND_FILE.exists():
        raise FileNotFoundError(
            f"Rental bond file not found: {BOND_FILE}"
        )

    bonds = pd.read_csv(BOND_FILE)

    merged = merge_airbnb_bonds(
        mapped,
        bonds
    )


    # --------------------------------------------------------
    # SAVE FINAL MERGED DATASET
    # --------------------------------------------------------

    merged.to_csv(
        MERGED_OUTPUT,
        index=False
    )

    print("\nMerged dataset saved:")
    print(MERGED_OUTPUT)

    print(f"Final merged rows: {len(merged)}")


    # --------------------------------------------------------
    # STEP 5 — RUN EXISTING ANALYSIS
    # --------------------------------------------------------

    print("\n[5/5] Running existing analysis...")

    analysis_df = load_and_validate_data(
        MERGED_OUTPUT
    )


    # --------------------------------------------------------
    # GENERATE UPDATED PLOTS
    # --------------------------------------------------------

    print("\nGenerating updated plots...")


    # Price gap — all areas
    plot_price_gap(
        analysis_df,
        "July-August 2026",
        OUTPUT_DIR / "price_gap_all_areas.png"
    )


    # Price gap — top 15 areas
    plot_price_gap(
        analysis_df,
        "July-August 2026 - Top 15 Areas",
        OUTPUT_DIR / "price_gap_top15.png",
        top_n=15
    )


    # Listing volumes — all areas
    plot_listing_volumes(
        analysis_df,
        "July-August 2026",
        OUTPUT_DIR / "listing_volumes_all_areas.png"
    )


    # Listing volumes — top 15 areas
    plot_listing_volumes(
        analysis_df,
        "July-August 2026 - Top 15 Areas",
        OUTPUT_DIR / "listing_volumes_top15.png",
        top_n=15
    )


    # --------------------------------------------------------
    # FINAL SUMMARY
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("D7 PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)

    print(f"Input Airbnb rows: {len(airbnb)}")
    print(f"Cleaned Airbnb rows: {len(cleaned)}")
    print(f"Area-coded rows: {len(mapped)}")
    print(f"Final merged rows: {len(merged)}")
    print(f"Rows used for analysis: {len(analysis_df)}")

    print(f"\nOutput directory:")
    print(OUTPUT_DIR)

    print("\nGenerated files:")
    print(f"- {MERGED_OUTPUT.name}")
    print("- price_gap_all_areas.png")
    print("- price_gap_top15.png")
    print("- listing_volumes_all_areas.png")
    print("- listing_volumes_top15.png")

    print("\nD7 automation finished.")


# ============================================================
# EXECUTE PIPELINE
# ============================================================

if __name__ == "__main__":
    run_pipeline()